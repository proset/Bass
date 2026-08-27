"""
ai/groq_client.py — Cliente Groq (Llama 3.1 70B). Determinista con temperature=0.
"""

import logging
import os

try:
    from groq import Groq
except ImportError:
    Groq = None

logger = logging.getLogger("GroqClient")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = "openai/gpt-oss-120b"  # verificar nombre actual

if GROQ_API_KEY and Groq:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY no detectada. Groq no estará disponible.")
    elif not Groq:
        logger.warning("Paquete 'groq' no instalado. Ejecuta: pip install groq")

def generate_content_groq(prompt, temperature=0, max_tokens=4000, response_mime_type=None):
    """
    Genera contenido usando Groq (Llama 3.1 70B).
    Determinista con temperature=0 (transformer estándar, no MoE).
    Interfaz compatible con generate_content_with_fallback.
    """
    if not client:
        raise RuntimeError("Groq no configurado. Verifica GROQ_API_KEY y pip install groq.")
    
    kwargs = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    
    # Si se pide JSON, forzar formato
    if response_mime_type == "application/json":
        kwargs["response_format"] = {"type": "json_object"}
    
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content

class MockResponse:
    def __init__(self, text):
        self.text = text

def generate_content_with_fallback_groq(prompt, response_mime_type=None, **kwargs):
    """
    Helper con fallback para Groq. Intenta el modelo principal.
    Interfaz compatible con generate_content_with_fallback (ai/gemini_client.py).
    """
    try:
        text = generate_content_groq(
            prompt=prompt,
            temperature=0,
            response_mime_type=response_mime_type,
        )
        return MockResponse(text)
    except Exception as e:
        logger.error(f"Error en Groq ({GROQ_MODEL}): {e}")
        raise
