import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import logging
import google.ai.generativelanguage_v1beta as gapic
from data.loaders import load_historical_data, load_model_parameters
from models.fit_models import fit_all_models, rank_and_select_best_model
from ai.gemini_client import generate_content_with_fallback
from models.analytical_projections import project_model
from ui.tab_projections import get_consensus_model
from ui.theme import apply_dark_theme, BRAND_COLORS, dark_table_html

logger = logging.getLogger("BassTabBenchmarking")



@st.cache_data(ttl=3600)
def get_fitted_models_cached(tech, df_hist):
    t_data = np.arange(len(df_hist))
    n_data = df_hist["adopcion_acumulada"].values
    return fit_all_models(t_data, n_data)

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
        
        y_proj = project_model(m_key, p, t_proj)
        
        # Monotonicidad solo a partir del último año histórico
        idx_future = np.where(np.array(anios_proj_full) > anios_reales[-1])[0]
        if len(idx_future) > 0:
            y_proj[idx_future] = np.maximum(y_proj[idx_future], df_hist["adopcion_acumulada"].iloc[-1])
        
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
                name=f"{tech.title} (Histórico)",
                marker=dict(color=color, size=8, symbol='circle')
            ))
            
            # Curva proyectada
            fig.add_trace(go.Scatter(
                x=data["anios_proj"],
                y=data["proj"],
                mode='lines',
                name=f"{tech.title} ({model_labels[data['modelo_usado']]})",
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
        with st.spinner("Gemini está recopilando datos de mercado y elaborando el informe comparativo..."):
            # Reunir información de las marcas para pasar al prompt
            brief_brands = []
            for tech, data in brand_data.items():
                params_m = data["params"]
                m_usado = data["modelo_usado"]
                # Intentar leer coeficientes p y q o m del modelo usado
                info_coefs = ""
                p_dict = params_m.get("params", params_m)
                if m_usado in ["Bass_Clasico", "Dual_Market", "VdB_Joshi"]:
                    info_coefs = f"Coef. Innovación (p1): {p_dict.get('param_p1', 'N/D')}, Coef. Imitación (q1): {p_dict.get('param_q1', 'N/D')}"
                elif m_usado == "Logistic_Diffusion_Convergence":
                    info_coefs = f"Tasa de Crecimiento (k2): {p_dict.get('param_p2', 'N/D')}, Punto Inflexión (t0): {p_dict.get('param_q1', 'N/D')}"
                
                # Cargar el reporte cualitativo si existe en BD
                from data.loaders import load_qualitative_analysis
                qualitative_txt = load_qualitative_analysis(tech) or "No hay informe cualitativo guardado."
                
                # Obtener proyección de hitos
                proj_5_idx = min(len(data["anios_reales"]) + 4, len(data["proj"]) - 1)
                proj_10_idx = min(len(data["anios_reales"]) + 9, len(data["proj"]) - 1)
                
                brief_brands.append(
                    f"- **Tecnología/Marca**: {tech.upper}\n"
                    f"  - Modelo Proyección Usado: {model_labels[m_usado]}\n"
                    f"  - Historial (años): {data['anios_reales']}\n"
                    f"  - Valores Reales (millones): {data['reales']}\n"
                    f"  - Proyección a 5 años (millones): {data['proj'][proj_5_idx]:.2f}\n"
                    f"  - Proyección a 10 años (millones): {data['proj'][proj_10_idx]:.2f}\n"
                    f"  - Coeficientes Clave: {info_coefs}\n"
                    f"  - Contexto Cualitativo Corto:\n{qualitative_txt[:600]}..."
                )
                
            brief_text = "\n\n".join(brief_brands)
            
            prompt = f"""
ROLE: Senior Competitive Intelligence Manager & Technology Forecasting Expert
CONTEXT: Estás realizando un análisis comparativo y de benchmarking estratégico entre marcas y tecnologías competidoras en base a modelos cuantitativos y datos cualitativos.

Marcas y Tecnologías seleccionadas para la comparativa:
{brief_text}

INSTRUCCIÓN: Genera un Informe de Consenso y Benchmarking Estratégico en español. Analiza la situación competitiva de las marcas indicadas y sintetiza la comparativa.

El informe debe estructurarse obligatoriamente con las siguientes secciones:
1. **Análisis de Dinámica Competitiva**:
   - Compara la velocidad de adopción de cada marca.
   - Explica cuál de ellas está liderada por la innovación y gasto publicitario (alto coeficiente de innovación $p$) y cuál se beneficia más de la recomendación, viralidad o boca a boca (alto coeficiente de imitación $q$).
2. **Diagnóstico del Cruce del Abismo**:
   - Analiza qué marcas han cruzado con éxito el "Abismo de Moore" hacia el mercado masivo y cuáles siguen estancadas o en riesgo de contracción (efecto saddle o saddle effect).
3. **Consenso sobre Evolución de Cuota de Mercado**:
   - Evalúa cómo cambiará la correlación de fuerzas competitivas a 5 y 10 años en el futuro.
4. **Recomendaciones de Marketing Estratégico**:
   - Aporta 2 recomendaciones específicas para cada marca basadas en sus parámetros matemáticos y realidad comercial (ej. si su $p$ es bajo, potenciar branding; si su $q$ es bajo, potenciar la retención de clientes y programas de referidos).

FORMATO: Markdown profesional en español. No escribas introducciones ni preámbulos informales.
"""
            try:
                respuesta = generate_content_with_fallback(
                    prompt=prompt,
                    tools=None
                )
                st.session_state.bench_ia_report[selected_key] = respuesta.text.strip()
            except Exception as e:
                logger.error(f"Error generando informe comparativo de IA: {e}")
                st.error(f"❌ Error al procesar tu consulta con la IA: {e}")

    # Mostrar informe RAG comparativo
    if selected_key in st.session_state.bench_ia_report:
        st.markdown("---")
        st.markdown("### Informe de Consenso y Benchmarking Estratégico")
        st.markdown(st.session_state.bench_ia_report[selected_key])
