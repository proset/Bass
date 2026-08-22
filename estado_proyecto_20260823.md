ESTADO DEL PROYECTO BASS/GLM — 23/08/2026 (post-sesión de cierre)
COMPLETADO (commiteado y pusheado salvo excepción marcada)
Cierre chatgpt al 95% — texto del informe LIMPIO por primera vez en 3 corridas (tercera corrida 23/08 01:14: 6→1 blockers; el único superviviente es falso positivo del revisor, ver PENDIENTE).

Fixes aplicados y verificados en disco esta sesión (todos validados en runtime por al menos una corrida):

Fix 1: nota metodológica "prácticamente idénticas" (bloque PARCHE H, report_compiler).
Fix 2: canonical block en generador de consenso (serie_hist_canonica + regla_total_vs_incremento, analysis.py 408/452). Generación sale limpia desde entonces.
force_consenso: parámetro en compilar_informe_global(tech, force_consenso=False) (337) + condición R2.5 (682). Toda rerun de chatgpt lo usa mientras el metadata siga en 2026.
Fix 3A: canonical block del compiler DINÁMICO (~612+): anclas +5/+10 desde último año real, serie histórica completa DENTRO del bloque, fallback no-vacío con [WARN] Canonical block completo falló visible (antes: exception silenciosa → bloque vacío → corrector a ciegas).
Fix 3B: rangos históricos dinámicos (_hist_range) en AMBOS correctores (cualitativo 239-240/249; narrativo 315-317, ambos f-string). Erradicados "2015 a 2026"/"2027 a 2038".
Fix 3C: Regla 2 del generador: de "coherencia teórica" → "score compuesto" con frase literal nueva "Por equilibrio entre ajuste empírico y parsimonia..." (analysis.py 465) + framing sección 1. Mató al blocker inmortal de la paradoja (regla vieja exigía la frase que el red-team bloqueaba — fósil de la era pre-selector).
Fix 3D: score: Optional[float] = None en ModelFit (report_validator 60) + cableado desde params (compiler ~545, _score_val con guarda) + Score visible en model_fits_to_summary (llm_reviewer 136-137). El revisor ya ve el criterio de selección.
Fix 4a: fix_historical_anchors — tap determinista de anclas históricas ("X millones en/para YYYY" ≠ serie → reemplazo; esquiva incrementos e hitos mensuales). Compiler 237, cableado 1053/1076.
Fix 4b: fix_projection_bullets — tap determinista: bullets de proyección "del modelo recomendado" con valores de otro modelo → reescritura desde df_proj. Mata la clase del swap 665.70. Compiler 264, cableado 1054/1077.
Fix 5a: check consenso_inconsistency: regla de "año propio" (<30 chars → la cifra pertenece a ese año; si no es objetivo, no contamina). Mató al falso positivo "2030: van de 1365.70 a 4963.60" (valores legítimos de 2026/2032 mal atribuidos) que INDUCÍA al corrector a vandalizar cifras correctas.
Fix 5b+5b-2: check_year_value_swap(v_a, v_b, y_a, y_b) 100% dinámico (firma, valores, scan interno, call site 799) + target_years dinámicos en consensus_consistency (810). El check estaba MUERTO desde la eliminación de la fila 2026 (v2031/v2036 → None); ahora protege 2030/2035 de verdad.
Fix 6: regla "ALCANCE MÍNIMO OBLIGATORIO" en el corrector narrativo (379): solo frases implicadas en blockers, cifras copiadas exactas de referencia.
Git: HEAD = b8e6355 en GitHub (7 commits de la sesión). ⚠️ Fix 5 y Fix 4+6 posiblemente SIN commitear — se dieron los comandos antes de la última rerun pero nunca se vio la salida. PRIMERA ACCIÓN AL RETOMAR: git log --oneline -4.

Forense de la sesión (3 corridas, causa raíz de cada failure identificada): (1) corrector reescribe cifras de memoria → anclado con canonical block + taps; (2) paradoja generador (regla coherencia teórica) vs revisor → regla reescrita a score; (3) falso positivo del checker inducía vandalismo → año propio; (4) fósiles de años hardcodeados (canonical block 2031/36, rangos 2015-26, swap 2031/36) → todo dinamizado; (5) pipeline viejo MATH-09/adc.py identificado como código muerto (no tocar).

