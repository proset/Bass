import streamlit as st
import os
import toml
import json
import logging
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
import psycopg2
from psycopg2 import pool as pg_pool
from psycopg2.extras import DictCursor, RealDictCursor
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# Configuración Inicial y Conexiones
# ==========================================
st.set_page_config(page_title="TechAdoption-Forecast", layout="wide")

try:
    if "postgres" in st.secrets:
        conn_params = st.secrets["postgres"]
    else:
        st.error("Error: Configura la sección [postgres] en .streamlit/secrets.toml")
        st.stop()
        
    GEMINI_API_KEY = st.secrets.get("gemini", {}).get("api_key") or st.secrets.get("gemini_api_key")
    if not GEMINI_API_KEY:
        st.error("Error: Configura GEMINI_API_KEY en .streamlit/secrets.toml")
        st.stop()
except Exception as e:
    st.error(f"Error leyendo secrets.toml: {e}")
    st.stop()

# ==========================================
# CRÍTICO #2 — Connection Pool (thread-safe)
# Reemplaza la conexión global frágil por un pool que:
# - Soporta múltiples usuarios concurrentes en Streamlit
# - Se recupera automáticamente de caídas de red
# - Nunca deja la app en estado irrecuperable
# ==========================================
@st.cache_resource
def _get_pool():
    """Crea y cachea un ThreadedConnectionPool para toda la sesión de Streamlit."""
    try:
        connection_pool = pg_pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            host=conn_params["host"],
            database=conn_params["database"],
            user=conn_params["user"],
            password=conn_params["password"],
            port=conn_params.get("port", 6543),
            connect_timeout=10,
        )
        logger.info("Connection pool creado correctamente.")
        return connection_pool
    except Exception as e:
        logger.error(f"Error creando connection pool: {e}")
        raise

def get_conn():
    """
    Obtiene una conexión del pool. Siempre usa este helper en lugar de 'conn' global.
    La conexión se devuelve al pool automáticamente cuando ya no es necesaria.
    Si el pool falla, intenta reconectar.
    """
    try:
        connection_pool = _get_pool()
        db_conn = connection_pool.getconn()
        db_conn.autocommit = True
        # Verificar que la conexión esté viva
        try:
            with db_conn.cursor() as cur:
                cur.execute("SELECT 1")
        except Exception:
            # Conexión muerta — reponer con una nueva
            try:
                connection_pool.putconn(db_conn, close=True)
            except Exception:
                pass
            db_conn = connection_pool.getconn()
            db_conn.autocommit = True
        return db_conn
    except Exception as e:
        logger.error(f"Error obteniendo conexión del pool: {e}")
        # Fallback: conexión directa de emergencia
        fallback = psycopg2.connect(
            host=conn_params["host"],
            database=conn_params["database"],
            user=conn_params["user"],
            password=conn_params["password"],
            port=conn_params.get("port", 6543),
        )
        fallback.autocommit = True
        return fallback

def release_conn(db_conn):
    """Devuelve una conexión al pool de forma segura."""
    try:
        connection_pool = _get_pool()
        connection_pool.putconn(db_conn)
    except Exception as e:
        logger.warning(f"No se pudo devolver la conexión al pool: {e}")
        try:
            db_conn.close()
        except Exception:
            pass

# Conexión de compatibilidad para pd.read_sql y operaciones directas de módulo
# (se obtiene una vez al inicio; el pool gestiona la resiliencia)
conn = get_conn()
genai.configure(api_key=GEMINI_API_KEY)

# ==========================================
# Mecanismo de Fallback para Llamadas a Gemini
# ==========================================
def generate_content_with_fallback(prompt, contents=None, primary_model="gemini-3.1-pro-preview", fallback_models=["gemini-flash-latest", "gemini-pro-latest"]):
    """
    Intenta generar contenido con el modelo primario.
    Si se encuentra un error de cuota/rate limit (429), reintenta secuencialmente con los modelos de fallback.
    """
    models_to_try = [primary_model] + fallback_models
    last_exception = None
    
    for i, model_name in enumerate(models_to_try):
        try:
            model = genai.GenerativeModel(model_name)
            if contents:
                response = model.generate_content(contents)
            else:
                response = model.generate_content(prompt)
            
            # Si no se usó el primario, avisar al usuario de forma informativa en Streamlit
            if i > 0:
                try:
                    st.info(f"ℹ️ El modelo primario está saturado (Límite 429 superado). Se ha generado la respuesta con el modelo alternativo '{model_name}'.")
                except Exception:
                    pass
            return response
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "Resource exhausted" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                last_exception = e
                print(f"[Gemini Fallback] El modelo '{model_name}' reportó 429. Reintentando...")
                continue
            else:
                raise e
    raise last_exception

# ==========================================
# Funciones Matemáticas Auxiliares
# ==========================================
def bass_classic(t, m, p, q):
    p = max(p, 1e-8)
    exp_term = np.exp(-(p + q) * t)
    numerator = m * (1 - exp_term)
    denominator = 1 + (q / p) * exp_term
    return numerator / denominator

def dual_market_bass(t, m1, p1, q1, m2, p2, q2):
    return bass_classic(t, m1, p1, q1) + bass_classic(t, m2, p2, q2)

def logistic_diffusion_convergence(t, b1, b0, k2, t0):
    b0 = max(b0, 1e-8)
    b1 = max(b1, b0 + 1e-8)
    k2 = max(k2, 1e-8)
    exponent = -k2 * (t - t0)
    exponent = np.clip(exponent, -700, 700)
    denom = 1 + ((b1 - b0) / b0) * np.exp(exponent)
    return b1 / denom

def calculate_mape(y_true, y_pred):
    mask = y_true != 0
    if not np.any(mask):
        return 0.0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0

# ==========================================
# Resolvedor Numérico RK4 y Modelos de Difusión Científicos
# ==========================================
def integrate_rk4(f, y0, t_grid, steps_per_unit=10):
    y = np.zeros(len(t_grid))
    y[0] = y0
    
    for idx in range(len(t_grid) - 1):
        t_start = t_grid[idx]
        t_end = t_grid[idx+1]
        dt = (t_end - t_start) / steps_per_unit
        
        current_y = y[idx]
        for _ in range(steps_per_unit):
            t = t_start + _ * dt
            k1 = f(t, current_y)
            k2 = f(t + dt/2, current_y + dt*k1/2)
            k3 = f(t + dt/2, current_y + dt*k2/2)
            k4 = f(t + dt, current_y + dt*k3)
            current_y += dt * (k1 + 2*k2 + 2*k3 + k4) / 6
            
        y[idx+1] = current_y
    return y

def tanny_derzko_model(t, n1, p1, n2, p2, q2):
    n = max(n1 + n2, 1e-8)
    p1 = max(p1, 1e-8)
    p2 = max(p2, 1e-8)
    q2 = max(q2, 0.0)
    
    t_grid = np.arange(int(max(t)) + 1)
    x1_grid = n1 * (1.0 - np.exp(-p1 * t_grid))
    
    def f(time, x2):
        x1_val = n1 * (1.0 - np.exp(-p1 * time))
        val = (p2 + q2 * (x1_val + x2) / n) * (n2 - x2)
        return max(val, 0.0)
        
    x2_grid = integrate_rk4(f, 0.0, t_grid)
    total_grid = x1_grid + x2_grid
    return total_grid[np.round(t).astype(int)]

def steffens_murthy_model(t, K1, alpha, beta, K2, gamma):
    alpha = max(alpha, 1e-8)
    beta = max(beta, 0.0)
    gamma = max(gamma, 0.0)
    
    t_grid = np.arange(int(max(t)) + 1)
    N1_grid = bass_classic(t_grid, K1, alpha, beta)
    
    def f(time, N2):
        N1_val = bass_classic(time, K1, alpha, beta)
        val = (K2 - N2) * gamma * (N1_val + N2)
        return max(val, 0.0)
        
    N2_grid = integrate_rk4(f, 0.0, t_grid)
    total_grid = N1_grid + N2_grid
    return total_grid[np.round(t).astype(int)]

def muller_yogev_model(t, Ni, pi, qi, Nm, pm, qm, qim):
    pi = max(pi, 1e-8)
    qi = max(qi, 0.0)
    pm = max(pm, 1e-8)
    qm = max(qm, 0.0)
    qim = max(qim, 0.0)
    
    t_grid = np.arange(int(max(t)) + 1)
    I_grid = bass_classic(t_grid, Ni, pi, qi)
    denom = max(Ni + Nm, 1e-8)
    
    def f(time, M):
        I_val = bass_classic(time, Ni, pi, qi)
        val = (pm + qm * M / denom + qim * I_val / denom) * (Nm - M)
        return max(val, 0.0)
        
    M_grid = integrate_rk4(f, 0.0, t_grid)
    total_grid = I_grid + M_grid
    return total_grid[np.round(t).astype(int)]

def vdb_joshi_model(t, M1, p1, q1, M2, q2, w):
    p1 = max(p1, 1e-8)
    q1 = max(q1, 0.0)
    q2 = max(q2, 0.0)
    w = np.clip(w, 0.0, 1.0)
    
    t_grid = np.arange(int(max(t)) + 1)
    F1_grid = bass_classic(t_grid, 1.0, p1, q1)
    
    def f(time, F2):
        F1_val = bass_classic(time, 1.0, p1, q1)
        val = q2 * (w * F1_val + (1.0 - w) * F2) * (1.0 - F2)
        return max(val, 0.0)
        
    F2_grid = integrate_rk4(f, 0.0, t_grid)
    total_grid = M1 * F1_grid + M2 * F2_grid
    return total_grid[np.round(t).astype(int)]

# ==========================================
# Descubrimiento Científico e Ingesta RAG
# ==========================================
import re
import requests
import tempfile
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

def buscar_arxiv(query, max_results=10):
    print(f"[ArXiv Search] Starting search for query: '{query}' with max results: {max_results}")
    try:
        query_encoded = urllib.parse.quote(query)
        url = f"http://export.arxiv.org/api/query?search_query=all:{query_encoded}&max_results={max_results}"
        print(f"[ArXiv Search] Fetching from URL: {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        xml_data = response.content
        print(f"[ArXiv Search] Successfully retrieved XML data, length: {len(xml_data)} bytes")
            
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        papers = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns)
            title_text = title.text.strip().replace('\n', ' ') if title is not None else "Sin título"
            
            summary = entry.find('atom:summary', ns)
            summary_text = summary.text.strip().replace('\n', ' ') if summary is not None else "Sin resumen"
            
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns)
                if name is not None:
                    authors.append(name.text.strip())
            
            published = entry.find('atom:published', ns)
            published_text = published.text.strip()[:10] if published is not None else "Desconocida"
            
            pdf_url = ""
            for link in entry.findall('atom:link', ns):
                if link.attrib.get('title') == 'pdf' or link.attrib.get('type') == 'application/pdf':
                    pdf_url = link.attrib.get('href', '')
                elif 'pdf' in link.attrib.get('href', ''):
                    pdf_url = link.attrib.get('href', '')
                    
            if not pdf_url:
                id_elem = entry.find('atom:id', ns)
                if id_elem is not None:
                    arxiv_id = id_elem.text.strip().split('/abs/')[-1]
                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                    
            papers.append({
                "titulo": title_text,
                "autores": authors,
                "abstract": summary_text,
                "url_pdf": pdf_url,
                "fecha_publicacion": published_text
            })
        print(f"[ArXiv Search] Parsed {len(papers)} papers successfully")
        return papers
    except Exception as e:
        print(f"[ArXiv Search] Exception encountered: {e}")
        st.error(f"Error en búsqueda de arXiv: {e}")
        return []

