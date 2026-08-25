ESTADO DEL PROYECTO BASS/GLM — 25/08/2026 (chatgpt + netflix CERRADOS)
HITOS
chatgpt CERRADO (23-24/08): GATE:True, backends 0, greps 7/7.
netflix CERRADO (24/08 tarde): GATE:True iter 3, Claude 0 blockers, tablas intactas, bloques deterministas verificados (Gompertz R²=0.9973). Gemini-backend: 1 falso positivo documentado (flaggea la Nota H de colapso paramétrico como "bug" — es diseño anunciado).
chatgpt RE-CERTIFICACIÓN PENDIENTE: sus §5/§6 aún llevan cifras pre-Fix-20 (0.9952, 7.82%, (2014), (1969)). Una corrida con Fix 20 lo deja al día. ES EL PRIMER PASO AL RETOMAR.
ARQUITECTURA VIGENTE ("burbujas" — Fix 20)
§1-§4 = territorio determinista/BD (intocable por el corrector: regla "SECCIÓN INTOCABLE" Fix 18).
§5-§6 = burbujas LLM: prohibición TOTAL de números en prosa (adopción, métricas, porcentajes, años de citación — reglas 0/8/9/10 en ai/analysis.py). Stripper v4 (strip_numeric_prose): solo aplica a burbujas, exime tablas/bullets-AÑO/blockquotes/notas.
Bloques deterministas "Datos oficiales (del motor)" insertados por código tras los headers de §5.1 y §6 (métricas del recomendado + líderes R²/MAPE + proyecciones 5/10y) — el dato entra al texto por sustitución determinista, jamás tecleado por LLM.
Corrector narrativo: regla 0 (no añadir cifras) + 0b (§1 intocable) + ALCANCE MÍNIMO (solo frases de blockers).
Revisor: cat-6 ELIMINADA + NOTA DE DISEÑO (la ausencia de cifras ES el diseño; pesos del score ≠ métricas; no marcar falta de valores numéricos).
Validador: check_numeric_prose (solo burbujas, patrones adopción+métricas+cita-años, con exención de bloques oficiales — Fix 22), anio_de_citacion_en_prosa, año-propio en consenso_inconsistente, años clave dinámicos +5/+10.
Taps activos: ceiling, fix_projection_increments, fix_historical_increments (forward), fix_bullet_values (canonización por VALOR), fix_delta_as_accumulated, fix_paper_ids, strip_numeric_prose. DESPEDIDOS por vandalismo: pat_rev/pat_paren (700→700), fix_citation_years (0.9973→0.1825).
FIXES 15-22 (24/08) — todos commiteados
15: anchors sin 2026 (claude/anthropic), guard _cy-1 anti-año-incompleto, anchors Netflix SEC 10-K · 16: MODEL_YEARS + líderes verificados en canonical_block + regla 9 · 17: conector &/y + fix_paper_ids (UUIDs) · 18: §1 intocable · 19: tap delta-como-acumulado (mató el 8.90M) · 20: burbujas + bloques deterministas (la estabilización mayor) · 21: test_backends.py parameterizado por tech · 22: fix_citation_years desactivado + exención bloques oficiales.

LECCIONES CRÍTICAS (protocolo nuevo)
Backends SIEMPRE con tech: python test_backends.py <backend> <tech> — estuvo hardcodeado a chatgpt y horas de "GATE:False de netflix" eran mediciones del archivo equivocado.
GATE:True del loop ≠ informe válido para backends: el loop valida pre-R2.4; los backends leen el archivo final (post-bloques). Ambos criterios, en ese orden.
Greps de artefacto ANTES de todo commit de cierre: tablas con valores reales · "Datos oficiales (del motor)" presente · sin cifras en prosa fuera de burbujas.
Blocker verbatim idéntico entre corridas = check determinista, no LLM → grep del slug en report_validator.py.
Ningún tap regex sobre texto con números legítimos ajenos (3 vandalizaciones lo demostraron).
Regex se diseña contra la frase REAL en disco (grep primero), nunca de hipótesis.
TUBERÍA DE DATOS (mapeada 24/08)
GLM = proyecto separado C:\Users\roset\GLM (persist_fit.py, models/fit_models.py — fit_and_rank/REGISTRY, models/rk4_solver.py, data/loaders.py — load_series_for_fit/validate_series/rebuild_popt). BD compartida Supabase.
Extracción verídica: Streamlit app.py → obtener_datos_y_analisis_ia (Gemini + Google Search Grounding) → ANCLAS_HISTORICAS sobrescriben (hitos verificados) → guard _cy-1 filtra filtra años incompletos → insertar_historico_db.
Netflix en BD: 2015-2025, 11 puntos (70.0→288.0M; 2024-2025 estimación Gemini, resto anchors SEC). Fit persistido vía Streamlit (no persist_fit): Gompertz recomendado.
GLM pendientes (confirmar/aplicar antes del barrido profundo): (A) DEFAULT_HISTORICAL_SOURCES tiene 2026 pre-mapeado en 8 techs — borrar; (B) validate_series no rechaza años futuros — añadir guard; (C) persist_fit.py TECH="chatgpt" hardcoded — parameterizar.
PENDIENTE INMEDIATO
Re-certificar chatgpt:
python -c "from data.report_compiler import compilar_informe_global; compilar_informe_global('chatgpt', force_consenso=True)"
→ python test_backends.py gemini chatgpt / python test_backends.py claude chatgpt
→ greps: tablas 57.0/700.0 intactas · "Datos oficiales (del motor)" · sin "400.00 M" · "prácticamente idénticas" presente → commit re-certificación.
Spotify: extracción (añadir anchors verificados a ANCLAS_HISTORICAS si se quiere máximo control; MAU trimestral público) → Streamlit botón inteligente o persist_fit → revisar serie en BD (monótona, sin 2026, ≥10 puntos) → compilar_informe_global('spotify') → backends con tech → greps → commit cierre.
anthropic, inteligencia artificial, meta quest, vr devices.
GLM gaps A/B/C; después: consolidación Bass→GLM, Fase 6 (google.generativeai deprecado), duplicados de catálogo SaaS.
PROTOCOLO (vigente)
Commit ANTES de parche · Select-String DESPUÉS · Antigravity propone, usuario aplica y re-verifica EN SU PowerShell · nada se da por aplicado sin verificación en disco · greps de artefacto pre-commit de cierre · f-strings verificados · años hardcodeados prohibidos · git destructivo prohibido · LLM nunca entra a historical_adoption sin is_estimate · Python se edita en archivo, nunca en PowerShell · sin && ·si un blocker es verbatim entre corridas: grep del slug en validador.
