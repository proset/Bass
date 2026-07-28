import os
import streamlit as st
import numpy as np
import pandas as pd
from data.loaders import load_historical_data, load_model_parameters
from data.pdf_generator import generar_pdf_informe

def extract_section(text, start_header, end_header=None):
    try:
        parts = text.split(start_header)
        if len(parts) < 2:
            return ""
        content = parts[1]
        if end_header:
            content = content.split(end_header)[0]
        return content.strip()
    except Exception:
        return ""

def render_tab_report(tecnologia_seleccionada):
    st.subheader("📄 Informe Global Unificado y Exportación PDF")
    st.markdown("Visualiza y descarga el dossier ejecutivo que consolida el análisis de mercado, ajuste histórico, proyecciones futuras e investigación científica RAG.")
    
    file_name = f"informe_global_{tecnologia_seleccionada}.md"
    
    # Controles superiores
    col_ctrl1, col_ctrl2 = st.columns([3, 1.5])
    with col_ctrl1:
        st.markdown(f"📂 **Archivo local:** `{file_name}`")
    with col_ctrl2:
        btn_compile = st.button("🔄 Generar / Actualizar Informe Unificado", use_container_width=True, type="primary")
        
    if btn_compile or not os.path.exists(file_name):
        with st.spinner("Compilando el informe completo con modelos matemáticos y RAG..."):
            try:
                from data.report_compiler import compilar_informe_global
                compilar_informe_global(tecnologia_seleccionada)
                st.cache_data.clear()
                st.success("¡Informe unificado compilado y guardado correctamente!")
                st.rerun()
            except Exception as e:
                st.error(f"Error compilando el informe: {e}")
                return
                
    # Si existe, mostrarlo y dar opción de descargar PDF
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            report_text = f.read()
            
        df_hist = load_historical_data(tecnologia_seleccionada)
        params = load_model_parameters(tecnologia_seleccionada)
        
        analisis_cualitativo = extract_section(report_text, "## 📄 1. Resumen Ejecutivo y Contexto de Mercado", "## 🔬 2. Datos Históricos y Resumen de Ajuste de Modelos")
        detalles_modelos = extract_section(report_text, "### 📐 Formulación Matemática de los Modelos Evaluados", "---")
        consenso_forecast = extract_section(report_text, "## 🔮 5. Pronóstico de Consenso Estratégico", "## 🤖 6. Informe Analítico Científico RAG")
        informe_cientifico = extract_section(report_text, "## 🤖 6. Informe Analítico Científico RAG")
        
        # Limpieza de títulos de sección en los textos crudos
        if analisis_cualitativo.startswith("### Análisis Cualitativo del Mercado"):
            analisis_cualitativo = analisis_cualitativo.replace("### Análisis Cualitativo del Mercado", "", 1).strip()
        if consenso_forecast.startswith("### Perspectiva Estratégica e Inteligencia Competitiva"):
            consenso_forecast = consenso_forecast.replace("### Perspectiva Estratégica e Inteligencia Competitiva", "", 1).strip()
        if informe_cientifico.startswith("### Contraste Académico con Literatura pgvector & Gemini"):
            informe_cientifico = informe_cientifico.replace("### Contraste Académico con Literatura pgvector & Gemini", "", 1).strip()
            
        try:
            pdf_bytes = generar_pdf_informe(
                tecnologia_seleccionada,
                df_hist,
                params,
                analisis_cualitativo,
                detalles_modelos,
                consenso_forecast,
                informe_cientifico
            )
            
            st.download_button(
                label="📥 Descargar Dossier Ejecutivo en PDF",
                data=bytes(pdf_bytes),
                file_name=f"informe_global_{tecnologia_seleccionada}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"No se pudo generar el PDF descargable: {e}")
            
        st.divider()
        st.markdown(report_text)