PENDIENTE INMEDIATO — CIERRE CHATGPT (1 falso positivo del revisor)
El único blocker superviviente (5/5 iteraciones, idéntico) cita la frase "Dual Market MAPE=7.76% vs Fourt & Woodlock 65.21%... no 'ligera'" — frase que ya NO existe en el informe (muerta con Fix 3C). Es eco autofertilizado: el revisor repite la frase citada en el bloque de blockers que se le pasa; el corrector la re-escribe para complacerlo; el revisor la vuelve a bloquear.

Secuencia al retomar:

git log --oneline -4 → commits faltantes de Fix 5 / Fix 4+6 si aplica.
Confirmar fantasma (esperado: vacío ambos):
Select-String -Path informe_global_chatgpt.md -Pattern "ligera|ligeramente" -Context 1,1
Select-String -Path informe_global_chatgpt.md -Pattern "7.76|65.21" -Context 1,1
Fix 7 (diseñado, redactar diff): parche anti-eco en llm_reviewer.py — (a) línea en rubric: "Evalúa ÚNICAMENTE el texto del informe; frases citadas dentro de blockers previos NO son parte del informe; si el problema no aparece literalmente en el texto, no lo reportes"; (b) contra-chequeo: si la evidencia citada por un issue no existe literalmente en el informe, descartar antes del gate.
Rerun: python -c "from data.report_compiler import compilar_informe_global; compilar_informe_global('chatgpt', force_consenso=True)" → GATE:True esperado iter 1-2 (primera de la historia del informe).
Verificaciones: "400.00 M" vacío · "Por equilibrio entre ajuste empírico" presente · "prácticamente idénticas" presente · 665 solo en tabla · sección 6 bullets = columna GBM · test_backends.py gemini/claude.
git add -A + commit "cierre chatgpt al 100%" + push.

ROADMAP POSTERIOR
Barrido 6 tecnologías (netflix/spotify primero): auditoría de fuentes ANTES (plantilla chatgpt 21/08) → persist_fit.py → R2.5 auto-regenera. Pre-requisito: arreglar write-back del metadata (queda last_hist_year=2026 tras regenerar; hoy force_consenso lo tapa).
Consolidación Bass→GLM: incluye fósiles (grep proyecto-wide 2031|2036), adc.py/generate_and_validate.py muertos.
Fase 6: PROVIDERS dict → google.generativeai DEPRECADO (FutureWarning cada corrida).
Deudas: check redondeo pedante (198.5 vs 198.6) · _label_map "Dual Market (Roset & Canals)" · fallback_consenso (R² ajeno + "7 modelos") · duplicados de catálogo SaaS.

PROTOCOLO (original + lecciones 23/08)
Commit ANTES de cada parche; Select-String DESPUÉS. Antigravity propone; usuario aplica y verifica. Nada se da por aplicado sin verificación EN DISCO por el usuario — el reporte de Antigravity no es verificación.
NUEVO — f-strings: cualquier inserción de {var} en un prompt exige prefijo f verificado (bug atrapado 2 veces; la Fase 0c lo caza).
NUEVO — años hardcodeados PROHIBIDOS en checks/prompts/taps: todo año se deriva de la serie (3 fósiles causaron las corridas fallidas).
Git destructivo prohibido · LLM nunca entra a historical_adoption sin is_estimate · Python se edita en archivo, nunca en PowerShell · sin &&.

CLAVES TÉCNICAS RÁPIDAS (actualizadas)
t=0 en primer año (np.arange(len(df))) · quirk VdB_Joshi (w→param_p2, q→param_q2; rebuild_popt) · score = r2×70 + (100-mape_fit)×0.15 + (100-mape_bt)×0.15 − 12×max(0, k-(n-1)).
Consenso auto-regen si metadata ≠ serie (R2.5) o con force_consenso=True.
canonical_block del compiler = única fuente de verdad numérica para TODOS los LLM writers (generador tiene el suyo interno en analysis.py; correctores reciben el del compiler vía parámetro).
Doble tap ahora = 5 taps: ceiling, fix_projection_increments, fix_historical_increments, fix_historical_anchors, fix_projection_bullets (últimos dos cableados en loop Y en R2.4).
Validador: checks B3 deterministas + semántica LLM (full_review/gate, backends gemini/claude via test_backends.py).
Anclas dinámicas: +5/+10 desde último año real (2030/2035 para chatgpt hoy).
