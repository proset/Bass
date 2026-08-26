#!/usr/bin/env python3
"""
llm_reviewer.py
-----------------
Capa 2 (semantica) con el proveedor LLM como parametro intercambiable.
Sustituye a semantic_reviewer.py y gemini_reviewer.py: la rubrica, el
prompt y la logica de fusion viven en UN solo lugar; cada backend solo
implementa "como llamar a su API y parsear su respuesta".
 
Uso:
    from llm_reviewer import full_review
 
    issues = full_review(texto, tabla_historica, model_fits, backend="claude")
    issues = full_review(texto, tabla_historica, model_fits, backend="gemini")
 
    # o via variable de entorno, para no tocar el codigo al cambiar de proveedor:
    #   export REVIEWER_BACKEND=gemini
    issues = full_review(texto, tabla_historica, model_fits)  # usa REVIEWER_BACKEND
 
Requiere segun el backend elegido:
    claude -> pip install anthropic   + ANTHROPIC_API_KEY
    gemini -> pip install google-genai + GEMINI_API_KEY
(Solo se importa el SDK del backend que realmente uses -- el otro es opcional.)
"""
 
from __future__ import annotations
import json
import os
from typing import List, Optional
 
from report_validator import Issue, ReportValidator, ModelFit  # capa 1
 
 
# --------------------------------------------------------------------------
# Rubrica y prompt -- compartidos por TODOS los backends. Un unico lugar
# donde añadir un patron de fallo nuevo (como el "2500M para 2026" de
# TikTok) beneficia a cualquier proveedor que se use.
# --------------------------------------------------------------------------
 
