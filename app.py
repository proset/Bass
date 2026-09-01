import streamlit as st # Reload trigger: hot-reload after switching model configurations to GEMINI_PRIMARY
import numpy as np
import pandas as pd
import re
import logging
from config import get_conn, release_conn
from data.loaders import get_tecnologias_disponibles, load_historical_data, load_model_parameters, normalize_tech_name
from data.ingestion import (
    insertar_historico_db, 
    guardar_analisis_cualitativo, 
    guardar_consenso_forecast, 
    eliminar_tecnologia, 
    guardar_parametros_db
)
from data.sources import descargar_dataset_owid
from ai.analysis import generar_analisis_cualitativo_solo, obtener_datos_y_analisis_ia, generar_consenso_pronostico_ia
from models.fit_models import fit_all_models
from ui.tab_projections import render_tab_projections
# from ui.tab_market import render_tab_market
# from ui.tab_scientific import render_tab_scientific
# from ui.tab_rag import render_tab_rag
from ui.tab_benchmarking import render_tab_benchmarking
# from ui.tab_report import render_tab_report
import subprocess
import os

BASS_DIR = os.path.dirname(os.path.abspath(__file__))

def render_tab_informe_global(tech):
    informe_path = os.path.join(BASS_DIR, f"informe_global_{tech}.md")
    if os.path.exists(informe_path):
        with open(informe_path, encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.info(f"No hay informe generado para '{tech}'. Usa el botón 'Carga Inteligente con IA' para generarlo (~5 min, $0.06).")

# Configurar logging básico para el servidor
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("BassApp")

# Configurar Streamlit
st.set_page_config(page_title="TechAdoption-Forecast", layout="wide")

# Inyectar CSS personalizado para el Look & Feel Premium
try:
    with open("ui/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception as e:
    pass

# Encabezado de barra lateral — Corporate Panel
sidebar_header_html = """
<div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:1.4rem; padding-bottom:1rem; border-bottom:1px solid rgba(255,255,255,0.14);">
    <div style="background:linear-gradient(135deg,#1a1a2e,#0f3460); width:34px; height:34px; border-radius:9px; display:flex; align-items:center; justify-content:center; flex-shrink:0; border:1px solid rgba(255,255,255,0.12);">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
             stroke="#93c5fd" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
             style="width:17px; height:17px;">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
        </svg>
    </div>
    <div>
        <div style="font-family:'Outfit',sans-serif; font-weight:700; font-size:0.82rem; color:#ffffff; letter-spacing:0.10em; text-transform:uppercase;">BASS Platform</div>
        <div style="font-size:0.65rem; color:#6b7280; letter-spacing:0.04em; margin-top:1px;">Tech Adoption Intelligence</div>
    </div>
</div>
"""
st.sidebar.markdown(sidebar_header_html, unsafe_allow_html=True)

tecnologias_disponibles = get_tecnologias_disponibles()

if "update_count" not in st.session_state:
    st.session_state.update_count = 0
if "force_tech" not in st.session_state:
    st.session_state.force_tech = None

# Determinar tecnología a mostrar por defecto
idx = 0
if st.session_state.force_tech in tecnologias_disponibles:
    idx = tecnologias_disponibles.index(st.session_state.force_tech)

tecnologia_seleccionada = st.sidebar.selectbox(
    "Seleccionar Tecnología",
    tecnologias_disponibles,
    index=idx,
    key=f"tech_dropdown_{st.session_state.update_count}"
)

# Cabecera Premium personalizada con isotipo geométrico moderno
header_html = f"""
<div class="premium-header">
    <div class="header-left">
        <div class="header-logo-bg">
            <!-- Logo: gráfico de área con línea de tendencia ascendente -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                 stroke-linecap="round" stroke-linejoin="round"
                 style="width:24px;height:24px;">
                <!-- Área de relleno inferior -->
                <path d="M3 18 L7 12 L11 15 L15 8 L19 10 L21 7 L21 18 Z"
                      fill="rgba(147,197,253,0.15)" stroke="none"/>
                <!-- Línea de tendencia principal -->
                <polyline points="3,18 7,12 11,15 15,8 19,10 21,7"
                          stroke="#93c5fd" stroke-width="2" fill="none"/>
                <!-- Puntos de datos -->
                <circle cx="7"  cy="12" r="1.5" fill="#93c5fd" stroke="none"/>
                <circle cx="15" cy="8"  r="1.5" fill="#93c5fd" stroke="none"/>
                <circle cx="21" cy="7"  r="1.5" fill="#bfdbfe" stroke="none"/>
                <!-- Ejes -->
                <line x1="3" y1="4" x2="3" y2="19" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
                <line x1="3" y1="19" x2="22" y2="19" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
            </svg>
        </div>
        <div class="header-title-container">
            <h1 class="header-title">{tecnologia_seleccionada.upper()} &amp; TECH ADOPTION</h1>
            <p class="header-subtitle">Plataforma de Inteligencia de Mercado &amp; Modelos de Difusión</p>
        </div>
    </div>
    <div class="header-right">
        <div class="badge-active">
            <span class="badge-dot"></span>
            LIVE INTELLIGENCE
        </div>
        <a href="#" class="action-btn">Solicitar Propuesta</a>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# --- Zona de Peligro: Eliminar Tecnología ---
if len(tecnologias_disponibles) > 1:
    st.sidebar.caption("🗑️ Zona de Peligro")
    confirmar_eliminar = st.sidebar.checkbox("Confirmar eliminación de la tecnología", help="Marca esta casilla para habilitar el botón de eliminación.")
    if st.sidebar.button("🗑️ Eliminar Tecnología Seleccionada", disabled=not confirmar_eliminar, use_container_width=True):
        if eliminar_tecnologia(tecnologia_seleccionada):
            st.sidebar.success(f"¡'{tecnologia_seleccionada}' eliminada con éxito!")
            st.session_state.force_tech = None
            st.session_state.update_count += 1
            st.cache_data.clear()
            st.rerun()
        else:
            st.sidebar.error("Error al eliminar la tecnología de la base de datos.")

# --- Formulario: Cargar Nueva Tecnología ---
st.sidebar.divider()
st.sidebar.subheader("📥 Cargar Nueva Tecnología")
st.sidebar.caption("Carga series reales de adopción acumulada desde Statista, CSV o Excel.")

with st.sidebar.form("nueva_tech_form"):
    nueva_tech = st.text_input("Nombre de la Tecnología", placeholder="Ej. Metaverso")
    
    manual_data_str = st.text_area(
        "Pegar Datos (Año, Millones)", 
        value="2015, 1.2\n2016, 3.4\n2017, 5.1\n2018, 5.5\n2019, 8.0\n2020, 12.5\n2021, 20.1\n2022, 45.0\n2023, 95.0\n2024, 180.0",
        help="Ingresa un año y su valor en millones por línea (separado por comas)."
    )
    
    uploaded_file = st.file_uploader(
        "O subir archivo CSV", 
        type=["csv"],
        help="El CSV debe tener una columna de año y otra de adopción."
    )
    
    submit_btn = st.form_submit_button("Cargar Manual/CSV")
    submit_statista = st.form_submit_button("🤖 Carga Inteligente con IA (pipeline v2)")

# Mostrar diálogo de sugerencia si falló la carga geográfica local
if "insufficient_local_data" in st.session_state:
    local_info = st.session_state.insufficient_local_data
    st.sidebar.warning(
        f"⚠️ **Datos locales no disponibles o excedidos** para *{local_info['tech_original']}*.\n\n"
        f"¿Deseas intentar modelar el **mercado global** de **{local_info['tech_global']}** en su lugar?"
    )
    if st.sidebar.button("🌍 Cargar Mercado Global en su lugar", use_container_width=True, type="primary"):
        st.session_state.force_global_load = local_info["tech_global"]
        del st.session_state.insufficient_local_data
        st.rerun()

if "force_global_load" in st.session_state:
    tech_to_load = st.session_state.force_global_load
    del st.session_state.force_global_load
    tech_norm = normalize_tech_name(tech_to_load)
    
    with st.status(f"Realizando carga inteligente con IA para el mercado global '{tech_to_load}'...", expanded=True) as status:
        status.update(label="🔍 Buscando reportes de Statista y estimaciones de mercado en la web...", state="running")
        parsed_data, analisis_text = obtener_datos_y_analisis_ia(tech_norm)
        if parsed_data:
            insertar_historico_db(tech_norm, parsed_data)
            if analisis_text:
                guardar_analisis_cualitativo(tech_norm, analisis_text)
            df_new = load_historical_data(tech_norm)
            t_data = np.arange(len(df_new))
            n_data = df_new["adopcion_acumulada"].values
            fits = fit_all_models(t_data, n_data)
            if fits:
                guardar_parametros_db(tech_norm, fits)
                new_params = load_model_parameters(tech_norm)
                if new_params and analisis_text:
                    consenso_text = generar_consenso_pronostico_ia(tech_norm, df_new, new_params, analisis_text)
                    if consenso_text:
                        guardar_consenso_forecast(tech_norm, consenso_text)
                try:
                    from data.report_compiler import compilar_informe_global
                    compilar_informe_global(tech_norm)
                    status.update(label=f"🎉 ¡'{tech_to_load}' cargada y verificada como PUBLICABLE!", state="complete")
                    st.session_state.force_tech = tech_norm
                    st.session_state.update_count += 1
                    st.cache_data.clear()
                    st.rerun()
                except Exception as ex_comp:
                    status.update(label=f"❌ Error de validación: {ex_comp}", state="error")
                    eliminar_tecnologia(tech_norm)
            else:
                status.update(label="❌ Fallo en el ajuste de curvas matemáticas.", state="error")
        else:
            status.update(label="❌ No se pudieron recuperar datos realistas en la web para esta tecnología.", state="error")

if nueva_tech:
    nueva_tech_norm = normalize_tech_name(nueva_tech)
    
    if submit_btn:
        if nueva_tech_norm in tecnologias_disponibles:
            st.sidebar.warning("Esta tecnología ya existe en la base de datos.")
            st.session_state.force_tech = nueva_tech_norm
            st.session_state.update_count += 1
            st.rerun()
        else:
            parsed_data = []
            
            # 1. Archivo subido
            if uploaded_file is not None:
                try:
                    df_upload = pd.read_csv(uploaded_file)
                    col_anio = df_upload.columns[0]
                    col_valor = df_upload.columns[1]
                    for _, row in df_upload.iterrows():
                        try:
                            parsed_data.append({"anio": int(row[col_anio]), "usuarios_millones": float(row[col_valor])})
                        except ValueError:
                            continue
                except Exception as e:
                    st.sidebar.error(f"Error leyendo CSV: {e}")
            
            # 2. Datos pegados manualmente
            if not parsed_data and manual_data_str.strip():
                lines = manual_data_str.strip().split("\n")
                for line in lines:
                    parts = re.split(r'[,\t;:]+', line.strip())
                    if len(parts) >= 2:
                        try:
                            parsed_data.append({"anio": int(parts[0].strip()), "usuarios_millones": float(parts[1].strip())})
                        except ValueError:
                            continue
            
            parsed_data = sorted(parsed_data, key=lambda x: x["anio"])
            
            if parsed_data:
                if len(parsed_data) < 5:
                    st.sidebar.error("Se necesitan al menos 5 puntos de datos para estimar las curvas de difusión.")
                else:
                    # Usar st.status para feedback progresivo
                    with st.status(f"Procesando '{nueva_tech}'...", expanded=True) as status:
                        status.update(label="💾 Guardando serie de adopción histórica en la base de datos...", state="running")
                        insertar_historico_db(nueva_tech_norm, parsed_data)
                        
                        status.update(label="🤖 Generando análisis cualitativo inicial de mercado con Gemini...", state="running")
                        analisis_text = generar_analisis_cualitativo_solo(nueva_tech_norm)
                        if analisis_text:
                            guardar_analisis_cualitativo(nueva_tech_norm, analisis_text)
                            
                        df_new = load_historical_data(nueva_tech_norm)
                        t_data = np.arange(len(df_new))
                        n_data = df_new["adopcion_acumulada"].values
                        
                        status.update(label="🔬 Ajustando los 7 modelos de difusión y calculando incertidumbre...", state="running")
                        fits = fit_all_models(t_data, n_data)
                        if fits:
                            guardar_parametros_db(nueva_tech_norm, fits)
                            
                            status.update(label="🔮 Sintetizando pronóstico de consenso RAG & IA...", state="running")
                            new_params = load_model_parameters(nueva_tech_norm)
                            if new_params and analisis_text:
                                consenso_text = generar_consenso_pronostico_ia(nueva_tech_norm, df_new, new_params, analisis_text)
                                if consenso_text:
                                    guardar_consenso_forecast(nueva_tech_norm, consenso_text)
                            
                            status.update(label="🧬 Compilando y auditando informe global (Fase 1 + Red-Team)...", state="running")
                            try:
                                from data.report_compiler import compilar_informe_global
                                compilar_informe_global(nueva_tech_norm)
                                
                                status.update(label=f"🎉 ¡'{nueva_tech}' cargada y verificada como PUBLICABLE!", state="complete")
                                st.session_state.force_tech = nueva_tech_norm
                                st.session_state.update_count += 1
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as ex_comp:
                                err_str = str(ex_comp)
                                if "MATH-14" in err_str or "demogr" in err_str.lower():
                                    st.session_state.insufficient_local_data = {
                                        "tech_original": nueva_tech,
                                        "tech_global": nueva_tech.lower().split(" en ")[0].split(" de ")[0].split(" para ")[0].strip().title()
                                    }
                                    st.rerun()
                                status.update(label=f"❌ Error de validación: {ex_comp}", state="error")
                                eliminar_tecnologia(nueva_tech_norm)
                        else:
                            status.update(label="❌ No se pudieron ajustar los modelos matemáticos a los datos.", state="error")
            else:
                st.sidebar.error("No se pudieron parsear datos válidos de la entrada.")
                
    elif submit_statista:
        if nueva_tech_norm in tecnologias_disponibles:
            st.sidebar.warning("Esta tecnología ya existe en la base de datos.")
            st.session_state.force_tech = nueva_tech_norm
            st.session_state.update_count += 1
            st.rerun()
        else:
            with st.spinner("Pipeline BASS v2: Extracción (Gemini) → Ajuste (GLM) → Análisis (Claude)... ~5 minutos"):
                result = subprocess.run(
                    ["python", "generate_report_v2.py", nueva_tech_norm],
                    cwd=BASS_DIR, capture_output=True, text=True, timeout=900
                )
            if result.returncode == 0:
                st.success(f"✅ Informe de '{nueva_tech_norm}' generado. Recargando...")
                st.session_state.force_tech = nueva_tech_norm
                st.session_state.update_count += 1
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"❌ Pipeline falló. Última salida:\n{result.stderr[-500:]}")

# --- Importar desde Our World in Data ---
st.sidebar.divider()
st.sidebar.subheader("🌍 Importar desde Our World in Data")

@st.cache_data(ttl=86400)
def cargar_owid_cached():
    return descargar_dataset_owid()

mostrar_owid = st.sidebar.checkbox("Activar catálogo OWID (Descarga remota)", value=False)

if mostrar_owid:
    df_owid = cargar_owid_cached()
    if not df_owid.empty:
        owid_entities = sorted(df_owid['Entity'].unique().tolist())
        owid_seleccionada = st.sidebar.selectbox("Selecciona Tecnología OWID", ["-- Selecciona --"] + owid_entities)
        cargar_owid_btn = st.sidebar.button("🌍 Importar y Modelar OWID", use_container_width=True)
        
        if cargar_owid_btn and owid_seleccionada != "-- Selecciona --":
            owid_norm = normalize_tech_name(owid_seleccionada)
            if owid_norm in tecnologias_disponibles:
                st.sidebar.warning(f"La tecnología '{owid_seleccionada}' ya existe.")
                st.session_state.force_tech = owid_norm
                st.session_state.update_count += 1
                st.rerun()
            else:
                with st.status(f"Importando '{owid_seleccionada}' desde OWID...", expanded=True) as status:
                    df_filtered = df_owid[df_owid['Entity'] == owid_seleccionada].copy()
                    val_col = 'Technology Diffusion (Comin and Hobijn (2004) and others)'
                    parsed_data = []
                    for _, row in df_filtered.iterrows():
                        try:
                            parsed_data.append({"anio": int(row['Year']), "usuarios_millones": float(row[val_col])})
                        except ValueError:
                            continue
                    
                    parsed_data = sorted(parsed_data, key=lambda x: x["anio"])
                    
                    if parsed_data:
                        status.update(label="💾 Ingestando serie histórica de OWID...", state="running")
                        insertar_historico_db(owid_norm, parsed_data)
                        
                        status.update(label="🤖 Generando análisis cualitativo con Gemini...", state="running")
                        analisis_text = generar_analisis_cualitativo_solo(owid_norm)
                        if analisis_text:
                            guardar_analisis_cualitativo(owid_norm, analisis_text)
                            
                        df_new = load_historical_data(owid_norm)
                        t_data = np.arange(len(df_new))
                        n_data = df_new["adopcion_acumulada"].values
                        
                        status.update(label="🔬 Ajustando curvas matemáticas con resolvedores numéricos...", state="running")
                        fits = fit_all_models(t_data, n_data)
                        if fits:
                            guardar_parametros_db(owid_norm, fits)
                            
                            status.update(label="🔮 Sintetizando pronóstico de consenso RAG & IA...", state="running")
                            new_params = load_model_parameters(owid_norm)
                            if new_params and analisis_text:
                                consenso_text = generar_consenso_pronostico_ia(owid_norm, df_new, new_params, analisis_text)
                                if consenso_text:
                                    guardar_consenso_forecast(owid_norm, consenso_text)
                            
                            status.update(label="🧬 Compilando y auditando informe global (Fase 1 + Red-Team)...", state="running")
                            try:
                                from data.report_compiler import compilar_informe_global
                                compilar_informe_global(owid_norm)
                                
                                status.update(label=f"🎉 ¡'{owid_seleccionada}' cargada y verificada como PUBLICABLE!", state="complete")
                                st.session_state.force_tech = owid_norm
                                st.session_state.update_count += 1
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as ex_comp:
                                status.update(label=f"❌ Error de validación: {ex_comp}", state="error")
                                eliminar_tecnologia(owid_norm)
                        else:
                            status.update(label="❌ No se pudieron ajustar las curvas matemáticas a los datos de OWID.", state="error")
                    else:
                        status.update(label="❌ Los datos de OWID están vacíos o no son válidos.", state="error")

# =======================================================
# Navegación Principal de Pestañas (Tabs)
# =======================================================
# import os  # Already imported
# report_file = f"informe_global_{tecnologia_seleccionada}.md"
# if not os.path.exists(report_file):
#     st.warning(f"⚠️ El informe global para '{tecnologia_seleccionada}' no está compilado o auditado en el sistema.")
#     ...
# else:

tabs = st.tabs(["📈 Proyecciones de Adopción", "📊 Comparativa de Tecnologías", "📄 Informe Global"])

with tabs[0]:
    render_tab_projections(tecnologia_seleccionada)

with tabs[1]:
    # Use render_tab_benchmarking for comparative
    render_tab_benchmarking(tecnologias_disponibles)

with tabs[2]:
    render_tab_informe_global(tecnologia_seleccionada)

# tab1, tab_bench, tab_market, tab2, tab3, tab_report = st.tabs([
#     "📈 Proyecciones de Adopción", 
#     "📊 Benchmarking Competitivo",
#     "📊 Análisis de Mercado", 
#     "🔬 Descubrimiento Científico", 
#     "🤖 Asistente RAG",
#     "📄 Informe Global"
# ])
# 
# with tab1:
#     render_tab_projections(tecnologia_seleccionada)
# 
# with tab_bench:
#     render_tab_benchmarking(tecnologias_disponibles)
# 
# with tab_market:
#     render_tab_market(tecnologia_seleccionada)
# 
# with tab2:
#     render_tab_scientific(tecnologia_seleccionada, tecnologias_disponibles)
# 
# with tab3:
#     render_tab_rag(tecnologia_seleccionada)
# 
# with tab_report:
#     render_tab_report(tecnologia_seleccionada)
