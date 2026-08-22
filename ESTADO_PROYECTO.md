ESTADO DEL PROYECTO BASS/GLM — 22/08/2026
COMPLETADO (todo commiteado y pusheado a GitHub)
Motor GLM validado (C:\Users\roset\GLM): 10 modelos de difusión,penalización DoF, multi-start, persist_fit.py persistescore/n_params/mape_ajuste/mape_backtest en BD.
Datos chatgpt depurados: serie 2021-2025 etiquetada fila a fila(source/metric_type/is_estimate), fila 2026 profética eliminada.
Compilador reconstruido (C:\Users\roset\Bass\data\report_compiler.py):R1 (3 tandas: fixes, selector, wrappers LLM) + R2 (4 sub-fases:summary_rows, llamadas, loop red-team, doble tap) + parches A-H.
Golden test final superado (corrida del 21/08): GATE:True en 2iteraciones, los 3 criterios verificados (tabla 10 modelos/GBM arriba94.97, recomendación textual GBM, cifras 4779.6/4978.2 = columna GBM).
Pipeline completo: carga BD → summary_rows con Score → selector porscore → canonical block completo por año → consenso auto-regenerado (R2.5)→ wrappers LLM → loop red-team (full_review/gate) → doble tap → guardado.
Parche H aplicado (22/08): nota metodológica automática cuando dosmodelos colapsan paramétricamente (métricas idénticas) — documentada enel informe tras la tabla de métricas.
Backends de revisión validados (22/08): Gemini y Claude ambosfuncionan (test_backends.py en la raíz de Bass). Credenciales OK.Ambos detectaron el mismo issue Bass≈Ladrón (validación cruzada delproblema conocido).
PENDIENTE INMEDIATO — CIERRE DE CHATGPT (2 fixes especificados)
La infraestructura está completa. La última corrida (post-parche H,22/08 tarde) introdujo 2 issues menores con fix ya diseñado:

FIX 1 — Redacción de la nota metodológica (1 palabra)
En report_compiler.py, bloque [PARCHE H], en methodology_note:CAMBIAR: "presentan métricas de ajuste idénticas."POR: "presentan métricas de ajuste prácticamente idénticas."(Motivo: el revisor detectó que a más decimales las métricas difierenlevemente; "idénticas" sobreafirma y genera un blocker nuevo.)

FIX 2 — Canonical block para el generador de consenso
El generador (ai/analysis.py::generar_consenso_pronostico_ia) NO recibeel canonical block: sus prompts (líneas ~389-425) llevan cifras deproyección pero NO la serie histórica completa ni la reglatotal-vs-incremento. Por ahí entró el error "400.00M en 2025" de laúltima corrida (citó el incremento 700−300=400 como si fuera elacumulado).Fix: añadir al prompt del generador, tras las cifras de proyección:

La serie histórica completa: - {año}: {valor}M por cada año real
La regla: "NUNCA cites un incremento anual como valor acumulado: elvalor de un año histórico es el acumulado de la serie, no ladiferencia con el año anterior. Ejemplo: si la serie dice 2025: 700M,la adopción acumulada de 2025 ES 700M, no 400M."
SECUENCIA DE CIERRE DE CHATGPT
Aplicar Fix 1 y Fix 2 (commit antes de cada uno)
python -m py_compile de ambos archivos + commit
Regenerar: python -c "from data.report_compiler import compilar_informe_global; compilar_informe_global('chatgpt')"
Verificar: nota metodológica presente y SIN "400.00 M" en el informe(Select-String -Path informe_global_chatgpt.md -Pattern "400.00 M"→ debe devolver vacío)
Re-test: python test_backends.py gemini / python test_backends.py claude
Commit final: "cierre chatgpt al 100%"
→ BARRIDO de las 6 tecnologías (ver roadmap)
ROADMAP POSTERIOR
Barrido de 6 tecnologías con filas-2026 proféticas (anthropic,inteligencia artificial, meta quest, netflix, spotify, vr devices):python persist_fit.py "<tech>" + el pipeline auto-regenera consensosobsoletos (R2.5 detecta metadata viejo solo). Auditoría de fuentes decada serie ANTES (plantilla: el procedimiento de chatgpt del 21/08).Empezar por netflix/spotify (fuentes públicas más auditables).
Consolidación Bass→GLM: un solo proyecto con el motor validado.
Fase 6: capa de abstracción LLM → GLM-4.7. El paquetegoogle.generativeai está DEPRECADO (FutureWarning en cada corrida).Diseño: PROVIDERS dict con base_url/model/key_env, clienteOpenAI-compatible.
Issues conocidos/aceptados: colapso paramétrico Bass≈Ladrón conseries de 5 puntos (nota metodológica lo documenta; se separa solocon más datos); rotación defensiva de credenciales Supabasependiente (opcional).
Duplicados de informes a consolidar (chatgpt/chatgpi, iphone/smartphone, tablets×4...) — limpieza de catálogo para el SaaS.
PROTOCOLO DE TRABAJO (lección del desastre del 20/08)
Commit ANTES de cada parche; verificación Select-String DESPUÉS.
Antigravity propone diffs; el usuario aplica y verifica en su PowerShell.
Nada se da por aplicado sin verificación mecánica en disco.
Comandos git destructivos (restore/checkout/reset) PROHIBIDOS salvoespecificación explícita.
La salida de un LLM jamás entra en historical_adoption sinis_estimate=true y source='Síntesis LLM'.
El código Python se edita en el ARCHIVO con el editor — NUNCA se pegaen PowerShell (el intérprete de comandos no entiende Python).
Los comandos && no funcionan en este PowerShell (versión antigua) —siempre en líneas separadas.
CLAVES TÉCNICAS RÁPIDAS
Convención temporal: t=0 en primer año de la serie (np.arange(len(df))).
Quirk BD: VdB_Joshi guarda w en param_p2; q2 en param_q2.Reconstrucción correcta: rebuild_popt() en GLM/data/loaders.py.
Selector: score = r2×70 + (100-mape_fit)×0.15 + (100-mape_bt)×0.15− 12×max(0, k-(n_obs-1)). Persistido en model_parameters.score.
El consenso se auto-regenera si metadata.last_hist_year ≠ último añode la serie (bloque R2.5 de report_compiler.py — lee el metadata dela BD original, no del texto en memoria que el selector ya limpió).
Validador: ReportValidator (determinista, con checks B3:check_totals_as_increments, check_year_value_swap) + revisión semánticaLLM (backend gemini o claude), orquestados porllm_reviewer.full_review(backend=...) + gate().
Generador de consenso: ai/analysis.py::generar_consenso_pronostico_ia(con recommended_model_key desde parche F — subordinado al motor).
model_labels (10 modelos) completo tras parche G — los modelos extintos(Tanny_Derzko, Steffens_Murthy) eliminados del dict.
Tests de backends: python test_backends.py gemini|claude (raíz de Bass).
Nota: el _label_map del parche F en analysis.py usa "Dual Market (Roset& Canals)" pero model_labels usa "Dual Market" — deuda menor, soloafecta si el motor recomendara Dual algún día (cae al fallback).