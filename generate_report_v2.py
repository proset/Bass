#!/usr/bin/env python
"""BASS v2: Gemini ext + GLM fit + Claude analysis. Sin Groq loop. $0.06/tech, 30 segundos."""

import sys
import os
import subprocess
import json
import numpy as np
import anthropic

BASS_DIR = r"C:\Users\roset\Bass"
GLM_DIR = r"C:\Users\roset\GLM"
sys.path.insert(0, BASS_DIR)

def data_quality_gate(real_series):
    """
    Gate determinista de calidad de datos. Retorna (ok, sospechosos, motivos).
    Reglas baratas que se comprueban ANTES de llamar a Claude.
    """
    import numpy as np
    years = sorted(real_series.keys())
    values = [real_series[y] for y in years]
    sospechosos = []
    motivos = []
    
    # Regla 1: puntos no-cero insuficientes ( Early Stage mínimo)
    non_zero = [v for v in values if v > 0]
    if len(non_zero) < 4:
        motivos.append(f"Solo {len(non_zero)} puntos no-cero (mínimo 4)")
        # No es fatal para el gate: Claude decidirá. Pero se marca.
        
    # Regla 2: saltos absurdos (>10x entre años consecutivos, ambos no-cero)
    for i in range(1, len(values)):
        prev, curr = values[i-1], values[i]
        if prev > 0 and curr > 0:
            ratio = curr / prev
            if ratio > 10:
                sospechosos.append(years[i])
                motivos.append(f"Salto {ratio:.0f}x en {years[i]} ({prev}→{curr})")
                
    # Regla 3: valor no-cero seguido de cero (adopción no puede "des-aparecer")
    for i in range(1, len(values)):
        if values[i-1] > 0 and values[i] == 0:
            sospechosos.append(years[i])
            motivos.append(f"Adopción cayó a 0 en {years[i]} tras {values[i-1]}M en {years[i-1]}")
            
    # Regla 4: no-monotonía (decrecimiento)
    for i in range(1, len(values)):
        if values[i] < values[i-1]:
            sospechosos.append(years[i])
            motivos.append(f"Serie decrece en {years[i]}")
            
    ok = len(sospechosos) == 0
    return ok, sorted(set(sospechosos)), motivos

def claude_judge_data(tech, real_series, sospechosos, motivos):
    """
    Claude juez: evalúa la serie extraída contra su conocimiento del sector.
    Detecta lo que las reglas no pueden: valores implausibles aunque
    formalmente consistentes (grok 2024=0.04M pasa las reglas si no hay salto).
    Retorna: (veredicto, años_sospechosos_claude, razonamiento)
    veredicto: "CONFIABLE" | "SOSPECHOSO" | "INSERVIBLE"
    """
    import anthropic, os, json
    
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    serie_str = "\n".join(f"  {y}: {v}M" for y, v in sorted(real_series.items()))
    sospechosos_str = ", ".join(str(y) for y in sospechosos) if sospechosos else "ninguno detectado por reglas"
    motivos_str = "; ".join(motivos) if motivos else "sin hallazgos deterministas"
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        temperature=0,
        messages=[{
            "role": "user",
            "content": f"""Eres un verificador de datos de adopción tecnológica. Juzga la siguiente serie extraída de la web para '{tech}' contra TU CONOCIMIENTO del sector. NO busques en la web — usa lo que sabes.

SERIE EXTRAÍDA (adopción acumulada en millones):
{serie_str}

HALLAZGOS DE REGLAS DETERMINISTAS:
  Años sospechosos: {sospechosos_str}
  Motivos: {motivos_str}

EVALÚA cada año:
1. ¿El valor es PLAUSIBLE para esta tecnología en ese año? (compara con lo que sabes del producto: lanzamiento, crecimiento, tamaño de mercado)
2. ¿La MÉTRICA parece consistente entre años? (MAU vs visitas vs acumulado — un salto 8x puede indicar métricas mezcladas)
3. ¿Faltan años con datos conocidos? (si el producto existía con usuarios y el valor es 0, es un error de extracción)

CASOS DE REFERENCIA de errores reales que debes detectar:
- Un valor casi-cero en un año donde el producto tenía millones de usuarios (ej: 0.04M) → error de extracción
- Un salto enorme compatible con mezcla de métricas (ej: MAU anual → usuarios acumulados) → inconsistencia
- Años con 0 cuando el producto ya estaba lanzado → dato faltante
- Producto discontinuado → la serie no debería proyectarse

RESPONDE EN ESTE FORMATO EXACTO (JSON):
{{
  "veredicto": "CONFIABLE" | "SOSPECHOSO" | "INSERVIBLE",
  "anos_sospechosos": [lista de años con problemas],
  "razon_por_ano": {{"año": "explicación breve del problema detectado"}},
  "producto_muerto": true | false,
  "razonamiento_general": "2-3 frases sobre la calidad global de la serie"
}}

CONFIABLE = datos defendibles, seguir al fit.
SOSPECHOSO = hay años problemáticos que necesitan re-extracción o corrección.
INSERVIBLE = la serie no sirve (producto muerto, métrica incoherente global, años imposibles) — no intentar corregir."""
        }]
    )
    
    text = response.content[0].text.strip()
    
    # Limpiar markdown wrapping si existe
    if text.startswith("```"):
        import re
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        
    try:
        result = json.loads(text)
        return result.get("veredicto", "SOSPECHOSO"), result.get("anos_sospechosos", []), result
    except json.JSONDecodeError:
        return "SOSPECHOSO", sospechosos, {"error": "JSON parse falló", "raw": text[:500]}

