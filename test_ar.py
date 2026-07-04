import os
import toml
import re
import urllib.request
import urllib.parse
import json
import google.generativeai as genai

try:
    secrets = toml.load(os.path.join(".streamlit", "secrets.toml"))
    GEMINI_API_KEY = secrets.get("gemini", {}).get("api_key") or secrets.get("gemini_api_key")
except Exception:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

def test_search(tech_name):
    query = f"site:statista.com {tech_name} adoption users numbers millions"
    query_encoded = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={query_encoded}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    context = ""
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        clean_snippets = []
        for s in snippets[:6]:
            s_clean = re.sub(r'<[^>]+>', '', s).strip()
            clean_snippets.append(s_clean)
        context = "\n\n".join(clean_snippets)
    except Exception as e:
        print(f"Search exception: {e}")
        
    print(f"Context found ({len(context)} chars):")
    print(context)
    
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
    model = genai.GenerativeModel("gemini-3.1-pro-preview")
    try:
        respuesta = model.generate_content(prompt)
        texto = respuesta.text.strip()
        print("\nRaw Gemini response:")
        print(texto)
        
        # Bulletproof JSON extraction
        match = re.search(r'\{[\s\S]*\}', texto)
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)
            print("\nParsed JSON successfully:")
            print(data)
        else:
            print("\nError: No JSON block found in response.")
    except Exception as e:
        print(f"Error in model execution: {e}")

test_search("Augmented Reality Headsets")
