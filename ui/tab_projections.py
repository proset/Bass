import streamlit as st
import re
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from ui.theme import apply_dark_theme, dark_table_html
from data.loaders import load_historical_data, load_model_parameters, load_consenso_forecast
from models.fit_models import fit_all_models, calculate_mape, estimate_uncertainty_bounds, bootstrap_uncertainty_bounds, rank_and_select_best_model
from models.rk4_solver import (
    bass_classic,
    dual_market_bass,
    fourt_woodlock_model,
    gompertz_model,
    generalized_bass_model,
    horsky_simon_model,
    muller_yogev_model,
    vdb_joshi_model,
    logistic_diffusion_convergence,
    ladron_puts_model
)

@st.cache_data(ttl=3600)
def get_fitted_models_cached(tech, df_hist):
    t_data = np.arange(len(df_hist))
    n_data = df_hist["adopcion_acumulada"].values
    return fit_all_models(t_data, n_data)

@st.cache_data(ttl=3600, show_spinner=False)
def compute_bootstrap_bands_cached(m_key, tech, t_hist_tuple, n_data_tuple, t_proj_tuple, popt_tuple, bounds, n_bootstrap=50):
    """Versión cacheada del bootstrap de bandas (evita recalcular en cada rerender)."""
    model_func_map = {
        "Bass_Clasico": bass_classic,
        "Dual_Market": dual_market_bass,
        "Fourt_Woodlock": fourt_woodlock_model,
        "Gompertz": gompertz_model,
        "Generalized_Bass": generalized_bass_model,
        "Horsky_Simon": horsky_simon_model,
        "Muller_Yogev": muller_yogev_model,
        "VdB_Joshi": vdb_joshi_model,
        "Logistic_Diffusion_Convergence": logistic_diffusion_convergence,
        "Ladron_Putsis": ladron_puts_model
    }
    model_func = model_func_map.get(m_key)
    if model_func is None:
        return None, None
    t_hist = np.array(t_hist_tuple)
    n_data = np.array(n_data_tuple)
    t_proj = np.array(t_proj_tuple)
    popt  = list(popt_tuple)
    try:
        lower, _, upper = bootstrap_uncertainty_bounds(
            model_func, t_hist, n_data, t_proj, popt, bounds, n_bootstrap=n_bootstrap
        )
        return lower.tolist(), upper.tolist()
    except Exception:
        return None, None

@st.cache_data(ttl=3600, show_spinner=False)
def get_breakpoint_fits_cached(tech, bp_year, t_bp_tuple, n_bp_tuple):
    """Versión cacheada del ajuste de modelos desde un punto de ruptura."""
    t_bp = np.array(t_bp_tuple)
    n_bp = np.array(n_bp_tuple)
    return fit_all_models(t_bp, n_bp)

def extract_recommended_model_from_consensus(consensus_text):
    """
    Extrae el model_key recomendado del texto de consenso generado por IA.
    Busca frases como 'Modelo Ideal Seleccionado:', 'modelo más adecuado:', etc.
    """
    if not consensus_text:
        return None
    text_lower = consensus_text.lower()
    
    # Mappings nombre legible -> model_key
    mappings = [
        (["dual market", "roset & canals", "roset y canals", "roset canals", "dos mercados"], "Dual_Market"),
        (["muller & yogev", "muller yogev", "efecto saddle", "saddle effect"], "Muller_Yogev"),
        (["van den bulte & joshi", "van den bulte joshi", "vdb & joshi", "influenciadores e imitadores"], "VdB_Joshi"),
        (["fourt & woodlock", "fourt", "woodlock", "innovación pura"], "Fourt_Woodlock"),
        (["gompertz", "sigmoide asimétrica", "asimétrica"], "Gompertz"),
        (["generalized bass", "bass generalizado", "gbm", "shocks de marketing", "precio"], "Generalized_Bass"),
        (["horsky & simon", "horsky", "publicidad", "esfuerzo publicitario"], "Horsky_Simon"),
        (["ladrón-de-guevara", "ladrón de guevara", "ladron putsis", "mercado potencial dinámico", "ladron"], "Ladron_Putsis"),
        (["logístico", "logistic", "ryu & kim", "difusión logística"], "Logistic_Diffusion_Convergence"),
        (["bass clásico", "bass clasico", "bass estándar"], "Bass_Clasico"),
    ]
    
    # Encontrar la línea que es un encabezado de sección de recomendación
    idx = -1
    for m in re.finditer(r'^#+\s+(?:\d+\.\s+)?(?:recomendación|recomendacion|modelo ideal)\b.*$', text_lower, re.MULTILINE):
        if "math-09" in m.group(0) or "nota est" in m.group(0):
            continue
        idx = m.start()
        
    if idx != -1:
        search_text = text_lower[idx:]
    else:
        search_text = text_lower
        
    sentences = re.split(r'[.\n]', search_text)
    
    recommendation_triggers = [
        "modelo ideal", "recomendado", "se recomienda", "concluye", 
        "mejor modelo", "recomendación", "elegimos", "ganador", "seleccionado"
    ]
    
    for sentence in sentences:
        if "math-09" in sentence or "nota estándar" in sentence or "nota estandar" in sentence:
            continue
        if "recomendación clínica" in sentence or "recomendacion clinica" in sentence or "recomendación médica" in sentence or "recomendacion medica" in sentence:
            if not any(t in sentence for t in ["modelo ideal", "se recomienda", "concluye"]):
                continue
                
        if any(trigger in sentence for trigger in recommendation_triggers):
            for keywords, model_key in mappings:
                if any(kw in sentence for kw in keywords):
                    return model_key
                    
    # Fallback si no se encontró en la sección específica
    if idx != -1:
        sentences_full = re.split(r'[.\n]', text_lower)
        for sentence in sentences_full:
            if "math-09" in sentence or "nota estándar" in sentence or "nota estandar" in sentence:
                continue
            if "recomendación clínica" in sentence or "recomendacion clinica" in sentence or "recomendación médica" in sentence or "recomendacion medica" in sentence:
                continue
            strict_triggers = ["modelo ideal", "se recomienda", "modelo recomendado", "modelo seleccionado", "concluye formalmente", "modelo ideal de difusión"]
            if any(trigger in sentence for trigger in strict_triggers):
                for keywords, model_key in mappings:
                    if any(kw in sentence for kw in keywords):
                        return model_key
                        
    return None

