#!/usr/bin/env python
"""BASS v3: Claude extracción + GLM fit + Claude análisis. Sin Gemini, sin Groq."""

import sys
import os
import subprocess
import json
import anthropic
import numpy as np

BASS_DIR = r"C:\Users\roset\Bass"
GLM_DIR = r"C:\Users\roset\GLM"
sys.path.insert(0, BASS_DIR)

def log(step, msg): 
    print(f"[{step}] {msg}")

def extract_with_claude(tech):
    """Claude web_search → datos estructurados."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"""Busca la adopción acumulada de '{tech}' en millones de usuarios/unidades (2015-2025). INSTRUCCIONES:
1. PRIMERO busca datos directos: MAU, subscribers, unidades vendidas publicadas por la empresa. Si la empresa publica oficialmente, usa esos valores.
2. Si no encuentra datos directos, busca estimaciones de analistas: SimilarWeb (visitas web mensuales al dominio de la empresa), SensorTower (descargas de app), eMarketer, Statista. Estas estimaciones incluyen usuarios free + paid.
3. Si no hay analistas, busca facturación anual + ARPU, calcula usuarios = facturación / ARPU.
4. Para 2015-2024: usa datos del año completo. Para 2025: usa la mejor estimación disponible. Marca años incompletos o estimados con [estimado] al lado del valor. Devuelve el resultado así:
===DATOS===
2015: valor [fuente, confianza: alta/media/baja]
2016: valor [fuente, confianza...]
... hasta 2025.
5. Si la empresa es privada, busca datos de SimilarWeb, SensorTower, Statista. NO uses solo facturación/ARPU como primer recurso — busca MAU first.
6. Busca visitas web mensuales en SimilarWeb para el dominio principal de la empresa si no encuentra datos de MAU.
Para empresas privadas (Anthropic, OpenAI, etc.):
- busca "SimilarWeb claude.ai" o "SimilarWeb chat.openai.com"
- busca "SensorTower [nombre de la app]
- busca "MAU [empresa] 2025"
- busca "eMarketer [empresa]"
Si encuentras un rango de valores, usa el valor medio."""
        }]
    )
    
    # Extraer texto
    text = ""
    for block in response.content:
        if getattr(block, "type", "") == "text":
            text += getattr(block, "text", "")
            
    # Parsear datos (formato: "2015: valor [fuente, confianza]")
    data = []
    for line in text.split("\n"):
        line = line.strip()
        if ":" in line and any(c.isdigit() for c in line[:4]):
            # Extraer año y valor
            parts = line.split(":")
            if len(parts) >= 2:
                try:
                    year = int(parts[0].strip())
                    # Extraer el primer número del segundo valor
                    val_str = parts[1].split()[0] if len(parts[1].split()) > 0 else "0"
                    val = float(val_str.replace(",", "."))
                    is_estimate = "[estimado]" in line or "estimado" in line
                    data.append({"anio": year, "usuarios_millones": val, "is_estimate": is_estimate, "source_date": None, "metric_type": None})
                except (ValueError, IndexError):
                    continue
                    
    print(f"[extract] {len(data)} puntos extraídos por Claude")
    for d in data:
        print(f"  {d['anio']}: {d['usuarios_millones']}M")
        
    return data, response.usage.input_tokens, response.usage.output_tokens

def insert_to_bd(tech, data):
    """Insertar datos en BD."""
    from config import get_conn, release_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM historical_adoption WHERE tecnologia = %s", (tech,))
    for d in data:
        cur.execute(
            "INSERT INTO historical_adoption (tecnologia, anio, adopcion_acumulada, is_estimate) VALUES (%s, %s, %s, %s)",
            (tech, d["anio"], d["usuarios_millones"], d["is_estimate"])
        )
    conn.commit()
    release_conn(conn)
    print(f"[insert] {len(data)} filas insertadas")

def fit_tech(tech):
    """GLM fit (subprocess)."""
    result = subprocess.run(["python", "persist_fit.py", tech], cwd=GLM_DIR, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr: print(result.stderr)
    return result.returncode == 0

def analyze_with_claude(tech):
    """Claude analysis (sin web_search)."""
    from data.loaders import load_historical_data, load_model_parameters
    from models.analytical_projections import project_model
    from data.report_compiler import model_labels
    
    df_hist = load_historical_data(tech)
    params = load_model_parameters(tech)
    real_series = {int(a): float(v) for a, v in zip(df_hist["anio"], df_hist["adopcion_acumulada"])}
    
    best_model = max(params.items(), key=lambda x: float(x[1].get("score", 0)))
    recommended_model_key = best_model[0]
    recommended_model_name = model_labels.get(recommended_model_key, recommended_model_key)
    recommended_params = best_model[1]
    
    # Proyecciones
    last_year = max(real_series.keys())
    t_proj = np.arange(len(real_series), len(real_series) + 10, dtype=float)
    y_proj = project_model(recommended_model_key, recommended_params, t_proj)
    last_val = list(real_series.values())[-1]
    y_proj = np.maximum(y_proj, last_val)
    
    # Claude analysis
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    hist_str = "\n".join(f"{int(df_hist.iloc[i]['anio'])}: {float(df_hist.iloc[i]['adopcion_acumulada']):.2f}M" for i in range(len(df_hist)))
    fit_str = "\n".join(f"- {model_labels.get(mk, mk)}: R²={float(p.get('r_cuadrado',0)):.4f}, MAPE={float(p.get('mape_ajuste',0)):.2f}%, Score={float(p.get('score',0)):.2f}" for mk, p in params.items())
    
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f"""Eres un analista de adopción tecnológica. Redacta el análisis cualitativo del informe de '{tech}'.
DATOS HISTÓRICOS:
{hist_str}
RESULTADOS DEL AJUSTE (10 modelos):
{fit_str}
MODELO RECOMENDADO: {recommended_model_name} (Score={float(recommended_params.get('score',0)):.2f})
PROYECCIONES:  2030: {float(y_proj[4]):.1f}M  2035: {float(y_proj[9]):.1f}M
INSTRUCCIONES:
1. NO números en prosa (todo en tablas).
2. NO años de citación (modelos SOLO por nombre).
3. Escribe: §1 Resumen Ejecutivo, §5 Análisis Cualitativo, §6 Marco Teórico, §4.2 Recomendación.
4. Explica selección de modelo, fase de crecimiento, advertencias (sobreajuste, escasez de datos).
5. Si la empresa es privada: "NOTA DE FUENTE DE DATOS: [empresa] no publica usuarios oficiales. Datos estimados. Incertidumbre: alta."
"""
        }]
    )
    
    analysis = ""
    for block in response.content:
        if getattr(block, "type", "") == "text":
            analysis += getattr(block, "text", "")
            
    # Tablas determinísticas
    hist_table = "## 2. Datos Históricos\n\n| Año | Adopción (M) |\n|---|---|\n"
    for a, v in sorted(real_series.items()):
        hist_table += f"| {a} | {v:.2f} M |\n"
        
    metrics_table = "## 3. Métricas\n\n| Modelo | R² | MAPE | Score | k |\n|---|---|---|---|---|\n"
    for mk, p in params.items():
        name = model_labels.get(mk, mk)
        metrics_table += f"| {name} | {float(p.get('r_cuadrado',0)):.4f} | {float(p.get('mape_ajuste',0)):.2f}% | {float(p.get('score',0)):.2f} | {p.get('n_params', '?')} |\n"
        
    proj_table = f"## 4. Proyecciones\n\n| Año | {recommended_model_name} (M) |\n|---|---|\n"
    for i, year in enumerate(range(last_year + 1, last_year + 11)):
        proj_table += f"| {year} | {float(y_proj[i]):.2f} M |\n"
        
    datos_oficiales = f"**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado ({recommended_model_name}): R²={float(recommended_params.get('r_cuadrado',0)):.4f}, MAPE={float(recommended_params.get('mape_ajuste',0)):.2f}%, Score={float(recommended_params.get('score',0)):.2f}."
    
    # Dummy formulations variable if not strictly defined in user snippet
    formulations = "## (Fórmulas...)"
    
    # Ensamblar
    report = f"# Informe de Adopción: {tech}\n\n{analysis}\n\n{hist_table}\n\n{metrics_table}\n\n{proj_table}\n\n{datos_oficiales}\n\n### 📐 Formulación Matemática\n\n{formulations}\n"
    
    report_file = f"informe_global_{tech}.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"[analysis] Claude tokens: {response.usage.input_tokens} input, {response.usage.output_tokens} output")
    print(f"[analysis] Reporte: {report_file}")
    return True

def main():
    tech = sys.argv[1] if len(sys.argv) > 1 else "electric vehicles"
    print(f"\n{'='*60}\n  BASS v3: Claude ext + GLM fit + Claude ana: '{tech}'\n{'='*60}\n")
    
    # 1. Claude extracción
    log("1/3", "Extracción con Claude web_search...")
    data, in_tok, out_tok = extract_with_claude(tech)
    log("1/3", f"Extraído: {len(data)} puntos")
    
    # 2. GLM fit
    log("2/3", "Fit con GLM...")
    insert_to_bd(tech, data)
    if not fit_tech(tech):
        print("\n*** ABORTADO: Fit falló. ***")
        sys.exit(1)
        
    # 3. Claude análisis
    log("3/3", "Análisis con Claude...")
    analyze_with_claude(tech)
    
    # Greps
    log("done", "Pipeline complete.")
    print(f"\n{'='*60}\n  REPORT: informe_global_{tech}.md\n{'='*60}\n")

if __name__ == "__main__":
    main()