REVIEW_RUBRIC = """
Eres un auditor de coherencia para informes de adopcion tecnologica generados
por IA. Tu unico trabajo es encontrar incoherencias INTERNAS del documento
-- no evaluar si las cifras son correctas en el mundo real, sino si el
documento se contradice a si mismo o afirma cosas que no se sostienen con
sus propios datos.
La fecha de hoy es {CURRENT_DATE}. Cualquier fecha del informe igual o anterior a esta es legítima — no la marques como 'futura' o 'inventada'.

NOTA DE DISEÑO (CRÍTICA): por decisión arquitectónica, la prosa narrativa NO
contiene cifras de adopción; todas las cifras viven en las tablas y en
bullets 'AÑO: valor'. (ad) La prosa narrativa NO contiene valores de métricas ni años de citación: si una sección menciona modelos solo por nombre y remite a los "Datos oficiales (del motor)", eso es el diseño correcto, no una omisión. NUNCA marques como fallo la ausencia de un valor numérico en la prosa. Por tanto: (a) NO marques como fallo la ausencia de
valores numéricos en la prosa ni el uso de '[ver tabla]' como remisión a la
tabla oficial; valida la coherencia cualitativa de las conclusiones contra
las tablas. (b) Los porcentajes de PESO del score compuesto (R² 70%, MAPE
15%, MAPE 15%) son parámetros metodológicos, NO valores de métricas: nunca
los compares con los R²/MAPE de las tablas. (c) El análisis cualitativo usa
lenguaje especulativo ('podría', 'es posible') para expresar incertidumbre
legítima: no lo trates como contradicción salvo que afirme algo directamente
opuesto a los datos.
 
Categorias de fallo a buscar activamente (con ejemplos reales ya detectados
en informes anteriores de este mismo pipeline):
 
1. CONTRADICCION NUMERICA ENTRE SECCIONES: una cifra mencionada en una parte
   del texto no coincide con la misma cifra en otra parte, o con la tabla
   oficial de datos. Ejemplo real: un informe afirmaba "ya cuenta con 2.210
   millones... y se proyecta que superara los 2.500 millones para finales
   de ese año", cuando 2.210M YA ERA el dato de cierre de ese año segun la
   tabla oficial -- una contradiccion de ~290M en la misma frase.
 
2. CONCLUSION QUE NO SE DERIVA DE LAS PREMISAS: la seccion de "consenso" o
   "recomendacion final" adopta una cifra que no es la que arrojan los
   modelos que el propio texto dice haber elegido. Ejemplo real: un informe
   recomendaba el modelo "Ladron-de-Guevara & Putsis" y decia adoptar su
   cifra "exacta" de 124.16M para 2030, pero dos parrafos antes el mismo
   informe habia proyectado un rango de consenso de 145-160M para el mismo
   año -- cifras que no tienen relacion entre si.
 
3. CITA ACADEMICA SOSPECHOSA: una referencia con autor y año que suena
   plausible pero no corresponde a ningun paper real conocido en el campo
   de modelos de difusion de innovaciones (Bass, Roset & Canals, Tanny &
   Derzko, Steffens & Murthy, Muller & Yogev, Van den Bulte & Joshi,
   Ladron-de-Guevara & Putsis, Fourt & Woodlock, Horsky & Simon, el
   Generalized Bass Model de Bass/Krishnan/Jain). Presta especial atencion
   a citas con año {CURRENT_YEAR} o posterior, que son las mas probables de ser
   inventadas.
 
4. RAZONAMIENTO CUALITATIVO INCONSISTENTE CON LOS DATOS: el texto describe
   un patron (ej. "crecimiento monotono decreciente", "aceleracion en
   2023") que, al verificarlo aritmeticamente contra la tabla de datos
   reales, no se cumple.
 
5. DOS MODELOS MATEMATICOS DISTINTOS CON RESULTADOS IDENTICOS: si dos
   modelos con formulaciones diferentes producen EXACTAMENTE los mismos
   numeros R², MAPE y proyecciones idénticos al 100% (hasta el ultimo decimal),
   es una señal de sobreajuste o bug. NOTA IMPORTANTE: Si dos modelos (ej. Dual
   Market y Muller & Yogev) muestran metricas similares pero distintas (ej. MAPE
   13.18% vs 13.32%), NO es un error ni un blocker; es convergencia empirica
   esperada de modelos multisegmento. NO marcar como BLOCKER si las cifras difieren.
 
 
INSTRUCCIONES DE SALIDA:
Devuelve EXCLUSIVAMENTE un array JSON (sin texto adicional, sin markdown,
sin ```), donde cada elemento tiene esta forma exacta:
{
  "severity": "BLOCKER" | "WARNING" | "INFO",
  "category": "<nombre_corto_snake_case>",
  "message": "<explicacion clara y concreta de la incoherencia>",
  "evidence": "<cita textual breve, menor a 25 palabras, que ubique el problema>"
}
 
Usa BLOCKER para contradicciones numericas directas o citas inventadas con
año reciente. Usa WARNING para razonamientos flojos o formulas mal
renderizadas. Usa INFO para observaciones menores. Si no encuentras nada,
devuelve un array vacio: []
 
No repitas hallazgos puramente estructurales que un validador por regex ya
detectaria facilmente (una tabla con celdas vacias, un numero mal formado);
concentra tu esfuerzo en lo que requiere ENTENDER el texto, no solo
patron-matchear.
"""
 
 
def build_review_prompt(narrative_text: str, tables_summary: str) -> str:
    import datetime as _dt
    _cy = _dt.datetime.now().year
    rubric_filled = REVIEW_RUBRIC.replace("{CURRENT_YEAR}", str(_cy))
    rubric_filled = rubric_filled.replace("{CURRENT_DATE}", _dt.datetime.now().strftime("%Y-%m-%d"))
    return f"""{rubric_filled}
 
--- TEXTO DEL INFORME ---
{narrative_text}
 
--- TABLAS DE DATOS (referencia para contrastar) ---
{tables_summary}
"""
 
 
def historical_table_to_summary(historical_table: dict) -> str:
    lines = ["Tabla historica real:"]
    for year in sorted(historical_table):
        lines.append(f"  {year}: {historical_table[year]}M")
    return "\n".join(lines)
 
 
def model_fits_to_summary(model_fits: List[ModelFit]) -> str:
    lines = ["Tabla de ajuste y proyecciones por modelo (la recomendación oficial se basa en el Score compuesto, que equilibra R², MAPE y parsimonia):"]
    for m in model_fits:
        proj = ", ".join(f"{y}={v}M" for y, v in sorted(m.projections.items()))
        _score = getattr(m, "score", None)
        _score_txt = f", Score={_score}" if _score is not None else ""
        lines.append(f"  {m.name}: R2={m.r2}, MAPE={m.mape}%{_score_txt}, proyecciones: {proj}")
    return "\n".join(lines)
 
 
