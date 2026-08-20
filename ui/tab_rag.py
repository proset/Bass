import streamlit as st
import logging
from config import get_conn, release_conn
from ai.rag import buscar_chunks_similares
from ai.gemini_client import generate_content_with_fallback

logger = logging.getLogger("BassTabRAG")

def render_tab_rag(tecnologia_seleccionada):
    st.subheader("🤖 Motor Analítico Predictivo RAG (Gemini 3.1 Pro)")
    st.markdown("Interactúa en un chat continuo con la IA para analizar la adopción tecnológica y contrastar modelos de difusión contra la literatura científica indexada.")
    
    # Listar artículos científicos indexados
    db_conn = get_conn()
    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT titulo, tecnologia, fecha_publicacion, url_pdf FROM papers_metadata WHERE procesado = TRUE ORDER BY fecha_publicacion DESC")
        ingested_papers = cursor.fetchall()
        cursor.close()
    except Exception as e:
        logger.error(f"Error consultando papers indexados: {e}")
        ingested_papers = []
    finally:
        release_conn(db_conn)
        
    if ingested_papers:
        with st.expander(f"📚 Artículos Científicos Disponibles en el Contexto RAG ({len(ingested_papers)})"):
            for title, tech, date, url_pdf in ingested_papers:
                if url_pdf:
                    st.markdown(f"- 📄 [**{title}**]({url_pdf}) (Tecnología: `{tech}`, Fecha: `{date}`)")
                else:
                    st.markdown(f"- 📄 **{title}** (Tecnología: `{tech}`, Fecha: `{date}`)")
    else:
        st.warning("⚠️ No hay artículos científicos indexados actualmente. Ve a la pestaña 'Descubrimiento Científico' para agregar literatura de soporte.")
        
    # --- Inicialización del Estado del Informe RAG per-tecnología ---
    if "rag_reports" not in st.session_state:
        st.session_state.rag_reports = {}
        
    query_usuario = st.text_input(
        "Consulta o enfoque adicional para el informe científico",
        placeholder="Escribe aquí tu consulta o hipótesis específica (ej. analizar el abismo de Moore, velocidad de transición...)",
        key=f"rag_query_input_{tecnologia_seleccionada}"
    )
    
    col_btn_gen, col_btn_clear = st.columns([4, 1])
    with col_btn_gen:
        btn_generar = st.button("🔬 Generar Informe Analítico Científico", use_container_width=True, type="primary")
    with col_btn_clear:
        btn_limpiar = st.button("🗑️ Limpiar", use_container_width=True)
        
    if btn_limpiar:
        if tecnologia_seleccionada in st.session_state.rag_reports:
            del st.session_state.rag_reports[tecnologia_seleccionada]
            st.rerun()

    if btn_generar:
        if not ingested_papers:
            st.error("No hay literatura en el contexto RAG para generar el informe. Por favor, indexa al menos un artículo científico primero.")
        else:
            with st.spinner("Generando reporte científico RAG..."):
                # Buscar fragmentos similares para la tecnología actual
                query_contexto = query_usuario if query_usuario.strip() else f"Análisis de adopción de {tecnologia_seleccionada}"
                context_chunks = buscar_chunks_similares(query_contexto, tecnologia_seleccionada, match_count=5)
                
                if not context_chunks:
                    context_text = "No se encontraron papers específicos en la base de datos para esta tecnología."
                else:
                    context_text = "\n\n".join([
                        f"--- Fragmento (Pág. {c['numero_pagina'] if 'numero_pagina' in c else 'N/D'}, Artículo: {c.get('titulo', 'Sin Título')}) ---\n{c['contenido_chunk']}" 
                        for c in context_chunks
                    ])
                    
                prompt = r"""
ROLE: Senior Data Scientist & Technology Forecasting Expert
CONTEXT: Eres el motor analítico de la plataforma. Analiza el estado de adopción basándote en este contexto científico de papers indexados: 
{CONTEXT_TEXT}

Adicionalmente, el usuario ha formulado esta consulta o hipótesis: "{QUERY_USUARIO}"

INSTRUCCIÓN: Genera un informe predictivo detallado de modelos de adopción para la tecnología: {TECNOLOGIA_SELECCIONADA}. Debe incluir obligatoriamente el modelado matemático detallado de los 10 modelos de difusión disponibles.
ESTRUCTURA OBLIGATORIA DEL INFORME:
1. Diagnóstico de Estado Actual: Determina si la tecnología está atrapada en el 'Abismo de Moore' o si ya saltó al Mercado 2 (Mayoría Pragmática). Justifica detalladamente con la literatura científica y los datos del mercado.
2. Contraste de Previsión y Modelos Científicos:
   Explica y compara cómo abordan la adopción los 10 modelos de difusión. Escribe la formulación matemática en formato de TEXTO PLANO (NO uses LaTeX, no uses $$ ni $, usa símbolos de texto simples como e^, / y *) para cada uno de los siguientes modelos:
   - **Modelo de Bass Clásico (1969)**:
     x(t) = m * (1 - exp(-(p + q) * t)) / (1 + (q / p) * exp(-(p + q) * t))
   - **Modelo de Dos Mercados Independientes - Roset & Canals (2011)**:
     x(t) = x1(t) + x2(t), donde x1 y x2 son modelos de Bass independientes.
   - **Modelo de Innovación Pura de Fourt & Woodlock (1960)**:
     N(t) = m * (1 - exp(-p * t))
   - **Modelo Asimétrico de Gompertz**:
     N(t) = m * exp(-exp(-k * (t - t0)))
   - **Modelo de Bass Generalizado - GBM (1994)**:
     dN/dt = (p + (q / m) * N(t)) * (m - N(t)) * (1 + beta * t)
   - **Modelo con Publicidad de Horsky & Simon (1983)**:
     dN/dt = (p0 + alpha * ln(1 + t) + (q / m) * N(t)) * (m - N(t))
   - **Modelo del Efecto Saddle de Muller & Yogev (2006)**:
     I(t) = Ni * (1 - exp(-(pi + qi) * t)) / (1 + (qi / pi) * exp(-(pi + qi) * t))
     dM/dt = (pm + qm * M(t) / (Ni + Nm) + qim * I(t) / (Ni + Nm)) * (Nm - M(t))
   - **Modelo de Influenciadores e Imitadores de Van den Bulte & Joshi (2007)**:
     F1(t) = (1 - exp(-(p1 + q1) * t)) / (1 + (q1 / p1) * exp(-(p1 + q1) * t))
     dF2/dt = q2 * (w * F1(t) + (1 - w) * F2(t)) * (1 - F2(t))
     N(t) = M1 * F1(t) + M2 * F2(t)
   - **Modelo Logístico de Convergencia**:
     L(t) = b1 / (1 + ((b1 - b0) / b0) * exp(-k2 * (t - t0)))
   - **Modelo de Mercado Potencial Dinámico y Endógeno de Ladrón-de-Guevara & Putsis (2011)**:
     C(t) = 1.0 - theta * exp(-gamma * N(t) / S), donde M(t) = C(t) * S y la difusión es:
     dN/dt = (alpha + beta * (N / M)) * (M - N)
3. Interpretación y Parámetros: Explica detalladamente el significado práctico de los coeficientes de interacción (como q_im, gamma, w, theta y la intensidad de red gamma de LGP), así como la tasa de crecimiento logístico k_2 y el punto de inflexión t_0, y cómo justifican o explican los saltos o baches entre mercados en el caso de {TECNOLOGIA_SELECCIONADA}.
4. Citas y Evidencia: Cita textualmente con Autor y Año los papers origen del contexto científico que sustentan el análisis (asegúrate de incluir y contrastar las teorías del paper de Ladrón-de-Guevara & Putsis 2011).
5. FORMATO: Markdown limpio en español, sin textos aclaratorios o introducciones de chat como "Aquí tienes...".RMATO: Markdown limpio en español, sin textos aclaratorios o introducciones de chat como "Aquí tienes...".
""".replace("{CONTEXT_TEXT}", context_text).replace("{QUERY_USUARIO}", query_usuario).replace("{TECNOLOGIA_SELECCIONADA}", tecnologia_seleccionada)
                
                try:
                    respuesta_gemini = generate_content_with_fallback(prompt=prompt)
                    st.session_state.rag_reports[tecnologia_seleccionada] = respuesta_gemini.text
                except Exception as e:
                    logger.error(f"Error generando informe RAG: {e}")
                    st.error(f"❌ Error al procesar tu consulta con la IA: {e}")

    # Mostrar informe si existe para la tecnología actual
    if tecnologia_seleccionada in st.session_state.rag_reports:
        st.markdown("---")
        st.markdown("### 📄 Informe de Análisis Científico RAG")
        st.markdown(st.session_state.rag_reports[tecnologia_seleccionada])
