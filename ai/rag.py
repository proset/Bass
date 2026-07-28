import re
import logging
from config import get_conn, release_conn, EMBEDDING_MODEL
from ai.gemini_client import get_genai_client
from psycopg2.extras import DictCursor
from data.loaders import normalize_tech_name

logger = logging.getLogger("BassRAG")

def smart_chunking(text, chunk_size=1200, overlap=200, metadata=None):
    """
    Divide el texto en fragmentos lógicos respetando ecuaciones matemáticas en LaTeX.
    Si se proporciona metadata (ej. dict con 'titulo' y 'autores'), se inyecta estructuradamente
    al inicio de cada fragmento para enriquecer la calidad de la búsqueda vectorial.
    """
    # Proteger bloques LaTeX de corte
    math_pattern = re.compile(r'(\$\$[\s\S]*?\$\$|\$[\s\S]*?\$)', re.MULTILINE)
    placeholders = {}
    
    def replacer(match):
        uid = f"__MATH_BLOCK_{len(placeholders)}__"
        placeholders[uid] = match.group(0)
        return uid
        
    text_masked = math_pattern.sub(replacer, text)
    paragraphs = text_masked.split('\n')
    
    meta_prefix = ""
    if metadata:
        meta_prefix = f"[Artículo: {metadata.get('titulo', 'Sin Título')} | Autores: {metadata.get('autores', 'Desconocido')}]\n"
        
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        if len(current_chunk) + len(p) < chunk_size:
            current_chunk += p + "\n"
        else:
            # Reinsertar ecuaciones y guardar
            final_chunk = current_chunk.strip()
            for uid, math_text in placeholders.items():
                final_chunk = final_chunk.replace(uid, math_text)
            
            if final_chunk:
                chunks.append(meta_prefix + final_chunk)
            
            # Continuar con el solape
            current_chunk = current_chunk[-overlap:] + p + "\n"
            
    if current_chunk.strip():
        final_chunk = current_chunk.strip()
        for uid, math_text in placeholders.items():
            final_chunk = final_chunk.replace(uid, math_text)
        if final_chunk:
            chunks.append(meta_prefix + final_chunk)
        
    return chunks

def buscar_chunks_similares(query, tecnologia, match_count=5, similarity_threshold=0.5):
    """
    Vectoriza la consulta y busca los fragmentos más similares en la base de datos
    usando la función PL/pgSQL match_chunks (case-insensitive para el filtro de tecnología).
    """
    tech_norm = normalize_tech_name(tecnologia)
    genai = get_genai_client()
    
    try:
        # Generar embedding de la consulta
        embedding_result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=query,
            task_type="retrieval_query",
            output_dimensionality=768
        )
        query_embedding = embedding_result['embedding']
        vec_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
    except Exception as e:
        logger.error(f"Error generando embedding de consulta para RAG: {e}")
        return []
        
    db_conn = get_conn()
    try:
        query_rpc = """
        SELECT * FROM match_chunks(
            %s::vector, 
            %s, 
            %s, 
            %s
        )
        """
        with db_conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query_rpc, (vec_str, similarity_threshold, match_count, tech_norm))
            results = cur.fetchall()
            
        logger.info(f"Búsqueda vectorial RAG devolvió {len(results)} fragmentos para '{tecnologia}'")
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error ejecutando búsqueda vectorial match_chunks: {e}")
        return []
    finally:
        release_conn(db_conn)