def _parse_issues_json(raw_text: str, source_label: str) -> List[Issue]:
    """Comun a ambos backends: limpia posibles fences de markdown y valida el JSON."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()
 
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Intento de recuperacion: Gemini a veces trunca la respuesta.
        # Extraemos los objetos JSON completos que hayan llegado antes del corte.
        recovered = []
        try:
            import re as _re
            # Busca objetos JSON completos { ... } dentro del texto recibido
            for m in _re.finditer(r'\{[^{}]*\}', cleaned, _re.DOTALL):
                try:
                    obj = json.loads(m.group())
                    recovered.append(obj)
                except Exception:
                    pass
        except Exception:
            pass
        if recovered:
            issues_out = [
                Issue(
                    severity=item.get("severity", "WARNING"),
                    category=item.get("category", "semantico_sin_categoria"),
                    message=item.get("message", ""),
                    evidence=item.get("evidence", ""),
                )
                for item in recovered
            ]
            issues_out.append(Issue(
                "WARNING", "respuesta_llm_truncada",
                f"La respuesta de {source_label} fue truncada; se recuperaron {len(recovered)} item(s) parciales.",
            ))
            return issues_out
        raise RuntimeError(
            f"La respuesta de {source_label} no fue JSON valido: {e}\n"
            f"Respuesta cruda:\n{raw_text[:500]}"
        ) from e
 
    return [
        Issue(
            severity=item.get("severity", "WARNING"),
            category=item.get("category", "semantico_sin_categoria"),
            message=item.get("message", ""),
            evidence=item.get("evidence", ""),
        )
        for item in parsed
    ]
 
 
# --------------------------------------------------------------------------
# Backends -- cada uno solo sabe "como hablar con su API". Nada de rubrica
# ni de logica de negocio vive aqui.
# --------------------------------------------------------------------------
 
def _call_claude(prompt: str, model: str, max_tokens: int) -> str:
    try:
        import anthropic
    except ImportError as e:
        raise RuntimeError(
            "Falta el paquete 'anthropic'. Instalar con: pip install anthropic"
        ) from e
 
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=model,
        temperature=0,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(
        block.text for block in response.content if getattr(block, "type", "") == "text"
    )
 
 
def _call_gemini(prompt: str, model: str, max_tokens: int) -> str:
    try:
        from google import genai
        from google.genai import types
    except ImportError as e:
        raise RuntimeError(
            "Falta el paquete 'google-genai'. Instalar con: pip install google-genai"
        ) from e
 
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=0,
            seed=42,
            response_mime_type="application/json",  # Gemini fuerza JSON valido nativamente
        ),
    )
    return response.text
 
 
# nombre de backend -> (funcion de llamada, modelo por defecto)
_BACKENDS = {
    "claude": (_call_claude, "claude-sonnet-5"),
    "gemini": (_call_gemini, "gemini-2.5-flash"),
}
 
 
def review_with_llm(
    narrative_text: str,
    tables_summary: str,
    backend: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: int = 8000,
) -> List[Issue]:
    """
    Punto de entrada unico de la capa semantica, independiente del proveedor.
 
    backend: "claude" | "gemini". Si se omite, usa la variable de entorno
             REVIEWER_BACKEND, o "claude" si tampoco esta definida.
    model:   nombre de modelo especifico; si se omite, usa el default de ese backend.
    """
    backend = (backend or os.environ.get("REVIEWER_BACKEND") or "gemini").lower()
    if backend not in _BACKENDS:
        raise ValueError(
            f"Backend '{backend}' no soportado. Opciones: {list(_BACKENDS)}"
        )
 
    call_fn, default_model = _BACKENDS[backend]
    prompt = build_review_prompt(narrative_text, tables_summary)
    raw_text = call_fn(prompt, model or default_model, max_tokens)
    return _parse_issues_json(raw_text, source_label=backend)
 
 
# --------------------------------------------------------------------------
# Orquestador combinado: capa 1 (determinista) + capa 2 (semantica, cualquier backend)
# --------------------------------------------------------------------------
 
def full_review(
    narrative_text: str,
    historical_table: dict,
    model_fits: List[ModelFit],
    backend: Optional[str] = None,
    use_llm: bool = True,
    df_proj=None,
) -> List[Issue]:
    """Corre ambas capas y devuelve la lista fusionada de hallazgos."""
    rv = ReportValidator(narrative_text, historical_table, model_fits, tolerance_pct=20.0, df_proj=df_proj)
    issues = rv.run_all()
 
    if use_llm:
        tables_summary = "\n\n".join([
            historical_table_to_summary(historical_table),
            model_fits_to_summary(model_fits),
        ])
        try:
            issues.extend(review_with_llm(narrative_text, tables_summary, backend=backend))
        except Exception as e:
            issues.append(Issue(
                "WARNING", "capa_semantica_no_disponible",
                f"No se pudo ejecutar la capa semantica: {e}",
            ))
 
    return issues
 
 
def gate(issues: List[Issue]) -> bool:
    """True si el informe pasa (0 BLOCKER), False si debe bloquearse."""
    return not any(i.severity == "BLOCKER" for i in issues)
 
 
if __name__ == "__main__":
    print(__doc__)
    print("Backends disponibles:", list(_BACKENDS))
    print("Usar full_review(texto, tabla_historica, model_fits, backend='claude'|'gemini').")
