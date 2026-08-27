from google import genai
from google.genai import types
import logging
from config import GEMINI_API_KEY, GEMINI_PRIMARY, GEMINI_FALLBACKS

logger = logging.getLogger("BassGeminiClient")

# Configurar API
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None
    logger.error("No se detectó la clave de API de Gemini. La IA no estará disponible.")

def get_genai_client():
    """Devuelve el cliente configurado de google-genai."""
    return client

def generate_content_with_fallback(prompt, contents=None, response_mime_type=None, tools=None):
    """
    Intenta generar contenido con el modelo primario de Gemini.
    Si se detecta un error de cuota o rate limit (429), reintenta
    secuencialmente con los modelos alternativos de fallback.
    """
    models_to_try = [GEMINI_PRIMARY] + GEMINI_FALLBACKS
    last_exception = None
    
    for i, model_name in enumerate(models_to_try):
        try:
            # Configurar formato de respuesta si es JSON
            config = types.GenerateContentConfig(temperature=0, seed=42)
            if response_mime_type:
                config.response_mime_type = response_mime_type
            
            # Grounding: the old codebase passes gapic Tool, we override it with the new SDK's format
            if tools:
                config.tools = [types.Tool(google_search=types.GoogleSearch())]
                
            logger.info(f"Intentando generación de contenido con modelo: {model_name}")
            if contents:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config
                )
            else:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
            
            # Avisar informativamente al usuario si se usó un fallback
            if i > 0:
                try:
                    import streamlit as st
                    st.info(f"ℹ️ El modelo primario está saturado. Se ha generado la respuesta con el modelo alternativo '{model_name}'.")
                except Exception:
                    pass
            return response
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "Resource exhausted" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                last_exception = e
                logger.warning(f"El modelo '{model_name}' reportó 429 (Resource Exhausted). Reintentando con el siguiente fallback...")
                continue
            else:
                logger.error(f"Error crítico en modelo '{model_name}': {e}")
                raise e
    raise last_exception
