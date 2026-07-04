import os
import toml
import re
import urllib.request
import urllib.parse
import google.generativeai as genai

try:
    secrets = toml.load(os.path.join(".streamlit", "secrets.toml"))
    GEMINI_API_KEY = secrets.get("gemini", {}).get("api_key") or secrets.get("gemini_api_key")
except Exception:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("API Key not found.")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

def search_ddg_statista(tech_name):
    query = f"site:statista.com {tech_name} adoption users numbers millions"
    query_encoded = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={query_encoded}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
        # Extract snippets from DDG HTML
        # DuckDuckGo HTML uses <a class="result__snippet" ...>snippet</a>
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        
        # Clean HTML tags from snippets
        clean_snippets = []
        for s in snippets[:6]:
            s_clean = re.sub(r'<[^>]+>', '', s).strip()
            clean_snippets.append(s_clean)
            
        return "\n\n".join(clean_snippets)
    except Exception as e:
        print(f"Error in DDG search: {e}")
        return ""

print("Searching DDG...")
context = search_ddg_statista("Virtual Reality")
print("Found context:")
print(context)

if context:
    print("\nAsking Gemini to extract year-by-year numbers...")
    prompt = f"""
    Basándote en este contexto recuperado de búsquedas de Statista:
    {context}
    
    Tu tarea es extraer o estimar de forma realista y coherente la serie histórica de adopción acumulada de usuarios globales en millones de 2015 a 2024 para "Virtual Reality".
    
    CRITICAL: Los datos deben alinearse lo más posible con las cifras reales del contexto. Si faltan años, interpolar o extrapolar de forma continua y lógica (los usuarios acumulados deben crecer o mantenerse estables).
    
    Genera EXCLUSIVAMENTE una respuesta en JSON válido con el siguiente esquema exacto, sin explicaciones ni markdown:
    {{
        "datos": [
            {{"anio": 2015, "usuarios_millones": 5.0}},
            ...
        ]
    }}
    """
    model = genai.GenerativeModel("gemini-3.1-pro-preview")
    resp = model.generate_content(prompt)
    print("Gemini response:")
    print(resp.text)
