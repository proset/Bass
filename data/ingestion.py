import os
import logging
import pandas as pd
from config import get_conn, release_conn
from data.loaders import normalize_tech_name

logger = logging.getLogger("BassIngestion")

def insertar_historico_db(tech, datos_json):
    """
    Inserta la serie de tiempo de adopción histórica.
    Normaliza el nombre a minúsculas para evitar duplicados por variaciones de caso.
    """
    tech_norm = normalize_tech_name(tech)
    db_conn = get_conn()
    try:
        cursor = db_conn.cursor()
        
        # Primero eliminar registros anteriores para esta tecnología normalizada para evitar conflictos UNIQUE
        cursor.execute("DELETE FROM historical_adoption WHERE LOWER(TRIM(tecnologia)) = %s", (tech_norm,))
        
        # Filtrar ceros iniciales excesivos: mantener máximo 1 año cero previo al primer año con adopción > 0
        non_zero_indices = [i for i, d in enumerate(datos_json) if float(d.get("usuarios_millones", 0)) > 0]
        if non_zero_indices and non_zero_indices[0] > 1:
            first_nz = non_zero_indices[0]
            datos_json = datos_json[first_nz - 1:]

        prev_acumulada = 0.0
        records = []
        for d in datos_json:
            anio = int(d["anio"])
            acumulada = float(d["usuarios_millones"])
            anual = acumulada - prev_acumulada if prev_acumulada > 0 else acumulada
            prev_acumulada = acumulada
            # Insertar como nombre normalizado en la BD
            records.append((tech_norm, anio, anual, acumulada))
            
        cursor.executemany("""
            INSERT INTO historical_adoption (tecnologia, anio, adopcion_anual, adopcion_acumulada)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (tecnologia, anio) DO UPDATE 
            SET adopcion_anual = EXCLUDED.adopcion_anual,
                adopcion_acumulada = EXCLUDED.adopcion_acumulada,
                updated_at = now();
        """, records)
        db_conn.commit()
        cursor.close()
        logger.info(f"Datos históricos insertados correctamente para la tecnología: {tech_norm}")
        return True
    except Exception as e:
        logger.error(f"Error insertando datos históricos en la base de datos: {e}")
        return False
    finally:
        release_conn(db_conn)

def guardar_analisis_cualitativo(tech, analisis_text):
    """Guarda o actualiza el informe cualitativo del mercado."""
    # Fix 37: None guard — protege todos los callers (pipeline, Streamlit, manual)
    if not analisis_text or (isinstance(analisis_text, str) and analisis_text.strip() == ""):
        analisis_text = "No disponible."
    tech_norm = normalize_tech_name(tech)
    db_conn = get_conn()
    try:
        cursor = db_conn.cursor()
        cursor.execute("""
            INSERT INTO qualitative_analysis (tecnologia, analisis)
            VALUES (%s, %s)
            ON CONFLICT (tecnologia) 
            DO UPDATE SET analisis = EXCLUDED.analisis, fecha_analisis = now()
        """, (tech_norm, analisis_text))
        db_conn.commit()
        cursor.close()
        logger.info(f"Análisis cualitativo guardado para la tecnología: {tech_norm}")
        return True
    except Exception as e:
        logger.error(f"Error guardando análisis cualitativo: {e}")
        return False
    finally:
        release_conn(db_conn)

def guardar_consenso_forecast(tech, consenso_text):
    """Guarda o actualiza el pronóstico de consenso."""
    tech_norm = normalize_tech_name(tech)
    db_conn = get_conn()
    try:
        cursor = db_conn.cursor()
        cursor.execute("""
            INSERT INTO consensus_forecast (tecnologia, consenso)
            VALUES (%s, %s)
            ON CONFLICT (tecnologia) 
            DO UPDATE SET consenso = EXCLUDED.consenso, fecha_calculo = now()
        """, (tech_norm, consenso_text))
        db_conn.commit()
        cursor.close()
        logger.info(f"Pronóstico de consenso guardado para la tecnología: {tech_norm}")
        return True
    except Exception as e:
        logger.error(f"Error guardando pronóstico de consenso: {e}")
        return False
    finally:
        release_conn(db_conn)

def eliminar_tecnologia(tech):
    """Elimina permanentemente una tecnología y todos sus datos relacionados."""
    tech_norm = normalize_tech_name(tech)
    db_conn = get_conn()
    try:
        cursor = db_conn.cursor()
        cursor.execute("DELETE FROM historical_adoption WHERE LOWER(TRIM(tecnologia)) = %s", (tech_norm,))
        cursor.execute("DELETE FROM model_parameters WHERE LOWER(TRIM(tecnologia)) = %s", (tech_norm,))
        cursor.execute("DELETE FROM qualitative_analysis WHERE LOWER(TRIM(tecnologia)) = %s", (tech_norm,))
        cursor.execute("DELETE FROM consensus_forecast WHERE LOWER(TRIM(tecnologia)) = %s", (tech_norm,))
        
        # Eliminar papers relacionados (la tabla embeddings tiene cascade delete)
        cursor.execute("DELETE FROM papers_metadata WHERE LOWER(TRIM(tecnologia)) = %s", (tech_norm,))
        
        db_conn.commit()
        cursor.close()
        logger.info(f"Tecnología '{tech_norm}' y sus datos asociados eliminados de forma permanente.")
        return True
    except Exception as e:
        logger.error(f"Error eliminando tecnología: {e}")
        return False
    finally:
        release_conn(db_conn)