def compute_weighted_consensus_projection(params, t_proj, ranked_list):
    """
    Curva de consenso matemático: media ponderada por 1/MAPE.
    Se usa como fallback si el informe no tiene valores concretos.
    """
    model_func_map = {
        "Bass_Clasico": bass_classic, "Dual_Market": dual_market_bass,
        "Fourt_Woodlock": fourt_woodlock_model, "Gompertz": gompertz_model,
        "Generalized_Bass": generalized_bass_model, "Horsky_Simon": horsky_simon_model,
        "Muller_Yogev": muller_yogev_model, "VdB_Joshi": vdb_joshi_model,
        "Logistic_Diffusion_Convergence": logistic_diffusion_convergence,
        "Ladron_Putsis": ladron_puts_model
    }
    weights, projections = [], []
    for item in ranked_list:
        m_key = item["model_name"]
        if item.get("m_total", 0) > 12000:
            continue
        if m_key not in params:
            continue
        p = params[m_key]
        popt = p.get("popt") or reconstruct_popt(m_key, p)
        mf = model_func_map.get(m_key)
        if popt is None or mf is None:
            continue
        mape_bt = item.get("mape_backtest")
        mape_fit = item.get("mape_ajuste", 50.0)
        mape_use = mape_bt if (mape_bt is not None and not np.isnan(float(mape_bt))) else mape_fit
        try:
            y_proj = mf(t_proj, *popt)
            if not np.all(np.isfinite(y_proj)):
                continue
            weights.append(1.0 / max(float(mape_use), 0.1))
            projections.append(y_proj)
        except Exception:
            continue
    if not projections:
        return None
    w = np.array(weights)
    w /= w.sum()  # bug fix: was w.sum (method reference, not call)
    result = np.sum(w[:, np.newaxis] * np.array(projections), axis=0)
    return np.clip(result, 0, None)

def extract_consensus_anchor_points(consensus_text):
    """
    Extrae los puntos de anclaje año-valor mencionados explícitamente en el
    informe de consenso IA. Busca patrones como:
      'Para 2030 ... ~28 a 35 Millones'
      'Para 2035 ... ~70 a 85 Millones'
    Devuelve lista de dicts [{'year': 2030, 'low': 28, 'high': 35, 'mid': 31.5}, ...]
    """
    if not consensus_text:
        return []
    text_lower = consensus_text.lower()
    import statistics
    anchors = []
    extracted_per_year = {}

    def parse_val(s):
        s = s.strip()
        if ',' in s and '.' in s:
            return float(s.replace(',', ''))
        sep = ',' if ',' in s else '.' if '.' in s else None
        if not sep:
            return float(s)
        parts = s.split(sep)
        if len(parts) == 2 and len(parts[1]) == 3:
            return float(s.replace(sep, ''))
        return float(s.replace(',', '.'))

    # Escaneo prioritario de líneas oficiales de resumen
    structured_anchors = {}
    for line in consensus_text.lower().split('\n'):
        # Matches: "año 2030: 0.78 m" or "adopción para 2035: 0.81m" or similar
        m = re.search(r'(?:a[ñn]o|adopci[oó]n|pron[oó]stico)\s+(20[2-5]\d)\s*:\s*\*?\*?\s*([\d.,]+)\s*\*?\*?\s*(?:millones?|m\b)', line)
        if m:
            y = int(m.group(1))
            v = parse_val(m.group(2))
            structured_anchors[y] = v

    sentences = re.split(r'\.\s+|\n', text_lower)
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Skip sentences comparing multiple years (e.g. historical ranges or comparative projections)
        years_in_sentence = list(set(re.findall(r'\b(20[2-5]\d)\b', sentence)))
        if len(years_in_sentence) > 1:
            continue
        ranges = list(re.finditer(r'([\d.,]+)\s*(?:a|-|–)\s*([\d.,]+)\s*(?:millones?|m\b)', sentence))
        singles = list(re.finditer(r'([\d.,]+)\s*(?:millones?|m\b)', sentence))
        
        for m_year in re.finditer(r'\b(20[2-5]\d)\b', sentence):
            year = int(m_year.group(1))
            best_dist = float('inf')
            best_val = None
            
            for r in ranges:
                context_before = sentence[max(0, r.start() - 45):r.start()]
                if any(w in context_before for w in ["crecimiento", "incremento", "otros", "adicionales", "aumento", "diferencia"]):
                    continue
                v1 = parse_val(r.group(1))
                v2 = parse_val(r.group(2))
                if (1900 <= v1 <= 2100) or (1900 <= v2 <= 2100):
                    continue
                dist = min(abs(m_year.start() - r.start()), abs(m_year.start() - r.end()))
                if dist < best_dist:
                    best_dist = dist
                    best_val = {'type': 'range', 'low': v1, 'high': v2}
                    
            for s in singles:
                context_before = sentence[max(0, s.start() - 45):s.start()]
                if any(w in context_before for w in ["crecimiento", "incremento", "otros", "adicionales", "aumento", "diferencia"]):
                    continue
                is_in_range = any(r.start() <= s.start() <= r.end() for r in ranges)
                if is_in_range:
                    continue
                dist = min(abs(m_year.start() - s.start()), abs(m_year.start() - s.end()))
                if dist < best_dist:
                    v = parse_val(s.group(1))
                    # Prevent extracting the year itself as a value (e.g. 2030 millones)
                    if v < 1900 or v > 2100:
                        best_dist = dist
                        best_val = {'type': 'single', 'val': v}
                        
            if best_val and best_dist < 80:
                if year not in extracted_per_year:
                    extracted_per_year[year] = {'lows': [], 'highs': [], 'mids': []}
                    
                if best_val['type'] == 'range':
                    extracted_per_year[year]['lows'].append(best_val['low'])
                    extracted_per_year[year]['highs'].append(best_val['high'])
                    extracted_per_year[year]['mids'].append((best_val['low'] + best_val['high']) / 2)
                else:
                    v = best_val['val']
                    extracted_per_year[year]['lows'].append(v * 0.88)
                    extracted_per_year[year]['highs'].append(v * 1.12)
                    extracted_per_year[year]['mids'].append(v)

    # Priorizar y sobreescribir con los datos estructurados oficiales si están presentes
    for y, v in structured_anchors.items():
        extracted_per_year[y] = {
            'lows': [v * 0.88],
            'highs': [v * 1.12],
            'mids': [v]
        }

    for year, data in extracted_per_year.items():
        if not data['mids']:
            continue
        anchors.append({
            'year': year,
            'low': statistics.median(data['lows']),
            'high': statistics.median(data['highs']),
            'mid': statistics.median(data['mids'])
        })

    return sorted(anchors, key=lambda x: x['year'])