def log(step, msg): 
    print(f"[{step}] {msg}")

def reextract_directed(tech, anos_sospechosos, razon_por_ano):
    """
    Re-extracción quirúrgica: solo los años que el juez marcó.
    Búsqueda dirigida por año con instrucciones específicas del problema.
    Retorna: dict {año: nuevo_valor} o None si no mejoró.
    """
    from ai.gemini_client import generate_content_with_fallback
    import json
    
    anos_str = ", ".join(str(a) for a in anos_sospechosos)
    razones_str = "\n".join(f"  {a}: {r}" for a, r in razon_por_ano.items())
    
    prompt = f"""Busca datos de adopción de '{tech}' ESPECÍFICAMENTE para los años: {anos_str}.

PROBLEMAS DETECTADOS EN LA EXTRACCIÓN ANTERIOR:
{razones_str}

INSTRUCCIONES DE BÚSQUEDAD DIRIGIDA:
1. Busca el MAU o usuarios activos de esta tecnología para CADA año listado.
2. Para productos web: "MAU {tech} {{año}}", "dominio traffic {{año}}"
3. Para apps: "app downloads/users {{año}} SensorTower"
4. Para APIs/empresas: "empresa users {{año}} earnings"
5. CITA LA FUENTE de cada valor.
6. Si el producto NO EXISTÍA ese año, responde 0.
7. Si no encuentras el dato, responde null (NO inventes).

FORMATO (JSON):
{{
  "correcciones": {{
    "año": {{"valor": X, "fuente": "...", "confianza": "alta|media|baja"}}
  }}
}}
IMPORTANTE: 'valor' DEBE ser estrictamente un NÚMERO (flotante) representando MILLONES de usuarios.
Ejemplo: si son 300,000 usuarios, valor = 0.3. Si son 1,500 millones, valor = 1500.0. NO uses texto ni rangos en 'valor'."""
    
    try:
        respuesta = generate_content_with_fallback(prompt=prompt, tools=[{"google_search": {}}])
        text = respuesta.text.strip()
        
        if text.startswith("```"):
            import re
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            
        data = json.loads(text)
        correcciones = {}
        for y_str, info in data.get("correcciones", {}).items():
            val = info.get("valor")
            correcciones[y_str] = val
        return correcciones
    except Exception as e:
        print(f"[verify] Error en re-extracción: {e}")
        return None

