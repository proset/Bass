import os
import re
import requests
import tempfile
import google.generativeai as genai
from supabase import create_client, Client

# Configuración de variables de entorno
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY]):
    raise ValueError("Faltan variables de entorno (SUPABASE_URL, SUPABASE_KEY o GEMINI_API_KEY)")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

# Configurar modelos
extraction_model = genai.GenerativeModel("gemini-1.5-pro")
EMBEDDING_MODEL = "models/text-embedding-004"

def download_pdf(url):
    """Descarga el PDF a un archivo temporal"""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    with os.fdopen(fd, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return temp_path

def extract_text_with_gemini(pdf_path):
    """Usa Gemini 1.5 Pro para extraer texto y ecuaciones de un PDF."""
    print("Subiendo documento a Gemini...")
    uploaded_file = genai.upload_file(path=pdf_path, display_name="Paper_PDF")
    
    prompt = (
        "Extract all the text from this scientific paper. "
        "Format the output in clean Markdown. "
        "CRITICAL: Keep all mathematical equations intact using LaTeX syntax, wrapped in $ for inline math or $$ for block math."
    )
    print("Extrayendo contenido estructurado...")
    response = extraction_model.generate_content([uploaded_file, prompt])
    
    # Limpieza
    genai.delete_file(uploaded_file.name)
    
    return response.text

def smart_chunking(text, chunk_size=1200, overlap=200):
    """
    Algoritmo de fragmentación inteligente que respeta delimitadores de LaTeX.
    """
    # 1. Encontrar todos los bloques de ecuaciones ($$ ... $$ o $ ... $)
    math_pattern = re.compile(r'(\$\$[\s\S]*?\$\$|\$[\s\S]*?\$)', re.MULTILINE)
    
    # Marcador temporal para no romper ecuaciones
    placeholders = {}
    
    def replacer(match):
        uid = f"__MATH_BLOCK_{len(placeholders)}__"
        placeholders[uid] = match.group(0)
        return uid
        
    text_masked = math_pattern.sub(replacer, text)
    
    # 2. Dividir por párrafos o saltos de línea para respetar estructura
    paragraphs = text_masked.split('\n')
    
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        if len(current_chunk) + len(p) < chunk_size:
            current_chunk += p + "\n"
        else:
            # Revertir placeholders antes de guardar
            for uid, math_text in placeholders.items():
                current_chunk = current_chunk.replace(uid, math_text)
            chunks.append(current_chunk.strip())
            
            # Tomar el overlap (aproximado) del chunk anterior
            current_chunk = current_chunk[-overlap:] + p + "\n"
            
    if current_chunk.strip():
        for uid, math_text in placeholders.items():
            current_chunk = current_chunk.replace(uid, math_text)
        chunks.append(current_chunk.strip())
        
    return chunks

def get_embedding(text):
    """Genera el embedding usando text-embedding-004 de Gemini."""
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']

def process_unprocessed_papers():
    """Busca papers no procesados, extrae texto, hace chunks, genera vectores y los guarda en Supabase."""
    print("Buscando papers sin procesar...")
    response = supabase.table("papers_metadata").select("*").eq("procesado", False).execute()
    papers = response.data
    
    if not papers:
        print("No hay papers pendientes de procesamiento.")
        return
        
    for paper in papers:
        paper_id = paper['id']
        pdf_url = paper['url_pdf']
        
        print(f"\nProcesando paper: {paper.get('titulo', paper_id)}")
        
        if not pdf_url:
            print("No hay URL de PDF válida. Saltando...")
            continue
            
        temp_pdf = None
        try:
            temp_pdf = download_pdf(pdf_url)
            full_text = extract_text_with_gemini(temp_pdf)
            chunks = smart_chunking(full_text)
            
            print(f"Generados {len(chunks)} fragmentos. Vectorizando...")
            
            # Insertar en base de datos
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                embedding = get_embedding(chunk)
                
                chunk_data = {
                    "paper_id": paper_id,
                    "contenido_chunk": chunk,
                    "vector_embedding": embedding,
                    "numero_pagina": 0 # Simplificado, ya que Gemini unifica el texto
                }
                supabase.table("papers_embeddings").insert(chunk_data).execute()
                
            # Marcar como procesado
            supabase.table("papers_metadata").update({"procesado": True}).eq("id", paper_id).execute()
            print(f"Paper {paper_id} procesado con éxito.")
            
        except Exception as e:
            print(f"Error procesando paper {paper_id}: {e}")
        finally:
            if temp_pdf and os.path.exists(temp_pdf):
                os.remove(temp_pdf)

if __name__ == "__main__":
    process_unprocessed_papers()