def build_consensus_curve_from_anchors(anchors, last_hist_year, last_hist_value, anios_proj):
    """
    Construye una curva suave (CubicSpline) que pasa por el último dato histórico
    y por los puntos de anclaje extraídos del informe IA.
    La curva NO extrapola más allá del último año del informe.
    Devuelve (anios_fut, y_low, y_mid, y_high) o (None, None, None, None) si no hay datos.
    """
    from scipy.interpolate import CubicSpline, interp1d

    future_anchors = [a for a in anchors if a['year'] > last_hist_year]
    if not future_anchors:
        return None, None, None, None

    last_anchor_year = max(a['year'] for a in future_anchors)

    yrs   = [last_hist_year] + [a['year']  for a in future_anchors]
    mids  = [last_hist_value] + [a['mid']  for a in future_anchors]
    lows  = [last_hist_value] + [a['low']  for a in future_anchors]
    highs = [last_hist_value] + [a['high'] for a in future_anchors]

    # Solo interpolar dentro del rango de los anchors (NO extrapolar más allá)
    anios_fut = [a for a in anios_proj if last_hist_year <= a <= last_anchor_year]
    if len(anios_fut) < 2:
        return None, None, None, None

    try:
        from scipy.interpolate import PchipInterpolator
        if len(yrs) >= 3:
            cs_mid  = PchipInterpolator(yrs, mids)
            cs_low  = PchipInterpolator(yrs, lows)
            cs_high = PchipInterpolator(yrs, highs)
        else:
            cs_mid  = interp1d(yrs, mids,  fill_value='extrapolate')
            cs_low  = interp1d(yrs, lows,  fill_value='extrapolate')
            cs_high = interp1d(yrs, highs, fill_value='extrapolate')

        y_mid  = np.clip(cs_mid(anios_fut),  0, None)
        y_low  = np.clip(cs_low(anios_fut),  0, None)
        y_high = np.clip(cs_high(anios_fut), 0, None)

        # Garantizar monotonía mínima
        for i in range(1, len(y_mid)):
            y_mid[i]  = max(y_mid[i],  y_mid[i-1]  * 0.98)
            y_low[i]  = max(y_low[i],  y_low[i-1]  * 0.98)
            y_high[i] = max(y_high[i], y_high[i-1] * 0.98)

        return anios_fut, y_low, y_mid, y_high
    except Exception:
        return None, None, None, None