def generar_informe_insuficiente(tech, serie, detalle):
    """Informe honesto cuando los datos no sirven. Producto válido, no error."""
    serie_str = "\n".join(f"| {y} | {v:.2f} M |" for y, v in sorted(serie.items()))
    razon = detalle.get("razonamiento_general", "Los datos disponibles no permiten un ajuste fiable.")
    muerto = detalle.get("producto_muerto", False)
    contexto_muerto = "\n\n**PRODUCTO DISCONTINUADO:** esta tecnología ya no existe en el mercado. Este informe documenta su trayectoria histórica y el motivo por el que no se proyecta." if muerto else ""
    
    informe = f"""# Informe de Adopción: {tech}

## DATOS INSUFICIENTES PARA PROYECCIÓN

Este informe no incluye proyecciones de adopción porque la calidad de los datos disponibles no permite un ajuste fiable.{contexto_muerto}

### Serie disponible
| Año | Adopción (M) |
|---|---|
{serie_str}

### Motivo
{razon}

### Qué haría falta
- Serie histórica más larga (mínimo 4-6 puntos con datos verificados)
- Métrica consistente entre años (MAU, usuarios, unidades — sin mezclar)
- Si la empresa no publica datos: añadir valores verificados a custom_anchors.json

### Cuándo reintentar
Re-ejecuta el pipeline cuando dispongas de más historial o anchors verificados: los productos jóvenes acumulan un punto de datos por año.
"""
    with open(f"informe_global_{tech}.md", "w", encoding="utf-8") as f:
        f.write(informe)

def persistir_serie_corregida(tech, serie):
    from data.ingestion import insertar_historico_db
    datos = []
    for a, v in sorted(serie.items()):
        datos.append({"anio": a, "usuarios_millones": v})
    insertar_historico_db(tech, datos)

def build_deviation_table(params, real_series, model_labels):
    """Desviación de cada modelo por año (histórico)."""
    from models.analytical_projections import project_model
    import numpy as np
    
    years = sorted(real_series.keys())
    t_hist = np.arange(len(years), dtype=float)
    real_vals = [real_series[y] for y in years]
    
    header = "| Año | Real (M) |"
    models = [mk for mk in params.keys()]
    for mk in models:
        name = model_labels.get(mk, mk)
        header += f" {name} (M) |"
    rows = [header, "|" + " --- |" * (len(models) + 1)]
    
    # Calcular predicciones de cada modelo para años históricos
    preds = {}
    for mk in models:
        p = params[mk]
        try:
            y_pred = project_model(mk, p, t_hist)
            preds[mk] = y_pred
        except Exception:
            preds[mk] = None
            
    for i, year in enumerate(years):
        row = f"| {year} | {real_vals[i]:.2f} |"
        for mk in models:
            if preds[mk] is not None and not np.isnan(preds[mk][i]):
                row += f" {preds[mk][i]:.2f} |"
            else:
                row += " N/D |"
        rows.append(row)
        
    return "\n".join(rows)

def build_all_projections_table(params, real_series, model_labels):
    """Proyecciones 2026-2035 de todos los modelos."""
    from models.analytical_projections import project_model
    import numpy as np
    
    years = sorted(real_series.keys())
    first_year = years[0]
    last_year = years[-1]
    
    t_proj = np.arange(len(years) + 10, dtype=float)
    proj_years = list(range(first_year, last_year + 11))
    
    # Ordenar modelos por Score (mejor primero)
    sorted_models = sorted(params.items(), key=lambda x: -float(x[1].get("score", 0)))
    
    header = "| Año |"
    for mk, p in sorted_models:
        name = model_labels.get(mk, mk)
        header += f" {name} (M) |"
    rows = [header, "|" + " --- |" * (len(sorted_models) + 1)]
    
    # Calcular proyecciones
    projections = {}
    for mk, p in sorted_models:
        try:
            y_proj = project_model(mk, p, t_proj)
            # Monotonicidad solo en proyecciones futuras
            last_val = list(real_series.values())[-1]
            idx_future = np.where(np.array(proj_years) > last_year)[0]
            if len(idx_future) > 0:
                y_proj[idx_future] = np.maximum(y_proj[idx_future], last_val)
            projections[mk] = y_proj
        except Exception:
            projections[mk] = None
            
    for i, year in enumerate(proj_years):
        row = f"| {year} |"
        for mk, p in sorted_models:
            if projections[mk] is not None and not np.isnan(projections[mk][i]):
                row += f" {projections[mk][i]:.2f} |"
            else:
                row += " N/D |"
        rows.append(row)
        
    return "\n".join(rows)

