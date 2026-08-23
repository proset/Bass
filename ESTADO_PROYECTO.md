ETADO DEL PROYECTO BASS/GLM — 24/08/2026 (CIERRE CHATGPT COMPLETADO)
🎯 HITO: CHATGPT CERRADO AL 100%
Primera corrida limpia de punta a punta en la historia del proyecto: GATE:True en 2 iteraciones, 0 blockers en Gemini Y Claude, y checklist de artefacto 7/7 (tablas intactas, §1 intacta, sin 400.00 M, sin 123.50, nota H presente, [ver tabla] solo en prosa narrativa). Logrado tras 8 corridas fallidas, 13 fixes con causa raíz identificada, y 1 reforma arquitectónica.

LA REFORMA ARQUITECTÓNICA (el aprendizaje central del proyecto)
"Narrativa sin cifras": el LLM escribe lenguaje; el código escribe hechos.

Prohibido escribir cifras de adopción (número + M/millones) en prosa narrativa — regla 0 en generador (analysis.py) y los 3 correctores (report_compiler).
Las cifras viven SOLO en: tablas deterministas, bullets "AÑO: valor" canonizados, y §1 (análisis cualitativo de BD, texto auditado, exento por diseño).
Stripper determinista v3 (strip_numeric_prose): línea a línea, exime tablas/bullets/§1/notas, no consume saltos; fuga de cifra → [ver tabla].
Canonización por VALOR (fix_bullet_values): todo bullet histórico con valor ≠ serie se reescribe con el valor real.
Check determinista cifra_en_prosa (report_validator): cifra en prosa = BLOCKER — la corrección ya no depende del humor del revisor LLM.
Revisor: categoría 6 ELIMINADA + NOTA DE DISEÑO en rubric (la ausencia de cifras ES el diseño; los pesos del score son parámetros, no métricas).
Por qué: análisis forense de 8 corridas mostró que el 100% de los blockers persistentes eran LLMs/taps/compitiendo por teclear números (transcripción, no razonamiento). Cada fix desplazaba el error; la arquitectura lo elimina por clase. Las métricas del modelo nunca estuvieron en duda — el motor GLM es 100% determinista y quedó intocado.

COMPLETADO (commiteado y pusheado)
Cierre chatgpt: corrida final GATE:True iter 2 + backends 0 blockers + greps de artefacto 7/7 + commit de cierre.
Fixes 1-10 (sesión 22-23/08): nota "prácticamente idénticas" · canonical block en generador · force_consenso · canonical block dinámico con fallback no-vacío · rangos de años dinámicos en correctores · regla 2 generador → score compuesto · Score visible para el revisor (ModelFit.score) · taps deterministas · año propio en consenso_inconsistente · años clave dinámicos (+5/+10) en year_value_swap · regla ALCANCE MÍNIMO del corrector.
Fix 11-13 + reforma: stripper v2→v3 (lección: v1 destruyó tablas — GATE:True ≠ informe intacto) · pesos del score fuera de prosa · cat-6 eliminada · Fix 13a: check_recommendation_vs_mape desactivado — el blocker "inmortal" de 3 diagnósticos era un CHECK DETERMINISTA zombi (~25 falsos positivos), no el LLM · Fix 13b: canonización de bullets por valor.
Fix 9 (pat_rev/pat_paren) DESACTIVADO por vandalismo: los patrones año-antes-del-valor machacaban valores de años futuros ("700→700 en 2030"). Quedan comentados; el forward original sigue activo y vigente.
PENDIENTE INMEDIATO — ARRANQUE DEL BARRIDO
Write-back del metadata (deuda obligatoria pre-barrido): last_hist_year queda en 2026 tras regenerar (debería ser 2025) → R2.5 dispara en cada corrida; hoy lo tapa force_consenso. Fix: escribir el metadata correcto tras regenerar consenso.
Netflix (primera del barrido, fuentes más auditables): auditoría de fuentes con plantilla del 21/08 (procedimiento chatgpt) → python persist_fit.py "netflix" → python -c "from data.report_compiler import compilar_informe_global; compilar_informe_global('netflix')" → greps de artefacto como checklist pre-commit ESTÁNDAR (adaptar los 7 de chatgpt a los valores de la serie: tablas intactas / bullet canonizado / sin cifras en prosa / [ver tabla] solo narrativo).
Spotify, luego las 4 restantes (anthropic, inteligencia artificial, meta quest, vr devices).
Nota: sin force_consenso tras arreglar el write-back — R2.5 auto-dispara al agregar años.
ROADMAP POSTERIOR
Consolidación Bass→GLM: fósiles (grep proyecto-wide 2031|2036), adc.py/generate_and_validate.py muertos, _label_map Dual Market, fallback_consenso (R² ajeno + "7 modelos").
Fase 6: PROVIDERS dict → google.generativeai DEPRECADO (FutureWarning en cada corrida) → cliente OpenAI-compatible.
Endurecimientos opcionales: guardia do-no-harm del corrector (snapshot + revert si empeoran checks) · check redondeo pedante (198.5 vs 198.6) · Fase 2 de la reforma (plantillas {{VALOR}} — LLM escribe prosa, código rellena cifras: para cuando el SaaS pida prosa con look cuantitativo).
Duplicados de catálogo (chatgpt/chatgpi, iphone/smartphone, tablets×4) — limpieza para el SaaS.
PROTOCOLO (acumulado)
Commit ANTES de cada parche; Select-String DESPUÉS; Antigravity propone, el usuario aplica y re-verifica en su propio PowerShell (el reporte de Antigravity no es verificación).
NUEVA REGLA — greps de artefacto ANTES de todo commit de cierre: GATE:True no garantiza informe intacto (lección del commit prematuro con tablas destruidas). Checklist: tablas con valores reales / bullets canonizados / sin cifras en prosa / [ver tabla] solo narrativo.
Diseño de regex contra la frase REAL en disco, nunca de hipótesis (lecciones: pat_rev vandalizó por ventana laxa; stripper v1 destruyó tablas por \s*).
Antes de culpar al LLM, verificar qué es determinista: el blocker más inmortal del proyecto era un check en código. Diagnóstico de recurrencia: si un blocker es VERBATIM idéntico corrida tras corrida → grep su slug en report_validator.py.
f-strings verificados en toda inserción {var} · años hardcodeados prohibidos (derivar de la serie) · git destructivo prohibido · LLM nunca entra a historical_adoption sin is_estimate=true · Python se edita en archivo, nunca en PowerShell · sin &&.
CLAVES TÉCNICAS RÁPIDAS
t=0 en primer año (np.arange(len(df))) · quirk VdB_Joshi (w→param_p2, q→param_q2; rebuild_popt) · score = r2×70 + (100-mape_fit)×0.15 + (100-mape_bt)×0.15 − 12×max(0, k−(n−1)).
Arquitectura de capas: motor GLM (determinista) → tablas/canonical block (deterministas) → prosa LLM (sin cifras) → stripper + taps (deterministas) → validador (checks deterministas + revisor semántico con nota de diseño) → gate.
Doble tap actual = ceiling + fix_projection_increments + fix_historical_increments (forward) + fix_bullet_values + strip_numeric_prose (pat_rev/pat_paren desactivados).
compilar_informe_global(tech, force_consenso=False) — force para regenerar consenso a demanda.
Anclas dinámicas: +5/+10 desde último año real (2030/2035 para chatgpt).
Checks desactivados: check_recommendation_vs_mape (zombi). Checks nuevos: cifra_en_prose.
Tests: python test_backends.py gemini|claude (raíz de Bass).