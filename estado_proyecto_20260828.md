ESTADO DEL PROYECTO BASS/GLM — 28/08/2026 (sistema production-ready + one-click pipeline)

HITOS
Netflix CERRADO (24/08): Fix 15-22, Gompertz R²=0.9973. Gemini 1 FP (Nota H).
Chatgpt RE-CERTIFICADO (25/08): Fix 15-24, GBM R²=0.9927. 0 blockers ambos.
Spotify CERTIFICADO (25/08): Fix 15-24+GLM-B, R&K R²=0.9990. Gemini 1 FP (fecha).
Smartphones CERTIFICADO (25/08): from scratch sin anchors, R&K R²=0.9873. 0 blockers 0 FPs.
IA CERTIFICADA (26/08): from scratch con fix de prosa cualitativa, R&K R²=0.9999. 0 blockers 0 FPs.
VR devices CERTIFICADA (26/08): Dual_Market R²=0.9997. 0 blockers 0 FPs.
Meta quest CERTIFICADA (26/08): VdB_Joshi R²=0.9957. 0 blockers 0 FPs.
Electric vehicles CERTIFICADA (28/08): from scratch via one-click pipeline, VdB_Joshi R²=0.9997. ALCANCE MÍNIMO validado (no truncamiento). Claude 0 blockers, Gemini 2 FPs doc.
Anthropic SALTADA: datos insuficientes (6 pts, 3 near-zero, MAPE=999%). Revisitar tras Fix 30.
DETERMINISMO LOGRADO (27/08): 7/293 diferencias (2.4%, cosmético). Groq determinista.
ONE-CLICK PIPELINE (28/08): generate_report.py funciona end-to-end. ALCANCE MÍNIMO resuelve truncamiento.

8 techs certificadas, 5 modelos ganadores distintos (Gompertz, GBM, R&K, Dual_Market, VdB_Joshi).

ARQUITECTURA VIGENTE
Extracción: Gemini + Google Search Grounding (MoE, 1 vez por tech, verificable).
Consenso: Groq / openai/gpt-oss-120b (temperature=0, determinista).
Corrector: Groq / openai/gpt-oss-120b (temperature=0, ALCANCE MÍNIMO — devuelve JSON de correcciones, no reescribe todo).
Reviewer loop: Groq / openai/gpt-oss-120b (temperature=0, determinista).
§6 RAG: Groq / openai/gpt-oss-120b (temperature=0). embed_content con Gemini (residual 7 líneas).
Backends: Gemini + Claude (validación cruzada).
Auto-retry: compilar_informe_global_con_retry (3 intentos).
One-click: python generate_report.py → extracción → limpieza → fit → compile → backends → greps → reporte.
§1-§4 determinista/BD (intocable por corrector). §5-§6 burbujas LLM sin números en prosa.
Fix 23: MODEL_EQUATIONS + model_labels (canonización tabla↔formulaciones).
Fix 26: MODEL_YEARS keyed by id (ASCII, fix Unicode).
Fix 27: fecha completa ({CURRENT_DATE}) en REVIEW_RUBRIC.
Fix 28: {current_date} en prompt de carta (ai/analysis.py).
Fix 33: temperature=0 en TODAS las llamadas LLM.
Fix 34: auto-retry (3 intentos).
ALCANCE MÍNIMO: corrector devuelve JSON de correcciones (find/replace), no reescribe el informe. Resuelve truncamiento en techs largas.
GLM-B: validate_series guard >= (rechazar año incompleto).
GLM-C: persist_fit.py TECH required (fail loud).
SDK: google.genai (migrado de google.generativeai).
Groq: ai/groq_client.py (openai/gpt-oss-120b, $0.15/$0.60 per 1M, 65K output, 500 T/SEC).