def build_formulations_section():
    """Renderiza las formulaciones de los 10 modelos (Fix 23/26)."""
    return """### 📐 Formulación Matemática de los Modelos Evaluados

* **Bass Clásico (1969)** — Modelo de Bass Clásico:
  x(t) = m * (1 - exp(-(p + q) * t)) / (1 + (q / p) * exp(-(p + q) * t))

* **Dual Market (Roset & Canals, 2011)** — Modelo de Dos Mercados Independientes:
  x(t) = x1(t) + x2(t), donde x1 y x2 son modelos clásicos de Bass independientes:
  xi(t) = mi * (1 - exp(-(pi + qi) * t)) / (1 + (qi / pi) * exp(-(pi + qi) * t))

* **Fourt & Woodlock (1960)** — Modelo de Innovación Pura:
  N(t) = m * (1 - exp(-p * t))

* **Gompertz (1825)** — Modelo Asimétrico de Gompertz:
  N(t) = m * exp(-exp(-k * (t - t0)))

* **Bass Generalizado (GBM) (1994)** — Modelo de Bass Generalizado:
  dN/dt = (p + (q / m) * N(t)) * (m - N(t)) * (1 + beta * t)

* **Horsky & Simon (1983)** — Modelo con Publicidad:
  dN/dt = (p0 + alpha * ln(1 + t) + (q / m) * N(t)) * (m - N(t))

* **Muller & Yogev (2006)** — Modelo del Efecto Saddle:
  I(t) = Ni * (1 - exp(-(pi + qi) * t)) / (1 + (qi / pi) * exp(-(pi + qi) * t))
  dM/dt = (pm + qm * M(t) / (Ni + Nm) + qim * I(t) / (Ni + Nm)) * (Nm - M(t))

* **Van den Bulte & Joshi (2007)** — Modelo de Influenciadores e Imitadores:
  F1(t) = (1 - exp(-(p1 + q1) * t)) / (1 + (q1 / p1) * exp(-(p1 + q1) * t))
  dF2/dt = q2 * (w * F1(t) + (1 - w) * F2(t)) * (1 - F2(t))
  N(t) = M1 * F1(t) + M2 * F2(t)

* **Difusión Logística R&K (Ryu & Kim)** — Modelo Logístico de Difusión-Convergencia:
  L(t) = b1 / (1 + ((b1 - b0) / b0) * exp(-k2 * (t - t0)))

* **Ladrón-de-Guevara & Putsis (2011)** — Modelo de Mercado Potencial Dinámico y Endógeno:
  C(t) = 1.0 - theta * exp(-gamma * N(t) / S), donde M(t) = C(t) * S y la difusión es:
  dN/dt = (alpha + beta * (N / M)) * (M - N)"""

