import os
import toml
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

try:
    print("Testing gemini-3.1-pro-preview with google_search tool...")
    model = genai.GenerativeModel(
        model_name="gemini-3.1-pro-preview",
        tools="google_search"
    )
    
    prompt = (
        "Find the actual historical adoption data of Virtual Reality (VR) users global in millions from Statista reports between 2015 and 2024. "
        "Return ONLY a clean JSON object with this format, no markdown block, no extra text: "
        '{"datos": [{"anio": 2015, "usuarios_millones": 5.0}, ...]}'
    )
    
    response = model.generate_content(prompt)
    print("Response text:")
    print(response.text)
    
    if response.candidates and response.candidates[0].grounding_metadata:
        metadata = response.candidates[0].grounding_metadata
        print("\nGrounding Metadata:")
        print(metadata)
except Exception as e:
    print(f"Error testing grounding: {e}")