PIPELINE ONE-CLICK (generate_report.py)
python generate_report.py 
[1] ¿Existe en BD? → SÍ: limpiar 2026 + prosa vieja | NO: extraer Gemini+Grounding (guardar AMBOS outputs) 
[2] Verificar BD (monótona, sin 2026, ≥5 pts) 
[3] Fit (persist_fit.py desde GLM) 
[4] Compile (Groq, ALCANCE MÍNIMO, auto-retry) 
[5] Backends (gemini + claude) 
[6] Greps (Datos oficiales ≥2, ## 6, formulations, 1969) 
[7] Reporte final (usuario verifica y commitea)

FIXES COMPLETOS (15-34 + GLM-B/C + SDK + Groq + ALCANCE MÍNIMO + one-click)
15-22: stack base (burbs, bloques, taps, exenciones) · 23: MODEL_EQUATIONS · 24a/b: fecha+boundary · 26: MODEL_YEARS by id · 27: fecha en rubric · 28: fecha en carta · 29: (pendiente) insertar_historico_db DELETE · 30: (pendiente) revenue÷ARPU · 31: (pendiente) auto-residual · 32: generate_report.py one-click · 33: temperature=0 · 33b: seed=42 (no funciona en MoE) · 34: auto-retry · GLM-B: validate_series >= · GLM-C: persist_fit TECH required · SDK: google.genai · Groq: openai/gpt-oss-120b · ALCANCE MÍNIMO: corrector JSON corrections.

LECCIONES CRÍTICAS
Gemini MoE no es determinista ni con temperature=0 + seed=42. Solución: Groq (transformer estándar).
Antigravity NO cambia configuración (modelo, parámetros, API) sin aprobación explícita del usuario.
Antigravity propone diffs → exigir EJECUCIÓN, no construcción a mano.
Extracción SIEMPRE guarda AMBOS outputs (insertar_historico_db + guardar_analisis_cualitativo).
Prosa cualitativa vieja causa contradicciones si no se borra antes de recompilar.
insertar_historico_db NO borra antes de insertar (Fix 29 pendiente — causa duplicados).
El corrector NO debe reescribir el informe completo → ALCANCE MÍNIMO (JSON corrections).
pycache stale causa que Fix 26 y bloques deterministas no se apliquen — limpiar antes de compilar.
Groq Developer plan: solo openai/gpt-oss-120b y openai/gpt-oss-20b disponibles. Llama requiere Enterprise.
Blockers incluyen evidence (cita textual) para que el LLM identifique qué frase corregir.

CERTIFICADAS EN BD:
Netflix (Gompertz), Chatgpt (GBM), Spotify (R&K), Smartphones (R&K), IA (R&K), VR devices (Dual_Market), Meta quest (VdB_Joshi), Electric vehicles (VdB_Joshi).

BACKLOG
Fix 30: revenue ÷ ARPU fallback (para Anthropic y techs privadas). Mediano.
Fix 29: insertar_historico_db DELETE antes de INSERT (prevenir duplicados). Pequeño.
Fix 31: auto-residual (0.1M para pre-lanzamiento cuando trimming < 5 pts). Pequeño.
Cachear embeddings (embed_content) → 0 diferencias. Pequeño.
Fix 25: cache invalidación al cambiar prompt-rules. Diseño.
git push: ~25 commits ahead de origin.
Fix 24a hardening: inyección determinística de fecha. Bajo.

PROTOCOLO (vigente)
Commit ANTES de parche · Select-String DESPUÉS · Antigravity propone, usuario aplica y re-verifica · nada se da por aplicado sin verificación en disco · greps de artefacto pre-commit de cierre · py_compile · años hardcodeados prohibidos · git destructivo prohibido · LLM nunca entra a historical_adoption sin is_estimate · Python se edita en archivo, nunca en PowerShell · sin && · blocker verbatim → grep slug en repo completo · blocker non-verbatim → varianza LLM · diffs de Antigravity → exigir ejecución · extracción SIEMPRE guarda ambos outputs · borrar prosa cualitativa vieja antes de recompilar · limpiar pycache tras code changes · Antigravity NO cambia configuración sin aprobación · Groq tier de pago para el corrector · corrector usa ALCANCE MÍNIMO (JSON corrections, no full rewrite).