def build_scenarios_table(params, real_series, model_labels):
    """Escenarios: conservador / base / optimista para 2030 y 2035."""
    from models.analytical_projections import project_model
    import numpy as np
    
    years = sorted(real_series.keys())
    last_year = years[-1]
    t_proj = np.arange(len(years), len(years) + 10, dtype=float)
    last_val = list(real_series.values())[-1]
    
    # Escenarios: conservador = modelo parsimonioso (k=3) con mejor R²;
    # base = modelo recomendado; optimista = modelo con proyección 2035 más alta (excluyendo absurdos)
    
    best_model = max(params.items(), key=lambda x: float(x[1].get("score", 0)))
    rec_key = best_model[0]
    
    # Parsimonioso: Bass_Clasico o Gompertz (k=3) con mejor R²
    parsimonious = [mk for mk in params if params[mk].get("n_params", 10) <= 3]
    cons_key = max(parsimonious, key=lambda mk: float(params[mk].get("r_cuadrado", 0))) if parsimonious else rec_key
    
    # Optimista: mejor proyección 2035 que no supere 3x el último dato (evitar absurdos)
    opt_key = None
    opt_2035 = -1
    for mk, p in params.items():
        try:
            y_proj = project_model(mk, p, t_proj)
            y_proj = np.maximum(y_proj, last_val)
            v2035 = float(y_proj[9])
            if v2035 <= last_val * 3 and v2035 > opt_2035:
                opt_2035 = v2035
                opt_key = mk
        except Exception:
            continue
    if opt_key is None:
        opt_key = rec_key
        
    rows = ["| Escenario | Modelo | 2030 (M) | 2035 (M) |", "| --- | --- | --- | --- |"]
    for label, mk in [("Conservador", cons_key), ("Base (recomendado)", rec_key), ("Optimista", opt_key)]:
        p = params[mk]
        y_proj = project_model(mk, p, t_proj)
        y_proj = np.maximum(y_proj, last_val)
        name = model_labels.get(mk, mk)
        rows.append(f"| {label} | {name} | {float(y_proj[4]):.2f} | {float(y_proj[9]):.2f} |")
        
    return "\n".join(rows)

def build_sources_table(df_hist, tech):
    """Tabla de fuentes: año, valor, tipo (real/estimado)."""
    rows = ["| Año | Valor (M) | Tipo |", "| --- | --- | --- |"]
    for _, row in df_hist.iterrows():
        is_est = bool(row.get("is_estimate", False))
        tipo = "Estimado (fuentes secundarias)" if is_est else "Real (reportado)"
        rows.append(f"| {int(row['anio'])} | {float(row['adopcion_acumulada']):.2f} | {tipo} |")
    return "\n".join(rows)

# --- Step 1: Gemini extraction (existing) ---
def extract(tech):
    from ai.analysis import obtener_datos_y_analisis_ia
    from data.ingestion import insertar_historico_db, guardar_analisis_cualitativo
    
    datos, analisis_text = obtener_datos_y_analisis_ia(tech)
    if analisis_text is None or (isinstance(analisis_text, str) and analisis_text.strip() == ""):
        analisis_text = "No disponible."
        
    insertar_historico_db(tech, datos)
    guardar_analisis_cualitativo(tech, analisis_text)
    log("1/3", f"Extraído: {len(datos)} puntos")
    return datos

