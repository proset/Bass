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

def log(step, msg): 
    print(f"[{step}] {msg}")

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

## 4.2. Recomendación a la Dirección
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
    hist_table = "## 2. Datos Históricos\n\n| Año | Adopción (M) |\n|---|---|\n"
    for a, v in sorted(real_series.items()):
        hist_table += f"| {a} | {v:.2f} M |\n"
        
    metrics_table = "## 3. Métricas\n\n| Modelo | R² | MAPE | Score | k |\n|---|---|---|---|---|\n"
    for mk, p in params.items():
        name = model_labels.get(mk, mk)
        metrics_table += f"| {name} | {float(p.get('r_cuadrado',0)):.4f} | {float(p.get('mape_ajuste',0)):.2f}% | {float(p.get('score',0)):.2f} | {p.get('n_params', '?')} |\n"
        
    proj_table = f"## 4. Proyecciones\n\n| Año | {recommended_model_name} (M) |\n|---|---|\n"
    for i, year in enumerate(range(last_year + 1, last_year + 11)):
        proj_table += f"| {year} | {float(y_proj[i]):.2f} M |\n"
        
    datos_oficiales = f"**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado ({recommended_model_name}): R²={float(recommended_params.get('r_cuadrado',0)):.4f}, MAPE={float(recommended_params.get('mape_ajuste',0)):.2f}%, Score={float(recommended_params.get('score',0)):.2f}."
    
    formulations = """* **Bass Clásico (1969)** — Modelo de Bass Clásico:
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
    
    report = f"# Informe de Adopción: {tech}\n\n{analysis}\n\n{hist_table}\n\n{metrics_table}\n\n{proj_table}\n\n{datos_oficiales}\n\n### 📐 Formulación Matemática de los Modelos Evaluados\n\n{formulations}\n"
    
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
    extract(tech)
    
    log("2/3", "Verificando y ajustando con GLM...")
    verify_and_fit(tech)
    
    log("3/3", "Análisis y redacción con Claude...")
    analyze_with_claude(tech)
    
    print(f"\n{'='*60}\n  REPORT: informe_global_{tech}.md\n{'='*60}\n")

if __name__ == "__main__":
    main()
