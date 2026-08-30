ESTADO DEL PROYECTO BASS/GLM — 26/08/2026 (3 techs certificados + backlog limpio)

HITOS
chatgpt RE-CERTIFICADO (25/08): Fix 15-24 stack, commit f95ddf0. GATE:True iter 2, gemini+claude 0 blockers. Modelo: GBM R²=0.9927 MAPE=10.52% Score=94.97.
netflix CERRADO (24/08): Fix 15-22, Gompertz R²=0.9973. Gemini 1 FP documentado (Nota H).
spotify CERTIFICADO (25/08): Fix 15-24+GLM-B, commit b745f9f. Modelo: Logistic_Diffusion_Convergence R²=0.9990 MAPE=2.81% Score=99.24. Gemini 1 FP documentado (fecha "futura" — pre-Fix 27).
smartphones CERTIFICADO (25/08): Fix 15-24+27+GLM-B, from scratch sin anchors. Modelo: Logistic_Diffusion_Convergence R²=0.9873 MAPE=4.15% Score=98.14. Extracción Gemini+Grounding sola (sin ANCLAS_HISTORICAS) produjo 11 puntos correctos (2500→5590M). Gemini+Claude 0 blockers 0 FPs. Primer tech con ambos backends limpios sin excepciones.
BACKLOG SWEEP (26/08): Fix 26+28+GLM-C+Cleanup. Commits 772a563/ee07e66/69f2c57. Working tree clean.

ARQUITECTURA VIGENTE ("burbujas" — Fix 20 + ampliaciones 24/26/27/28)
§1-§4 = territorio determinista/BD (intocable por el corrector: regla "SECCIÓN INTOCABLE" Fix 18). Incluye carta del Comité de Dirección (fecha dinámica via Fix 28).
§5-§6 = burbujas LLM: prohibición TOTAL de números en prosa (reglas 0/8/9/10 en ai/analysis.py). Stripper v4 (strip_numeric_prose): solo aplica a burbujas, exime tablas/bullets-AÑO/blockquotes/notas.
Bloques deterministas "Datos oficiales (del motor)" insertados por código tras los headers de §5.1 y §6 (métricas del recomendado + líderes R²/MAPE + proyecciones 5/10y) — el dato entra al texto por sustitución determinista, jamás tecleado por LLM.
Fix 23: MODEL_EQUATIONS (dict, key=ID canónico) + model_labels (dict, key=ID→label) alimentan AMBOS renderizadores (tabla de métricas + formulaciones). Invariante: label de model_labels es prefijo del header de formulación. Assertion de keys al inicio del loop.
Fix 26: MODEL_YEARS rekeyeado por ID (ASCII, no label) — fix del bug de Unicode (acentos en "Bass Clásico"/"Ladrón-de-Guevara" causaban lookup fallido). 10/10 modelos con año verificado.
Fix 24a: fecha dinámica en prompt de §6 (report_compiler.py). Fix 24b: regla 1b en corrector (boundary hist/proy).
Fix 27: fecha COMPLETA ({CURRENT_DATE}) inyectada en REVIEW_RUBRIC (llm_reviewer.py) — Gemini ya no flaggea la fecha del informe como "futura".
Fix 28: {current_date} inyectado en prompt de carta (ai/analysis.py L433) — el LLM no alucina fechas stales en la carta del Comité de Dirección.
GLM-B: validate_series guard con >= (rechaza año en curso incompleto, no solo futuro). Espejo del _cy-1 del Streamlit.
GLM-C: persist_fit.py TECH required (fail loud sin argumento, no default silencioso "chatgpt").
Corrector narrativo: regla 0 (no añadir cifras) + 0b (§1 intocable) + ALCANCE MÍNIMO (solo frases de blockers) + regla 1b (no agrupar hist+proy).
Revisor (llm_reviewer.py): REVIEW_RUBRIC con {CURRENT_YEAR}+{CURRENT_DATE} dinámicos. cat-6 ELIMINADA + NOTA DE DISEÑO (ausencia de cifras = diseño). Backend y loop comparten el mismo rubric (test_backends.py importa full_review de llm_reviewer.py).
Validador: check_numeric_prose (solo burbujas, exención bloques oficiales Fix 22), anio_de_citacion_en_prosa, contradiccion_numerica_entre_secciones, razonamiento_cualitativo_inconsistente (LLM-judged, no determinista).
Taps activos: ceiling, fix_projection_increments, fix_historical_increments, fix_bullet_values, fix_delta_as_accumulated, fix_paper_ids, strip_numeric_prose.
Taps DESPEDIDOS por vandalismo: pat_rev/pat_paren (700→700), fix_citation_years (0.9973→0.1825).

FIXES COMPLETOS (15-28 + GLM-B/C)
15: anchors sin 2026, guard _cy-1 · 16: MODEL_YEARS + líderes en canonical_block · 17: conector &/y + fix_paper_ids · 18: §1 intocable · 19: tap delta-como-acumulado · 20: burbujas + bloques deterministas · 21: test_backends parameterizado · 22: fix_citation_years desactivado + exención bloques · 23: MODEL_EQUATIONS + model_labels canonización tabla↔formulaciones + assertion · 24a: fecha dinámica §6 · 24b: regla 1b corrector · 26: MODEL_YEARS keyed by id (Unicode fix) · 27: fecha completa en REVIEW_RUBRIC · 28: current_date en prompt de carta (ai/analysis.py) · GLM-B: validate_series >= · GLM-C: persist_fit TECH required.