# --- Step 2: Verify + Fit (existing) ---
def verify_and_fit(tech):
    result = subprocess.run(["python", "persist_fit.py", tech], cwd=GLM_DIR, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        log("2/3", "ERROR: fit failed")
        sys.exit(1)

def get_extraction_context(tech):
    """Lee la prosa de extracción de Gemini (qualitative_analysis en BD)."""
    from data.loaders import load_qualitative_analysis
    text = load_qualitative_analysis(tech)
    if not text or text.strip() == "" or "No disponible" in text:
        return "No hay contexto de mercado disponible de la extracción."
    return text

# --- Step 3: Claude analysis ---
def analyze_with_claude(tech):
    from data.loaders import load_historical_data, load_model_parameters
    from models.analytical_projections import project_model
    
    model_labels = {
        "Bass_Clasico": "Bass Clásico",
        "Dual_Market": "Dual Market",
        "Fourt_Woodlock": "Fourt & Woodlock",
        "Gompertz": "Gompertz",
        "Generalized_Bass": "Bass Generalizado (GBM)",
        "Horsky_Simon": "Horsky & Simon",
        "Muller_Yogev": "Muller & Yogev",
        "VdB_Joshi": "Van den Bulte & Joshi",
        "Logistic_Diffusion_Convergence": "Difusión Logística R&K",
        "Ladron_Putsis": "Ladrón-de-Guevara & Putsis",
    }
    
    df_hist = load_historical_data(tech)
    params = load_model_parameters(tech)
    real_series = {int(a): float(v) for a, v in zip(df_hist["anio"], df_hist["adopcion_acumulada"])}
    
    best_model = max(params.items(), key=lambda x: float(x[1].get("score", 0)))
    recommended_model_key = best_model[0]
    recommended_model_name = model_labels.get(recommended_model_key, recommended_model_key)
    recommended_params = best_model[1]
    
    # Proyecciones
    last_year = max(real_series.keys())
    t_proj = np.arange(len(real_series), len(real_series) + 10, dtype=float)
    y_proj = project_model(recommended_model_key, recommended_params, t_proj)
    last_val = list(real_series.values())[-1]
    y_proj = np.maximum(y_proj, last_val)
    
    # Extraer contexto cualitativo
    extraction_context = get_extraction_context(tech)
    
    # Claude analysis
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    hist_str = "\n".join(f"{int(df_hist.iloc[i]['anio'])}: {float(df_hist.iloc[i]['adopcion_acumulada']):.2f}M" for i in range(len(df_hist)))
    fit_str = "\n".join(f"- {model_labels.get(mk, mk)}: R²={float(p.get('r_cuadrado',0)):.4f}, MAPE={float(p.get('mape_ajuste',0)):.2f}%, Score={float(p.get('score',0)):.2f}" for mk, p in params.items())
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        temperature=0.0,
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f"""Eres un analista de adopción tecnológica. Redacta el análisis cualitativo del informe de '{tech}'.

CONTEXTO DE MERCADO (de la extracción con búsqueda web — úsalo como base, corrígelo si contiene errores, complétalo con tu conocimiento del sector):
{extraction_context}

DATOS HISTÓRICOS:
{hist_str}
RESULTADOS DEL AJUSTE (10 modelos):
{fit_str}
MODELO RECOMENDADO: {recommended_model_name} (Score={float(recommended_params.get('score',0)):.2f})
PROYECCIONES:  2030: {float(y_proj[4]):.1f}M  2035: {float(y_proj[9]):.1f}M

INSTRUCCIONES ESTRICTAS:
1. NO escribas NINGÚN número en la prosa narrativa (ni adopción, ni R², ni MAPE, ni Score, ni porcentajes, ni incrementos). Las cifras van en tablas aparte. ÚNICA excepción: números dentro de tablas markdown que tú mismo generes (señaladas como tablas, con formato de | Año | Valor |).
2. NO cites años entre paréntesis (modelos SOLO por nombre: "Gompertz", "Dual Market").
3. FORMATO DE NÚMEROS EN TABLAS: usa punto decimal (1052.00), NUNCA coma como miles (no "~1,052"). Sin virgulillas (~). Formato idéntico a las tablas de Python: valor con 2 decimales.
4. Escribe estas secciones:

## 1. Resumen Ejecutivo
(Resumen. Modelo seleccionado y por qué. Fase de crecimiento. Nivel de confianza de la proyección: ALTA/MEDIA/BAJA con justificación.)

## 3. Análisis del Mercado y Contexto Competitivo
(Usa el CONTEXTO DE MERCADO de la extracción y tu conocimiento del sector. Cubre: drivers de adopción (factores que impulsan), competidores clave y dinámica competitiva, barreras de adopción (factores que frenan), tendencias tecnológicas y regulatorias, y factores externos relevantes (pandemias, políticas, crisis). Sin cifras en prosa.)

## 5. Análisis Cualitativo y Validación Estadística
Además del análisis cualitativo, realiza ESTAS 4 validaciones analíticas:
a) CONTROL DE SOBREAJUSTE (AIC mental): Con n puntos de datos y k parámetros por modelo, evalúa si el modelo ganador justifica su complejidad. Regla práctica: si k_ganador > n/2, advierte explícitamente "riesgo alto de sobreajuste". Si dos modelos tienen R² similares pero k distinto, señala que el parsimonioso puede generalizar mejor.
b) DETECCIÓN DE DEGENERACIÓN PARAMÉTRICA: Si dos o más modelos muestran métricas de ajuste prácticamente idénticas (R² y MAPE iguales), explica que esto indica colapso paramétrico: los parámetros "extra" del modelo complejo se vuelven irrelevantes con pocos datos, y el modelo colapsa matemáticamente al más simple. NO es un error de cálculo, es una limitación de identificabilidad.
c) CONTRASTE CON REFERENCIAS EXTERNAS: Usa tu conocimiento del sector. Si conoces proyecciones de autoridades de referencia (IEA para energía/vehículos, Gartner/IDC para tecnología, OMS para salud), compáralas CUALITATIVAMENTE con la proyección del modelo. Si divergen fuertemente (más de 2x), advierte explícitamente: "la proyección del modelo se sitúa muy por debajo/encima de la referencia del sector, que atribuye la diferencia a factores que los datos históricos no capturan (políticas, precios, mercados emergentes)". NO inventes cifras de referencias — si no conoces una referencia confiable, escribe "no se identificó referencia externa confiable para contraste".
d) MODULACIÓN DE CONFIANZA: Concluye el análisis con una valoración explícita:
   - Datos (n puntos): suficientes/insuficientes para el modelo seleccionado
   - Sobreajuste: riesgo alto/medio/bajo (justificar con k vs n)
   - Conclusión: "proyección OPERATIVA" (fiable para decisiones) o "proyección INDICATIVA" (sujeta a revisión) o "proyección TENTATIVA" (no usar para decisiones sin más datos)

## 6. Marco Académico Teórico
(Formulación conceptual del modelo. Comparación con otros modelos. Relación con teoría de difusión.)

## 7. Recomendación a la Dirección
(Recomendación estratégica que INTEGRE el nivel de confianza del punto (d): si la proyección es INDICATIVA o TENTATIVA, la recomendación debe reflejar cautela. Sin cifras específicas.)

Si la empresa es privada (no publica usuarios oficiales), incluye al inicio del Resumen Ejecutivo:
"NOTA DE FUENTE DE DATOS: [empresa] no publica usuarios oficiales. Datos estimados. Incertidumbre: alta."
"""
        }]
    )
    
    analysis = ""
    for block in response.content:
        if getattr(block, "type", "") == "text":
            analysis += getattr(block, "text", "")
            
    # Tablas determinísticas
    hist_table = "| Año | Adopción (M) |\n|---|---|\n"
    for a, v in sorted(real_series.items()):
        hist_table += f"| {a} | {v:.2f} M |\n"
        
    deviation_table = build_deviation_table(params, real_series, model_labels)
    sources_table = build_sources_table(df_hist, tech)
        
    metrics_table = "## 3bis. Métricas\n\n| Modelo | R² | MAPE | Score | k |\n|---|---|---|---|---|\n"
    for mk, p in params.items():
        name = model_labels.get(mk, mk)
        metrics_table += f"| {name} | {float(p.get('r_cuadrado',0)):.4f} | {float(p.get('mape_ajuste',0)):.2f}% | {float(p.get('score',0)):.2f} | {p.get('n_params', '?')} |\n"
        
    all_projections_table = build_all_projections_table(params, real_series, model_labels)
    scenarios_table = build_scenarios_table(params, real_series, model_labels)
    formulations_section = build_formulations_section()
        
    r2 = float(recommended_params.get('r_cuadrado',0))
    mape = float(recommended_params.get('mape_ajuste',0))
    score = float(recommended_params.get('score',0))
    
    report = f"""# Informe de Adopción: {tech}

{analysis}

## 2. Datos Históricos y Desviaciones

### 2.1 Serie Histórica Real
{hist_table}

### 2.2 Desviaciones por Modelo (Ajuste Histórico)
{deviation_table}

### 2.3 Fuentes de Datos
{sources_table}

{metrics_table}

## 4. Proyecciones

### 4.1 Proyecciones de Todos los Modelos
{all_projections_table}

### 4.2 Escenarios de Consenso
{scenarios_table}

**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado ({recommended_model_name}): R²={r2:.4f}, MAPE de ajuste={mape:.2f}%, Score={score:.2f}.

{formulations_section}
"""
    
    report_file = f"informe_global_{tech}.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
        
    log("3/3", f"Claude tokens: {response.usage.input_tokens} input, {response.usage.output_tokens} output")
    log("3/3", f"Reporte generado: {report_file}")
    return True