def reconstruct_popt(m_key, p):
    """Reconstruye el vector popt a partir de los parámetros sueltos de la base de datos o dict."""
    try:
        # Si ya viene en formato cargado en memoria con popt
        if "popt" in p and p["popt"] is not None:
            return p["popt"]
            
        # De lo contrario, mapear campos individuales
        if m_key == "Bass_Clasico":
            return [p["param_m1"], p["param_p1"], p["param_q1"]]
        elif m_key == "Dual_Market":
            return [p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"], p["param_q2"]]
        elif m_key == "Fourt_Woodlock":
            return [p["param_m1"], p["param_p1"]]
        elif m_key == "Gompertz":
            return [p["param_m1"], p["param_p1"], p["param_q1"]]
        elif m_key == "Generalized_Bass":
            return [p["param_m1"], p["param_p1"], p["param_q1"], p["param_p2"]]
        elif m_key == "Horsky_Simon":
            return [p["param_m1"], p["param_p1"], p["param_q1"], p["param_p2"]]
        elif m_key == "Muller_Yogev":
            return [p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"], p["param_q2"], p["param_q12"]]
        elif m_key == "VdB_Joshi":
            return [p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_q2"], p["param_p2"]]
        elif m_key == "Logistic_Diffusion_Convergence":
            return [p["param_m1"], p["param_p1"], p["param_q1"], p["param_p2"]]
        elif m_key == "Ladron_Putsis":
            return [p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"]]
    except Exception:
        pass
    return None

def render_tab_projections(tecnologia_seleccionada):
    df_hist = load_historical_data(tecnologia_seleccionada)
    
    if df_hist.empty:
        st.warning("⚠️ No hay suficientes datos históricos para esta tecnología.")
        return
        
    # Cargar directamente los parámetros de los modelos de la base de datos (inmediato, sin coste computacional)
    params = load_model_parameters(tecnologia_seleccionada)
        
    # Botón para recalcular parámetros con cotas físicas (si el usuario detecta anomalías)
    col_title, col_recalc = st.columns([3, 1])
    with col_title:
        st.subheader(f"📈 Previsión de Adopción: {tecnologia_seleccionada.title()}")
    with col_recalc:
        if st.button("🔄 Ajustar con Cotas Físicas", help="Recalcula y optimiza los 7 modelos limitando el mercado potencial (m) a un máximo razonable para evitar curvas explosivas."):
            with st.spinner("Re-ajustando modelos matemáticos con restricciones..."):
                t_data = np.arange(len(df_hist))
                n_data = df_hist["adopcion_acumulada"].values
                fits = fit_all_models(t_data, n_data)
                if fits:
                    from data.ingestion import guardar_parametros_db
                    guardar_parametros_db(tecnologia_seleccionada, fits)
                    st.success("¡Modelos recalculados con éxito!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("No se pudieron ajustar los modelos.")

    if not params:
        st.warning("⚠️ No se pudieron cargar parámetros para esta tecnología. Por favor, pulsa el botón '🔄 Ajustar con Cotas Físicas' de arriba para ajustarlos por primera vez.")
        return

    # ----------------- KPIs del Modelo Ganador -----------------
    # Clasificar modelos estadísticamente
    best_model, ranked_list = rank_and_select_best_model(params)

    # Cargar consenso IA y extraer modelo recomendado
    consensus_text = load_consenso_forecast(tecnologia_seleccionada)
    ia_recommended_model = extract_recommended_model_from_consensus(consensus_text)
    # El modelo a mostrar por defecto: preferencia IA > estadístico
    default_model = ia_recommended_model if (ia_recommended_model and ia_recommended_model in params) else best_model

    model_labels = {
        "Bass_Clasico": "Bass Clásico",
        "Dual_Market": "Dual Market (Roset & Canals)",
        "Fourt_Woodlock": "Fourt & Woodlock (Innovación Pura)",
        "Gompertz": "Gompertz (Asimétrico)",
        "Generalized_Bass": "Generalized Bass (GBM + Precio)",
        "Horsky_Simon": "Horsky & Simon (Publicidad)",
        "Muller_Yogev": "Muller & Yogev (Saddle)",
        "VdB_Joshi": "Van den Bulte & Joshi",
        "Logistic_Diffusion_Convergence": "Modelo Logístico de Convergencia",
        "Ladron_Putsis": "Ladrón-de-Guevara & Putsis (Market Dinámico)"
    }

    if ranked_list:
        best_data = ranked_list[0]
        mape_bt = best_data['mape_backtest']
        
        kpis_html = f"""
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-title">R² Máximo del Ajuste</div>
                <div class="kpi-value-container">
                    <div class="kpi-value">{best_data['r_cuadrado']:.4f}</div>
                </div>
                <div class="kpi-desc">Coeficiente de determinación del modelo óptimo</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">MAPE Ajuste Histórico</div>
                <div class="kpi-value-container">
                    <div class="kpi-value">{best_data['mape_ajuste']:.2f}%</div>
                </div>
                <div class="kpi-desc">Error absoluto medio del ajuste histórico</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">MAPE Validación Backtest</div>
                <div class="kpi-value-container">
                    <div class="kpi-value">{"N/D" if mape_bt is None or np.isnan(mape_bt) else f"{mape_bt:.2f}%"}</div>
                </div>
                <div class="kpi-desc">Error de validación cruzada en backtesting</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Modelo Recomendado (IA)</div>
                <div class="kpi-value-container">
                    <div class="kpi-value" style="font-size: 1.25rem; font-weight: 700; color: #06b6d4; padding-top: 0.4rem;">
                        {model_labels[ia_recommended_model].split("(")[0].strip() if (ia_recommended_model and ia_recommended_model in model_labels) else "N/D"}
                    </div>
                </div>
                <div class="kpi-desc">Modelo óptimo elegido por inteligencia de mercado</div>
            </div>
        </div>
        """
        st.markdown(kpis_html, unsafe_allow_html=True)

    # Banner si la IA recomienda un modelo diferente al estadístico
    if ia_recommended_model and ia_recommended_model != best_model and ia_recommended_model in model_labels:
        st.info(
            f"🤖 **La IA recomienda '{model_labels[ia_recommended_model]}'** basado en el análisis del consenso, "
            f"mientras que el método estadístico puro seleccionaría '{model_labels.get(best_model, best_model)}'. "
            f"El gráfico se ha inicializado con el modelo de la IA."
        )

    st.divider

    # ----------------- Controles de Horizonte y Selección -----------------
    col_ctrl1, col_ctrl2 = st.columns([1.5, 2])
    with col_ctrl1:
        horizon_years = st.slider("📅 Horizonte de proyección (años)", 5, 20, 10, help="Elige el número de años a predecir hacia el futuro.")
    with col_ctrl2:
        modelos_seleccionados = st.multiselect(
            "Visualizar Modelos de Difusión",
            options=list(model_labels.keys()),
            default=[default_model] if default_model else ["Bass_Clasico", "Dual_Market"],
            format_func=lambda x: model_labels[x]
        )

    # Opciones avanzadas de visualización
    col_extra1, col_extra2, col_extra3 = st.columns(3)
    with col_extra1:
        mostrar_bandas = st.checkbox(
            "📊 Bandas de Incertidumbre IC 95%",
            value=False,
            help="Bandas de confianza Monte Carlo al 95%. Requiere que los parámetros estén en memoria (pulsa 'Recalcular' si no aparecen). Añade ~3-5 seg. al cálculo."
        )
    with col_extra2:
        usar_breakpoint = st.checkbox(
            "🔀 Análisis de Ruptura Estructural",
            value=False,
            help="Reajusta los modelos usando únicamente los datos desde un año de ruptura específico (útil para capturar cambios estructurales de mercado)"
        )
    with col_extra3:
        mostrar_consenso = st.checkbox(
            "🥇 Curva de Consenso Ponderado",
            value=True,
            help="Muestra una curva de consenso calculada como media ponderada de todos los modelos (peso = 1/MAPE backtest). Se excluyen proyecciones físicamente absurdas."
        )

    # ----------------- Cálculos y Gráfico -----------------
    t_hist = np.arange(len(df_hist))
    t_proj = np.arange(len(df_hist) + horizon_years)
    anios_reales = df_hist["anio"].values
    ultimo_anio = anios_reales[-1] if len(anios_reales) > 0 else 2024
    
    # Proyectar años futuros
    primer_anio_hist = anios_reales[0]
    anios_proj = [primer_anio_hist + i for i in t_proj]

    # Selector de año de ruptura (requiere anios_reales calculado antes)
    bp_year = None
    if usar_breakpoint:
        anios_opciones = [int(a) for a in anios_reales[1:-2]] if len(anios_reales) >= 5 else []
        if anios_opciones:
            bp_year = st.select_slider(
                "📍 Año de Inicio del Reajuste (Breakpoint)",
                options=anios_opciones,
                value=anios_opciones[len(anios_opciones) // 3],
                help="Los modelos se reajustarán usando únicamente los datos desde este año en adelante"
            )
        else:
            st.info("⚠️ Se necesitan al menos 5 puntos históricos para el análisis de ruptura estructural.")

    fig = go.Figure()
    
    # Agregar datos reales
    fig.add_trace(go.Scatter(
        x=anios_reales, 
        y=df_hist["adopcion_acumulada"], 
        mode='markers+lines', 
        name='Datos Históricos Reales', 
        marker=dict(color='#ffffff', size=9, line=dict(color='#06b6d4', width=1.5)),
        line=dict(color='#ffffff', width=3)
    ))

    df_export_curves = pd.DataFrame({"Anio": anios_proj})
    df_export_curves["Datos Reales"] = df_hist["adopcion_acumulada"].reindex(df_export_curves.index).values

    # Paleta de colores para las curvas de proyección
    color_palette = {
        "Bass_Clasico": "#2563EB",
        "Dual_Market": "#DC2626",
        "Fourt_Woodlock": "#059669",
        "Gompertz": "#06B6D4",
        "Generalized_Bass": "#D946EF",
        "Horsky_Simon": "#B45309",
        "Muller_Yogev": "#6366F1",
        "VdB_Joshi": "#A855F7",
        "Logistic_Diffusion_Convergence": "#84CC16",
        "Ladron_Putsis": "#F97316"
    }

    df_comparativa = pd.DataFrame({
        "Año": anios_reales,
        "Reales (M)": df_hist["adopcion_acumulada"].values
    })
    style_formatters = {"Reales (M)": "{:.1f}"}

    for m_key in modelos_seleccionados:
        if m_key not in params:
            continue
            
        p = params[m_key]
        popt = p.get("popt")
        if popt is None:
            popt = reconstruct_popt(m_key, p)
            
        if popt is None:
            continue
            
        pcov = p.get("pcov")
        bounds = p.get("bounds")
        r2_val = p.get("r_cuadrado", 0.0)
        
        # Determinar modelo matemático
        if m_key == "Bass_Clasico":
            model_func = lambda t, *args: bass_classic(t, *args)
        elif m_key == "Dual_Market":
            model_func = lambda t, *args: dual_market_bass(t, *args)
        elif m_key == "Fourt_Woodlock":
            model_func = lambda t, *args: fourt_woodlock_model(t, *args)
        elif m_key == "Gompertz":
            model_func = lambda t, *args: gompertz_model(t, *args)
        elif m_key == "Generalized_Bass":
            model_func = lambda t, *args: generalized_bass_model(t, *args)
        elif m_key == "Horsky_Simon":
            model_func = lambda t, *args: horsky_simon_model(t, *args)
        elif m_key == "Muller_Yogev":
            model_func = lambda t, *args: muller_yogev_model(t, *args)
        elif m_key == "VdB_Joshi":
            model_func = lambda t, *args: vdb_joshi_model(t, *args)
        elif m_key == "Logistic_Diffusion_Convergence":
            model_func = lambda t, *args: logistic_diffusion_convergence(t, *args)
        elif m_key == "Ladron_Putsis":
            model_func = lambda t, *args: ladron_puts_model(t, *args)
            
        # Evaluar
        y_proj = model_func(t_proj, *popt)
        df_export_curves[f"Prediccion_{m_key}"] = y_proj
        
        color = color_palette.get(m_key, "#6B7280")
        
        # Agregar la curva proyectada
        fig.add_trace(go.Scatter(
            x=anios_proj, 
            y=y_proj, 
            mode='lines', 
            name=f'{model_labels[m_key]} (R²={r2_val:.3f})', 
            line=dict(color=color, width=2.5)
        ))
        
        # Bandas de incertidumbre Bootstrap de Residuos al 95% (cacheadas)
        if mostrar_bandas:
            try:
                n_data_hist = df_hist["adopcion_acumulada"].values
                lower_b_list, upper_b_list = compute_bootstrap_bands_cached(
                    m_key,
                    tecnologia_seleccionada,
                    tuple(t_hist.tolist()),
                    tuple(n_data_hist.tolist()),
                    tuple(t_proj.tolist()),
                    tuple(popt) if isinstance(popt, list) else tuple(popt.tolist()),
                    bounds,
                    n_bootstrap=50
                )
                if lower_b_list is not None:
                    hex_c = color.lstrip('#')
                    r_c, g_c, b_c = int(hex_c[0:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16)
                    fill_c = f'rgba({r_c},{g_c},{b_c},0.13)'
                    fig.add_trace(go.Scatter(
                        x=list(anios_proj) + list(reversed(anios_proj)),
                        y=upper_b_list + list(reversed(lower_b_list)),
                        fill='toself',
                        fillcolor=fill_c,
                        line=dict(color='rgba(255,255,255,0)'),
                        showlegend=False,
                        hoverinfo='skip',
                        name=f'IC 95% {model_labels[m_key]}'
                    ))
            except Exception:
                pass

        # Rellenar tabla comparativa histórica
        y_hist = model_func(t_hist, *popt)
        df_comparativa[f"{model_labels[m_key]} (M)"] = y_hist
        acc = np.where(df_hist["adopcion_acumulada"].values == 0, 100.0, 
                       100.0 * (1.0 - np.abs(df_hist["adopcion_acumulada"].values - y_hist) / df_hist["adopcion_acumulada"].values))
        df_comparativa[f"Accuracy {model_labels[m_key]}"] = np.clip(acc, 0.0, 100.0)
        
        style_formatters[f"{model_labels[m_key]} (M)"] = "{:.1f}"
        style_formatters[f"Accuracy {model_labels[m_key]}"] = "{:.2f}%"

    # Proyecciones desde el punto de ruptura estructural
    if usar_breakpoint and bp_year is not None:
        bp_mask = df_hist["anio"] >= bp_year
        df_bp = df_hist[bp_mask].reset_index(drop=True)
        if len(df_bp) >= 3:
            t_bp_data = np.arange(len(df_bp))
            n_bp_data = df_bp["adopcion_acumulada"].values
            with st.spinner(f"⏳ Calculando ruptura desde {bp_year} (solo la primera vez)..."):
                fits_bp = get_breakpoint_fits_cached(
                    tecnologia_seleccionada,
                    bp_year,
                    tuple(t_bp_data.tolist()),
                    tuple(n_bp_data.tolist())
                )
            if fits_bp:
                # Línea vertical de ruptura
                fig.add_vline(
                    x=bp_year,
                    line_dash="dash",
                    line_color="orange",
                    line_width=2,
                    annotation_text=f"📍 Ruptura: {bp_year}",
                    annotation_position="top right",
                    annotation_font_color="darkorange"
                )
                # Proyecciones desde el breakpoint para cada modelo seleccionado
                bp_model_funcs = {
                    "Bass_Clasico": bass_classic,
                    "Dual_Market": dual_market_bass,
                    "Fourt_Woodlock": fourt_woodlock_model,
                    "Gompertz": gompertz_model,
                    "Generalized_Bass": generalized_bass_model,
                    "Horsky_Simon": horsky_simon_model,
                    "Muller_Yogev": muller_yogev_model,
                    "VdB_Joshi": vdb_joshi_model,
                    "Logistic_Diffusion_Convergence": logistic_diffusion_convergence,
                    "Ladron_Putsis": ladron_puts_model
                }
                for m_key_bp in modelos_seleccionados:
                    if m_key_bp not in fits_bp:
                        continue
                    p_bp = fits_bp[m_key_bp]
                    popt_bp = p_bp.get("popt") or reconstruct_popt(m_key_bp, p_bp)
                    mf_bp = bp_model_funcs.get(m_key_bp)
                    if popt_bp is None or mf_bp is None:
                        continue
                    t_proj_bp = np.arange(len(df_bp) + horizon_years)
                    anios_proj_bp = [int(bp_year) + i for i in t_proj_bp]
                    y_proj_bp = mf_bp(t_proj_bp, *popt_bp)
                    color_bp = color_palette.get(m_key_bp, "#6B7280")
                    fig.add_trace(go.Scatter(
                        x=anios_proj_bp,
                        y=y_proj_bp,
                        mode='lines',
                        name=f'{model_labels[m_key_bp]} (Ruptura {bp_year})',
                        line=dict(color=color_bp, width=2, dash='dot')
                    ))

    # Curva de Consenso IA (anclada a los valores del informe; fallback: media matemática)
    if mostrar_consenso:
        last_hist_year  = int(ultimo_anio)
        last_hist_val   = float(df_hist["adopcion_acumulada"].iloc[-1])
        consensus_anchors = [a for a in extract_consensus_anchor_points(consensus_text) if a['year'] > last_hist_year]

        anios_fut_c, y_low_c, y_mid_c, y_high_c = build_consensus_curve_from_anchors(
            consensus_anchors, last_hist_year, last_hist_val, anios_proj
        )

        if anios_fut_c is not None:
            # Banda de incertidumbre del rango [low, high] del informe
            fig.add_trace(go.Scatter(
                x=list(anios_fut_c) + list(reversed(anios_fut_c)),
                y=list(y_high_c) + list(reversed(list(y_low_c))),
                fill='toself',
                fillcolor='rgba(245, 158, 11, 0.15)',
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False,
                hoverinfo='skip',
                name='Rango Consenso IA'
            ))
            # Línea central del consenso
            fig.add_trace(go.Scatter(
                x=anios_fut_c,
                y=y_mid_c,
                mode='lines',
                name='🥇 Consenso IA (Informe)',
                line=dict(color='#F59E0B', width=3.5, dash='dashdot'),
                hovertemplate='Consenso IA: %{y:.1f}M<extra></extra>'
            ))
            # Anotaciones en los puntos de anclaje del informe
            for anchor in consensus_anchors:
                if anchor['year'] in anios_proj:
                    fig.add_annotation(
                        x=anchor['year'],
                        y=anchor['mid'],
                        text=f"IA: {anchor['low']:.0f}-{anchor['high']:.0f}M",
                        showarrow=True,
                        arrowhead=2,
                        arrowcolor='#F59E0B',
                        font=dict(color='#F59E0B', size=11),
                        bgcolor='rgba(245,158,11,0.1)',
                        bordercolor='#F59E0B'
                    )
        else:
            # Fallback: media ponderada matemática
            if ranked_list:
                y_consenso = compute_weighted_consensus_projection(params, t_proj, ranked_list)
                if y_consenso is not None:
                    fig.add_trace(go.Scatter(
                        x=anios_proj,
                        y=y_consenso,
                        mode='lines',
                        name='🥇 Consenso Ponderado (estimación matemática)',
                        line=dict(color='#F59E0B', width=3.5, dash='dashdot'),
                    ))

    apply_dark_theme(
        fig,
        title=dict(
            text=f"Proyección de Difusión — {tecnologia_seleccionada.title()}",
            font=dict(color="#f1f5f9", size=15), x=0.02, xanchor="left"
        ),
        xaxis_title="Año",
        yaxis_title="Adopción Acumulada (Millones)",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Caja informativa sobre los valores del consenso extraídos del informe
    if mostrar_consenso and consensus_anchors:
        anchor_lines = " | ".join(
            [f"**{a['year']}**: {a['low']:.0f}–{a['high']:.0f}M (mid: {a['mid']:.1f}M)"
             for a in consensus_anchors]
        )
        st.caption(
            f"🥇 **Consenso IA extraído del informe:** {anchor_lines}. "
            f"La curva dorada interpola entre estos valores y el último dato histórico "
            f"({int(ultimo_anio)}: {float(df_hist['adopcion_acumulada'].iloc[-1]):.1f}M). "
            f"Si estos valores no coinciden con el informe más reciente, "
            f"regenera el consenso en n8n para actualizar la base de datos."
        )
    elif mostrar_consenso and not consensus_anchors:
        st.caption(
            "🥇 **Consenso IA:** No se encontraron valores numéricos concretos en el informe "
            "(p.ej. 'Para 2030: ~28 a 35 Millones'). Se usa media ponderada matemática como fallback. "
            "Actualiza el consenso en n8n para activar la curva anclada al informe."
        )

    # ----------------- Tabla Comparativa de Ajustes e Histórico -----------------
    with st.expander("Ver Tabla Comparativa de Desviación Histórica Año a Año"):
        st.markdown(dark_table_html(df_comparativa.round(2)), unsafe_allow_html=True)

    # ----------------- Parámetros de los Modelos y Validación Cruzada -----------------
    st.markdown("#### Parámetros del Ajuste y Errores de Backtesting")
    
    y_true = df_hist["adopcion_acumulada"].values
    param_rows = []
    
    for m_key in list(model_labels.keys()):
        if m_key not in params:
            continue
        p = params[m_key]
        popt = p.get("popt")
        if popt is None:
            popt = reconstruct_popt(m_key, p)
            
        if popt is None:
            continue
        
        # Calcular MAPE del ajuste
        if m_key == "Bass_Clasico":
            y_h = bass_classic(t_hist, *popt)
        elif m_key == "Dual_Market":
            y_h = dual_market_bass(t_hist, *popt)
        elif m_key == "Fourt_Woodlock":
            y_h = fourt_woodlock_model(t_hist, *popt)
        elif m_key == "Gompertz":
            y_h = gompertz_model(t_hist, *popt)
        elif m_key == "Generalized_Bass":
            y_h = generalized_bass_model(t_hist, *popt)
        elif m_key == "Horsky_Simon":
            y_h = horsky_simon_model(t_hist, *popt)
        elif m_key == "Muller_Yogev":
            y_h = muller_yogev_model(t_hist, *popt)
        elif m_key == "VdB_Joshi":
            y_h = vdb_joshi_model(t_hist, *popt)
        elif m_key == "Logistic_Diffusion_Convergence":
            y_h = logistic_diffusion_convergence(t_hist, *popt)
        elif m_key == "Ladron_Putsis":
            y_h = ladron_puts_model(t_hist, *popt)
            
        mape_fit = calculate_mape(y_true, y_h)
        mape_bt = p.get("mape_backtest")
        
        row_dict = {
            "Modelo": model_labels[m_key],
            "R²": f"{p.get('r_cuadrado', 0.0):.4f}",
            "MAPE Ajuste": f"{mape_fit:.2f}%",
            "MAPE Backtest (Fuera de muestra)": f"{mape_bt:.2f}%" if mape_bt is not None and not np.isnan(mape_bt) else "N/D",
            "m₁ (Límite M1)": f"{popt[0]:.1f}",
            "p₁ (Innovación M1)": f"{popt[1]:.5f}",
            "q₁ (Imitación M1)": f"{popt[2]:.5f}" if m_key not in ["Fourt_Woodlock"] and len(popt) > 2 else "-",
            "m₂ (Límite M2)": f"{popt[3]:.3f}" if len(popt) > 3 and m_key in ["Dual_Market", "Muller_Yogev", "VdB_Joshi", "Ladron_Putsis"] else "-",
        }
        param_rows.append(row_dict)
        
    if param_rows:
        df_params = pd.DataFrame(param_rows)
        st.markdown(dark_table_html(df_params), unsafe_allow_html=True)

    if st.button("Recalcular y Ajustar Curvas Matemáticas", key="recalculate_models_btn", use_container_width=True):
        with st.spinner("Ejecutando resolvedores RK4 y ajustando todos los modelos de difusión..."):
            t_data = np.arange(len(df_hist))
            n_data = df_hist["adopcion_acumulada"].values
            fits = fit_all_models(t_data, n_data)
            if fits:
                from data.ingestion import guardar_parametros_db, guardar_consenso_forecast
                from data.loaders import load_qualitative_analysis
                from ai.analysis import generar_consenso_pronostico_ia
                
                guardar_parametros_db(tecnologia_seleccionada, fits)
                
                # También regenerar automáticamente el consenso basado en las nuevas curvas
                analisis_text = load_qualitative_analysis(tecnologia_seleccionada)
                if analisis_text:
                    new_params = load_model_parameters(tecnologia_seleccionada)
                    consenso_text = generar_consenso_pronostico_ia(tecnologia_seleccionada, df_hist, new_params, analisis_text)
                    if consenso_text:
                        guardar_consenso_forecast(tecnologia_seleccionada, consenso_text)
                        
                st.cache_data.clear()
                st.success("¡Modelos matemáticos recalculados y consenso actualizado exitosamente!")
                st.rerun()
            else:
                st.error("No se pudieron recalcular las curvas matemáticas.")

    # ----------------- Exportación de Resultados -----------------
    st.subheader("💾 Exportación Científica")
    csv_data = df_export_curves.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Curvas de Proyección en CSV",
        data=csv_data,
        file_name=f"proyecciones_adopcion_{tecnologia_seleccionada}.csv",
        mime="text/csv",
        use_container_width=True
    )

    # ----------------- Análisis de Sensibilidad Interactivo -----------------
    st.divider
    st.subheader("🎛️ Simulador / Análisis de Sensibilidad de Parámetros")
    st.markdown("Ajusta manualmente los parámetros para ver el impacto de cambios en las dinámicas de mercado (coeficientes de innovación e imitación) sobre la curva final.")
    
    sens_model = st.selectbox("Selecciona Modelo para Simular", ["Bass Clásico", "Dual Market"])
    
    if sens_model == "Bass Clásico":
        p_bass = params.get("Bass_Clasico")
        if p_bass:
            popt_s = p_bass.get("popt")
            if popt_s is None:
                popt_s = reconstruct_popt("Bass_Clasico", p_bass)
                
            if popt_s is None:
                st.warning("No se pudieron simular parámetros para Bass Clásico.")
                return
                
            val_m = st.slider("m - Límite de mercado (Millones)", float(popt_s[0]*0.2), float(popt_s[0]*2.0), float(popt_s[0]))
            val_p = st.slider("p - Coeficiente de Innovación (Publicidad)", 0.00001, 0.10000, float(popt_s[1]), format="%.5f")
            val_q = st.slider("q - Coeficiente de Imitación (Boca a boca)", 0.001, 1.000, float(popt_s[2]), format="%.3f")
            
            y_sens = bass_classic(t_proj, val_m, val_p, val_q)
            
            fig_s = go.Figure()
            fig_s.add_trace(go.Scatter(x=anios_reales, y=df_hist["adopcion_acumulada"], mode='markers', name='Datos Reales', marker=dict(color='black')))
            fig_s.add_trace(go.Scatter(x=anios_proj, y=bass_classic(t_proj, *popt_s), mode='lines', name='Ajuste Óptimo', line=dict(color='#2563EB', dash='dash')))
            fig_s.add_trace(go.Scatter(x=anios_proj, y=y_sens, mode='lines', name='Curva Simulada', line=dict(color='#10B981', width=3)))
            
            fig_s.update_layout(title="Simulador de Sensibilidad: Bass Clásico", xaxis_title="Año", yaxis_title="Millones de adoptantes")
            st.plotly_chart(fig_s, use_container_width=True)
            
    elif sens_model == "Dual Market":
        p_dual = params.get("Dual_Market")
        if p_dual:
            popt_s = p_dual.get("popt")
            if popt_s is None:
                popt_s = reconstruct_popt("Dual_Market", p_dual)
                
            if popt_s is None:
                st.warning("No se pudieron simular parámetros para Dual Market.")
                return
                
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown("**Segmento 1 (Innovadores)**")
                val_m1 = st.slider("m₁ - Mercado 1 (Millones)", float(popt_s[0]*0.1), float(popt_s[0]*2.5), float(popt_s[0]))
                val_p1 = st.slider("p₁ - Innovación M1", 0.0001, 0.1, float(popt_s[1]), format="%.4f")
                val_q1 = st.slider("q₁ - Imitación M1", 0.01, 1.0, float(popt_s[2]), format="%.3f")
            with col_s2:
                st.markdown("**Segmento 2 (Mayoría Pragmática)**")
                val_m2 = st.slider("m₂ - Mercado 2 (Millones)", float(popt_s[3]*0.1), float(popt_s[3]*2.5), float(popt_s[3]))
                val_p2 = st.slider("p₂ - Innovación M2", 0.00001, 0.05, float(popt_s[4]), format="%.5f")
                val_q2 = st.slider("q₂ - Imitación M2", 0.01, 1.0, float(popt_s[5]), format="%.3f")
                
            y_sens = dual_market_bass(t_proj, val_m1, val_p1, val_q1, val_m2, val_p2, val_q2)
            
            fig_s = go.Figure()
            fig_s.add_trace(go.Scatter(x=anios_reales, y=df_hist["adopcion_acumulada"], mode='markers', name='Datos Reales', marker=dict(color='black')))
            fig_s.add_trace(go.Scatter(x=anios_proj, y=dual_market_bass(t_proj, *popt_s), mode='lines', name='Ajuste Óptimo', line=dict(color='#DC2626', dash='dash')))
            fig_s.add_trace(go.Scatter(x=anios_proj, y=y_sens, mode='lines', name='Curva Simulada', line=dict(color='#10B981', width=3)))
            
            fig_s.update_layout(title="Simulador de Sensibilidad: Dual Market", xaxis_title="Año", yaxis_title="Millones de adoptantes")
            st.plotly_chart(fig_s, use_container_width=True)