LECCIONES CRÍTICAS (protocolo actualizado)
Backends SIEMPRE con tech: python test_backends.py <tech>.
GATE:True del loop ≠ informe válido para backends: el loop valida pre-R2.4; los backends leen el archivo final (post-bloques). Ambos criterios, en ese orden.
Greps de artefacto ANTES de todo commit de cierre.
Blocker verbatim entre corridas → grep del slug en el REPO COMPLETO (no solo report_validator.py — puede vivir en llm_reviewer.py).
Blocker NON-verbatim entre corridas → varianza del LLM, no check determinista. No perseguir cada blocker individual — fixear los underlying issues reales.
Antigravity propone diffs → exigir EJECUCIÓN del render/diff, no construcción a mano. (R2 hand-constructed era mentiroso — la ausencia de un valor lo delató.)
Gemini no sabe la fecha actual (cutoff ~2024). Fix 27 (fecha completa en rubric) resuelve FPs de "fecha futura" tanto en el informe como en citas académicas.
El LLM alucina fechas en cartas/documentos formales si el prompt no se las da. Fix 28 las inyecta.
Cache de consenso en Supabase porta alucinaciones (fecha 2024-05-20, agrupamiento 2025-2026). force_consenso=True regenera, pero el cache solo valida staleness de metadata, no calidad de contenido. (Fix 25 pendiente.)
MODEL_YEARS keyed by label tiene bugs de Unicode (acentos composed vs decomposed). Keyear por id (ASCII) es la solución de raíz.
validate_series tenía > en vez de >= (un caracter). Misma clase que el hardcode "2024" del rubric.
persist_fit tenía default silencioso "chatgpt" — mismo ADN que el hardcode de test_backends que costó horas.
La extracción (Gemini+Grounding) funciona SIN anchors para techs bien documentadas (smartphones). Los anchors son defensa, no requisito.
Regex se diseña contra la frase REAL en disco (grep primero), nunca de hipótesis. Ningún tap regex sobre texto con números legítimos ajenos.
Ningún año hardcodeado: todo dinámico (datetime / _cy).

TUBERÍA DE DATOS (mapeada y validada 26/08)
GLM = proyecto separado C:\Users\roset\GLM (sin .git). persist_fit.py (TECH required), models/fit_models.py (fit_and_rank/REGISTRY), models/rk4_solver.py, data/loaders.py (load_series_for_fit/validate_series con guard >= /DEFAULT_HISTORICAL_SOURCES sin 2026/rebuild_popt). BD compartida Supabase.
BASS = C:\Users\roset\Bass (con .git, 12 commits ahead de origin). data/report_compiler.py (MODEL_EQUATIONS+model_labels+MODEL_YEARS por id), llm_reviewer.py (REVIEW_RUBRIC con {CURRENT_DATE}+{CURRENT_YEAR}), report_validator.py, test_backends.py (importa full_review de llm_reviewer), ai/analysis.py (obtener_datos_y_analisis_ia con prompt de carta + {current_date}).
Extracción verídica: ai/analysis.py → obtener_datos_y_analisis_ia (Gemini + Google Search Grounding) → ANCLAS_HISTORICAS sobrescriben (si existen) → _aplicar_anclas filtra años incompletos (_cy-1) → insertar_historico_db.
VALIDADO: extracción sin anchors para smartphones = 11 puntos correctos (2500→5590M), 2026 filtrado, sin alucinaciones.

CERTIFICADOS EN BD:
chatgpt: 2015-2025, modelo GBM, Fix 15-24.
netflix: 2015-2025, modelo Gompertz, Fix 15-22.
spotify: 2015-2025, modelo Logistic_Diffusion_Convergence, Fix 15-24+GLM-B.
smartphones: 2015-2025, modelo Logistic_Diffusion_Convergence, extracción from scratch.

BACKLOG (out-of-scope, necesitan diseño)
Fix 25: invalidación de cache de consenso al cambiar prompt-rules (hash de prompt-rules en metadata? siempre force_consenso=True para certificación?).
Fix 24a hardening: inyección determinística de fecha (string replacement post-LLM, no prompt rule).
Fase 6: migrar google.generativeai → google.genai (FutureWarning visible en cada corrida).
git push: 12 commits ahead de origin. Push cuando haya punto estable.
GLM sin .git: GLM-B (validate_series >=) y GLM-C (persist_fit TECH required) están unversioned. Considerar init .git en GLM.

PENDIENTE INMEDIATO
Barrido profundo: anthropic, inteligencia artificial, meta quest, vr devices.
Precondiciones YA CUMPLIDAS:
Fix 27 (current_date en rubric) ✓
Fix 28 (current_date en carta prompt) ✓
GLM-B (validate_series >=) ✓
GLM-C (persist_fit TECH required) ✓
Fix 26 (MODEL_YEARS by id) ✓
Cleanup (.gitignore scratch) ✓

Secuencia por tech:
DELETE 2026 de la BD si existe (el guard >= fallará loud si no se hace).
python persist_fit.py <tech> (GLM, fail loud sin argumento).
compilar_informe_global('<tech>', force_consenso=True) (BASS).
python test_backends.py <tech> gemini / python test_backends.py <tech> claude .
greps de artefacto (valores del tech, "Datos oficiales" ≥2, formulaciones presentes, sin cifras en burbujas).
commit de cierre.

PROTOCOLO (vigente)
Commit ANTES de parche · Select-String DESPUÉS · Antigravity propone, usuario aplica y re-verifica EN SU PowerShell · nada se da por aplicado sin verificación en disco · greps de artefacto pre-commit de cierre · f-strings verificados (py_compile) · años hardcodeados prohibidos · git destructivo prohibido · LLM nunca entra a historical_adoption sin is_estimate · Python se edita en archivo, nunca en PowerShell · sin && · blocker verbatim → grep slug en repo completo · blocker non-verbatim → varianza LLM, fixear underlying issues · diffs de Antigravity → exigir ejecución, no construcción a mano · un fix = un commit · alcance mínimo.
