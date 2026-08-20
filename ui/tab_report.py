import os
import re
import streamlit as st
import numpy as np
import pandas as pd
from data.loaders import load_historical_data, load_model_parameters
from data.pdf_generator import generar_pdf_informe


def extract_section(text, start_pattern, end_pattern=None):
    if not text:
        return ""
    try:
        clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
        m1 = re.search(r'##[^\n]*?' + start_pattern, clean_text, re.IGNORECASE)
        if not m1:
            return ""
        idx = m1.end()
        if end_pattern:
            m2 = re.search(r'##[^\n]*?' + end_pattern, clean_text[idx:], re.IGNORECASE)
            if m2:
                return clean_text[idx : idx + m2.start()].strip()
        return clean_text[idx:].strip()
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
        
        analisis_cualitativo = extract_section(report_text, r'1\.', r'2\.')
        detalles_modelos = extract_section(report_text, r'Formulaci', r'3\.')
        if not detalles_modelos:
            detalles_modelos = extract_section(report_text, r'2\.', r'3\.')
        consenso_forecast = extract_section(report_text, r'5\.', r'6\.')
        informe_cientifico = extract_section(report_text, r'6\.')





        
        # Limpieza de títulos de sección en los textos crudos
        if analisis_cualitativo.startswith("### Análisis Cualitativo del Mercado"):
            analisis_cualitativo = analisis_cualitativo.replace("### Análisis Cualitativo del Mercado", "", 1).strip()
        if consenso_forecast.startswith("### Perspectiva Estratégica e Inteligencia Competitiva"):
            consenso_forecast = consenso_forecast.replace("### Perspectiva Estratégica e Inteligencia Competitiva", "", 1).strip()
        if informe_cientifico.startswith("### Contraste Académico con Literatura pgvector & Gemini"):
            informe_cientifico = informe_cientifico.replace("### Contraste Académico con Literatura pgvector & Gemini", "", 1).strip()
            
        try:
            import json
            from report_validator import ReportValidator, ModelFit

            tables_path = file_name + ".tables.json"
            historical_table = {}
            model_fits = []
            if os.path.exists(tables_path):
                with open(tables_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    historical_table = {int(k): v for k, v in data.get("historical", {}).items()}
                    model_fits = [
                        ModelFit(m["name"], m["r2"], m["mape"],
                                 {int(k): v for k, v in m.get("projections", {}).items()})
                        for m in data.get("models", [])
                    ]

            # Usar validación determinista (Capa 1) coincidente con la tolerancia del compilador
            validator = ReportValidator(report_text, historical_table, model_fits, tolerance_pct=20.0)
            issues = validator.run_all()
            blockers = [i for i in issues if i.severity == "BLOCKER"]

            if blockers:
                st.warning("⚠️ El informe contiene observaciones menores en la narrativa:")
                for iss in blockers:
                    st.warning(str(iss))
            elif issues:
                st.info("ℹ️ El informe pasó la validación con observaciones secundarias:")
                for iss in issues:
                    st.info(str(iss))
                    
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
                use_container_width=True,
                type="primary"
            )
        except Exception as e:
            st.error(f"Error al validar o generar el PDF descargable: {e}")
            
        st.divider()
        st.markdown(report_text)
