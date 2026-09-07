import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import logging
import google.ai.generativelanguage_v1beta as gapic
from data.loaders import load_historical_data, load_model_parameters, normalize_tech_name
from models.fit_models import fit_all_models, rank_and_select_best_model
from models.analytical_projections import project_model
from ui.tab_projections import get_consensus_model
from ui.theme import apply_dark_theme, BRAND_COLORS, dark_table_html
from generate_report_v2 import data_quality_gate, claude_judge_data
import anthropic
import os

logger = logging.getLogger("BassTabBenchmarking")



@st.cache_data(ttl=3600)
def get_fitted_models_cached(tech, df_hist):
    t_data = np.arange(len(df_hist))
    n_data = df_hist["adopcion_acumulada"].values
    return fit_all_models(t_data, n_data)

def validar_comparabilidad(techs):
    """Cada tech debe tener: serie en BD + fit persistido."""
    validas = []
    for tech in techs:
        tech_norm = normalize_tech_name(tech)
        df = load_historical_data(tech_norm)
        params = load_model_parameters(tech_norm)
        if len(df) >= 3 and params:
            validas.append(tech_norm)
        else:
            st.warning(f"⚠️ **{tech_norm.title()}**: sin datos o fit suficientes en BD — excluida de la comparación. Ejecuta `python generate_report_v2.py \"{tech_norm}\"` en terminal primero.")
    return validas

@st.cache_data(ttl=3600)
def cascada_benchmarking(tech):
    """Ejecuta la cascada v2.3 sobre la serie de una tech y retorna (serie_validada, confianza, detalle)."""
    df_hist = load_historical_data(tech)
    if df_hist.empty:
        return {}, "INSERVIBLE", "No hay datos en BD"
    serie = {int(row["anio"]): float(row["adopcion_acumulada"]) for _, row in df_hist.iterrows()}
    
    ok, sospechosos, motivos = data_quality_gate(serie)
    veredicto, anos_claude, detalle = claude_judge_data(tech, serie, sospechosos, motivos)
    return serie, veredicto, detalle

def confianza_benchmarking(veredictos):
    """La confianza de la comparación = la MÍNIMA de las individuales.
    Sin veredictos → NO COMPARABLE (no hay nada que comparar)."""
    if not veredictos:
        return "NO COMPARABLE"
    jerarquia = {"CONFIABLE": 2, "SOSPECHOSO": 1, "INSERVIBLE": 0}
    minimo = min(jerarquia.get(v, 0) for v in veredictos.values())
    etiqueta = {2: "OPERATIVA", 1: "INDICATIVA", 0: "NO COMPARABLE"}
    return etiqueta.get(minimo, "NO COMPARABLE")

def calidad_relativa(techs_data):
    """Retorna dict por tech: n_puntos, años_cubiertos, veredicto."""
    info = {}
    for tech, (serie, veredicto, detalle) in techs_data.items():
        pts_reales = sum(1 for v in serie.values() if v > 0)
        rango = f"{min(serie.keys())}-{max(serie.keys())}" if serie else "N/D"
        info[tech] = {
            "puntos_reales": pts_reales,
            "rango": rango,
            "veredicto": veredicto,
        }
    return info

def normalizar_tam_cluster(techs_data, clasifs, brand_data):
    """
    Cluster competitivo (competidores mutuos) -> TAM común -> re-escalar 
    las proyecciones de las techs del cluster contra el TAM común.
    Las cuotas relativas no cambian; la suma del cluster pasa a significar 
    la cuota total capturada del mercado común.
    """
    # 1. Detectar cluster mutuo (misma lógica que gate_coherencia_competitiva)
    ids = list(techs_data.keys())
    cluster = set()
    for t1 in ids:
        for t2 in ids:
            if t1 == t2: continue
            comp1 = set(c.lower() for c in clasifs.get(t1, {}).get("competidores_directos", []))
            if any(t2.lower() in c or c in t2.lower() for c in comp1):
                cluster.add(t1)
                cluster.add(t2)
                
    if not cluster:
        return brand_data, None  # sin cluster -> sin normalización
        
    # 2. TAM común = máximo de los mercados del cluster
    mercados = {t: float(clasifs.get(t, {}).get("mercado_direccionable_M", 0)) for t in cluster}
    tam_comun = max(mercados.values()) if mercados else 0
    if tam_comun <= 0:
        return brand_data, None
        
    # 3. Verificar coherencia del cluster vs TAM de categoría (Fix 54)
    info_normalizacion = {"tam_comun": tam_comun, "techs": {}}
    suma_techos = 0
    for tech in cluster:
        mercado_propio = mercados[tech]
        info_normalizacion["techs"][tech] = {"mercado_original": mercado_propio, "factor": 1.0}
        
        bdata = brand_data[tech]
        pdict = bdata["params"].get("params", bdata["params"])
        techo = float(pdict.get("param_m1") or pdict.get("param_m") or pdict.get("techo") or 0)
        suma_techos += techo

    if tam_comun > 0:
        delta = abs(suma_techos - tam_comun) / tam_comun
        if delta > 0.15:
            techs_str = ", ".join([t.title() for t in cluster])
            advertencia = (
                f"*Advertencia de Divergencia (Fix 54): los techos persistidos de {techs_str} "
                f"suman {suma_techos:.0f}M, lo que diverge del mercado común de su categoría "
                f"({tam_comun:.0f}M) en más del 15%. Probablemente provienen de corridas en momentos "
                f"distintos con datos distintos. Regenerar los informes individuales para unificar.*\n"
            )
            return brand_data, {"tam_comun": tam_comun, "techs": info_normalizacion["techs"], "advertencia": advertencia}

    return brand_data, {"tam_comun": tam_comun, "techs": info_normalizacion["techs"], "advertencia": ""}

