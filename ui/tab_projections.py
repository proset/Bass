import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from ui.theme import apply_dark_theme
from data.loaders import load_historical_data, load_model_parameters
from models.analytical_projections import project_model

def get_available_models(tech):
    from config import get_conn, release_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT modelo_tipo FROM model_parameters WHERE tecnologia = %s ORDER BY score DESC",
        (tech,)
    )
    rows = cur.fetchall()
    release_conn(conn)
    return [r[0] for r in rows]

def get_consensus_model(tech):
    """Modelo ganador: mejor Score en model_parameters (NO texto de consenso viejo)."""
    from config import get_conn, release_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT modelo_tipo, score FROM model_parameters WHERE tecnologia = %s ORDER BY score DESC LIMIT 1",
        (tech,)
    )
    row = cur.fetchone()
    release_conn(conn)
    if row:
        return row[0], float(row[1])  # modelo_tipo, score
    return None, None

def render_tab_projections(tecnologia_seleccionada):
    df_hist = load_historical_data(tecnologia_seleccionada)
    
    if df_hist.empty:
        st.warning("⚠️ No hay suficientes datos históricos para esta tecnología.")
        return
        
    import os
    
    is_analogical = False
    informe_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", f"informe_global_{tecnologia_seleccionada}.md"))
    
    params = load_model_parameters(tecnologia_seleccionada)
    if not params:
        # Check if analogical forecast exists (by reading informe)
        if os.path.exists(informe_path):
            with open(informe_path, encoding="utf-8") as f:
                if "PROYECCIÓN POR ANALOGÍA" in f.read():
                    is_analogical = True
                    
        if not is_analogical:
            st.warning("⚠️ No se pudieron cargar parámetros para esta tecnología ni se encontró proyección por analogía.")
            return

    if not is_analogical:
        consensus_key, consensus_score = get_consensus_model(tecnologia_seleccionada)
        if not consensus_key:
            st.warning("⚠️ No hay modelo de consenso válido con Score.")
            return
        available_models = get_available_models(tecnologia_seleccionada)

    if not is_analogical:
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

        selected_models = st.multiselect(
            "Modelos a comparar (el de consenso siempre visible):",
            options=available_models,
            default=[consensus_key],  # solo el consenso
            format_func=lambda x: model_labels.get(x, x)
        )
    else:
        st.info("📌 Esta es una tecnología en adopción temprana (Young Tech). Se muestra el pronóstico **Analogical Forecast** extraído del informe.")
        selected_models = []
        model_labels = {}
        consensus_key = None

    anios_reales = df_hist["anio"].values
    adopcion_real = df_hist["adopcion_acumulada"].values
    ultimo_anio = int(anios_reales[-1]) if len(anios_reales) > 0 else 2024
    primer_anio_hist = int(anios_reales[0])
    
    # Proyecciones hasta 2035 por defecto
    horizonte_final = 2035
    if ultimo_anio >= 2035:
        horizonte_final = ultimo_anio + 5
        
    num_years = horizonte_final - primer_anio_hist + 1
    t_proj = np.arange(num_years)
    anios_proj = [primer_anio_hist + i for i in t_proj]
    last_hist_value = adopcion_real[-1]

    fig = go.Figure()

    # Datos históricos
    fig.add_trace(go.Scatter(
        x=anios_reales, 
        y=adopcion_real, 
        mode='markers+lines', 
        name='Real (histórico)', 
        marker=dict(color='#ffffff', size=9, line=dict(color='#06b6d4', width=1.5)),
        line=dict(color='#ffffff', width=3)
    ))

    # Zona sombreada desde el último año real hasta 2035
    fig.add_vrect(
        x0=ultimo_anio, 
        x1=horizonte_final, 
        fillcolor="rgba(147, 197, 253, 0.1)", 
        line_width=0, 
        layer="below",
        annotation_text="Proyección", annotation_position="top left",
        annotation_font_color="rgba(255,255,255,0.5)"
    )

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

    if is_analogical:
        # Parse analogical scenarios from Markdown
        try:
            with open(informe_path, encoding="utf-8") as f:
                content = f.read()
            
            # Find the section ## Proyecciones por escenario
            import re
            match = re.search(r"## Proyecciones por escenario\s*\| Año \| Conservador \| Base \| Optimista \|\s*\|---\|---\|---\|---\|\s*((?:\| \d{4} \| [\d\.]+ \| [\d\.]+ \| [\d\.]+ \|\s*)+)", content)
            if match:
                table_lines = match.group(1).strip().split('\n')
                years_ana = []
                cons_ana = []
                base_ana = []
                opt_ana = []
                for line in table_lines:
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) == 4:
                        years_ana.append(int(parts[0]))
                        cons_ana.append(float(parts[1]))
                        base_ana.append(float(parts[2]))
                        opt_ana.append(float(parts[3]))
                
                # Plot Analogical scenarios
                # Join historical last point with first projection point to avoid gaps
                if len(years_ana) > 0 and len(anios_reales) > 0:
                    years_plot = [anios_reales[-1]] + years_ana
                    cons_plot = [adopcion_real[-1]] + cons_ana
                    base_plot = [adopcion_real[-1]] + base_ana
                    opt_plot = [adopcion_real[-1]] + opt_ana
                else:
                    years_plot = years_ana
                    cons_plot = cons_ana
                    base_plot = base_ana
                    opt_plot = opt_ana

                fig.add_trace(go.Scatter(
                    x=years_plot, y=opt_plot, mode='lines', name='Optimista (p75)',
                    line=dict(color="#10B981", width=2, dash='dot')
                ))
                fig.add_trace(go.Scatter(
                    x=years_plot, y=base_plot, mode='lines', name='Base (p50)',
                    line=dict(color="#3B82F6", width=3, dash='dash')
                ))
                fig.add_trace(go.Scatter(
                    x=years_plot, y=cons_plot, mode='lines', name='Conservador (p25)',
                    line=dict(color="#F59E0B", width=2, dash='dot')
                ))
        except Exception as e:
            st.error(f"No se pudieron parsear las proyecciones analógicas: {e}")
    else:
        models_to_plot = set(selected_models)
        models_to_plot.add(consensus_key)
    
        for m_key in models_to_plot:
            if m_key not in params:
                continue
                
            y_proj = project_model(m_key, params[m_key], t_proj)
            
            # Monotonicidad INTERNA: la curva no decrece respecto a sí misma
            for i in range(1, len(y_proj)):
                if y_proj[i] < y_proj[i-1]:
                    y_proj[i] = y_proj[i-1]
            
            color = color_palette.get(m_key, "#6B7280")
            is_consensus = (m_key == consensus_key)
            name = f"{model_labels.get(m_key, m_key)} (recomendado)" if is_consensus else model_labels.get(m_key, m_key)
            
            if is_consensus:
                idx_hist = np.where(np.array(anios_proj) <= ultimo_anio)[0]
                idx_proj = np.where(np.array(anios_proj) >= ultimo_anio)[0]
                
                fig.add_trace(go.Scatter(
                    x=np.array(anios_proj)[idx_hist], 
                    y=y_proj[idx_hist], 
                    mode='lines', 
                    name=f'{name} - Ajuste', 
                    line=dict(color=color, width=3, dash='solid'),
                    showlegend=False
                ))
                
                fig.add_trace(go.Scatter(
                    x=np.array(anios_proj)[idx_proj], 
                    y=y_proj[idx_proj], 
                    mode='lines', 
                    name=name, 
                    line=dict(color=color, width=3, dash='dash')
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=anios_proj, 
                    y=y_proj, 
                    mode='lines', 
                    name=name, 
                    line=dict(color=color, width=1.5, dash='solid')
                ))

    if is_analogical:
        title_text = "Analogical Forecast (Escenarios extraídos del informe)"
    else:
        title_text = f"Modelo de Consenso: {model_labels.get(consensus_key, consensus_key)} (Score {consensus_score:.2f})"

    apply_dark_theme(
        fig,
        title=dict(
            text=title_text,
            font=dict(color="#f1f5f9", size=15), x=0.02, xanchor="left"
        ),
        xaxis_title="Año",
        yaxis_title="Adopción Acumulada (Millones)",
    )
    
    st.plotly_chart(fig, use_container_width=True)