def main():
    tech = sys.argv[1] if len(sys.argv) > 1 else "electric vehicles"
    print(f"\n{'='*60}\n  BASS v2 FINAL: Gemini ext + GLM fit + Claude ana: '{tech}'\n{'='*60}\n")
    
    log("1/3", "Extracción con Gemini...")
    from data.loaders import load_historical_data
    extract(tech)
    
    # FASE 1.5: CASCADA DE VERIFICACIÓN (v2.3)
    df_hist = load_historical_data(tech)
    serie = {int(row["anio"]): float(row["adopcion_acumulada"]) for _, row in df_hist.iterrows()}
    
    ok, sospechosos, motivos = data_quality_gate(serie)
    veredicto, anos_claude, detalle = claude_judge_data(tech, serie, sospechosos, motivos)
    
    print(f"[verify] Gate determinista: {'OK' if ok else 'SOSPECHOSO'} ({len(sospechosos)} años)")
    print(f"[verify] Claude juez: {veredicto}")
    if detalle.get("razonamiento_general"):
        razonamiento = detalle['razonamiento_general'][:200].replace('→', '->')
        print(f"[verify] Claude: {razonamiento}")
        
    if veredicto == "INSERVIBLE" or detalle.get("producto_muerto"):
        generar_informe_insuficiente(tech, serie, detalle)
        print("[verify] INSERVIBLE — informe de datos insuficientes generado")
        sys.exit(0)
        
    anos_problema = sorted(set(sospechosos) | set(anos_claude))
    
    if veredicto == "SOSPECHOSO" and anos_problema:
        print(f"[verify] Re-extracción dirigida para: {anos_problema}")
        correcciones = reextract_directed(tech, anos_problema, detalle.get("razon_por_ano", {}))
        if correcciones:
            # Aplicar correcciones a la serie
            corrigio_algo = False
            for ano, val in correcciones.items():
                if val is not None:
                    val_str = str(val).replace('M', '').replace('m', '').replace(',', '').strip()
                    serie[int(ano)] = float(val_str)
                    print(f"[verify] Corregido {ano}: -> {val_str}M")
                    corrigio_algo = True
            
            if corrigio_algo:
                # Re-juzgar la serie corregida (una sola vez)
                veredicto2, _, detalle2 = claude_judge_data(tech, serie, [], [])
                print(f"[verify] Segunda evaluación: {veredicto2}")
                if veredicto2 == "INSERVIBLE":
                    generar_informe_insuficiente(tech, serie, detalle2)
                    sys.exit(0)
                # Persistir la serie corregida en BD
                persistir_serie_corregida(tech, serie)
                
    log("2/3", "Verificando y ajustando con GLM...")
    verify_and_fit(tech)
    
    log("3/3", "Análisis y redacción con Claude...")
    analyze_with_claude(tech)
    
    print(f"\n{'='*60}\n  REPORT: informe_global_{tech}.md\n{'='*60}\n")

if __name__ == "__main__":
    main()