def buscar_openalex(query, max_results=10):
    print(f"[OpenAlex Search] Starting search for query: '{query}' with max results: {max_results}")
    try:
        url = f"https://api.openalex.org/works?search={urllib.parse.quote(query)}&per_page={max_results}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mailto': 'technology adoption'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        
        papers = []
        for paper in results:
            title = paper.get("title", "Sin título")
            
            # Extract authors
            authorships = paper.get("authorships", [])
            authors = [a.get("author", {}).get("display_name", "Desconocido") for a in authorships]
            
            # Reconstruct abstract
            abstract_inverted = paper.get("abstract_inverted_index")
            abstract_text = "Sin resumen disponible."
            if abstract_inverted:
                try:
                    word_positions = {}
                    for word, positions in abstract_inverted.items():
                        for pos in positions:
                            word_positions[pos] = word
                    sorted_positions = sorted(word_positions.keys())
                    abstract_text = " ".join([word_positions[pos] for pos in sorted_positions])
                except Exception:
                    pass
            
            # Find PDF URL or alternate URL
            pdf_url = paper.get("open_access", {}).get("oa_url")
            if not pdf_url:
                pdf_url = paper.get("doi") or paper.get("id") or ""
                
            published_text = paper.get("publication_date", "Desconocida")
            
            papers.append({
                "titulo": title,
                "autores": authors,
                "abstract": abstract_text,
                "url_pdf": pdf_url,
                "fecha_publicacion": published_text
            })
        print(f"[OpenAlex Search] Parsed {len(papers)} papers successfully")
        return papers
    except Exception as e:
        print(f"[OpenAlex Search] Exception encountered: {e}")
        st.error(f"Error en búsqueda de OpenAlex: {e}")
        return []

def download_pdf(url):
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()
    
    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    with os.fdopen(fd, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return temp_path

def smart_chunking(text, chunk_size=1200, overlap=200):
    math_pattern = re.compile(r'(\$\$[\s\S]*?\$\$|\$[\s\S]*?\$)', re.MULTILINE)
    placeholders = {}
    
    def replacer(match):
        uid = f"__MATH_BLOCK_{len(placeholders)}__"
        placeholders[uid] = match.group(0)
        return uid
        
    text_masked = math_pattern.sub(replacer, text)
    paragraphs = text_masked.split('\n')
    
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        if len(current_chunk) + len(p) < chunk_size:
            current_chunk += p + "\n"
        else:
            for uid, math_text in placeholders.items():
                current_chunk = current_chunk.replace(uid, math_text)
            chunks.append(current_chunk.strip())
            current_chunk = current_chunk[-overlap:] + p + "\n"
            
    if current_chunk.strip():
        for uid, math_text in placeholders.items():
            current_chunk = current_chunk.replace(uid, math_text)
        chunks.append(current_chunk.strip())
        
    return chunks

def ingestar_paper_db(paper, tecnologia, status_placeholder):
    temp_pdf = None
    cursor = None
    try:
        if 'local_pdf_path' in paper:
            temp_pdf = paper['local_pdf_path']
        else:
            pdf_url = paper.get('url_pdf', '')
            # Check if we have a PDF URL and try downloading it
            if pdf_url and ('pdf' in pdf_url.lower() or pdf_url.endswith('.pdf')):
                try:
                    status_placeholder.update(label="📥 Descargando archivo PDF desde el repositorio...", state="running")
                    temp_pdf = download_pdf(pdf_url)
                except Exception as e:
                    print(f"[Ingesta RAG] PDF download failed from {pdf_url}: {e}")
                    temp_pdf = None
        
        cursor = conn.cursor()
        
        # Insert metadatos
        cursor.execute("""
            INSERT INTO papers_metadata (titulo, autores, abstract, url_pdf, tecnologia, fecha_publicacion, procesado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            paper['titulo'], 
            paper['autores'], 
            paper['abstract'], 
            paper['url_pdf'] if paper['url_pdf'] else None, 
            tecnologia, 
            pd.to_datetime(paper['fecha_publicacion']).date() if paper.get('fecha_publicacion') and paper['fecha_publicacion'] != "Desconocida" else None, 
            False
        ))
        paper_id = cursor.fetchone()[0]
        
        if temp_pdf:
            status_placeholder.update(label="🧠 Analizando contenido científico y ecuaciones con Gemini 3.1 Pro...", state="running")
            uploaded_file = genai.upload_file(path=temp_pdf, display_name="Paper_PDF")
            
            prompt = (
                "Extract all the text from this scientific paper. "
                "Format the output in clean Markdown. "
                "CRITICAL: Keep all mathematical equations intact using LaTeX syntax, wrapped in $ for inline math or $$ for block math."
            )
            response = generate_content_with_fallback(
                prompt=prompt,
                contents=[uploaded_file, prompt],
                primary_model="gemini-3.1-pro-preview",
                fallback_models=["gemini-pro-latest", "gemini-flash-latest"]
            )
            full_text = response.text
            
            try:
                genai.delete_file(uploaded_file.name)
            except Exception:
                pass
                
            status_placeholder.update(label="✂️ Segmentando el contenido en fragmentos lógicos (Smart Chunking)...", state="running")
            chunks = smart_chunking(full_text)
        else:
            # Fallback to abstract indexing
            status_placeholder.update(label="📝 PDF no disponible o no accesible. Indexando resumen (Abstract)...", state="running")
            chunks = [f"Resumen del artículo: {paper['titulo']}\nAutores: {', '.join(paper['autores'])}\nAbstract: {paper['abstract']}"]
        
        status_placeholder.update(label="🔢 Generando embeddings vectoriales con gemini-embedding-001 y guardando en pgvector...", state="running")
        
        # Insertar chunks vectorizados
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
        status_placeholder.update(label=f"❌ Error durante la ingesta: {str(e)}", state="error")
        st.error(f"Detalle del error: {e}")
        return False
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if temp_pdf and os.path.exists(temp_pdf):
            try:
                os.remove(temp_pdf)
            except Exception:
                pass

# ==========================================
# Motor Lógico: Inferencia de Gartner y Solver
# ==========================================
def inferir_datos_gartner(tech_name):
    prompt = f"""
    Eres un experto analista en el Gartner Hype Cycle y previsión tecnológica. 
    Tu tarea es estimar el volumen histórico de adopción acumulada (usuarios totales en millones a nivel global) para cada año desde 2015 hasta 2024 para la tecnología: "{tech_name}".
    
    Analiza mentalmente en qué fase del Gartner Hype Cycle se encuentra (Innovation Trigger, Peak, Trough of Disillusionment, Slope of Enlightenment o Plateau of Productivity) y plasma esos baches o aceleraciones (ej. el abismo de Moore) en el volumen anual.

    IMPORTANTE: La adopción acumulada NUNCA puede decrecer. Cada año debe ser igual o mayor al anterior.
    
    Genera EXCLUSIVAMENTE una respuesta en JSON válido con el siguiente esquema exacto, sin explicaciones ni formato markdown:
    {{
        "datos": [
            {{"anio": 2015, "usuarios_millones": 1.2}},
            {{"anio": 2016, "usuarios_millones": 3.4}},
            {{"anio": 2017, "usuarios_millones": 5.1}},
            {{"anio": 2018, "usuarios_millones": 5.5}},
            {{"anio": 2019, "usuarios_millones": 8.0}},
            {{"anio": 2020, "usuarios_millones": 12.5}},
            {{"anio": 2021, "usuarios_millones": 20.1}},
            {{"anio": 2022, "usuarios_millones": 45.0}},
            {{"anio": 2023, "usuarios_millones": 95.0}},
            {{"anio": 2024, "usuarios_millones": 180.0}}
        ]
    }}
    """
    try:
        respuesta = generate_content_with_fallback(
            prompt=prompt,
            primary_model="gemini-3.1-pro-preview",
            fallback_models=["gemini-flash-latest", "gemini-pro-latest"]
        )
        texto = respuesta.text.strip()
        if texto.startswith("```json"):
            texto = texto[7:]
        if texto.endswith("```"):
            texto = texto[:-3]
        data = json.loads(texto)
        return data.get("datos")
    except Exception as e:
        st.error(f"Error infiriendo datos de Gartner: {e}")
        return None

def obtener_datos_statista_web(tech_name):
    print(f"[Statista Search] Querying DuckDuckGo for tech: '{tech_name}'")
    query = f"site:statista.com {tech_name} adoption users numbers millions"
    query_encoded = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={query_encoded}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    context = ""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
        print(f"[Statista Search] Retrieved HTML length: {len(html)} bytes")
            
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        clean_snippets = []
        for s in snippets[:6]:
            s_clean = re.sub(r'<[^>]+>', '', s).strip()
            clean_snippets.append(s_clean)
        context = "\n\n".join(clean_snippets)
        print(f"[Statista Search] Extracted {len(clean_snippets)} search snippets")
    except Exception as e:
        print(f"[Statista Search] DDG request failed: {e}")
        pass
        
    if not context:
        context = f"Adoptantes históricos y actuales de la tecnología {tech_name} en millones de usuarios según Statista."

    prompt = f"""
    Basándote en este contexto recuperado de búsquedas de informes de Statista:
    {context}
    
    Tu tarea es extraer o estimar de forma realista y coherente con las cifras públicas de Statista la serie histórica de adopción acumulada de usuarios globales en millones de 2015 a 2024 para la tecnología: "{tech_name}".
    
    CRITICAL: Los datos deben alinearse lo más posible con las cifras reales del contexto. Si faltan años, interpola de forma continua y lógica (los usuarios acumulados deben crecer o mantenerse estables, nunca decrecer).
    
    Genera EXCLUSIVAMENTE una respuesta en JSON válido con el siguiente esquema exacto, sin explicaciones ni formato markdown:
    {{
        "datos": [
            {{"anio": 2015, "usuarios_millones": 5.0}},
            {{"anio": 2016, "usuarios_millones": 12.0}},
            {{"anio": 2017, "usuarios_millones": 20.0}},
            {{"anio": 2018, "usuarios_millones": 35.0}},
            {{"anio": 2019, "usuarios_millones": 50.0}},
            {{"anio": 2020, "usuarios_millones": 75.0}},
            {{"anio": 2021, "usuarios_millones": 105.0}},
            {{"anio": 2022, "usuarios_millones": 130.0}},
            {{"anio": 2023, "usuarios_millones": 155.0}},
            {{"anio": 2024, "usuarios_millones": 170.0}}
        ]
    }}
    """
    try:
        respuesta = generate_content_with_fallback(
            prompt=prompt,
            primary_model="gemini-3.1-pro-preview",
            fallback_models=["gemini-flash-latest", "gemini-pro-latest"]
        )
        texto = respuesta.text.strip()
        
        # Extractor JSON robusto con soporte para preámbulos y formatos múltiples
        match = re.search(r'\{[\s\S]*\}', texto)
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)
            return data.get("datos")
        else:
            st.error(f"Error: No se encontró un bloque JSON válido en la respuesta de la IA. Respuesta recibida: {texto[:150]}")
            return None
    except Exception as e:
        st.error(f"Error procesando búsqueda web de Statista: {e}")
        return None

def insertar_historico_db(tech_name, datos_json):
    try:
        cursor = conn.cursor()
        prev_acumulada = 0
        records = []
        for d in datos_json:
            anio = d["anio"]
            acumulada = float(d["usuarios_millones"])
            anual = acumulada - prev_acumulada if prev_acumulada > 0 else acumulada
            prev_acumulada = acumulada
            records.append((tech_name, anio, anual, acumulada))
            
        cursor.executemany("""
            INSERT INTO historical_adoption (tecnologia, anio, adopcion_anual, adopcion_acumulada)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, records)
        cursor.close()
    except Exception as e:
        st.error(f"Error insertando datos en BD: {e}")

def guardar_analisis_cualitativo(tech, analisis_text):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO qualitative_analysis (tecnologia, analisis)
            VALUES (%s, %s)
            ON CONFLICT (tecnologia) 
            DO UPDATE SET analisis = EXCLUDED.analisis
        """, (tech, analisis_text))
        cursor.close()
    except Exception as e:
        print(f"Error saving qualitative analysis: {e}")

def load_qualitative_analysis(tech):
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("SELECT analisis FROM qualitative_analysis WHERE tecnologia = %s", (tech,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return row["analisis"]
    except Exception as e:
        print(f"Error loading qualitative analysis: {e}")
    return None

def buscar_web_ddg(query):
    print(f"[DDG Search] Querying: '{query}'")
    query_encoded = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={query_encoded}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        clean_snippets = []
        for s in snippets[:6]:
            s_clean = re.sub(r'<[^>]+>', '', s).strip()
            clean_snippets.append(s_clean)
        return "\n\n".join(clean_snippets)
    except Exception as e:
        print(f"[DDG Search] Failed: {e}")
        return ""

def obtener_datos_y_analisis_ia(tech_name):
    context1 = buscar_web_ddg(f"site:statista.com {tech_name} adoption users numbers millions")
    context2 = buscar_web_ddg(f"{tech_name} global market size volume units millions adoption reports")
    context = context1 + "\n\n" + context2
    
    if not context.strip():
        context = f"Adoptantes históricos y actuales de la tecnología {tech_name} en millones de usuarios/unidades."

    prompt = f"""
    Basándote en este contexto recuperado de búsquedas de informes de mercado sobre la tecnología: "{tech_name}":
    {context}
    
    Tu tarea es:
    1. Extraer o estimar de forma realista la serie histórica de adopción acumulada de usuarios globales (o unidades acumuladas vendidas) en millones desde 2015 hasta 2025/2026.
       CRITICAL: Los datos deben ser coherentes con las cifras reales del contexto. Si faltan años, interpola de forma continua y lógica (los usuarios acumulados deben crecer o mantenerse estables, nunca decrecer).
    2. Redactar un reporte de análisis cualitativo del mercado sumamente detallado, estructurado y extenso en español que explique:
       - **Introducción y Contexto del Mercado**: Definición y madurez de la tecnología.
       - **Análisis Detallado de la Serie Temporal (Causas de Variación)**: Explicación de los hitos año a año (2015-2025). Justifica detalladamente cualquier salto, meseta o aceleración en la adopción basándote en lanzamientos de productos, cambios de estrategia, fusiones o discontinuaciones.
       - **Fuentes y Metodologías de Analistas**: Estimaciones de IDC, Gartner, Statista, Counterpoint, etc.
       - **Modelos de Negocio y Segmentos Clave**: Comparación de precios (ASP), sector industrial/militar vs consumo masivo.
       - **Hitos y Eventos Tecnológicos Críticos**: Línea de tiempo de lanzamientos o discontinuaciones clave.
       
    Genera EXCLUSIVAMENTE una respuesta en JSON válido con el siguiente esquema exacto, sin explicaciones ni formato markdown fuera del JSON:
    {{
        "datos": [
            {{"anio": 2015, "usuarios_millones": 1.2}},
            {{"anio": 2016, "usuarios_millones": 3.4}},
            {{"anio": 2017, "usuarios_millones": 5.1}},
            {{"anio": 2018, "usuarios_millones": 5.5}},
            {{"anio": 2019, "usuarios_millones": 8.0}},
            {{"anio": 2020, "usuarios_millones": 12.5}},
            {{"anio": 2021, "usuarios_millones": 20.1}},
            {{"anio": 2022, "usuarios_millones": 45.0}},
            {{"anio": 2023, "usuarios_millones": 95.0}},
            {{"anio": 2024, "usuarios_millones": 180.0}},
            {{"anio": 2025, "usuarios_millones": 220.0}}
        ],
        "analisis_cualitativo": "Markdown detallado y extenso en español..."
    }}
    """
    try:
        respuesta = generate_content_with_fallback(
            prompt=prompt,
            primary_model="gemini-3.1-pro-preview",
            fallback_models=["gemini-flash-latest", "gemini-pro-latest"]
        )
        texto = respuesta.text.strip()
        
        match = re.search(r'\{[\s\S]*\}', texto)
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)
            return data.get("datos"), data.get("analisis_cualitativo")
        else:
            return None, None
    except Exception as e:
        print(f"[IA Search] Error: {e}")
        return None, None

def generar_analisis_cualitativo_solo(tech_name):
    context1 = buscar_web_ddg(f"site:statista.com {tech_name} adoption users numbers millions")
    context2 = buscar_web_ddg(f"{tech_name} global market size volume units millions adoption reports")
    context = context1 + "\n\n" + context2
    
    if not context.strip():
        context = f"Adoptantes históricos y actuales de la tecnología {tech_name} en millones de usuarios/unidades."

    prompt = f"""
    Basándote en este contexto recuperado de búsquedas de informes de mercado sobre la tecnología: "{tech_name}":
    {context}
    
    Tu tarea es redactar un reporte de análisis cualitativo del mercado sumamente detallado, estructurado y extenso en español sobre la tecnología: "{tech_name}". 
    El reporte debe explicar obligatoriamente:
    - **Introducción y Contexto del Mercado**: Definición y madurez de la tecnología.
    - **Análisis Detallado de la Serie Temporal (Causas de Variación)**: Explicación de los hitos año a año (2015-2025). Justifica detalladamente cualquier salto, meseta o aceleración en la adopción basándote en lanzamientos de productos, cambios de estrategia, fusiones o discontinuaciones.
    - **Fuentes y Metodologías de Analistas**: Estimaciones de IDC, Gartner, Statista, Counterpoint, etc.
    - **Modelos de Negocio y Segmentos Clave**: Comparación de precios (ASP), sector industrial/militar vs consumo masivo.
    - **Hitos y Eventos Tecnológicos Críticos**: Línea de tiempo de lanzamientos o discontinuaciones clave.
    
    Redacta en formato Markdown profesional en español. No respondas nada más que el reporte Markdown.
    """
    try:
        respuesta = generate_content_with_fallback(
            prompt=prompt,
            primary_model="gemini-3.1-pro-preview",
            fallback_models=["gemini-flash-latest", "gemini-pro-latest"]
        )
        return respuesta.text.strip()
    except Exception as e:
        print(f"[IA Analisis] Error: {e}")
        return None

def guardar_consenso_forecast(tech, consenso_text):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO consensus_forecast (tecnologia, consenso)
            VALUES (%s, %s)
            ON CONFLICT (tecnologia) 
            DO UPDATE SET consenso = EXCLUDED.consenso
        """, (tech, consenso_text))
        cursor.close()
    except Exception as e:
        print(f"Error saving consensus forecast: {e}")

