# ESTADO DEL PROYECTO BASS/GLM — 27/08/2026 (sistema production-ready)

## HITOS
- Netflix CERRADO (24/08): Fix 15-22, Gompertz R²=0.9973. Gemini 1 FP documentado (Nota H).
- Chatgpt RE-CERTIFICADO (25/08): Fix 15-24, commit f95ddf0. GBM R²=0.9927. 0 blockers ambos backends.
- Spotify CERTIFICADO (25/08): Fix 15-24+GLM-B, commit b745f9f. R&K R²=0.9990. Gemini 1 FP documentado (fecha, pre-Fix 27).
- Smartphones CERTIFICADO (25/08): from scratch sin anchors, commit (informe_global_smartphones.md). R&K R²=0.9873. Extracción Gemini+Grounding sola (11 pts correctos). 0 blockers 0 FPs.
- IA CERTIFICADA (26/08): from scratch con fix de prosa cualitativa (guardar_analisis_cualitativo), commit 2076300. R&K R²=0.9999. 0 blockers 0 FPs.
- VR devices CERTIFICADA (26/08): commit 8184f92. Dual_Market R²=0.9997. 0 blockers 0 FPs. Cuarto modelo ganador distinto.
- Meta quest CERTIFICADA (26/08): commit (informe_global_meta quest.md). VdB_Joshi R²=0.9957. Quinto modelo ganador distinto. 0 blockers 0 FPs.
- Anthropic SALTADA: 6 pts (3 near-zero), MAPE=999%. Revisitar tras Fix 30 (revenue ÷ ARPU).
- DETERMINISMO LOGRADO (27/08): 7/293 diferencias (2.4%, cosmético). Pipeline production-ready.

## ARQUITECTURA VIGENTE
- Extracción: Gemini + Google Search Grounding (MoE, 1 vez por tech, verificable).
- Consenso: Groq / Llama 3.1 70B (temperature=0, determinista).
- Corrector: Groq / Llama 3.1 70B (temperature=0, determinista).
- Reviewer loop: Groq / Llama 3.1 70B (temperature=0, determinista).
- §6 RAG: Groq / Llama 3.1 70B (temperature=0, determinista). embed_content con Gemini (residual 7 líneas).
- Backends: Gemini + Claude (validación cruzada).
- Auto-retry: compilar_informe_global_con_retry (3 intentos, casi nunca se activa).
- §1-§4 = territorio determinista/BD (intocable por corrector).
- §5-§6 = burbujas LLM sin números en prosa (Fix 20 + stripper v4).
- Bloques deterministas "Datos oficiales (del motor)" tras headers §5.1 y §6.
- Fix 23: MODEL_EQUATIONS + model_labels (canonización tabla↔formulaciones, assertion de keys).
- Fix 26: MODEL_YEARS keyed by id (ASCII, fix Unicode accent issue).
- Fix 27: fecha COMPLETA ({CURRENT_DATE}) en REVIEW_RUBRIC (llm_reviewer.py).
- Fix 28: {current_date} en prompt de carta (ai/analysis.py L433).
- Fix 33: temperature=0 en TODAS las llamadas LLM (Gemini + Claude + Groq).
- Fix 34: auto-retry wrapper (compilar_informe_global_con_retry).
- GLM-B: validate_series guard >= (rechazar año en curso incompleto).
- GLM-C: persist_fit.py TECH required (fail loud sin argumento).
- SDK migrado: google.generativeai → google.genai (ai/gemini_client.py, data/report_compiler.py, report_generator.py). llm_reviewer.py era la referencia.
- Groq integrado: ai/groq_client.py (Llama 3.1 70B), review_with_groq en llm_reviewer.py, default del loop cambiado a "groq".

## FIXES COMPLETOS (15-34 + GLM-B/C + SDK migration + Groq integration)
15: anchors sin 2026 · 16: MODEL_YEARS + líderes · 17: conector &/y + fix_paper_ids · 18: §1 intocable · 19: delta-como-acumulado · 20: burbujas + bloques deterministas · 21: test_backends parameterizado · 22: exención bloques · 23: MODEL_EQUATIONS canonización · 24a: fecha dinámica §6 · 24b: regla 1b boundary · 26: MODEL_YEARS by id · 27: fecha completa en rubric · 28: current_date en carta · 29: (pendiente) insertar_historico_db DELETE · 30: (pendiente) revenue ÷ ARPU · 31: (pendiente) auto-residual · 32: (pendiente) one-click pipeline · 33: temperature=0 · 33b: seed=42 (no funciona en MoE) · 34: auto-retry · GLM-B: validate_series >= · GLM-C: persist_fit TECH required · SDK: google.genai migration · Groq: Llama 3.1 70B para el loop.

