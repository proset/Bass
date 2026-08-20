#!/usr/bin/env python3
"""
semantic_reviewer.py
---------------------
DEPRECADO como fuente de la logica: toda la rubrica, el prompt y el
manejo de backends ahora viven en llm_reviewer.py. Este archivo se
mantiene solo por compatibilidad con codigo que ya importa desde aqui
(ej. `from semantic_reviewer import full_review`).
 
Para proyectos nuevos, importar directamente de llm_reviewer:
    from llm_reviewer import full_review, review_with_llm, gate
"""
 
from llm_reviewer import (  # noqa: F401  (re-exportado por compatibilidad)
    REVIEW_RUBRIC,
    build_review_prompt,
    historical_table_to_summary,
    model_fits_to_summary,
    review_with_llm,
    gate,
)
from report_validator import Issue, ReportValidator, ModelFit  # noqa: F401
from typing import List
 
 
def review_with_llm_claude(narrative_text: str, tables_summary: str, **kwargs):
    """Alias que fuerza backend='claude', para el codigo que llamaba a la version original."""
    return review_with_llm(narrative_text, tables_summary, backend="claude", **kwargs)
 
 
def full_review(
    narrative_text: str,
    historical_table: dict,
    model_fits: List[ModelFit],
    use_llm: bool = True,
) -> List[Issue]:
    """Firma identica a la version original: siempre usa backend='claude'."""
    from llm_reviewer import full_review as _full_review
    return _full_review(narrative_text, historical_table, model_fits, backend="claude", use_llm=use_llm)
 
 
if __name__ == "__main__":
    print(__doc__)
