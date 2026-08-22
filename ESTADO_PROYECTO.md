ESTADO DEL PROYECTO BASS/GLM — 21/08/2026
COMPLETADO (todo commiteado y pusheado a GitHub)
Motor GLM validado (C:\Users\roset\GLM): 10 modelos de difusión,penalización DoF, multi-start, persist_fit.py persistescore/n_params/mape_ajuste/mape_backtest en BD.
Datos chatgpt depurados: serie 2021-2025 etiquetada fila a fila(source/metric_type/is_estimate), fila 2026 profética eliminada.
Compilador reconstruido (C:\Users\roset\Bass\data\report_compiler.py):R1 (3 tandas: fixes, selector, wrappers LLM) + R2 (4 sub-fases:summary_rows, llamadas, loop red-team, doble tap) + parches A-F.Último commit: 54725b2.
Golden test superado: convergencia GATE:True en 3 iteraciones (dos veces).
Pipeline completo: carga BD → summary_rows con Score → selector porscore → canonical block completo por año → consenso auto-regenerado (R2.5)→ wrappers LLM → loop red-team (full_review/gate) → doble tap → guardado.
Parche G aplicado: model_labels con los 10 modelos — tablas completas,GBM visible, recomendación y cifras unificadas. Golden test final:GATE:True en 2 iteraciones, los 3 criterios verificados (tabla 10/GBMarriba, recomendación GBM, cifras 4779.6/4978.2 = columna GBM).
Verificación tras parchear:

Tabla de métricas con los 10 modelos, GBM arriba (94.97)
Tabla de proyecciones con columna GBM
Recomendación textual = GBM ("Bass Generalizado")
Cifras 2030/2035 del consenso = columna GBM de la tabla
Golden test: convergencia GATE:True
ROADMAP POSTERIOR
Barrido de 6 tecnologías con filas-2026 proféticas (anthropic,inteligencia artificial, meta quest, netflix, spotify, vr devices):python persist_fit.py "<tech>" + el pipeline auto-regenera consensosobsoletos (R2.5 detecta metadata viejo solo). Auditoría de fuentesde cada serie antes.
Consolidación Bass→GLM: un solo proyecto con el motor validado.
Fase 6: capa de abstracción LLM → GLM-4.7. El paquetegoogle.generativeai está DEPRECADO (FutureWarning en cada corrida).Diseño: PROVIDERS dict con base_url/model/key_env, cliente OpenAI-compatible.
Issues conocidos/aceptados: colapso paramétrico Bass≈Ladrón conseries de 5 puntos (se separa solo con más datos); rotación defensivade credenciales Supabase pendiente (opcional).
Duplicados de informes a consolidar (chatgpt/chatgpi, iphone/smartphone, tablets×4...) — limpieza de catálogo para el SaaS.
PROTOCOLO DE TRABAJO (lección del desastre del 20/08)
Commit ANTES de cada parche; verificación Select-String DESPUÉS.
Antigravity propone diffs; el usuario aplica y verifica en su PowerShell.
Nada se da por aplicado sin verificación mecánica en disco.
Comandos git destructivos (restore/checkout/reset) PROHIBIDOS salvoespecificación explícita.
La salida de un LLM jamás entra en historical_adoption sinis_estimate=true y source='Síntesis LLM'.
CLAVES TÉCNICAS RÁPIDAS
Convención temporal: t=0 en primer año de la serie (np.arange(len(df))).
Quirk BD: VdB_Joshi guarda w en param_p2; q2 en param_q2.Reconstrucción correcta: rebuild_popt() en GLM/data/loaders.py.
Selector: score = r2×70 + (100-mape_fit)×0.15 + (100-mape_bt)×0.15
12×max(0, k-(n_obs-1)). Persistido en model_parameters.score.
El consenso se auto-regenera si metadata.last_hist_year ≠ último añode la serie (bloque R2.5 de report_compiler.py).
Validador: ReportValidator (determinista, con checks B3:check_totals_as_increments, check_year_value_swap) + revisión semánticaLLM, orquestados por llm_reviewer.full_review() + gate().
Generador de consenso: ai/analysis.py::generar_consenso_pronostico_ia(con recommended_model_key desde parche F — subordinado al motor).