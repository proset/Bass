import os
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import requests
import tempfile
import pandas as pd
import logging

logger = logging.getLogger("BassSources")

def buscar_arxiv(query, max_results=10):
    """Realiza una búsqueda de papers científicos en arXiv API."""
    logger.info(f"Iniciando búsqueda en ArXiv con consulta: '{query}' (máx resultados: {max_results})")
    try:
        query_encoded = urllib.parse.quote(query)
        url = f"http://export.arxiv.org/api/query?search_query=all:{query_encoded}&max_results={max_results}"
        
        response = requests.get(url, timeout=12)
        response.raise_for_status()
        xml_data = response.content
            
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
        logger.info(f"Se encontraron {len(papers)} papers en ArXiv.")
        return papers
    except Exception as e:
        logger.error(f"Error en búsqueda de arXiv: {e}")
        return []

def buscar_openalex(query, max_results=10):
    """Realiza una búsqueda de literatura científica global en la API pública de OpenAlex."""
    logger.info(f"Iniciando búsqueda en OpenAlex con consulta: '{query}' (máx resultados: {max_results})")
    try:
        url = f"https://api.openalex.org/works?search={urllib.parse.quote(query)}&per_page={max_results}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mailto': 'technology-adoption-bass@aumentasolutions.com'
        }
        
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        
        papers = []
        for paper in results:
            title = paper.get("title", "Sin título")
            
            # Autores
            authorships = paper.get("authorships", [])
            authors = [a.get("author", {}).get("display_name", "Desconocido") for a in authorships]
            
            # Reconstruir abstract (OpenAlex devuelve un índice invertido)
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
            
            # Enlace al PDF o DOI
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
        logger.info(f"Se encontraron {len(papers)} papers en OpenAlex.")
        return papers
    except Exception as e:
        logger.error(f"Error en búsqueda de OpenAlex: {e}")
        return []

def download_pdf(url):
    """Descarga un PDF de internet y devuelve la ruta al archivo temporal local."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers, stream=True, timeout=30)
    response.raise_for_status()
    
    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    with os.fdopen(fd, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return temp_path

def descargar_dataset_owid():
    """Descarga el dataset completo de difusión tecnológica de Our World in Data."""
    logger.info("Descargando dataset de difusión tecnológica desde Our World in Data...")
    url = "https://ourworldindata.org/grapher/technology-adoption-by-households-in-the-united-states.csv"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        content = response.content
            
        fd, temp_path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, 'wb') as f:
            f.write(content)
            
        df = pd.read_csv(temp_path)
        os.remove(temp_path)
        return df
    except Exception as e:
        logger.error(f"Error descargando el dataset de OWID: {e}")
        return pd.DataFrame()

def buscar_web_ddg(query):
    """Realiza una búsqueda básica en DuckDuckGo HTML y extrae fragmentos relevantes."""
    logger.info(f"Realizando búsqueda web en DuckDuckGo: '{query}'")
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
        logger.error(f"Error en búsqueda DuckDuckGo: {e}")
        return ""

