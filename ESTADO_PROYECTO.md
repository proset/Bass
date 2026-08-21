ESTADO DEL PROYECTO BASS/GLM — 21/08/2026

COMPLETADO:
- Motor GLM validado (C:\Users\roset\GLM): 10 modelos, penalización DoF, 
  persist_fit.py con score/n_params/mape en BD
- Datos chatgpt depurados: serie 2021-2025 etiquetada fila a fila, 
  2026 profético eliminado
- Compilador reconstruido (C:\Users\roset\Bass): R1 (3 tandas) + R2 
  (4 sub-fases) + parches A-F — todo commiteado en GitHub (último: 54725b2)
- Golden test: convergencia GATE:True en 3 iteraciones (dos veces)
- Pipeline: carga → summary_rows con Score → selector por score → 
  canonical block completo → consenso auto-regenerado (R2.5) → 
  wrappers LLM → loop red-team (full_review/gate) → doble tap → guardado

PENDIENTE INMEDIATO (parche G):
- Las tablas del informe (métricas y proyecciones) renderizan solo 6 
  modelos hardcodeados — GBM (el ganador, score 94.97) NO aparece en 
  las tablas, por lo que el corrector alinea la recomendación con el 
  mejor visible (Bass Clásico, 94.49)
- Fix: localizar la lista fija de 6 modelos en report_compiler.py 
  (template o bucle de df_proj) y renderizar TODOS los modelos de 
  summary_rows/df_proj
- Verificar tras parchear: tabla con 10 modelos, GBM arriba, 
  recomendación textual = GBM, cifras 2030/2035 de su columna

ROADMAP DESPUÉS:
1. Barrido 6 tecnologías con filas-2026 (anthropic, IA, meta quest, 
   netflix, spotify, vr devices): persist_fit + auto-regeneración de 
   consensos obsoletos (R2.5 lo detecta solo)
2. Consolidación Bass→GLM (un proyecto)
3. Fase 6: capa abstracción LLM → GLM-4.7 (google.generativeai 
   deprecado — FutureWarning en cada corrida)
4. Conocidos/aceptados: colapso Bass≈Ladrón con series cortas; 
   .env ya excluido del repo; credenciales rotadas pendientes opcional

PROTOCOLO DE TRABAJO (lección del desastre):
- Commit antes de cada parche, verificación Select-String después
- Antigravity propone diffs, el usuario aplica y verifica
- Nada se da por aplicado sin verificación mecánica en disco
