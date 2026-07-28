import streamlit as st
import logging
import os
import tempfile
from data.sources import buscar_arxiv, buscar_openalex
from data.ingestion import ingestar_paper_db, get_conn, release_conn

logger = logging.getLogger("BassTabScientific")

def render_tab_scientific(tecnologia_seleccionada, tecnologias_disponibles):
    st.subheader("🔬 Descubrimiento y Búsqueda de Literatura Científica")
    st.markdown("Busca e indexa artículos científicos y de planificación en el motor RAG para fundamentar los análisis predictivos y los pronósticos de consenso.")
    
    subtab_search, subtab_upload = st.tabs(["🔍 Buscar en Línea", "📤 Subir Archivo PDF Local"])
    
    # --- Subtab 1: Buscar en Línea ---
    with subtab_search:
        col_q, col_src, col_num = st.columns([3, 1.5, 1])
        with col_q:
            search_query = st.text_input("Consulta de literatura", value=f"{tecnologia_seleccionada} diffusion model technology adoption", placeholder="Ej. Bass diffusion model application")
        with col_src:
            fuente_busqueda = st.selectbox("Fuente de Literatura", ["arXiv (Preprints Abiertos)", "ResearchGate / OpenAlex (Global)"], key="sci_source_select")
        with col_num:
            max_results = st.slider("Resultados máximos", min_value=1, max_value=20, value=5, key="sci_max_results_slider")
            
        btn_buscar = st.button("🔍 Buscar en Bases de Datos Científicas", use_container_width=True)
        
        # Guardar resultados en session_state para evitar perderlos al interactuar
        if "scientific_search_results" not in st.session_state:
            st.session_state.scientific_search_results = []
            
        if btn_buscar:
            with st.spinner(f"Consultando {fuente_busqueda}..."):
                if "arXiv" in fuente_busqueda:
                    st.session_state.scientific_search_results = buscar_arxiv(search_query, max_results)
                else:
                    st.session_state.scientific_search_results = buscar_openalex(search_query, max_results)
                
        if st.session_state.scientific_search_results:
            st.markdown(f"#### Resultados de la búsqueda ({len(st.session_state.scientific_search_results)})")
            
            for idx, paper in enumerate(st.session_state.scientific_search_results):
                with st.container(border=True):
                    col_info, col_action = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"##### 📄 {paper['titulo']}")
                        st.markdown(f"**Autores:** {', '.join(paper['autores'])}")
                        st.caption(f"📅 Publicado: {paper['fecha_publicacion']} | 🔗 [Ver Artículo original/Enlace]({paper['url_pdf']})")
                        
                        with st.expander("👁️ Ver Resumen / Abstract"):
                            st.write(paper['abstract'])
                            
                    with col_action:
                        selected_tech = st.selectbox(
                            "Asociar a tecnología",
                            tecnologias_disponibles,
                            index=tecnologias_disponibles.index(tecnologia_seleccionada) if tecnologia_seleccionada in tecnologias_disponibles else 0,
                            key=f"paper_tech_{idx}"
                        )
                        
                        # Comprobar si ya está indexado
                        db_conn = get_conn()
                        try:
                            cursor = db_conn.cursor()
                            cursor.execute("SELECT id FROM papers_metadata WHERE url_pdf = %s", (paper['url_pdf'],))
                            exists = cursor.fetchone()
                            cursor.close()
                        except Exception:
                            exists = False
                        finally:
                            release_conn(db_conn)
                            
                        if exists:
                            st.info("✓ Ya indexado en RAG")
                        else:
                            if st.button("📥 Indexar en RAG", key=f"ingest_{idx}", use_container_width=True):
                                # Usar st.status para feedback progresivo
                                with st.status("Iniciando la ingesta en RAG...", expanded=True) as status:
                                    success = ingestar_paper_db(paper, selected_tech, status)
                                    if success:
                                        st.success("¡Artículo indexado con éxito!")
                                        st.session_state.scientific_search_results = [] # Limpiar para actualizar
                                        st.rerun()
        else:
            st.info("💡 Ingresa un término de búsqueda (ej. 'diffusion models smart grid') y haz clic en 'Buscar' para recuperar papers.")
            
    # --- Subtab 2: Subir PDF Local ---
    with subtab_upload:
        st.markdown("### 📤 Indexar Artículo Científico Local")
        st.markdown("Sube un archivo PDF directamente para extraer sus fórmulas matemáticas e indexar su contenido en el motor RAG.")
        
        with st.form("form_upload_local_paper", clear_on_submit=True):
            uploaded_paper_file = st.file_uploader("Selecciona archivo PDF", type=["pdf"])
            upload_title = st.text_input("Título del Artículo", placeholder="Ej. Estudio empírico sobre difusión de computación cuántica...")
            upload_authors = st.text_input("Autores (Separados por comas)", placeholder="Ej. Pere Roset, Isaac Boixaderas")
            upload_abstract = st.text_area("Resumen / Abstract", placeholder="Copia aquí el resumen del artículo...")
            upload_date = st.date_input("Fecha de Publicación")
            
            upload_tech = st.selectbox(
                "Asociar a tecnología",
                tecnologias_disponibles,
                index=tecnologias_disponibles.index(tecnologia_seleccionada) if tecnologia_seleccionada in tecnologias_disponibles else 0,
                key="upload_tech_select"
            )
            
            submit_upload = st.form_submit_button("📥 Procesar e Indexar PDF Local")
            
        if submit_upload:
            if not uploaded_paper_file:
                st.error("Por favor, selecciona un archivo PDF primero.")
            elif not upload_title.strip():
                st.error("El título del artículo es obligatorio.")
            else:
                with st.spinner("Preparando archivo temporal..."):
                    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
                    with os.fdopen(fd, 'wb') as f:
                        f.write(uploaded_paper_file.getvalue())
                        
                    autores_list = [a.strip() for a in upload_authors.split(",") if a.strip()]
                    if not autores_list:
                        autores_list = ["Desconocido"]
                        
                    paper_data = {
                        "titulo": upload_title.strip(),
                        "autores": autores_list,
                        "abstract": upload_abstract.strip() if upload_abstract.strip() else "Sin resumen disponible.",
                        "url_pdf": f"local://{uploaded_paper_file.name}",
                        "fecha_publicacion": str(upload_date),
                        "local_pdf_path": temp_path
                    }
                    
                with st.status("Indexando PDF local...", expanded=True) as status:
                    success = ingestar_paper_db(paper_data, upload_tech, status)
                    if success:
                        st.success("¡Artículo PDF local procesado y guardado exitosamente!")
                        st.rerun()
