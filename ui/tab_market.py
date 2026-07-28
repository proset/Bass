import streamlit as st
import logging
from data.loaders import load_historical_data, load_model_parameters, load_qualitative_analysis, load_consenso_forecast
from data.ingestion import guardar_analisis_cualitativo, guardar_consenso_forecast
from ai.analysis import generar_analisis_cualitativo_solo, generar_consenso_pronostico_ia

logger = logging.getLogger("BassTabMarket")

def render_tab_market(tecnologia_seleccionada):
    st.subheader(f"📊 Inteligencia de Mercado: {tecnologia_seleccionada.title()}")
    
    # Cargar datos e informes
    df_hist = load_historical_data(tecnologia_seleccionada)
    params = load_model_parameters(tecnologia_seleccionada)
    analisis_cualitativo = load_qualitative_analysis(tecnologia_seleccionada)
    consenso_text = load_consenso_forecast(tecnologia_seleccionada)
    
    subtab_qualitative, subtab_consensus = st.tabs([
        "📄 Informe Cualitativo del Mercado", 
        "🔮 Pronóstico de Consenso RAG & IA"
    ])
    
    # --- Subtab 1: Informe Cualitativo ---
    with subtab_qualitative:
        if analisis_cualitativo:
            st.markdown(analisis_cualitativo)
            st.divider()
            
            # Exportar informe cualitativo
            st.download_button(
                label="📥 Exportar Informe Cualitativo (Markdown)",
                data=analisis_cualitativo.encode("utf-8"),
                file_name=f"analisis_cualitativo_{tecnologia_seleccionada}.md",
                mime="text/markdown",
                use_container_width=True
            )
            
            st.caption("Re-evaluar el mercado utilizando datos actualizados de la web:")
            if st.button("🔄 Regenerar Análisis Cualitativo (Búsqueda Web)", key="regen_qual_btn", use_container_width=True):
                with st.spinner("Buscando informes en la web y regenerando análisis cualitativo..."):
                    new_text = generar_analisis_cualitativo_solo(tecnologia_seleccionada)
                    if new_text:
                        guardar_analisis_cualitativo(tecnologia_seleccionada, new_text)
                        st.success("¡Análisis cualitativo regenerado e indexado con éxito!")
                        st.rerun()
                    else:
                        st.error("No se pudo obtener una respuesta válida de la IA.")
        else:
            st.info("ℹ️ No hay un análisis cualitativo guardado para esta tecnología.")
            if st.button("🤖 Generar Análisis Cualitativo con IA (Web)", key="generate_qual_btn", use_container_width=True):
                with st.spinner("Realizando búsquedas en la web y generando informe..."):
                    new_text = generar_analisis_cualitativo_solo(tecnologia_seleccionada)
                    if new_text:
                        guardar_analisis_cualitativo(tecnologia_seleccionada, new_text)
                        st.success("¡Análisis generado correctamente!")
                        st.rerun()
                    else:
                        st.error("Error al generar el informe con la IA.")
                        
    # --- Subtab 2: Pronóstico de Consenso RAG & IA ---
    with subtab_consensus:
        if consenso_text:
            st.markdown(consenso_text)
            st.divider()
            
            # Exportar pronóstico de consenso
            st.download_button(
                label="📥 Exportar Pronóstico de Consenso (Markdown)",
                data=consenso_text.encode("utf-8"),
                file_name=f"pronostico_consenso_{tecnologia_seleccionada}.md",
                mime="text/markdown",
                use_container_width=True
            )
            
            st.caption("Regenerar el consenso basándose en el análisis cualitativo y las últimas proyecciones:")
            if st.button("🔄 Regenerar Pronóstico de Consenso", key="regen_consensus_btn", use_container_width=True):
                if not df_hist.empty and params and analisis_cualitativo:
                    with st.spinner("Sintetizando curvas matemáticas y análisis cualitativo..."):
                        new_consenso = generar_consenso_pronostico_ia(tecnologia_seleccionada, df_hist, params, analisis_cualitativo)
                        if new_consenso:
                            guardar_consenso_forecast(tecnologia_seleccionada, new_consenso)
                            st.success("¡Pronóstico de consenso regenerado!")
                            st.rerun()
                        else:
                            st.error("Error al generar el pronóstico de consenso.")
                else:
                    st.error("Asegúrate de que la tecnología tenga datos históricos, modelos ajustados y un análisis cualitativo previo.")
        else:
            st.info("ℹ️ Aún no se ha generado el pronóstico de consenso para esta tecnología.")
            if st.button("🤖 Generar Pronóstico de Consenso con IA", key="generate_consensus_btn", use_container_width=True):
                if not df_hist.empty and params and analisis_cualitativo:
                    with st.spinner("Integrando curvas de difusión y narrativa de mercado..."):
                        new_consenso = generar_consenso_pronostico_ia(tecnologia_seleccionada, df_hist, params, analisis_cualitativo)
                        if new_consenso:
                            guardar_consenso_forecast(tecnologia_seleccionada, new_consenso)
                            st.success("¡Pronóstico de consenso generado con éxito!")
                            st.rerun()
                        else:
                            st.error("Error en la generación por la IA.")
                else:
                    st.error("Se requieren datos históricos, parámetros y un análisis cualitativo. Genera primero el análisis en la pestaña correspondiente.")