## LECCIONES CRÍTICAS (protocolo actualizado)
- Backends SIEMPRE con tech: python test_backends.py <tech>.
- GATE:True del loop ≠ informe válido para backends: ambos criterios, en ese orden.
- Greps de artefacto ANTES de todo commit de cierre.
- Blocker verbatim → grep del slug en el REPO COMPLETO (no solo report_validator.py — puede vivir en llm_reviewer.py).
- Blocker non-verbatim → varianza del LLM, no check determinista.
- Antigravity propone diffs → exigir EJECUCIÓN del render/diff, no construcción a mano.
- Gemini MoE es no-determinista incluso con temperature=0 + seed=42. Solución: Groq/Llama (transformer estándar, determinista).
- Extracción SIEMPRE guarda AMBOS outputs: insertar_historico_db + guardar_analisis_cualitativo.
- Prosa cualitativa vieja causa contradicciones si no se borra antes de recompilar (3er incidente con VR devices).
- insertar_historico_db NO borra antes de insertar (Fix 29 pendiente — causa duplicados).
- Cache de consenso en Supabase porta alucinaciones (fecha 2024-05-20, agrupamiento 2025-2026). force_consenso=True para certificación.
- MODEL_YEARS keyed by label tiene bugs de Unicode. Keyear por id (ASCII).
- Valores residuales (0.1M) para años pre-lanzamiento cuando trimming reduce < 5 pts.
- Python pycache puede servir versión stale — limpiar antes de compilar tras code changes.
- Groq free tier: 8,000 TPM limit — el corrector envía ~13,000 tokens. Necesita tier de pago.
- La extracción funciona SIN anchors para techs bien documentadas (smartphones: 11 pts correctos solo con Gemini+Grounding).

## TUBERÍA DE DATOS
- GLM = proyecto separado C:\Users\roset\GLM (sin .git). persist_fit.py (TECH required), models/fit_models.py (fit_and_rank/REGISTRY), data/loaders.py (load_series_for_fit/validate_series con guard >= /DEFAULT_HISTORICAL_SOURCES sin 2026).
- BASS = C:\Users\roset\Bass (con .git, ~20 commits ahead de origin). data/report_compiler.py (MODEL_EQUATIONS+model_labels+MODEL_YEARS por id+Groq corrector), llm_reviewer.py (REVIEW_RUBRIC con {CURRENT_DATE}+{CURRENT_YEAR}+Groq reviewer default), ai/gemini_client.py (SDK nuevo, Grounding), ai/groq_client.py (Llama 3.1 70B, temperature=0), ai/analysis.py (extracción Gemini+Grounding, consenso Groq), test_backends.py (Gemini+Claude backends), report_generator.py (SDK nuevo+Groq).

## CERTIFICADAS EN BD:
- chatgpt: 2015-2025, GBM.
- netflix: 2015-2025, Gompertz.
- spotify: 2015-2025, R&K.
- smartphones: 2015-2025, R&K (extracción from scratch sin anchors).
- IA: 2015-2025, R&K (extracción from scratch con fix de prosa cualitativa).
- vr devices: 2015-2025, Dual_Market.
- meta quest: 2018-2025, VdB_Joshi.

## DETERMINISMO:
- Consenso + Corrector + Reviewer + §6 RAG: Groq/Llama 3.1 70B, temperature=0, determinista.
- Extracción: Gemini+Grounding (MoE, 1 vez por tech, verificable).
- embed_content: Gemini (residual 7/293 líneas, cosmético).
- Auto-retry: 3 intentos, casi nunca se activa.
- Total: 7 diferencias (2.4%), todas en espaciado de tabla markdown.

## BACKLOG
- Cachear embeddings (embed_content) → 0 diferencias. Pequeño.
- Fix 30: revenue ÷ ARPU fallback (para Anthropic y techs privadas). Mediano.
- Fix 29: insertar_historico_db DELETE antes de INSERT (prevenir duplicados). Pequeño.
- Fix 32: generate_report.py (one-click pipeline: extracción→fit→compile→backends→greps→commit). Mediano.
- Fix 31: auto-residual (0.1M para pre-lanzamiento cuando trimming < 5 pts). Pequeño.
- Fix 25: cache invalidation al cambiar prompt-rules. Diseño.
- Fase 6: completar migración SDK (mayormente hecho, limpiar residuales). Bajo.
- git push: ~20 commits ahead de origin.
- Fix 24a hardening: inyección determinística de fecha (no prompt rule). Bajo.

## PROTOCOLO (vigente)
Commit ANTES de parche · Select-String DESPUÉS · Antigravity propone, usuario aplica y re-verifica EN SU PowerShell · nada se da por aplicado sin verificación en disco · greps de artefacto pre-commit de cierre · f-strings verificados (py_compile) · años hardcodeados prohibidos · git destructivo prohibido · LLM nunca entra a historical_adoption sin is_estimate · Python se edita en archivo, nunca en PowerShell · sin && · blocker verbatim → grep slug en repo completo · blocker non-verbatim → varianza LLM · diffs de Antigravity → exigir ejecución, no construcción a mano · extracción SIEMPRE guarda ambos outputs (insertar_historico_db + guardar_analisis_cualitativo) · borrar prosa cualitativa vieja antes de recompilar techs existentes · limpiar pycache tras code changes · Groq tier de pago para el corrector (necesita >8000 TPM).
