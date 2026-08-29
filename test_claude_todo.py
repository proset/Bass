import anthropic
import os
import sys
import hashlib

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
TECH = sys.argv[1] if len(sys.argv) > 1 else "electric vehicles"
RUN = sys.argv[2] if len(sys.argv) > 2 else "1"

prompt = f"""Analiza la adopción acumulada global de '{TECH}'.
1. Busca datos históricos de adopción acumulada en millones (2015-2025).
2. Ajusta los 10 modelos de difusión (Bass Clásico, Dual Market, Gompertz, Fourt & Woodlock, GBM, Horsky & Simon, Muller & Yogev, Van den Bulte & Joshi, Difusión Logística R&K, Ladrón-de-Guevara & Putsis).
3. Proyecta a 2030 y 2035 para cada modelo.
4. Escribe el análisis cualitativo del informe (sin cifras en prosa, sin años de citación).
5. Devuelve el resultado en este formato EXACTO:

===DATOS===
Año: valor (fuente, confianza: alta/media/baja)
...
===PARAMETROS===
Modelo: m=valor, p=valor, q=valor | R²=valor, MAPE=valor, Score=valor, k=valor...
===PROYECCIONES===
Modelo | 2026 | 2030 | 2035
Modelo1 | valor | valor | valor
...
===ANALISIS===
(Texto cualitativo, sin cifras en prosa. Explica selección de modelo, fase de crecimiento, advertencias.)"""

print(f"\n{'='*60}")
print(f"  CLAUDE-TODO TEST: '{TECH}' (Run {RUN})")
print(f"{'='*60}\n")

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=8000,
    temperature=0,
    messages=[{"role": "user", "content": prompt}]
)

# Extraer el texto final
result_text = ""
for block in response.content:
    if hasattr(block, "text"):
        result_text += block.text

# Guardar resultado
output_file = f"claude_todo_{TECH.replace(' ', '_')}_run{RUN}.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(result_text)

print(result_text)
print(f"\n{'='*60}")
print(f"Resultado guardado en: {output_file}")
print(f"Tokens input: {response.usage.input_tokens}")
print(f"Tokens output: {response.usage.output_tokens}")

# Hash para comparar reproducibilidad
hash_val = hashlib.md5(result_text.encode("utf-8")).hexdigest()
print(f"MD5: {hash_val}")
print(f"{'='*60}\n")