def ingestar_paper_db(paper, tecnologia, status_placeholder):
    """
    Indexa un paper científico en la base de datos RAG.
    La implementación final utiliza las dependencias de Gemini y RAG modular.
    (La importaremos en el bloque principal o la ejecutamos aquí importando los módulos en caliente).
    """
    from ai.gemini_client import generate_content_with_fallback, get_genai_client
    from ai.rag import smart_chunking
    
    tech_norm = normalize_tech_name(tecnologia)
    temp_pdf = None
    db_conn = get_conn()
    cursor = None
    try:
        if 'local_pdf_path' in paper:
            temp_pdf = paper['local_pdf_path']
        else:
            from data.sources import download_pdf
            pdf_url = paper.get('url_pdf', '')
            if pdf_url and ('pdf' in pdf_url.lower() or pdf_url.endswith('.pdf')):
                try:
                    status_placeholder.update(label="📥 Descargando archivo PDF desde el repositorio...", state="running")
                    temp_pdf = download_pdf(pdf_url)
                except Exception as e:
                    logger.warning(f"La descarga del PDF falló para {pdf_url}: {e}")
                    temp_pdf = None
        
        cursor = db_conn.cursor()
        
        # Insertar metadatos del paper
        cursor.execute("""
            INSERT INTO papers_metadata (titulo, autores, abstract, url_pdf, tecnologia, fecha_publicacion, procesado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            paper['titulo'], 
            paper['autores'], 
            paper['abstract'], 
            paper['url_pdf'] if paper['url_pdf'] else None, 
            tech_norm, 
            pd.to_datetime(paper['fecha_publicacion']).date() if paper.get('fecha_publicacion') and paper['fecha_publicacion'] != "Desconocida" else None, 
            False
        ))
        paper_id = cursor.fetchone()[0]
        
        # Procesar con Gemini si el PDF está disponible
        if temp_pdf:
            status_placeholder.update(label="🧠 Analizando contenido científico y ecuaciones con Gemini Pro...", state="running")
            genai = get_genai_client()
            uploaded_file = genai.upload_file(path=temp_pdf, display_name="Paper_PDF")
            
            prompt = (
                "Extract all the text from this scientific paper. "
                "Format the output in clean Markdown. "
                "CRITICAL: Keep all mathematical equations intact using LaTeX syntax, wrapped in $ for inline math or $$ for block math."
            )
            response = generate_content_with_fallback(
                prompt=prompt,
                contents=[uploaded_file, prompt]
            )
            full_text = response.text
            
            try:
                genai.delete_file(uploaded_file.name)
            except Exception:
                pass
                
            status_placeholder.update(label="✂️ Segmentando el contenido en fragmentos lógicos (Smart Chunking)...", state="running")
            # Añadir metadatos al chunking para un RAG más estructurado
            chunks = smart_chunking(full_text, metadata={"titulo": paper['titulo'], "autores": ", ".join(paper['autores'])})
        else:
            status_placeholder.update(label="📝 PDF no disponible o no accesible. Indexando resumen (Abstract)...", state="running")
            abstract_text = f"Resumen del artículo: {paper['titulo']}\nAutores: {', '.join(paper['autores'])}\nAbstract: {paper['abstract']}"
            chunks = [abstract_text]
        
        status_placeholder.update(label="🔢 Generando embeddings vectoriales con gemini-embedding-001 y guardando en pgvector...", state="running")
        
        genai = get_genai_client()
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
                
            embedding_result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=chunk,
                task_type="retrieval_document",
                output_dimensionality=768
            )
            embedding = embedding_result['embedding']
            vec_str = "[" + ",".join(str(x) for x in embedding) + "]"
            
            cursor.execute("""
                INSERT INTO papers_embeddings (paper_id, contenido_chunk, vector_embedding, numero_pagina)
                VALUES (%s, %s, %s::vector, %s)
            """, (paper_id, chunk, vec_str, i + 1))
            
        cursor.execute("""
            UPDATE papers_metadata
            SET procesado = TRUE
            WHERE id = %s
        """, (paper_id,))
        
        msg = f"🎉 ¡El artículo '{paper['titulo'][:30]}...' ha sido indexado con éxito!"
        if not temp_pdf:
            msg += " (Abstract únicamente)"
        status_placeholder.update(label=msg, state="complete")
        return True
    except Exception as e:
        logger.error(f"Error durante la ingesta del paper: {e}")
        if status_placeholder is not None:
            status_placeholder.update(label=f"❌ Error durante la ingesta: {str(e)}", state="error")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        release_conn(db_conn)
        if temp_pdf and os.path.exists(temp_pdf) and not paper.get('local_pdf_path'):
            try:
                os.remove(temp_pdf)
            except Exception:
                pass

def guardar_parametros_db(tech, fits):
    """Guarda los parámetros estimados de los modelos en la base de datos."""
    tech_norm = normalize_tech_name(tech)
    db_conn = get_conn()
    try:
        cursor = db_conn.cursor()
        cursor.execute("DELETE FROM model_parameters WHERE LOWER(TRIM(tecnologia)) = %s", (tech_norm,))
        
        for modelo_tipo, fit_data in fits.items():
            params = fit_data["params"]
            cols = ["tecnologia", "modelo_tipo", "r_cuadrado"] + list(params.keys())
            vals = [tech_norm, modelo_tipo, fit_data["r_cuadrado"]] + list(params.values())
            placeholders = ", ".join(["%s"] * len(vals))
            query = f"INSERT INTO model_parameters ({', '.join(cols)}) VALUES ({placeholders})"
            cursor.execute(query, vals)
            
        db_conn.commit()
        cursor.close()
        logger.info(f"Parámetros de modelos guardados para la tecnología: {tech_norm}")
        return True
    except Exception as e:
        logger.error(f"Error guardando parámetros de modelos: {e}")
        return False
    finally:
        release_conn(db_conn)

