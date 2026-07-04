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
    pdf_path = "dual_market_diffussion_model (1).pdf"
    if not os.path.exists(pdf_path):
        print(f"PDF file not found at {pdf_path}")
        exit(1)
        
    print(f"Uploading {pdf_path} to Gemini...")
    uploaded_file = genai.upload_file(path=pdf_path, display_name="Dual_Market_Paper")
    
    prompt = (
        "Analyze this scientific paper. Specifically, find and extract the section that describes the parameter estimation, "
        "parameter search, or non-linear regression methodology (búsqueda de parámetros, regresión no lineal, estimación). "
        "Provide the exact text or equations and explain the step-by-step search methodology used for the Dual Market / Roset model."
    )
    
    print("Asking Gemini to analyze the paper section...")
    model = genai.GenerativeModel("gemini-3.1-pro-preview")
    response = model.generate_content([uploaded_file, prompt])
    
    print("\n--- RESULTS FROM PAPER ---")
    print(response.text)
    
    # Cleanup
    genai.delete_file(uploaded_file.name)
    
except Exception as e:
    print(f"Error: {e}")