def load_consenso_forecast(tech):
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("SELECT consenso FROM consensus_forecast WHERE tecnologia = %s", (tech,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return row["consenso"]
    except Exception as e:
        print(f"Error loading consensus forecast: {e}")
    return None

def generar_consenso_pronostico_ia(tech, df_hist, params, analisis_cualitativo):
    t_hist = np.arange(len(df_hist))
    anios_reales = df_hist["anio"].values
    ultimo_anio = anios_reales[-1] if len(anios_reales) > 0 else 2024
    
    t_5 = len(df_hist) + 4
    t_10 = len(df_hist) + 9
    anio_5 = ultimo_anio + 5
    anio_10 = ultimo_anio + 10
    
    model_projections_text = ""
    for m_key, p in params.items():
        try:
            if m_key == "Bass_Clasico":
                y_5 = bass_classic(t_5, p["param_m1"], p["param_p1"], p["param_q1"])
                y_10 = bass_classic(t_10, p["param_m1"], p["param_p1"], p["param_q1"])
                model_projections_text += f"- **Bass Clásico**: Proyecta {y_5:.2f} millones en {anio_5} y {y_10:.2f} millones en {anio_10} (R²={p.get('r_cuadrado', 0):.4f}).\n"
            elif m_key == "Dual_Market":
                y_5 = dual_market_bass(t_5, p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"], p["param_q2"])
                y_10 = dual_market_bass(t_10, p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"], p["param_q2"])
                model_projections_text += f"- **Dual Market (Roset & Canals)**: Proyecta {y_5:.2f} millones en {anio_5} y {y_10:.2f} millones en {anio_10} (R²={p.get('r_cuadrado', 0):.4f}).\n"
            elif m_key == "Tanny_Derzko":
                y_5 = tanny_derzko_model(np.array([t_5]), p["param_m1"], p["param_p1"], p["param_m2"], p["param_p2"], p["param_q2"])[0]
                y_10 = tanny_derzko_model(np.array([t_10]), p["param_m1"], p["param_p1"], p["param_m2"], p["param_p2"], p["param_q2"])[0]
                model_projections_text += f"- **Tanny & Derzko**: Proyecta {y_5:.2f} millones en {anio_5} y {y_10:.2f} millones en {anio_10} (R²={p.get('r_cuadrado', 0):.4f}).\n"
            elif m_key == "Steffens_Murthy":
                y_5 = steffens_murthy_model(np.array([t_5]), p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_q2"])[0]
                y_10 = steffens_murthy_model(np.array([t_10]), p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_q2"])[0]
                model_projections_text += f"- **Steffens & Murthy**: Proyecta {y_5:.2f} millones en {anio_5} y {y_10:.2f} millones en {anio_10} (R²={p.get('r_cuadrado', 0):.4f}).\n"
            elif m_key == "Muller_Yogev":
                y_5 = muller_yogev_model(np.array([t_5]), p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"], p["param_q2"], p["param_q12"])[0]
                y_10 = muller_yogev_model(np.array([t_10]), p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"], p["param_q2"], p["param_q12"])[0]
                model_projections_text += f"- **Muller & Yogev**: Proyecta {y_5:.2f} millones en {anio_5} y {y_10:.2f} millones en {anio_10} (R²={p.get('r_cuadrado', 0):.4f}).\n"
            elif m_key == "VdB_Joshi":
                y_5 = vdb_joshi_model(np.array([t_5]), p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_q2"], p["param_p2"])[0]
                y_10 = vdb_joshi_model(np.array([t_10]), p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_q2"], p["param_p2"])[0]
                model_projections_text += f"- **Van den Bulte & Joshi**: Proyecta {y_5:.2f} millones en {anio_5} y {y_10:.2f} millones en {anio_10} (R²={p.get('r_cuadrado', 0):.4f}).\n"
            elif m_key == "Logistic_Diffusion_Convergence":
                y_5 = logistic_diffusion_convergence(t_5, p["param_m1"], p["param_p1"], p["param_q1"], p["param_p2"])
                y_10 = logistic_diffusion_convergence(t_10, p["param_m1"], p["param_p1"], p["param_q1"], p["param_p2"])
                model_projections_text += f"- **Difusión-Convergencia Logística**: Proyecta {y_5:.2f} millones en {anio_5} y {y_10:.2f} millones en {anio_10} (R²={p.get('r_cuadrado', 0):.4f}).\n"
        except Exception as ex:
            print(f"Error projecting in consensus for {m_key}: {ex}")
            
    prompt = f"""
    Actúa como un Director de Inteligencia de Mercado y Planificación Estratégica de Gartner. 
    Tu tarea es redactar un **Pronóstico de Consenso y Perspectiva Futura Integrada** para la tecnología: "{tech}".
    
    Tienes dos conjuntos de insumos clave:
    1. **Proyecciones Matemáticas de los Modelos de Difusión** (año {ultimo_anio} al {anio_10}):
    {model_projections_text}
    
    2. **Análisis Cualitativo del Mercado**:
    {analisis_cualitativo}
    
    Genera un reporte estratégico sumamente completo y detallado en español estructurado con los siguientes apartados:
    
    ### 🔮 Pronóstico de Consenso RAG & IA
    
    #### 1. Evaluación de Modelos y Ajuste Real
    Analiza cuál de los modelos matemáticos se alinea mejor con los hechos del mercado. Por ejemplo:
    - ¿La tecnología muestra dinámicas de mercado dual (como un segmento industrial caro y uno de consumo masivo posterior)? En ese caso, explica por qué el modelo *Dual Market* o *Tanny & Derzko* es el más coherente físicamente.
    - ¿Muestra una desaceleración prematura o convergencia rápida hacia un límite? Relaciónalo con el modelo de *Difusión-Convergencia Logística* o *Muller-Yogev*.
    - Compara R² y MAPE frente a la coherencia teórica.
    
    #### 2. Proyección de Consenso Razonada (Escenario Base)
    Establece un pronóstico definitivo de consenso para los próximos 5 y 10 años. Combina las proyecciones cuantitativas de los modelos más adecuados con el análisis cualitativo. Explica el volumen de usuarios/unidades esperado y el porqué de esa cifra.
    
    #### 3. Drivers de Mercado y Disparadores Tecnológicos
    Identifica qué factores específicos acelerarán la difusión (ej. bajadas de precio, nuevos estándares, subsidios) o la frenarán (ej. obsolescencia, competidores sustitutos).
    
    #### 4. Conclusiones y Recomendaciones Estratégicas
    Recomendación formal para tomadores de decisiones sobre qué modelo matemático y qué cifras adoptar en sus planes de negocio.
    
    Escribe el reporte en formato Markdown profesional en español. Sé sumamente específico, proporciona cifras concretas e hilvana los datos matemáticos con la narrativa cualitativa. No respondas nada más que el reporte Markdown.
    """
    try:
        respuesta = generate_content_with_fallback(
            prompt=prompt,
            primary_model="gemini-3.1-pro-preview",
            fallback_models=["gemini-flash-latest", "gemini-pro-latest"]
        )
        return respuesta.text.strip()
    except Exception as e:
        print(f"[IA Consenso] Error: {e}")
        return None

def resolver_y_guardar_modelos(tech_name, df_hist):
    # CRÍTICO #3 — Fallos silenciosos: cada except ahora loguea el error
    # con su nombre de modelo para diagnóstico. Los modelos que no convergen
    # simplemente se omiten (comportamiento esperado con datos escasos),
    # pero el motivo es visible en los logs del servidor.
    db_conn = get_conn()
    try:
        t_data = np.arange(len(df_hist))
        y_data = df_hist["adopcion_acumulada"].values
        cursor = db_conn.cursor()
        
        # Eliminar modelos anteriores si existen
        cursor.execute("DELETE FROM model_parameters WHERE tecnologia = %s", (tech_name,))
        modelos_ajustados = []
        modelos_fallidos = []
        
        # Bass Clásico
        try:
            popt_bass, _ = curve_fit(bass_classic, t_data, y_data, bounds=(0, [np.inf, 1, 1]))
            r2_bass = r2_score(y_data, bass_classic(t_data, *popt_bass))
            cursor.execute("""
                INSERT INTO model_parameters (tecnologia, modelo_tipo, param_m1, param_p1, param_q1, r_cuadrado)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (tech_name, 'Bass_Clasico', float(popt_bass[0]), float(popt_bass[1]), float(popt_bass[2]), float(r2_bass)))
            modelos_ajustados.append(f'Bass Clásico (R²={r2_bass:.4f})')
        except Exception as e:
            logger.warning(f"[{tech_name}] Bass Clásico no convergió: {e}")
            modelos_fallidos.append('Bass Clásico')
            
        # Dual Market (Roset & Canals) - Búsqueda Óptima de Parámetros mediante Multi-Start NLLS
        try:
            best_popt = None
            best_r2 = -np.inf
            m_max = max(y_data)
            
            # Rejilla multi-start para evitar convergencia en mínimos locales
            candidate_p0s = [
                [m_max * 0.1, 0.03, 0.38, m_max * 0.9, 0.01, 0.4],
                [m_max * 0.3, 0.02, 0.40, m_max * 0.7, 0.005, 0.3],
                [m_max * 0.5, 0.01, 0.30, m_max * 0.5, 0.01, 0.3],
                [m_max * 0.7, 0.05, 0.50, m_max * 0.3, 0.001, 0.4],
                [m_max * 0.2, 0.04, 0.35, m_max * 0.8, 0.015, 0.45],
                [m_max * 0.4, 0.03, 0.45, m_max * 0.6, 0.008, 0.35]
            ]
            bounds_dual = ([0, 1e-6, 0, 0, 1e-6, 0], [np.inf, 1.0, 1.0, np.inf, 1.0, 1.0])
            
            for p0_cand in candidate_p0s:
                try:
                    popt_cand, _ = curve_fit(dual_market_bass, t_data, y_data, p0=p0_cand, bounds=bounds_dual, maxfev=15000)
                    r2_cand = r2_score(y_data, dual_market_bass(t_data, *popt_cand))
                    if r2_cand > best_r2:
                        best_r2 = r2_cand
                        best_popt = popt_cand
                except Exception:
                    continue
            
            if best_popt is not None:
                cursor.execute("""
                    INSERT INTO model_parameters (tecnologia, modelo_tipo, param_m1, param_p1, param_q1, param_m2, param_p2, param_q2, r_cuadrado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (tech_name, 'Dual_Market', float(best_popt[0]), float(best_popt[1]), float(best_popt[2]), float(best_popt[3]), float(best_popt[4]), float(best_popt[5]), float(best_r2)))
                modelos_ajustados.append(f'Dual Market (R²={best_r2:.4f})')
            else:
                logger.warning(f"[{tech_name}] Dual Market: ningún punto de partida convergió.")
                modelos_fallidos.append('Dual Market')
        except Exception as e:
            logger.warning(f"[{tech_name}] Dual Market error inesperado: {e}")
            modelos_fallidos.append('Dual Market')

        # Tanny & Derzko
        try:
            bounds_tanny = ([0, 1e-5, 0, 1e-5, 0], [np.inf, 1.0, np.inf, 1.0, 1.0])
            p0_tanny = [max(y_data)*0.2, 0.01, max(y_data)*0.8, 0.005, 0.1]
            popt_tanny, _ = curve_fit(tanny_derzko_model, t_data, y_data, p0=p0_tanny, bounds=bounds_tanny, maxfev=10000)
            r2_tanny = r2_score(y_data, tanny_derzko_model(t_data, *popt_tanny))
            cursor.execute("""
                INSERT INTO model_parameters (tecnologia, modelo_tipo, param_m1, param_p1, param_m2, param_p2, param_q2, r_cuadrado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (tech_name, 'Tanny_Derzko', float(popt_tanny[0]), float(popt_tanny[1]), float(popt_tanny[2]), float(popt_tanny[3]), float(popt_tanny[4]), float(r2_tanny)))
            modelos_ajustados.append(f'Tanny & Derzko (R²={r2_tanny:.4f})')
        except Exception as e:
            logger.warning(f"[{tech_name}] Tanny & Derzko no convergió: {e}")
            modelos_fallidos.append('Tanny & Derzko')

        # Steffens & Murthy
        try:
            bounds_steffens = ([0, 1e-5, 0, 0, 0], [np.inf, 1.0, 1.0, np.inf, 1.0])
            p0_steffens = [max(y_data)*0.2, 0.01, 0.1, max(y_data)*0.8, 0.05]
            popt_steffens, _ = curve_fit(steffens_murthy_model, t_data, y_data, p0=p0_steffens, bounds=bounds_steffens, maxfev=10000)
            r2_steffens = r2_score(y_data, steffens_murthy_model(t_data, *popt_steffens))
            cursor.execute("""
                INSERT INTO model_parameters (tecnologia, modelo_tipo, param_m1, param_p1, param_q1, param_m2, param_q2, r_cuadrado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (tech_name, 'Steffens_Murthy', float(popt_steffens[0]), float(popt_steffens[1]), float(popt_steffens[2]), float(popt_steffens[3]), float(popt_steffens[4]), float(r2_steffens)))
            modelos_ajustados.append(f'Steffens & Murthy (R²={r2_steffens:.4f})')
        except Exception as e:
            logger.warning(f"[{tech_name}] Steffens & Murthy no convergió: {e}")
            modelos_fallidos.append('Steffens & Murthy')

        # Muller & Yogev
        try:
            bounds_muller = ([0, 1e-5, 0, 0, 1e-5, 0, 0], [np.inf, 1.0, 1.0, np.inf, 1.0, 1.0, 1.0])
            p0_muller = [max(y_data)*0.2, 0.01, 0.1, max(y_data)*0.8, 0.005, 0.05, 0.05]
            popt_muller, _ = curve_fit(muller_yogev_model, t_data, y_data, p0=p0_muller, bounds=bounds_muller, maxfev=10000)
            r2_muller = r2_score(y_data, muller_yogev_model(t_data, *popt_muller))
            cursor.execute("""
                INSERT INTO model_parameters (tecnologia, modelo_tipo, param_m1, param_p1, param_q1, param_m2, param_p2, param_q2, param_q12, r_cuadrado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (tech_name, 'Muller_Yogev', float(popt_muller[0]), float(popt_muller[1]), float(popt_muller[2]), float(popt_muller[3]), float(popt_muller[4]), float(popt_muller[5]), float(popt_muller[6]), float(r2_muller)))
            modelos_ajustados.append(f'Muller & Yogev (R²={r2_muller:.4f})')
        except Exception as e:
            logger.warning(f"[{tech_name}] Muller & Yogev no convergió: {e}")
            modelos_fallidos.append('Muller & Yogev')

        # Van den Bulte & Joshi
        try:
            bounds_vdb = ([0, 1e-5, 0, 0, 0, 0.0], [np.inf, 1.0, 1.0, np.inf, 1.0, 1.0])
            p0_vdb = [max(y_data)*0.2, 0.01, 0.1, max(y_data)*0.8, 0.05, 0.5]
            popt_vdb, _ = curve_fit(vdb_joshi_model, t_data, y_data, p0=p0_vdb, bounds=bounds_vdb, maxfev=10000)
            r2_vdb = r2_score(y_data, vdb_joshi_model(t_data, *popt_vdb))
            cursor.execute("""
                INSERT INTO model_parameters (tecnologia, modelo_tipo, param_m1, param_p1, param_q1, param_m2, param_q2, param_p2, r_cuadrado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (tech_name, 'VdB_Joshi', float(popt_vdb[0]), float(popt_vdb[1]), float(popt_vdb[2]), float(popt_vdb[3]), float(popt_vdb[4]), float(popt_vdb[5]), float(r2_vdb)))
            modelos_ajustados.append(f'VdB & Joshi (R²={r2_vdb:.4f})')
        except Exception as e:
            logger.warning(f"[{tech_name}] VdB & Joshi no convergió: {e}")
            modelos_fallidos.append('VdB & Joshi')
            
        # Logistic Diffusion-Convergence (Ryu & Kim, 2025)
        try:
            y_max = max(max(y_data), 1e-5)
            y_min = y_data[0] if y_data[0] > 0 else 1.0
            bounds_log = ([y_max, 1e-8, 1e-8, -100.0], [np.inf, max(y_max, 2e-8), 5.0, len(t_data) * 3])
            p0_log = [y_max * 1.5, np.clip(y_min, 2e-8, y_max * 0.99), 0.1, len(t_data) / 2]
            popt_log, _ = curve_fit(logistic_diffusion_convergence, t_data, y_data, p0=p0_log, bounds=bounds_log, maxfev=10000)
            r2_log = r2_score(y_data, logistic_diffusion_convergence(t_data, *popt_log))
            cursor.execute("""
                INSERT INTO model_parameters (tecnologia, modelo_tipo, param_m1, param_p1, param_q1, param_p2, r_cuadrado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (tech_name, 'Logistic_Diffusion_Convergence', float(popt_log[0]), float(popt_log[1]), float(popt_log[2]), float(popt_log[3]), float(r2_log)))
            modelos_ajustados.append(f'Logístico R&K (R²={r2_log:.4f})')
        except Exception as e:
            logger.warning(f"[{tech_name}] Logistic Diffusion-Convergence no convergió: {e}")
            modelos_fallidos.append('Logístico R&K')
            
        cursor.close()
        
        # Resumen informativo del ajuste
        logger.info(f"[{tech_name}] Modelos ajustados: {modelos_ajustados}")
        if modelos_fallidos:
            logger.warning(f"[{tech_name}] Modelos que no convergieron: {modelos_fallidos}")
            if not modelos_ajustados:
                st.error(f"Ningún modelo pudo ajustarse para '{tech_name}'. Verifica que los datos sean monótonamente crecientes y tengas al menos 5 puntos.")
            else:
                st.info(f"ℹ️ {len(modelos_ajustados)}/{len(modelos_ajustados)+len(modelos_fallidos)} modelos ajustados. Los siguientes no convergieron con estos datos: {', '.join(modelos_fallidos)}.")
    except Exception as e:
        logger.error(f"Error crítico ajustando modelos para '{tech_name}': {e}")
        st.error(f"Error ajustando modelos matemáticos: {e}")
    finally:
        release_conn(db_conn)

# ==========================================
# Carga de Datos y Parámetros
# ==========================================
@st.cache_data(ttl=3600)
def descargar_dataset_owid():
    print("[OWID Ingest] Downloading dataset from Our World in Data...")
    url = "https://ourworldindata.org/grapher/technology-adoption-by-households-in-the-united-states.csv"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        content = response.content
        print(f"[OWID Ingest] Download completed: {len(content)} bytes")
            
        import tempfile
        fd, temp_path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, 'wb') as f:
            f.write(content)
            
        df = pd.read_csv(temp_path)
        os.remove(temp_path)
        return df
    except Exception as e:
        st.error(f"Error descargando Our World in Data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_tecnologias_disponibles():
    query = "SELECT DISTINCT tecnologia FROM historical_adoption ORDER BY tecnologia"
    df = pd.read_sql(query, conn)
    return df['tecnologia'].tolist() if not df.empty else ["Inteligencia Artificial"]

@st.cache_data(ttl=600)
def load_historical_data(tech):
    # CRÍTICO #1 — Query parametrizada: nunca interpolar datos de usuario en SQL
    db_conn = get_conn()
    try:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM historical_adoption WHERE tecnologia = %s ORDER BY anio",
                (tech,)
            )
            rows = cur.fetchall()
        return pd.DataFrame(rows) if rows else pd.DataFrame()
    except Exception as e:
        logger.error(f"Error cargando datos históricos para '{tech}': {e}")
        return pd.DataFrame()
    finally:
        release_conn(db_conn)

@st.cache_data(ttl=600)
def load_model_parameters(tech):
    # CRÍTICO #1 — Query parametrizada
    db_conn = get_conn()
    try:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM model_parameters WHERE tecnologia = %s",
                (tech,)
            )
            rows = cur.fetchall()
        if not rows:
            return {}
        return {row["modelo_tipo"]: dict(row) for row in rows}
    except Exception as e:
        logger.error(f"Error cargando parámetros de modelos para '{tech}': {e}")
        return {}
    finally:
        release_conn(db_conn)


# ==========================================
# Interfaz Gráfica (UI)
# ==========================================
st.title("📈 TechAdoption-Forecast")
st.markdown("Sistema de Inteligencia Competitiva para Previsión de Adopción (Bass vs Dual Market)")

st.sidebar.header("Configuración de Previsión")
tecnologias_disponibles = get_tecnologias_disponibles()

if "update_count" not in st.session_state:
    st.session_state.update_count = 0
if "force_tech" not in st.session_state:
    st.session_state.force_tech = None

idx = 0
if st.session_state.force_tech in tecnologias_disponibles:
    idx = tecnologias_disponibles.index(st.session_state.force_tech)

tecnologia_seleccionada = st.sidebar.selectbox(
    "Selecciona Tecnología", 
    tecnologias_disponibles, 
    index=idx,
    key=f"tech_dropdown_{st.session_state.update_count}"
)

# Botón para eliminar tecnología seleccionada con confirmación de seguridad
if len(tecnologias_disponibles) > 1:
    st.sidebar.caption("🗑️ Zona de Peligro")
    confirmar_eliminar = st.sidebar.checkbox("Confirmar eliminación de la tecnología", help="Marca esta casilla para habilitar el botón de eliminación permanente.")
    if st.sidebar.button("🗑️ Eliminar Tecnología Seleccionada", disabled=not confirmar_eliminar, use_container_width=True):
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM historical_adoption WHERE tecnologia = %s", (tecnologia_seleccionada,))
            cursor.execute("DELETE FROM model_parameters WHERE tecnologia = %s", (tecnologia_seleccionada,))
            cursor.execute("DELETE FROM papers_metadata WHERE tecnologia = %s", (tecnologia_seleccionada,))
            cursor.close()
            st.sidebar.success(f"¡'{tecnologia_seleccionada}' eliminada con éxito!")
            st.session_state.force_tech = None
            st.session_state.update_count += 1
            st.cache_data.clear()
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error al eliminar la tecnología: {e}")

# Bloque de agregar nueva tecnología con datos reales
st.sidebar.divider()
st.sidebar.subheader("📥 Cargar Nueva Tecnología")
st.sidebar.caption("Carga series reales de adopción acumulada desde Statista, Excel o reportes externos corporativos.")

with st.sidebar.form("nueva_tech_form"):
    nueva_tech = st.text_input("Nombre de la Tecnología", placeholder="Ej. Metaverso")
    
    manual_data_str = st.text_area(
        "Pegar Datos (Año, Millones)", 
        value="2015, 1.2\n2016, 3.4\n2017, 5.1\n2018, 5.5\n2019, 8.0\n2020, 12.5\n2021, 20.1\n2022, 45.0\n2023, 95.0\n2024, 180.0",
        help="Ingresa un año y su valor en millones por línea. Puedes copiar y pegar directamente desde Excel (separado por tabulación o comas)."
    )
    
    uploaded_file = st.file_uploader(
        "O subir archivo CSV", 
        type=["csv"],
        help="El archivo CSV debe contener una columna para el año y otra para la adopción acumulada en millones."
    )
    
    submit_btn = st.form_submit_button("Cargar Manual/CSV")
    submit_statista = st.form_submit_button("🤖 Carga Inteligente con IA (Web)")
    
if nueva_tech:
    nueva_tech = nueva_tech.strip()
    
    if submit_btn:
        if nueva_tech in tecnologias_disponibles:
            st.sidebar.warning("Esta tecnología ya existe en la base de datos.")
            st.session_state.force_tech = nueva_tech
            st.session_state.update_count += 1
            st.cache_data.clear()
            st.rerun()
        else:
            parsed_data = []
            
            # 1. Intentar procesar archivo subido primero si existe
            if uploaded_file is not None:
                try:
                    df_upload = pd.read_csv(uploaded_file)
                    col_anio = None
                    col_valor = None
                    for c in df_upload.columns:
                        c_lower = c.lower()
                        if "anio" in c_lower or "año" in c_lower or "year" in c_lower:
                            col_anio = c
                        elif "acumulada" in c_lower or "usuarios" in c_lower or "users" in c_lower or "valor" in c_lower or "millones" in c_lower or "value" in c_lower:
                            col_valor = c
                    
                    if col_anio is None or col_valor is None:
                        col_anio = df_upload.columns[0]
                        col_valor = df_upload.columns[1]
                    
                    for _, row in df_upload.iterrows():
                        try:
                            anio_val = int(row[col_anio])
                            val_val = float(row[col_valor])
                            parsed_data.append({"anio": anio_val, "usuarios_millones": val_val})
                        except ValueError:
                            continue
                except Exception as e:
                    st.sidebar.error(f"Error leyendo CSV: {e}")
            
            # 2. Si no se subió archivo, usar los datos pegados manualmente
            if not parsed_data and manual_data_str.strip():
                lines = manual_data_str.strip().split("\n")
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    parts = re.split(r'[,\t;:]+', line)
                    if len(parts) >= 2:
                        try:
                            anio_val = int(parts[0].strip())
                            val_val = float(parts[1].strip())
                            parsed_data.append({"anio": anio_val, "usuarios_millones": val_val})
                        except ValueError:
                            continue
            
            parsed_data = sorted(parsed_data, key=lambda x: x["anio"])
                
            if parsed_data:
                if len(parsed_data) < 5:
                    st.sidebar.error("Se necesitan al menos 5 años de datos para realizar un ajuste de curvas estable.")
                else:
                    with st.spinner(f"Cargando serie real para '{nueva_tech}'..."):
                        insertar_historico_db(nueva_tech, parsed_data)
                        
                        st.sidebar.info("Generando análisis cualitativo con IA...")
                        analisis_text = generar_analisis_cualitativo_solo(nueva_tech)
                        if analisis_text:
                            guardar_analisis_cualitativo(nueva_tech, analisis_text)
                            
                        df_new = load_historical_data(nueva_tech)
                        
                        st.sidebar.info("Ajustando los 6 modelos matemáticos con resolvedores RK4...")
                        resolver_y_guardar_modelos(nueva_tech, df_new)
                        
                        st.sidebar.success(f"¡'{nueva_tech}' cargada y modelada con éxito!")
                        st.session_state.force_tech = nueva_tech
                        st.session_state.update_count += 1
                        st.cache_data.clear()
                        st.rerun()
            else:
                st.sidebar.error("No se pudieron extraer datos válidos. Verifica el formato de entrada.")
                
    elif submit_statista:
        if nueva_tech in tecnologias_disponibles:
            st.sidebar.warning("Esta tecnología ya existe en la base de datos.")
            st.session_state.force_tech = nueva_tech
            st.session_state.update_count += 1
            st.cache_data.clear()
            st.rerun()
        else:
            with st.spinner(f"Buscando reportes y datos con IA para '{nueva_tech}'..."):
                parsed_data, analisis_text = obtener_datos_y_analisis_ia(nueva_tech)
                if parsed_data:
                    with st.spinner(f"Cargando serie real para '{nueva_tech}'..."):
                        insertar_historico_db(nueva_tech, parsed_data)
                        if analisis_text:
                            guardar_analisis_cualitativo(nueva_tech, analisis_text)
                        
                        df_new = load_historical_data(nueva_tech)
                        
                        st.sidebar.info("Ajustando los 6 modelos matemáticos con resolvedores RK4...")
                        resolver_y_guardar_modelos(nueva_tech, df_new)
                        
                        st.sidebar.info("Generando pronóstico de consenso con IA...")
                        new_params = load_model_parameters(nueva_tech)
                        if new_params and analisis_text:
                            consenso_text = generar_consenso_pronostico_ia(nueva_tech, df_new, new_params, analisis_text)
                            if consenso_text:
                                guardar_consenso_forecast(nueva_tech, consenso_text)
                        
                        st.sidebar.success(f"¡'{nueva_tech}' cargada desde la web con IA con éxito!")
                        st.session_state.force_tech = nueva_tech
                        st.session_state.update_count += 1
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.sidebar.error("No se pudieron recuperar datos con IA para esta tecnología.")

# Bloque de agregar tecnología desde Our World in Data (OWID)
st.sidebar.divider()
st.sidebar.subheader("🌍 Cargar desde Our World in Data")
st.sidebar.caption("Carga series históricas reales de difusión doméstica en EEUU (1860-2024) directamente desde OWID.")

df_owid = descargar_dataset_owid()
if not df_owid.empty:
    owid_entities = sorted(df_owid['Entity'].unique().tolist())
    owid_seleccionada = st.sidebar.selectbox("Selecciona Tecnología OWID", ["-- Selecciona --"] + owid_entities)
    cargar_owid_btn = st.sidebar.button("🌍 Importar y Modelar OWID", use_container_width=True)
    
    if cargar_owid_btn and owid_seleccionada != "-- Selecciona --":
        if owid_seleccionada in tecnologias_disponibles:
            st.sidebar.warning(f"La tecnología '{owid_seleccionada}' ya existe en la base de datos.")
            st.session_state.force_tech = owid_seleccionada
            st.session_state.update_count += 1
            st.cache_data.clear()
            st.rerun()
        else:
            with st.spinner(f"Importando '{owid_seleccionada}' desde OWID..."):
                df_filtered = df_owid[df_owid['Entity'] == owid_seleccionada].copy()
                val_col = 'Technology Diffusion (Comin and Hobijn (2004) and others)'
                parsed_data = []
                for _, row in df_filtered.iterrows():
                    try:
                        anio_val = int(row['Year'])
                        val_val = float(row[val_col])
                        parsed_data.append({"anio": anio_val, "usuarios_millones": val_val})
                    except ValueError:
                        continue
                
                parsed_data = sorted(parsed_data, key=lambda x: x["anio"])
                
                if parsed_data:
                    insertar_historico_db(owid_seleccionada, parsed_data)
                    
                    st.sidebar.info("Generando análisis cualitativo con IA...")
                    analisis_text = generar_analisis_cualitativo_solo(owid_seleccionada)
                    if analisis_text:
                        guardar_analisis_cualitativo(owid_seleccionada, analisis_text)
                        
                    df_new = load_historical_data(owid_seleccionada)
                    
                    st.sidebar.info("Ajustando los 6 modelos matemáticos con resolvedores RK4...")
                    resolver_y_guardar_modelos(owid_seleccionada, df_new)
                    
                    st.sidebar.success(f"¡'{owid_seleccionada}' importada con éxito desde OWID!")
                    st.session_state.force_tech = owid_seleccionada
                    st.session_state.update_count += 1
                    st.cache_data.clear()
                    st.rerun()

# ----------------- UI Tabs Navigation -----------------
tab1, tab_market, tab2, tab3 = st.tabs([
    "📈 Proyecciones de Adopción", 
    "📊 Análisis de Mercado", 
    "🔬 Descubrimiento Científico", 
    "🤖 Asistente RAG"
])

# =======================================================
# TAB 1: PROYECCIONES DE ADOPCIÓN
# =======================================================
with tab1:
    df_hist = load_historical_data(tecnologia_seleccionada)
    params = load_model_parameters(tecnologia_seleccionada)
    
    st.subheader(f"Curvas de Adopción para: {tecnologia_seleccionada}")
    
    if df_hist.empty or not params:
        st.warning("No hay suficientes datos históricos o parámetros de modelos procesados.")
    else:
        model_options = {
            "Bass_Clasico": "Bass Clásico",
            "Dual_Market": "Dual Market (Roset & Canals)",
            "Tanny_Derzko": "Tanny & Derzko (1988)",
            "Steffens_Murthy": "Steffens & Murthy (1992)",
            "Muller_Yogev": "Muller & Yogev (2006)",
            "VdB_Joshi": "Van den Bulte & Joshi (2007)",
            "Logistic_Diffusion_Convergence": "Difusión Logística (Ryu & Kim, 2025)"
        }
        
        modelos_seleccionados = st.multiselect(
            "Selecciona los Modelos de Difusión a Visualizar e Interpolar",
            options=list(model_options.keys()),
            default=["Bass_Clasico", "Dual_Market"],
            format_func=lambda x: model_options[x]
        )
        
        t_hist = np.arange(len(df_hist))
        t_proj = np.arange(len(df_hist) + 10)
        anios_reales = df_hist["anio"].values
        ultimo_anio = anios_reales[-1] if len(anios_reales) > 0 else 2024
        anios_proj = [ultimo_anio - len(anios_reales) + 1 + i for i in t_proj]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=anios_reales, 
            y=df_hist["adopcion_acumulada"], 
            mode='markers+lines', 
            name='Datos Reales', 
            marker=dict(color='black', size=8),
            line=dict(color='black', width=2)
        ))

        df_comparativa = pd.DataFrame({
            "Año": anios_reales,
            "Datos Reales (Millones)": df_hist["adopcion_acumulada"].values
        })
        
        style_dict = {
            "Datos Reales (Millones)": "{:.1f}"
        }

        for m_key in modelos_seleccionados:
            if m_key not in params:
                continue
            
            p = params[m_key]
            r2_val = p.get("r_cuadrado", 0)
            
            if m_key == "Bass_Clasico":
                y_proj = bass_classic(t_proj, p["param_m1"], p["param_p1"], p["param_q1"])
                fig.add_trace(go.Scatter(
                    x=anios_proj, 
                    y=y_proj, 
                    mode='lines', 
                    name=f'Bass Clásico (R²={r2_val:.2f})', 
                    line=dict(dash='dash', color='#2563EB', width=2)
                ))
                
                y_hist = bass_classic(t_hist, p["param_m1"], p["param_p1"], p["param_q1"])
                df_comparativa["Predicción Bass"] = y_hist
                acc = np.where(df_hist["adopcion_acumulada"].values == 0, 100.0, 
                               100.0 * (1.0 - np.abs(df_hist["adopcion_acumulada"].values - y_hist) / df_hist["adopcion_acumulada"].values))
                df_comparativa["Accuracy Bass (%)"] = np.clip(acc, 0, 100)
                
                style_dict["Predicción Bass"] = "{:.1f}"
                style_dict["Accuracy Bass (%)"] = "{:.2f}%"

            elif m_key == "Dual_Market":
                y_proj = dual_market_bass(t_proj, p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"], p["param_q2"])
                y_n1 = bass_classic(t_proj, p["param_m1"], p["param_p1"], p["param_q1"])
                y_n2 = bass_classic(t_proj, p["param_m2"], p["param_p2"], p["param_q2"])
                
                fig.add_trace(go.Scatter(
                    x=anios_proj, 
                    y=y_proj, 
                    mode='lines', 
                    name=f'Dual Market (Total) (R²={r2_val:.2f})', 
                    line=dict(color='#DC2626', width=3)
                ))
                fig.add_trace(go.Scatter(
                    x=anios_proj, 
                    y=y_n1, 
                    mode='lines', 
                    name='Mercado 1 (Innovadores)', 
                    line=dict(color='#F97316', dash='dot', width=1.5)
                ))
                fig.add_trace(go.Scatter(
                    x=anios_proj, 
                    y=y_n2, 
                    mode='lines', 
                    name='Mercado 2 (Mayoría)', 
                    line=dict(color='#8B5CF6', dash='dot', width=1.5)
                ))
                
                y_hist = dual_market_bass(t_hist, p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"], p["param_q2"])
                df_comparativa["Predicción Dual"] = y_hist
                acc = np.where(df_hist["adopcion_acumulada"].values == 0, 100.0, 
                               100.0 * (1.0 - np.abs(df_hist["adopcion_acumulada"].values - y_hist) / df_hist["adopcion_acumulada"].values))
                df_comparativa["Accuracy Dual (%)"] = np.clip(acc, 0, 100)
                
                style_dict["Predicción Dual"] = "{:.1f}"
                style_dict["Accuracy Dual (%)"] = "{:.2f}%"

            elif m_key == "Tanny_Derzko":
                y_proj = tanny_derzko_model(t_proj, p["param_m1"], p["param_p1"], p["param_m2"], p["param_p2"], p["param_q2"])
                fig.add_trace(go.Scatter(
                    x=anios_proj, 
                    y=y_proj, 
                    mode='lines', 
                    name=f'Tanny & Derzko (R²={r2_val:.2f})', 
                    line=dict(color='#059669', width=2)
                ))
                
                y_hist = tanny_derzko_model(t_hist, p["param_m1"], p["param_p1"], p["param_m2"], p["param_p2"], p["param_q2"])
                df_comparativa["Predicción Tanny & Derzko"] = y_hist
                acc = np.where(df_hist["adopcion_acumulada"].values == 0, 100.0, 
                               100.0 * (1.0 - np.abs(df_hist["adopcion_acumulada"].values - y_hist) / df_hist["adopcion_acumulada"].values))
                df_comparativa["Accuracy Tanny & Derzko (%)"] = np.clip(acc, 0, 100)
                
                style_dict["Predicción Tanny & Derzko"] = "{:.1f}"
                style_dict["Accuracy Tanny & Derzko (%)"] = "{:.2f}%"

            elif m_key == "Steffens_Murthy":
                y_proj = steffens_murthy_model(t_proj, p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_q2"])
                fig.add_trace(go.Scatter(
                    x=anios_proj, 
                    y=y_proj, 
                    mode='lines', 
                    name=f'Steffens & Murthy (R²={r2_val:.2f})', 
                    line=dict(color='#06B6D4', width=2)
                ))
                
                y_hist = steffens_murthy_model(t_hist, p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_q2"])
                df_comparativa["Predicción Steffens & Murthy"] = y_hist
                acc = np.where(df_hist["adopcion_acumulada"].values == 0, 100.0, 
                               100.0 * (1.0 - np.abs(df_hist["adopcion_acumulada"].values - y_hist) / df_hist["adopcion_acumulada"].values))
                df_comparativa["Accuracy Steffens & Murthy (%)"] = np.clip(acc, 0, 100)
                
                style_dict["Predicción Steffens & Murthy"] = "{:.1f}"
                style_dict["Accuracy Steffens & Murthy (%)"] = "{:.2f}%"

            elif m_key == "Muller_Yogev":
                y_proj = muller_yogev_model(t_proj, p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"], p["param_q2"], p["param_q12"])
                fig.add_trace(go.Scatter(
                    x=anios_proj, 
                    y=y_proj, 
                    mode='lines', 
                    name=f'Muller & Yogev (R²={r2_val:.2f})', 
                    line=dict(color='#D946EF', width=2)
                ))
                
                y_hist = muller_yogev_model(t_hist, p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"], p["param_q2"], p["param_q12"])
                df_comparativa["Predicción Muller & Yogev"] = y_hist
                acc = np.where(df_hist["adopcion_acumulada"].values == 0, 100.0, 
                               100.0 * (1.0 - np.abs(df_hist["adopcion_acumulada"].values - y_hist) / df_hist["adopcion_acumulada"].values))
                df_comparativa["Accuracy Muller & Yogev (%)"] = np.clip(acc, 0, 100)
                
                style_dict["Predicción Muller & Yogev"] = "{:.1f}"
                style_dict["Accuracy Muller & Yogev (%)"] = "{:.2f}%"

            elif m_key == "VdB_Joshi":
                y_proj = vdb_joshi_model(t_proj, p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_q2"], p["param_p2"])
                fig.add_trace(go.Scatter(
                    x=anios_proj, 
                    y=y_proj, 
                    mode='lines', 
                    name=f'VdB & Joshi (R²={r2_val:.2f})', 
                    line=dict(color='#B45309', width=2)
                ))
                
                y_hist = vdb_joshi_model(t_hist, p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_q2"], p["param_p2"])
                df_comparativa["Predicción VdB & Joshi"] = y_hist
                acc = np.where(df_hist["adopcion_acumulada"].values == 0, 100.0, 
                               100.0 * (1.0 - np.abs(df_hist["adopcion_acumulada"].values - y_hist) / df_hist["adopcion_acumulada"].values))
                df_comparativa["Accuracy VdB & Joshi (%)"] = np.clip(acc, 0, 100)
                
                style_dict["Predicción VdB & Joshi"] = "{:.1f}"
                style_dict["Accuracy VdB & Joshi (%)"] = "{:.2f}%"

            elif m_key == "Logistic_Diffusion_Convergence":
                y_proj = logistic_diffusion_convergence(t_proj, p["param_m1"], p["param_p1"], p["param_q1"], p["param_p2"])
                fig.add_trace(go.Scatter(
                    x=anios_proj, 
                    y=y_proj, 
                    mode='lines', 
                    name=f'Difusión-Convergencia Logística (R²={r2_val:.2f})', 
                    line=dict(color='#84CC16', width=2)
                ))
                
                y_hist = logistic_diffusion_convergence(t_hist, p["param_m1"], p["param_p1"], p["param_q1"], p["param_p2"])
                df_comparativa["Predicción Logística R&K"] = y_hist
                acc = np.where(df_hist["adopcion_acumulada"].values == 0, 100.0, 
                               100.0 * (1.0 - np.abs(df_hist["adopcion_acumulada"].values - y_hist) / df_hist["adopcion_acumulada"].values))
                df_comparativa["Accuracy Logística (%)"] = np.clip(acc, 0, 100)
                
                style_dict["Predicción Logística R&K"] = "{:.1f}"
                style_dict["Accuracy Logística (%)"] = "{:.2f}%"

        fig.update_layout(
            title="Proyección Comparativa de Adopción Acumulada (Modelos de Difusión)", 
            xaxis_title="Año", 
            yaxis_title="Adopción Acumulada (Millones)", 
            hovermode="x unified",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabla Comparativa y Accuracy
        st.markdown("#### 📊 Tabla Comparativa de Ajuste y Desviaciones (Histórico)")
        st.dataframe(df_comparativa.style.format(style_dict), use_container_width=True, hide_index=True)

        # Parámetros Estimados de los Modelos
        st.markdown("#### 🔬 Parámetros Estimados de los Modelos")
        
        y_true = df_hist["adopcion_acumulada"].values
        param_rows = []
        for m_key in modelos_seleccionados:
            if m_key not in params:
                continue
            p = params[m_key]
            
            if m_key == "Bass_Clasico":
                y_h = bass_classic(t_hist, p["param_m1"], p["param_p1"], p["param_q1"])
                mape = calculate_mape(y_true, y_h)
                param_rows.append({
                    "Modelo": model_options[m_key],
                    "R²": f"{p.get('r_cuadrado', 0):.4f}",
                    "MAPE (%)": f"{mape:.2f}%",
                    "m₁ (Potencial M1)": f"{p['param_m1']:.1f}",
                    "p₁ (Innovación)": f"{p['param_p1']:.5f}",
                    "q₁ (Imitación)": f"{p['param_q1']:.5f}",
                    "m₂ (Potencial M2)": "-",
                    "p₂ (Innovación M2) / w": "-",
                    "q₂ (Imitación M2)": "-",
                    "q₁₂ (Imitación cruzada)": "-"
                })
            elif m_key == "Dual_Market":
                y_h = dual_market_bass(t_hist, p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"], p["param_q2"])
                mape = calculate_mape(y_true, y_h)
                param_rows.append({
                    "Modelo": model_options[m_key],
                    "R²": f"{p.get('r_cuadrado', 0):.4f}",
                    "MAPE (%)": f"{mape:.2f}%",
                    "m₁ (Potencial M1)": f"{p['param_m1']:.1f}",
                    "p₁ (Innovación)": f"{p['param_p1']:.5f}",
                    "q₁ (Imitación)": f"{p['param_q1']:.5f}",
                    "m₂ (Potencial M2)": f"{p['param_m2']:.1f}",
                    "p₂ (Innovación M2) / w": f"{p['param_p2']:.5f}",
                    "q₂ (Imitación M2)": f"{p['param_q2']:.5f}",
                    "q₁₂ (Imitación cruzada)": "-"
                })
            elif m_key == "Tanny_Derzko":
                y_h = tanny_derzko_model(t_hist, p["param_m1"], p["param_p1"], p["param_m2"], p["param_p2"], p["param_q2"])
                mape = calculate_mape(y_true, y_h)
                param_rows.append({
                    "Modelo": model_options[m_key],
                    "R²": f"{p.get('r_cuadrado', 0):.4f}",
                    "MAPE (%)": f"{mape:.2f}%",
                    "m₁ (Potencial M1)": f"{p['param_m1']:.1f}",
                    "p₁ (Innovación)": f"{p['param_p1']:.5f}",
                    "q₁ (Imitación)": "-",
                    "m₂ (Potencial M2)": f"{p['param_m2']:.1f}",
                    "p₂ (Innovación M2) / w": f"{p['param_p2']:.5f}",
                    "q₂ (Imitación M2)": f"{p['param_q2']:.5f}",
                    "q₁₂ (Imitación cruzada)": "-"
                })
            elif m_key == "Steffens_Murthy":
                y_h = steffens_murthy_model(t_hist, p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_q2"])
                mape = calculate_mape(y_true, y_h)
                param_rows.append({
                    "Modelo": model_options[m_key],
                    "R²": f"{p.get('r_cuadrado', 0):.4f}",
                    "MAPE (%)": f"{mape:.2f}%",
                    "m₁ (Potencial M1)": f"{p['param_m1']:.1f}",
                    "p₁ (Innovación)": f"{p['param_p1']:.5f}",
                    "q₁ (Imitación)": f"{p['param_q1']:.5f}",
                    "m₂ (Potencial M2)": f"{p['param_m2']:.1f}",
                    "p₂ (Innovación M2) / w": "-",
                    "q₂ (Imitación M2)": f"{p['param_q2']:.5f}",
                    "q₁₂ (Imitación cruzada)": "-"
                })
            elif m_key == "Muller_Yogev":
                y_h = muller_yogev_model(t_hist, p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_p2"], p["param_q2"], p["param_q12"])
                mape = calculate_mape(y_true, y_h)
                param_rows.append({
                    "Modelo": model_options[m_key],
                    "R²": f"{p.get('r_cuadrado', 0):.4f}",
                    "MAPE (%)": f"{mape:.2f}%",
                    "m₁ (Potencial M1)": f"{p['param_m1']:.1f}",
                    "p₁ (Innovación)": f"{p['param_p1']:.5f}",
                    "q₁ (Imitación)": f"{p['param_q1']:.5f}",
                    "m₂ (Potencial M2)": f"{p['param_m2']:.1f}",
                    "p₂ (Innovación M2) / w": f"{p['param_p2']:.5f}",
                    "q₂ (Imitación M2)": f"{p['param_q2']:.5f}",
                    "q₁₂ (Imitación cruzada)": f"{p['param_q12']:.5f}"
                })
            elif m_key == "VdB_Joshi":
                y_h = vdb_joshi_model(t_hist, p["param_m1"], p["param_p1"], p["param_q1"], p["param_m2"], p["param_q2"], p["param_p2"])
                mape = calculate_mape(y_true, y_h)
                param_rows.append({
                    "Modelo": model_options[m_key],
                    "R²": f"{p.get('r_cuadrado', 0):.4f}",
                    "MAPE (%)": f"{mape:.2f}%",
                    "m₁ (Potencial M1)": f"{p['param_m1']:.1f}",
                    "p₁ (Innovación)": f"{p['param_p1']:.5f}",
                    "q₁ (Imitación)": f"{p['param_q1']:.5f}",
                    "m₂ (Potencial M2)": f"{p['param_m2']:.1f}",
                    "p₂ (Innovación M2) / w": f"{p['param_p2']:.5f} (w)",
                    "q₂ (Imitación M2)": f"{p['param_q2']:.5f}",
                    "q₁₂ (Imitación cruzada)": "-"
                })
            elif m_key == "Logistic_Diffusion_Convergence":
                y_h = logistic_diffusion_convergence(t_hist, p["param_m1"], p["param_p1"], p["param_q1"], p["param_p2"])
                mape = calculate_mape(y_true, y_h)
                param_rows.append({
                    "Modelo": model_options[m_key],
                    "R²": f"{p.get('r_cuadrado', 0):.4f}",
                    "MAPE (%)": f"{mape:.2f}%",
                    "m₁ (Potencial M1)": f"{p['param_m1']:.1f} (b₁)",
                    "p₁ (Innovación)": f"{p['param_p1']:.5f} (b₀)",
                    "q₁ (Imitación)": f"{p['param_q1']:.5f} (k₂)",
                    "m₂ (Potencial M2)": "-",
                    "p₂ (Innovación M2) / w": f"{p['param_p2']:.5f} (t₀)",
                    "q₂ (Imitación M2)": "-",
                    "q₁₂ (Imitación cruzada)": "-"
                })
                
        df_params = pd.DataFrame(param_rows)
        st.dataframe(df_params, use_container_width=True, hide_index=True)


# =======================================================
# TAB: ANÁLISIS DE MERCADO
# =======================================================
with tab_market:
    st.subheader(f"📊 Inteligencia de Mercado: {tecnologia_seleccionada}")
    
    # Cargar datos locales para el pronóstico de consenso
    df_hist_m = load_historical_data(tecnologia_seleccionada)
    params_m = load_model_parameters(tecnologia_seleccionada)
    
    subtab_qualitative, subtab_consensus = st.tabs([
        "📄 Informe Cualitativo del Mercado", 
        "🔮 Pronóstico de Consenso RAG & IA"
    ])
    
    analisis_cualitativo = load_qualitative_analysis(tecnologia_seleccionada)
    
    with subtab_qualitative:
        if analisis_cualitativo:
            st.markdown(analisis_cualitativo)
            st.divider()
            col_btn1, _ = st.columns([2.0, 3.0])
            with col_btn1:
                if st.button("🔄 Regenerar Análisis Cualitativo (Web)", key="regenerate_market_analysis", use_container_width=True):
                    with st.spinner("Buscando en la web y regenerando análisis de mercado..."):
                        analisis_text = generar_analisis_cualitativo_solo(tecnologia_seleccionada)
                        if analisis_text:
                            guardar_analisis_cualitativo(tecnologia_seleccionada, analisis_text)
                            st.success("¡Análisis cualitativo regenerado con éxito!")
                            st.rerun()
                        else:
                            st.error("No se pudo regenerar el análisis.")
        else:
            st.info("No hay un análisis cualitativo guardado para esta tecnología.")
            col_btn2, _ = st.columns([2.0, 3.0])
            with col_btn2:
                if st.button("🤖 Generar Análisis Cualitativo con IA", key="generate_market_analysis", use_container_width=True):
                    with st.spinner("Buscando en la web y generando análisis de mercado..."):
                        analisis_text = generar_analisis_cualitativo_solo(tecnologia_seleccionada)
                        if analisis_text:
                            guardar_analisis_cualitativo(tecnologia_seleccionada, analisis_text)
                            st.success("¡Análisis cualitativo generado con éxito!")
                            st.rerun()
                        else:
                            st.error("No se pudo generar el análisis.")
                            
    with subtab_consensus:
        consenso_text = load_consenso_forecast(tecnologia_seleccionada)
        
        if consenso_text:
            st.markdown(consenso_text)
            st.divider()
            col_btn3, _ = st.columns([2.0, 3.0])
            with col_btn3:
                if st.button("🔄 Regenerar Pronóstico de Consenso", key="regenerate_consensus_btn", use_container_width=True):
                    if not df_hist_m.empty and params_m and analisis_cualitativo:
                        with st.spinner("Generando pronóstico de consenso..."):
                            new_consenso = generar_consenso_pronostico_ia(tecnologia_seleccionada, df_hist_m, params_m, analisis_cualitativo)
                            if new_consenso:
                                guardar_consenso_forecast(tecnologia_seleccionada, new_consenso)
                                st.success("¡Pronóstico de consenso regenerado!")
                                st.rerun()
                            else:
                                st.error("No se pudo generar el consenso.")
                    else:
                        st.error("Asegúrate de que la tecnología tenga datos históricos, modelos ajustados y un análisis cualitativo previo.")
        else:
            st.info("Aún no se ha generado el pronóstico de consenso para esta tecnología.")
            col_btn4, _ = st.columns([2.0, 3.0])
            with col_btn4:
                if st.button("🤖 Generar Pronóstico de Consenso con IA", key="generate_consensus_btn", use_container_width=True):
                    if not df_hist_m.empty and params_m and analisis_cualitativo:
                        with st.spinner("Integrando curvas de difusión y datos cualitativos..."):
                            new_consenso = generar_consenso_pronostico_ia(tecnologia_seleccionada, df_hist_m, params_m, analisis_cualitativo)
                            if new_consenso:
                                guardar_consenso_forecast(tecnologia_seleccionada, new_consenso)
                                st.success("¡Pronóstico de consenso generado!")
                                st.rerun()
                            else:
                                st.error("No se pudo generar el consenso.")
                    else:
                        st.error("Se requieren datos históricos, modelos ajustados y un análisis cualitativo previo. Si falta el análisis cualitativo, genéralo primero en la pestaña correspondiente.")


# =======================================================
# TAB 2: DESCUBRIMIENTO CIENTÍFICO
# =======================================================
with tab2:
    st.subheader("🔬 Descubrimiento y Búsqueda de Literatura Científica")
    st.markdown("Busca, descubre e indexa artículos de literatura científica en el motor RAG en tiempo real para fundamentar los análisis predictivos.")
    
    subtab_search, subtab_upload = st.tabs(["🔍 Buscar en Línea", "📤 Subir Archivo PDF Local"])
    
    with subtab_search:
        col_q, col_src, col_num = st.columns([3, 1.5, 1])
        with col_q:
            search_query = st.text_input("Consulta de literatura", value="diffusion model technology adoption", placeholder="Ej. Bass diffusion model application")
        with col_src:
            fuente_busqueda = st.selectbox("Fuente de Literatura", ["arXiv (Preprints Abiertos)", "ResearchGate / OpenAlex (Global)"])
        with col_num:
            max_results = st.slider("Resultados máximos", min_value=1, max_value=20, value=5)
            
        btn_buscar = st.button("🔍 Buscar en Bases de Datos Científicas", use_container_width=True)
        
        # Session state to store search results
        if "arxiv_search_results" not in st.session_state:
            st.session_state.arxiv_search_results = []
            
        if btn_buscar:
            with st.spinner(f"Consultando {fuente_busqueda}..."):
                if "arXiv" in fuente_busqueda:
                    st.session_state.arxiv_search_results = buscar_arxiv(search_query, max_results)
                else:
                    st.session_state.arxiv_search_results = buscar_openalex(search_query, max_results)
                
        if st.session_state.arxiv_search_results:
            st.markdown(f"#### Resultados de la búsqueda ({len(st.session_state.arxiv_search_results)})")
            
            for idx, paper in enumerate(st.session_state.arxiv_search_results):
                with st.container(border=True):
                    # Usar columnas para hacer la tarjeta compacta y elegante
                    col_info, col_action = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"##### 📄 {paper['titulo']}")
                        st.markdown(f"**Autores:** {', '.join(paper['autores'])}")
                        st.caption(f"📅 Publicado: {paper['fecha_publicacion']} | 🔗 [Ver Artículo/Enlace original]({paper['url_pdf']})")
                        
                        with st.expander("👁️ Resumen / Abstract"):
                            st.write(paper['abstract'])
                    with col_action:
                        selected_tech = st.selectbox(
                            "Asociar a tecnología",
                            tecnologias_disponibles,
                            index=tecnologias_disponibles.index(tecnologia_seleccionada) if tecnologia_seleccionada in tecnologias_disponibles else 0,
                            key=f"paper_tech_{idx}"
                        )
                        
                        # Verificar si ya está en la DB
                        cursor_check = conn.cursor()
                        cursor_check.execute("SELECT id FROM papers_metadata WHERE url_pdf = %s", (paper['url_pdf'],))
                        exists = cursor_check.fetchone()
                        cursor_check.close()
                        
                        if exists:
                            st.info("✓ Ya indexado en RAG")
                        else:
                            ingest_clicked = st.button("📥 Indexar en RAG", key=f"ingest_{idx}", use_container_width=True)
                            if ingest_clicked:
                                status_container = st.status("Preparando ingesta...", expanded=True)
                                success = ingestar_paper_db(paper, selected_tech, status_container)
                                if success:
                                    st.rerun()
        else:
            st.info("Ingresa una consulta y presiona buscar para consultar literatura científica.")

    with subtab_upload:
        st.markdown("### 📤 Indexar Artículo Científico Local")
        st.markdown("Sube un archivo PDF directamente desde tu computadora para extraer sus ecuaciones e indexarlo en la base de datos RAG.")
        
        with st.form("form_upload_local_paper", clear_on_submit=True):
            uploaded_paper_file = st.file_uploader("Selecciona archivo PDF", type=["pdf"])
            upload_title = st.text_input("Título del Artículo", placeholder="Ej. Estudio empírico sobre difusión logísitica-convergencia...")
            upload_authors = st.text_input("Autores (Separados por coma)", placeholder="Ej. Giho Ryu, Taehoon Kim")
            upload_abstract = st.text_area("Resumen / Abstract", placeholder="Escribe el resumen del artículo aquí...")
            upload_date = st.date_input("Fecha de Publicación")
            
            upload_tech = st.selectbox(
                "Asociar a tecnología",
                tecnologias_disponibles,
                index=tecnologias_disponibles.index(tecnologia_seleccionada) if tecnologia_seleccionada in tecnologias_disponibles else 0
            )
            
            submit_upload = st.form_submit_button("📥 Procesar e Indexar PDF Local")
            
        if submit_upload:
            if not uploaded_paper_file:
                st.error("Por favor, selecciona un archivo PDF primero.")
            elif not upload_title.strip():
                st.error("El título es obligatorio.")
            else:
                with st.spinner("Procesando archivo local..."):
                    # Escribir el archivo subido a un archivo temporal
                    import tempfile
                    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
                    with os.fdopen(fd, 'wb') as f:
                        f.write(uploaded_paper_file.getvalue())
                    
                    # Normalizar autores a una lista
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
                    
                    status_container = st.status("Preparando ingesta...", expanded=True)
                    success = ingestar_paper_db(paper_data, upload_tech, status_container)
                    if success:
                        st.success("¡Artículo local indexado con éxito!")
                        st.rerun()


# =======================================================
# TAB 3: ASISTENTE RAG
# =======================================================
with tab3:
    st.subheader("🤖 Motor Analítico Predictivo RAG (Gemini 3.1 Pro)")
    st.markdown("Genera informes científicos que contrastan los datos históricos y modelos predictivos contra la literatura indexada en el sistema.")
    
    # Listar artículos científicos indexados
    cursor_list = conn.cursor()
    cursor_list.execute("SELECT titulo, tecnologia, fecha_publicacion, url_pdf FROM papers_metadata WHERE procesado = TRUE ORDER BY fecha_publicacion DESC")
    ingested_papers = cursor_list.fetchall()
    cursor_list.close()
    
    if ingested_papers:
        with st.expander(f"📚 Artículos Científicos Disponibles en el Contexto RAG ({len(ingested_papers)})"):
            for title, tech, date, url_pdf in ingested_papers:
                if url_pdf:
                    st.markdown(f"- 📄 [**{title}**]({url_pdf}) (Tecnología: `{tech}`, Fecha: `{date}`)")
                else:
                    st.markdown(f"- 📄 **{title}** (Tecnología: `{tech}`, Fecha: `{date}`)")
    else:
        st.warning("No hay artículos científicos indexados actualmente. Ve a la pestaña 'Descubrimiento Científico' para agregar literatura de soporte.")
        
    query_usuario = st.text_input("Consulta adicional para RAG", placeholder="Escribe aquí tu consulta específica sobre los modelos de adopción...")
    
    if st.button("Generar Informe Analítico", use_container_width=True):
        if not ingested_papers:
            st.error("No hay literatura en el contexto RAG para generar el informe basado en papers. Por favor, indexa al menos un artículo científico primero.")
        else:
            with st.spinner("Generando reporte científico..."):
                try:
                    query_embed_resp = genai.embed_content(
                        model="models/gemini-embedding-001",
                        content=query_usuario if query_usuario else f"Análisis de adopción de {tecnologia_seleccionada}",
                        task_type="retrieval_query",
                        output_dimensionality=768
                    )
                    query_embedding = query_embed_resp['embedding']
                    
                    vec_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
                    
                    query_rpc = """
                    SELECT * FROM match_chunks(
                        %s::vector, 
                        0.5, 
                        5, 
                        %s
                    )
                    """
                    cursor = conn.cursor(cursor_factory=DictCursor)
                    cursor.execute(query_rpc, (vec_str, tecnologia_seleccionada))
                    context_chunks = cursor.fetchall()
                    cursor.close()
                    
                    if not context_chunks:
                        context_text = "No se encontraron papers relevantes en la base de datos para esta tecnología específica."
                    else:
                        context_text = "\n\n".join([f"- {c['contenido_chunk']}" for c in context_chunks])
                        
                    prompt = r"""
ROLE: Senior Data Scientist & Technology Forecasting Expert
CONTEXT: Eres el motor analítico de la plataforma. Analiza el estado de adopción basándote en este contexto científico indexado: 
{CONTEXT_TEXT}

Adicionalmente, el usuario ha preguntado: "{QUERY_USUARIO}"

INSTRUCCIÓN: Genera un informe predictivo detallado de modelos de adopción para {TECNOLOGIA_SELECCIONADA}. Debe incluir obligatoriamente el modelado matemático detallado de los 7 modelos de difusión disponibles.
ESTRUCTURA OBLIGATORIA DE LA RESPUESTA:
1. Diagnóstico de Estado Actual: Determina si la tecnología está atrapada en el 'Abismo de Moore' o si ya saltó al Mercado 2 (Mayoría Pragmática). Justifica con los datos.
2. Contraste de Previsión y Modelos Científicos:
   Explica y compara cómo abordan la adopción los 7 modelos de difusión. Debes escribir la formulación matemática en LaTeX (usando $$ para bloques y $ para fórmulas en línea) para cada uno de los siguientes modelos:
   - **Modelo de Bass Clásico (1969)**:
     $$x(t) = m \frac{1 - e^{-(p+q)t}}{1 + \frac{q}{p}e^{-(p+q)t}}$$
   - **Modelo de Dos Mercados Independientes - Roset & Canals (2011)**:
     $$x(t) = x_1(t) + x_2(t)$$ donde $x_1(t)$ y $x_2(t)$ son modelos clásicos de Bass independientes:
     $$x_i(t) = m_i \frac{1 - e^{-(p_i+q_i)t}}{1 + \frac{q_i}{p_i}e^{-(p_i+q_i)t}}$$
   - **Modelo de Tanny & Derzko (1988)**:
     $$x_1(t) = n_1 (1 - e^{-p_1 t})$$
     $$\frac{dx_2}{dt} = \left(p_2 + q_2 \frac{x_1(t) + x_2(t)}{n_1 + n_2}\right)(n_2 - x_2(t))$$
   - **Modelo de Steffens & Murthy (1992)**:
     $$N_1(t) = K_1 \frac{1 - e^{-(\alpha + \beta)t}}{1 + \frac{\beta}{\alpha} e^{-(\alpha + \beta)t}}$$
     $$\frac{dN_2}{dt} = (K_2 - N_2(t)) \gamma (N_1(t) + N_2(t))$$
   - **Modelo del Efecto Saddle de Muller & Yogev (2006)**:
     $$I(t) = N_i \frac{1 - e^{-(p_i + q_i)t}}{1 + \frac{q_i}{p_i} e^{-(p_i + q_i)t}}$$
     $$\frac{dM}{dt} = \left( p_m + q_m \frac{M(t)}{N_i + N_m} + q_{im} \frac{I(t)}{N_i + N_m} \right) (N_m - M(t))$$
   - **Modelo de Influenciadores e Imitadores de Van den Bulte & Joshi (2007)**:
     $$F_1(t) = \frac{1 - e^{-(p_1 + q_1)t}}{1 + \frac{q_1}{p_1} e^{-(p_1 + q_1)t}}$$
     $$\frac{dF_2}{dt} = q_2 (w F_1(t) + (1 - w) F_2(t)) (1 - F_2(t))$$
     $$N(t) = M_1 F_1(t) + M_2 F_2(t)$$
   - **Modelo Logístico de Difusión-Convergencia (Ryu & Kim, 2025)**:
     $$L(t) = \frac{b_1}{1 + \left(\frac{b_1 - b_0}{b_0}\right) e^{-k_2(t - t_0)}}$$
3. Interpretación y Parámetros: Explica detalladamente el significado práctico de los coeficientes de interacción (como $q_{im}$, $\gamma$, $w$), así como la tasa de crecimiento logístico $k_2$ y el punto de inflexión $t_0$, y cómo justifican o explican los saltos o baches entre mercados.
4. Citas y Evidencia: Cita textualmente con Autor y Año los papers origen del contexto científico que sustentan el análisis.
FORMATO: Markdown limpio directamente en la interfaz de Streamlit, sin preámbulos.
""".replace("{CONTEXT_TEXT}", context_text).replace("{QUERY_USUARIO}", query_usuario).replace("{TECNOLOGIA_SELECCIONADA}", tecnologia_seleccionada)
                    
                    respuesta_gemini = generate_content_with_fallback(
                        prompt=prompt,
                        primary_model="gemini-3.1-pro-preview",
                        fallback_models=["gemini-flash-latest", "gemini-pro-latest"]
                    )
                    st.markdown(respuesta_gemini.text)
                    
                except Exception as e:
                    st.error(f"Error generando el informe: {e}")