def anclar_cuotas_al_presente(techs_data, clasifs, brand_data, norm_info):
    """
    Fix 53: las cuotas de ESCENARIO BASE se anclan a las cuotas OBSERVADAS 
    hoy (último dato real de cada tech del cluster). Las cuotas de Claude 
    quedan como desviación escénica (optimista/pesimista), no como default.
    
    Racional: sin modelo dinámico, el presente es la mejor predicción del 
    reparto futuro cercano. Cambiar el reparto requiere mecanismo — y no lo hay.
    """
    if not norm_info:
        return brand_data, None  # sin cluster -> sin anclaje
        
    cluster = list(norm_info["techs"].keys())
    tam_comun = norm_info["tam_comun"]
    
    # 1. Cuotas OBSERVADAS hoy (último valor real de cada serie)
    valores_hoy = {}
    for tech in cluster:
        serie = techs_data[tech][0]  # (serie, veredicto, detalle)
        if serie:
            ultimo_anio = max(serie.keys())
            valores_hoy[tech] = serie[ultimo_anio]
            
    total_hoy = sum(valores_hoy.values())
    if total_hoy <= 0:
        return brand_data, None
        
    # 2. Detectar divergencia: cuota hoy vs cuota proyectada del techo
    divergencia_info = {}
    for tech in cluster:
        cuota_hoy = valores_hoy[tech] / total_hoy
        bdata = brand_data[tech]
        pdict = bdata["params"].get("params", bdata["params"])
        techo_actual = float(pdict.get("param_m1") or pdict.get("param_m") or pdict.get("techo") or 0)
        cuota_proyectada = techo_actual / tam_comun if tam_comun else 0
        divergencia_info[tech] = {
            "cuota_hoy": cuota_hoy,
            "cuota_proyectada": cuota_proyectada,
            "delta": cuota_proyectada - cuota_hoy,
            "techo_actual": techo_actual
        }
        
    # 3. Si alguna delta > 10 puntos -> ADVERTENCIA de divergencia (Fix 54)
    max_delta = max(abs(d["delta"]) for d in divergencia_info.values())
    if max_delta <= 0.10:
        return brand_data, None  # coherente -> sin acción
        
    techs_str = ", ".join([t.title() for t in cluster])
    ultimo_anio_max = max(divergencia_info.keys(), key=lambda t: divergencia_info[t]["cuota_hoy"]) # fallback simple
    
    nota_anclaje = (
        f"*Advertencia de Divergencia (Fix 54): el reparto proyectado de {techs_str} "
        f"diverge de las cuotas observadas en la actualidad en más de 10 puntos. "
        f"Esto indica que los informes individuales se generaron con asunciones competitivas "
        f"desactualizadas. Regenerar los informes individuales para sincronizar las cuotas "
        f"con el reparto actual.*\n"
    )
    return brand_data, {"nota": nota_anclaje, "divergencias": divergencia_info}

def gate_coherencia_competitiva(techs_data, clasifs, brand_data):
    """
    Si las techs comparadas son competidoras directas entre sí 
    (según clasificador), la suma de sus techos no puede superar 
    TAM × factor_multiplataforma (~1.5: un usuario puede usar 2-3 
    asistentes, no 10).
    """
    FACTOR_MULTIPLATAFORMA = 1.5
    
    # Detectar cluster competitivo: techs que se listan mutuamente como 
    # competidores directos
    ids = list(techs_data.keys())
    clusters = set()
    for t1 in ids:
        for t2 in ids:
            if t1 == t2: continue
            comp1 = set(c.lower() for c in clasifs.get(t1, {}).get("competidores_directos", []))
            if any(t2.lower() in c or c in t2.lower() for c in comp1):
                clusters.add(t1)
                clusters.add(t2)
                
    if not clusters:
        return None  # no hay competencia cruzada -> sin gate
        
    # Suma de techos del cluster vs mercado común
    mercados = [float(clasifs.get(t, {}).get("mercado_direccionable_M", 0)) for t in clusters]
    tam = max(mercados) if mercados else 0
    
    suma_techos = 0
    for t in clusters:
        p = brand_data[t]["params"]
        pdict = p.get("params", p) if isinstance(p.get("params", None), dict) else p
        m = pdict.get('param_m1', pdict.get('param_m', 0))
        if m == 'N/D': m = 0
        suma_techos += float(m)
        
    if tam > 0 and suma_techos > tam * FACTOR_MULTIPLATAFORMA:
        warning = (f"⚠️ INCOHERENCIA COMPETITIVA: la suma de techos proyectados "
                   f"({suma_techos:.0f}M) supera {FACTOR_MULTIPLATAFORMA}x el mercado "
                   f"direccionable común ({tam:.0f}M). Las proyecciones tratan a "
                   f"competidores como monopolios independientes — interpretar como "
                   f"escenarios teóricos individuales, no como reparto real del mercado.")
        return warning
    return None

