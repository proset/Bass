import google.generativeai as genai
import logging
from config import GEMINI_API_KEY, GEMINI_PRIMARY, GEMINI_FALLBACKS

logger = logging.getLogger("BassGeminiClient")

# Configurar API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.error("No se detectó la clave de API de Gemini. La IA no estará disponible.")

def get_genai_client():
    """Devuelve el módulo configurado de google-generativeai."""
    return genai

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
            generation_config = {"temperature": 0}
            if response_mime_type:
                generation_config["response_mime_type"] = response_mime_type
                
            model = genai.GenerativeModel(model_name, generation_config=generation_config, tools=tools)
            
            logger.info(f"Intentando generación de contenido con modelo: {model_name}")
            if contents:
                response = model.generate_content(contents)
            else:
                response = model.generate_content(prompt)
            
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