def build_benchmarking_prompt(techs_data, calidad, confianza_comp, brand_data, model_labels):
    """Prompt con honestidad estructural: confianza, asimetría, nombres reales."""
    bloques = []
    for tech, (serie, veredicto, detalle) in techs_data.items():
        serie_str = ", ".join(f"{y}: {v}M" for y, v in sorted(serie.items()))
        
        bdata = brand_data[tech]
        m_usado = bdata["modelo_usado"]
        modelo_str = model_labels[m_usado]
        
        # Extraer métricas si existen
        p = bdata["params"]
        pdict = p.get("params", p) if isinstance(p.get("params", None), dict) else p
        
        # Keys CORRECTAS (copiadas de generate_report_v2.py, que funciona):
        r2 = p.get('r_cuadrado', pdict.get('r_cuadrado', 'N/D'))
        if isinstance(r2, (int, float)): r2 = f"{float(r2):.4f}"
        mape = p.get('mape_ajuste', pdict.get('mape_ajuste', 'N/D'))
        if isinstance(mape, (int, float)): mape = f"{float(mape):.2f}%"
        
        # Proyecciones 2030 / 2035
        proj_map = dict(zip(bdata["anios_proj"], bdata["proj"]))
        p30 = f"{proj_map.get(2030, 0):.2f}"
        p35 = f"{proj_map.get(2035, 0):.2f}"
        
        cal = calidad[tech]
        
        bloques.append(f"### {tech.upper()}\n"
                       f"Serie: {serie_str}\n"
                       f"Puntos reales (no-cero): {cal['puntos_reales']} de {len(serie)} años\n"
                       f"Veredicto de datos: {veredicto}\n"
                       f"Modelo recomendado: {modelo_str} (R²={r2}, MAPE={mape})\n"
                       f"Proyecciones: 2030={p30}M, 2035={p35}M")
                       
    bloques_texto = "\n\n".join(bloques)
    
    prompt = f"""Eres un analista estratégico de adopción tecnológica. Redacta el informe de benchmarking comparativo entre las tecnologías listadas abajo.

DATOS DE LAS TECNOLOGÍAS:
{bloques_texto}

CONFIANZA GLOBAL DE ESTA COMPARACIÓN: {confianza_comp}
(La confianza de una comparación es la MÍNIMA de las confianzas individuales.)

INSTRUCCIONES ESTRICTAS:
1. Usa SIEMPRE los nombres reales de las tecnologías. NUNCA "Marca A", "Marca B" ni equivalentes.
2. NO escribas cifras en la prosa narrativa (solo en el contexto de análisis conceptual). Las cifras exactas de series y proyecciones van en las tablas que se generan aparte.
3. ASIMETRÍA DE CALIDAD: si una tecnología tiene notablemente menos puntos de datos o un veredicto más débil que la otra, DEBES señalarlo explícitamente: "las proyecciones de [tech] se basan en [n] puntos y deben tratarse con cautela mayor que las de [tech2] ([m] puntos)".
4. MODULA LAS CONCLUSIONES por la confianza global:
   - OPERATIVA: conclusiones firmes permitidas
   - INDICATIVA: conclusiones siempre condicionadas ("si las tendencias actuales se mantienen", "proyección sujeta a revisión")
   - NO COMPARABLE: (no llegará aquí — se bloquea antes)
5. NUNCA declares "líder indiscutible" o conclusiones definitivas de largo plazo basándote en la proyección de una tech con datos débiles. Las conclusiones competitivas deben reflejar la calidad relativa de cada fuente.
6. Estructura del informe:
   ## 1. Dinámica Competitiva (velocidad de adopción, fase de cada una, coeficientes p/q cuando existan para AMBAS)
   ## 2. Cruce del Abismo (fase de adopción de cada una)
   ## 3. Evolución Comparada (trayectorias, puntos de cruce proyectados SI la confianza lo permite — con cautela si asimétrico)
   ## 4. Advertencias y Limitaciones (asimetría de datos, confianza global, qué fortalecería el análisis)
   ## 5. Recomendaciones Estratégicas (por tecnología, moduladas por la confianza)
"""
    return prompt

def claude_benchmarking_writer(prompt):
    """Llama a Claude para redactar el informe comparativo (mismo modelo analítico que pipeline individual)."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.content[0].text

def ensamblar_informe_benchmarking(techs_data, calidad, confianza_comp, brand_data, model_labels, ia_text, nota_tam=""):
    """Ensambla el informe final con las 4 tablas determinísticas y el texto de la IA."""
    techs_names = [t.title() for t in techs_data.keys()]
    titulo = f"# Informe de Consenso y Benchmarking Estratégico: {' vs '.join(techs_names)}\n"
    titulo += f"**CONFIANZA DE LA COMPARACIÓN: {confianza_comp}**\n\n"
    
    # 1. Serie histórica comparada
    all_years = set()
    for serie, _, _ in techs_data.values():
        all_years.update(serie.keys())
    all_years = sorted(list(all_years))
    
    t1 = "### 1. Serie Histórica Comparada (Millones)\n"
    t1 += "| Año | " + " | ".join(techs_names) + " |\n"
    t1 += "|---|" + "|".join(["---"] * len(techs_names)) + "|\n"
    for y in all_years:
        row = [str(y)]
        for tech in techs_data.keys():
            val = techs_data[tech][0].get(y, "-")
            row.append(str(val) if val == "-" else f"{val}")
        t1 += "| " + " | ".join(row) + " |\n"
    t1 += "\n"
    
    # 2. Modelos recomendados y métricas
    t2 = "### 2. Modelos Recomendados y Métricas de Ajuste\n"
    t2 += "| Tecnología | Modelo | R² | MAPE | Score | k | Puntos Reales |\n"
    t2 += "|---|---|---|---|---|---|---|\n"
    for tech in techs_data.keys():
        bdata = brand_data[tech]
        m_usado = bdata["modelo_usado"]
        modelo_str = model_labels[m_usado]
        p = bdata["params"]
        pdict = p.get("params", p) if isinstance(p.get("params", None), dict) else p
        
        # Keys CORRECTAS (copiadas de generate_report_v2.py, que funciona):
        r2 = p.get('r_cuadrado', pdict.get('r_cuadrado', 'N/D'))
        if isinstance(r2, (int, float)): r2 = f"{float(r2):.4f}"
        mape = p.get('mape_ajuste', pdict.get('mape_ajuste', 'N/D'))
        if isinstance(mape, (int, float)): mape = f"{float(mape):.2f}%"
        score = p.get('score', pdict.get('score', 'N/D'))
        if isinstance(score, (int, float)): score = f"{float(score):.2f}"
        k = p.get('n_params', pdict.get('n_params', 'N/D'))
        pts = calidad[tech]['puntos_reales']
        
        t2 += f"| {tech.title()} | {modelo_str} | {r2} | {mape} | {score} | {k} | {pts} |\n"
    t2 += "\n"
    
    # 3. Proyecciones comparadas
    t3 = "### 3. Proyecciones Estratégicas (Millones)\n"
    t3 += "| Tecnología | 2030 | 2035 | Calidad de Datos (juez) |\n"
    t3 += "|---|---|---|---|\n"
    for tech in techs_data.keys():
        bdata = brand_data[tech]
        proj_map = dict(zip(bdata["anios_proj"], bdata["proj"]))
        p30 = f"{proj_map.get(2030, 0):.2f}"
        p35 = f"{proj_map.get(2035, 0):.2f}"
        conf = techs_data[tech][1]
        t3 += f"| {tech.title()} | {p30} | {p35} | {conf} |\n"
    t3 += "\n*Nota: 'Calidad de Datos' es el veredicto del juez sobre la serie de entrada (CONFIABLE/SOSPECHOSO). La confianza de la PROYECCIÓN (OPERATIVA/INDICATIVA/TENTATIVA) está en cada informe individual.*\n"
    if nota_tam:
        t3 += nota_tam + "\n"
    t3 += "\n"
    
    # 4. Parámetros de difusión
    t4 = "### 4. Parámetros de Difusión\n"
    t4 += "| Tecnología | p (Innovación) | q (Imitación) | m (Mercado Potencial) |\n"
    t4 += "|---|---|---|---|\n"
    for tech in techs_data.keys():
        bdata = brand_data[tech]
        m_usado = bdata["modelo_usado"]
        p = bdata["params"]
        pdict = p.get("params", p) if isinstance(p.get("params", None), dict) else p
        
        param_m = pdict.get('param_m1', pdict.get('param_m', 'N/D'))
        if isinstance(param_m, (int, float)): param_m = f"{float(param_m):.2f}"
        
        if m_usado in ["Bass_Clasico", "Dual_Market", "VdB_Joshi"]:
            param_p = pdict.get('param_p1', 'N/D')
            if isinstance(param_p, (int, float)): param_p = f"{float(param_p):.2e}"
            
            param_q = pdict.get('param_q1', 'N/D')
            if isinstance(param_q, (int, float)): param_q = f"{float(param_q):.4f}"
        else:
            param_p = "N/D — parametrización distinta"
            param_q = "N/D — parametrización distinta"
            if param_m == 'N/D' and 'param_k' in pdict: # Example of another parameter
                 param_m = "N/D — parametrización distinta"
                 
        t4 += f"| {tech.title()} | {param_p} | {param_q} | {param_m} |\n"
    t4 += "\n"
    
    # Ensamblado Final
    informe = titulo + t1 + t2 + t3 + t4 + "---\n### 5. Análisis de Inteligencia Competitiva (IA)\n\n" + ia_text
    return informe

def render_tab_benchmarking(tecnologias_disponibles):
    st.subheader("Benchmarking Competitivo y Multimarca")
    st.markdown("Compara las trayectorias de adopción de múltiples marcas o tecnologías en un solo panel interactivo y genera análisis estratégicos de cuota de mercado mediante IA.")
    
    if len(tecnologias_disponibles) < 2:
        st.warning("⚠️ Debes tener al menos 2 tecnologías cargadas en el sistema para realizar comparaciones.")
        return

    # 1. Controles Principales
    col1, col2 = st.columns([2.5, 1.5])
    with col1:
        techs_seleccionadas = st.multiselect(
            "Selecciona Marcas / Tecnologías a Comparar",
            options=tecnologias_disponibles,
            default=tecnologias_disponibles[:2] if len(tecnologias_disponibles) >= 2 else [tecnologias_disponibles[0]],
            format_func=lambda x: x.title()
        )
    with col2:
        horizon_years = st.slider(
            "📅 Horizonte de Proyección (años futuros)",
            min_value=5,
            max_value=20,
            value=10,
            key="bench_horizon_slider"
        )
        
    if len(techs_seleccionadas) < 2:
        st.info("💡 Por favor, selecciona al menos 2 tecnologías/marcas para activar las comparativas.")
        return

    # FASE 1: Nombres siempre reales + Validación de comparabilidad
    techs_seleccionadas = validar_comparabilidad(techs_seleccionadas)
    
    if len(techs_seleccionadas) < 2:
        st.error("❌ No hay suficientes tecnologías válidas (mínimo 2 con datos y fit en BD) para realizar la comparativa.")
        return

    model_labels = {
        "Analogical_Forecast": "Proyección por Analogía (Early-Tech)",
        "Bass_Clasico": "Bass Clásico",
        "Dual_Market": "Dual Market (Roset & Canals)",
        "Fourt_Woodlock": "Fourt & Woodlock (Innovación Pura)",
        "Gompertz": "Gompertz (Asimétrico)",
        "Generalized_Bass": "Generalized Bass (GBM + Precio)",
        "Horsky_Simon": "Horsky & Simon (Publicidad)",
        "Muller_Yogev": "Muller & Yogev (Saddle)",
        "VdB_Joshi": "Van den Bulte & Joshi",
        "Logistic_Diffusion_Convergence": "Modelo Logístico de Convergencia",
        "Ladron_Putsis": "Ladrón-de-Guevara & Putsis (Market Dinámico)",
        "Consenso IA": "Consenso IA (Anclado al Informe)",
        "Consenso Matemático": "Consenso Ponderado Matemático"
    }

    # 2. Selección de Modalidad de Modelado
    st.markdown("#### 🔬 Configuración del Modelo de Previsión")
    modo_modelo = st.radio(
        "Elige el método de asignación de modelos de proyección:",
        ["Modelo de Consenso (Mejor Score BD)", "Modelo Ganador Estadístico (Automático)", "Modelo Común (Global para todas)", "Personalizado por Marca / Tecnología"],
        horizontal=True,
        key="bench_model_mode"
    )

    global_model = "Bass_Clasico"
    custom_models = {}

    if modo_modelo == "Modelo Común (Global para todas)":
        global_model = st.selectbox(
            "Selecciona el modelo común para la comparación:",
            options=list(model_labels.keys()),
            format_func=lambda x: model_labels[x],
            key="bench_global_model_select"
        )
    elif modo_modelo == "Personalizado por Marca / Tecnología":
        st.markdown("<small>Asigna un modelo de difusión para cada marca seleccionada:</small>", unsafe_allow_html=True)
        # Mostrar filas de selectores
        cols_custom = st.columns(min(len(techs_seleccionadas), 4))
        for idx, tech in enumerate(techs_seleccionadas):
            col_idx = idx % len(cols_custom)
            with cols_custom[col_idx]:
                # Cargar el mejor modelo por defecto para inicializar
                params_temp = load_model_parameters(tech)
                best_temp, _ = rank_and_select_best_model(params_temp)
                custom_models[tech] = st.selectbox(
                    f"Modelo para {tech.title}",
                    options=list(model_labels.keys()),
                    index=list(model_labels.keys()).index(best_temp) if best_temp in model_labels else 0,
                    key=f"bench_custom_model_{tech}"
                )

    # Checkbox para cuota de mercado relativa
    ver_market_share = st.checkbox("📊 Mostrar Participación de Mercado Relativa (%)", value=False, key="bench_show_share")

    # Restricciones de Capping Jerárquico
    cap_enabled = st.checkbox(
        "🔒 Limitar proyecciones de marcas al total de una categoría madre",
        value=False,
        help="Si activas esta opción, puedes definir qué tecnología representa el total del mercado (ej. 'Coche Eléctrico') para evitar que marcas hijas (ej. 'Tesla') la superen."
    )
    parent_tech = None
    if cap_enabled:
        parent_tech = st.selectbox(
            "Selecciona la Categoría Madre (Límite Superior):",
            options=techs_seleccionadas,
            format_func=lambda x: x.title(),
            key="bench_parent_tech"
        )

    # 3. Procesar datos para cada marca
    brand_data = {}
    years_union = set()
    years_all_proj = set()

    for tech in techs_seleccionadas:
        df_hist = load_historical_data(tech)
        if df_hist.empty:
            continue
            
        params = load_model_parameters(tech)
        if not params:
            # Calcular en caliente si no existen en BD
            params = get_fitted_models_cached(tech, df_hist)

        anios_reales = df_hist["anio"].values
        primer_anio = anios_reales[0]
        t_proj = np.arange(len(df_hist) + horizon_years)
        anios_proj_full = [int(primer_anio + i) for i in t_proj]

        # Determinar qué modelo usar
        if modo_modelo == "Modelo de Consenso (Mejor Score BD)":
            m_key, _ = get_consensus_model(tech)
            if not m_key:
                m_key = "Bass_Clasico"
        elif modo_modelo == "Modelo Ganador Estadístico (Automático)":
            m_key, _ = rank_and_select_best_model(params)
            if not m_key:
                m_key = "Bass_Clasico"
        elif modo_modelo == "Modelo Común (Global para todas)":
            m_key = global_model
        else:
            m_key = custom_models.get(tech, "Bass_Clasico")

        # Recuperar parámetros y calcular proyección
        p = params.get(m_key, {})
        
        if m_key == "Analogical_Forecast":
            from data.loaders import load_qualitative_analysis
            import json
            analisis_txt = load_qualitative_analysis(tech)
            try:
                analisis_json = json.loads(analisis_txt) if analisis_txt else {}
            except Exception:
                analisis_json = {}
            escenario_base = analisis_json.get("analogia", {}).get("base", {})
            params_analogia = escenario_base.get("params")
            techo_analogia = escenario_base.get("techo")
            
            if params_analogia and techo_analogia:
                from models.analogical_forecast import project
                
                # FIX: The analogical fit in generate_report_v2 was done ONLY on non-zero points.
                # If we pass the full df_hist (with zeros), t=0 is shifted, causing huge projection differences.
                reales_no_zero = [v for v in df_hist["adopcion_acumulada"].values if v > 0]
                zeros_count = len(df_hist) - len(reales_no_zero)
                
                proj_no_zero = project(reales_no_zero, params_analogia, techo_analogia, years_ahead=horizon_years)
                
                if proj_no_zero is not None:
                    y_proj = np.zeros(len(t_proj))
                    # Align the projection with the correct starting year
                    y_proj[zeros_count : zeros_count + len(proj_no_zero)] = proj_no_zero
                    
                    # For analogical forecast, the theoretical curve fit on the first few points is loose
                    # due to the fixed ceiling. Overwrite the historical portion with real data to connect the dots.
                    hist_len = len(df_hist)
                    y_proj[:hist_len] = df_hist["adopcion_acumulada"].values
                else:
                    y_proj = np.zeros(len(t_proj))
            else:
                y_proj = np.zeros(len(t_proj))
        else:
            y_proj = project_model(m_key, p, t_proj)
        
        # Monotonicidad INTERNA: la curva no decrece respecto a sí misma
        for i in range(1, len(y_proj)):
            if y_proj[i] < y_proj[i-1]:
                y_proj[i] = y_proj[i-1]
        
        # Guardar en diccionario estructurado
        brand_data[tech] = {
            "anios_reales": list(anios_reales),
            "reales": list(df_hist["adopcion_acumulada"].values),
            "anios_proj": anios_proj_full,
            "proj": list(y_proj),
            "modelo_usado": m_key,
            "params": p
        }
        
        # Guardar años para la alineación del gráfico y la tabla
        for y in anios_reales:
            years_union.add(int(y))
        for y in anios_proj_full:
            years_all_proj.add(int(y))

    if not brand_data:
        st.error("No se pudieron cargar datos ni ajustar proyecciones para las tecnologías seleccionadas.")
        return

    # APLICAR CAPPING JERÁRQUICO
    if cap_enabled and parent_tech in brand_data:
        parent_map = dict(zip(brand_data[parent_tech]["anios_proj"], brand_data[parent_tech]["proj"]))
        for tech in brand_data:
            if tech != parent_tech:
                new_proj = []
                for y, val in zip(brand_data[tech]["anios_proj"], brand_data[tech]["proj"]):
                    limit_val = parent_map.get(int(y), np.inf)
                    if int(y) in brand_data[tech]["anios_reales"]:
                        new_proj.append(val)
                    else:
                        new_proj.append(min(val, limit_val))
                brand_data[tech]["proj"] = new_proj

    sorted_years_proj = sorted(list(years_all_proj))

    # 4. Paleta de colores para marcas
    brand_colors = BRAND_COLORS

    # 5. Renderizar Gráficos
    if not ver_market_share:
        # Gráfico Comparativo Absoluto
        fig = go.Figure()
        for idx, (tech, data) in enumerate(brand_data.items()):
            color = brand_colors[idx % len(brand_colors)]
            
            # Puntos históricos
            fig.add_trace(go.Scatter(
                x=data["anios_reales"],
                y=data["reales"],
                mode='markers',
                name=f"{tech.title()} (Histórico)",
                marker=dict(color=color, size=8, symbol='circle')
            ))
            
            # Curva proyectada
            fig.add_trace(go.Scatter(
                x=data["anios_proj"],
                y=data["proj"],
                mode='lines',
                name=f"{tech.title()} ({model_labels[data['modelo_usado']]})",
                line=dict(color=color, width=2.5)
            ))
            
        apply_dark_theme(
            fig,
            title=dict(text="Comparación Absoluta de Adopción (Millones)", font=dict(color="#f1f5f9", size=14), x=0.02, xanchor="left"),
            xaxis_title="Año",
            yaxis_title="Adopción (Millones)",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Gráfico de Cuota de Mercado Relativa (%) - Stacked Area
        # Primero, alinear los datos por año en un dataframe común
        df_share = pd.DataFrame({"anio": sorted_years_proj})
        for tech, data in brand_data.items():
            # Crear serie mapeada por año
            val_map = dict(zip(data["anios_proj"], data["proj"]))
            # Rellenar años antes del histórico con 0.0
            df_share[tech] = df_share["anio"].map(val_map).fillna(0.0)
            
        # Calcular el total por año para normalizar a 100%
        tech_cols = list(brand_data.keys())
        df_share["total_anual"] = df_share[tech_cols].sum(axis=1)
        
        # Evitar divisiones por cero
        df_share["total_anual"] = np.where(df_share["total_anual"] == 0, 1e-9, df_share["total_anual"])
        
        # Calcular porcentajes
        for tech in tech_cols:
            df_share[f"{tech}_pct"] = 100.0 * df_share[tech] / df_share["total_anual"]
            
        fig_share = go.Figure()
        for idx, tech in enumerate(tech_cols):
            color = brand_colors[idx % len(brand_colors)]
            fig_share.add_trace(go.Scatter(
                x=df_share["anio"],
                y=df_share[f"{tech}_pct"],
                mode='lines',
                stackgroup='one', # Habilita stacked area
                name=f"{tech.title} (%)",
                line=dict(color=color, width=1.5),
                hoverinfo='x+y+name'
            ))
            
        apply_dark_theme(
            fig_share,
            title=dict(text="Evolución de la Participación de Mercado Relativa (%)", font=dict(color="#f1f5f9", size=14), x=0.02, xanchor="left"),
            xaxis_title="Año",
            yaxis=dict(ticksuffix="%", range=[0, 100], gridcolor="rgba(255,255,255,0.05)", zeroline=False, tickfont=dict(color="#64748b", size=11), title=dict(font=dict(color="#94a3b8"))),
        )
        st.plotly_chart(fig_share, use_container_width=True)

    # 6. Tabla Comparativa de Hitos clave
    st.markdown("#### Hitos Proyectados y Comparativa de Valores")

    # Determinar qué años hito mostrar
    ultimo_real = max(int(max(d["anios_reales"])) for d in brand_data.values())
    milestone_years = sorted(list({
        ultimo_real - 3,
        ultimo_real,
        ultimo_real + 2,
        ultimo_real + 5,
        ultimo_real + 10,
        ultimo_real + horizon_years
    }))
    # Filtrar que los hitos estén dentro de nuestro rango de proyección
    milestone_years = [int(y) for y in milestone_years if y in sorted_years_proj]

    df_milestones = pd.DataFrame({"Año": milestone_years})

    for tech, data in brand_data.items():
        val_map = dict(zip(data["anios_proj"], data["proj"]))
        hist_years = set(data["anios_reales"])

        col_name = f"{tech.title} (M)"
        vals_list = []
        for y in milestone_years:
            val = val_map.get(y, 0.0)
            tipo = "Real" if y in hist_years else "Proy."
            vals_list.append(f"{val:.2f} ({tipo})")

        df_milestones[col_name] = vals_list

    st.markdown(dark_table_html(df_milestones), unsafe_allow_html=True)

    # 7. Análisis RAG / IA de Consenso Comparativo
    st.divider
    st.markdown("#### Análisis de Consenso e Inteligencia Competitiva")
    st.markdown("Solicita un informe comparativo a la IA para interpretar la dinámica de adopción, contrastar los coeficientes $p$ y $q$ de las marcas, y estimar tendencias estratégicas.")
    
    # Inicialización del informe comparativo en session state
    if "bench_ia_report" not in st.session_state:
        st.session_state.bench_ia_report = {}

    selected_key = "_".join(sorted(techs_seleccionadas))
    
    col_btn, col_clear = st.columns([4, 1])
    with col_btn:
        btn_ia_bench = st.button("Generar Consenso y Análisis Comparativo con IA", use_container_width=True, type="primary")
    with col_clear:
        btn_clear_ia = st.button("Limpiar Informe", use_container_width=True)
        
    if btn_clear_ia:
        if selected_key in st.session_state.bench_ia_report:
            del st.session_state.bench_ia_report[selected_key]
            st.rerun()

    if btn_ia_bench:
        with st.spinner("Claude está elaborando el análisis comparativo..."):
            # 1. Ejecutar cascada de evaluación para todas las tecnologías seleccionadas
            techs_data = {}
            veredictos = {}
            for tech in techs_seleccionadas:
                serie, veredicto, detalle = cascada_benchmarking(tech)
                techs_data[tech] = (serie, veredicto, detalle)
                veredictos[tech] = veredicto
            
            # 2. Calcular confianza global y abortar si es INSERVIBLE
            confianza_comp = confianza_benchmarking(veredictos)
            
            has_analogia = any(brand_data[t]["modelo_usado"] == "Analogical_Forecast" for t in techs_seleccionadas)
            if has_analogia and confianza_comp != "NO COMPARABLE":
                confianza_comp = "TENTATIVA"
                
            if confianza_comp == "NO COMPARABLE":
                techs_inservibles = [t for t, v in veredictos.items() if v == "INSERVIBLE"]
                st.error(f"❌ La comparación no puede generarse: {', '.join(techs_inservibles).title()} no tiene datos comparables (veredicto INSERVIBLE).")
                return
                
            calidad = calidad_relativa(techs_data)
            
            # Cargar clasificaciones para el gate competitivo
            clasifs = {}
            for tech in techs_seleccionadas:
                from data.loaders import load_qualitative_analysis
                import json
                txt = load_qualitative_analysis(tech)
                try:
                    if txt and "{" in txt:
                        start = txt.find("{")
                        end = txt.rfind("}") + 1
                        js = json.loads(txt[start:end])
                    else:
                        js = {}
                    # Para analogical forecast, la info de claude está en js["analogia"]
                    clasifs[tech] = js.get("analogia", js)
                except Exception as e:
                    logger.error(f"Error parsing json for {tech}: {e}")
                    clasifs[tech] = {}
                    
            # FIX 54: Verificador de coherencia de TAM de categoría (no re-escala)
            brand_data, norm_info = normalizar_tam_cluster(techs_data, clasifs, brand_data)
            nota_tam = ""
            if norm_info:
                advertencia_norm = norm_info.get("advertencia", "")
                if advertencia_norm:
                    nota_tam = "\n\n" + advertencia_norm
                    st.warning(advertencia_norm)
                    
            # FIX 54: Verificador de coherencia de cuotas (no re-escala)
            brand_data, anclaje_info = anclar_cuotas_al_presente(techs_data, clasifs, brand_data, norm_info)
            if anclaje_info:
                nota_divergencia = anclaje_info.get("nota", "")
                if nota_divergencia:
                    nota_tam += "\n\n" + nota_divergencia
                    st.warning(nota_divergencia)
                    
            warning_competitivo = gate_coherencia_competitiva(techs_data, clasifs, brand_data)
            if warning_competitivo:
                st.warning(warning_competitivo)
            
            prompt = build_benchmarking_prompt(techs_data, calidad, confianza_comp, brand_data, model_labels)
            if nota_tam:
                prompt = nota_tam + "\n" + prompt
            if warning_competitivo:
                prompt = warning_competitivo + "\n\n" + prompt
                
            try:
                ia_text = claude_benchmarking_writer(prompt)
                informe_final = ensamblar_informe_benchmarking(
                    techs_data, calidad, confianza_comp, brand_data, model_labels, ia_text, nota_tam
                )
                st.session_state.bench_ia_report[selected_key] = informe_final
            except Exception as e:
                logger.error(f"Error generando informe comparativo de IA: {e}")
                st.error(f"❌ Error al procesar tu consulta con la IA: {e}")

    # Mostrar informe RAG comparativo
    if selected_key in st.session_state.bench_ia_report:
        st.markdown("---")
        st.markdown(st.session_state.bench_ia_report[selected_key])
        
        # Botón de descarga
        st.download_button(
            label="Descargar Informe de Benchmarking (Markdown)",
            data=st.session_state.bench_ia_report[selected_key],
            file_name=f"benchmarking_{selected_key}.md",
            mime="text/markdown",
            use_container_width=True
        )
