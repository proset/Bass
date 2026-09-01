ESTADO DEL PROYECTO BASS/GLM — 31/08/2026 (FINAL — BASS v2.2 production-ready)

RESUMEN EJECUTIVO
BASS v2.2 está COMPLETO y VALIDADO. Sistema one-command que genera informes de adopción tecnológica con análisis de calidad consultoría senior, por $0.06/tech en ~5 minutos. Pipeline + frontend + BD limpios y sincronizados. Proyecto cerrado.

ARQUITECTURA (DEFINITIVA — 3 roles)
Gemini: BUSCADOR      ($0.02) — extracción de datos via Google Search Grounding
GLM:    MATEMÁTICO    ($0.00) — fit de 10 modelos con curve_fit (Python, determinista)
Claude: ESCRITOR-ANALISTA ($0.04) — claude-sonnet-4-6, temperature=0, 1 llamada
Pipeline: python generate_report_v2.py <tech> → informe completo + validación.

LO QUE HAY AHORA
BD (limpiada 31/08 — 1.280 filas de basura eliminadas, backup JSON commiteado)
Tech	Puntos	Modelos	Nota
anthropic	11	10	Privada, anchors MAU (8/72/182M)
electric vehicles	11	10	Dual_Market R²=0.9997
instagram	15	10	R&K R²=0.9973, OPERATIVA
tesla	11	10	R&K R²=0.9999, escenarios 12.5-22.7M
zoom	11	10	GBM R²=0.9834 (spike COVID)
Backup completo en backup_historical_adoption.json (commiteado). Las 15+ techs v1 (Netflix, Spotify, etc.) se restauran desde ahí si se necesitan.

Pipeline (generate_report_v2.py)
[1/3] Gemini Flash + Grounding ($0.02) → datos + custom_anchors.json + contexto de mercado
[2/3] GLM persist_fit.py ($0.00) → 10 modelos, determinista, backtest (anti-sobreajuste)
[3/3] Claude claude-sonnet-4-6 temp=0 ($0.04) → análisis + 4 validaciones
Python ensambla: 6 tablas determinísticas + escenarios + formulaciones

Informe generado (estructura completa)
Sección	Genera	Contenido
§1 Resumen Ejecutivo	Claude	+ confianza ALTA/MEDIA/BAJA + NOTA FUENTE si privada
§3 Análisis de Mercado	Claude	drivers, competidores, barreras, tendencias (contexto Gemini + conocimiento)
§5 Validación Estadística	Claude	4 validaciones: AIC-sobreajuste, colapso paramétrico, contraste externo (IEA/Gartner), confianza OPERATIVA/INDICATIVA/TENTATIVA
§6 Marco Académico	Claude	Rogers aplicado al caso
§7 Recomendación	Claude	integrada al nivel de confianza
§2.1 Serie Histórica	Python	determinista
§2.2 Desviaciones por Modelo	Python	todos vs real
§2.3 Fuentes	Python	data lineage real/estimado
§3bis Métricas	Python	R²/MAPE/Score/k todos
§4.1 Proyecciones Todos	Python	10 modelos × 2026-2035
§4.2 Escenarios	Python	Conservador/Base/Optimista
📐 Formulaciones	Python	MODEL_EQUATIONS + MODEL_YEARS by id

Frontend (Streamlit — 3 pestañas)
📈 Proyecciones: gráfico consenso (mejor Score de BD) + histórico + proyección dashed hasta 2035 + zona sombreada. Multiselect 10 modelos, consenso SIEMPRE visible. Verificado con Tesla.
📊 Comparativa: multi-tech (tab_benchmarking adaptada a v2).
📄 Informe Global: renderiza informe_global_{tech}.md.
Sidebar: 🤖 Carga Inteligente (subprocess v2, spinner 5min, rerun/error) + CSV + Edición manual + Eliminar (todo conservado).
Ocultadas (comentadas, no borradas): tab_market, tab_scientific, tab_rag, tab_report.

Validación
python test_backends.py claude <tech>   → ESTÁNDAR (0/5 corridas con blockers en v2.x)
python test_backends.py gemini <tech>   → secundario (FPs semánticos conocidos, documentar)
Validación independiente (Claude replicó el fit "al decimal"): matemática correcta y reproducible. ✓

HISTORIA DEL PROYECTO (aprendizajes)
Fase	Fechas	Resultado
BASS v1 (Groq loop)	25-28/08	20+ fixes, 70% fiabilidad, whack-a-mole — REEMPLAZADO
Experimentos	29-30/08	Claude-todo: no reproducible (m=850↔1250). Claude-ext: N/A pre-lanzamiento, sin temp=0 en sonnet-5 — DESCARTADOS
BASS v2	30/08	Arquitectura 3 roles, validada (Anthropic, EV, Zoom)
v2.1	31/08	Claude-analista senior (4 validaciones en prompt) — FPs eliminados por auto-documentación
v2.2	31/08	Informes completos (6 tablas + mercado + escenarios) + frontend + limpieza BD

Lecciones críticas (10)
1. LLM correcto por rol: buscar ≠ calcular ≠ escribir. Gemini busca, Python calcula, Claude escribe.
2. Groq era determinista pero incorrecto — 20+ fixes compensaban sus limitaciones. Claude es determinista Y correcto: 0 fixes.
3. El fit SIEMPRE en Python (curve_fit), nunca en LLM — Claude-todo falló por matemática no reproducible.
4. Privadas sin datos: SimilarWeb es JavaScript → ningún buscador lo indexa → custom_anchors.json (usuario pone MAU verificado).
5. claude-sonnet-4-6 soporta temp=0; sonnet-5 no. Modelo correcto para determinismo.
6. El prompt correcto convierte a Claude en analista senior: 4 validaciones espontáneas, sin código extra.
7. El informe que documenta sus limitaciones elimina sus propios FPs (colapso explicado → reviewer no lo flaggea).
8. Score con backtest penaliza sobreajuste implícitamente (R²=1.0 + MAPE_bt=1209% = último).
9. Escenarios > cifra única: el rango Conservador/Optimista ES la información.
10. Whack-a-mole = arquitectura mal: si cada fix crea un problema nuevo, rediseñar, no parchear.

COMPONENTES CLAVE
generate_report_v2.py — pipeline one-command (v2.2)
models/analytical_projections.py — proyecciones (5 analíticas + RK4+NaN handling)
custom_anchors.json — anchors verificados (usuario edita JSON, no Python)
data/loaders.py — zero-filter guard (min 5 pts)
persist_fit.py (GLM) — TECH required (fail loud)
backup_historical_adoption.json — backup completo pre-limpieza

FIXES VIGENTES vs ELIMINADOS
Vigentes: 23 (MODEL_EQUATIONS), 26 (MODEL_YEARS by id), 29 (DELETE antes INSERT), 30b/30c (jerarquía + anchors JSON), zero-filter guard (ex-31), 35 (Grounding sin JSON mode), 36 (precisión .2f).
Eliminados (compensaban Groq-loop): 20/22, 24a/24b, 25, 27/28, 33/33b, 34, 37, 38/38b.

PROTOCOLO (vigente)
Commit ANTES de parche · Select-String DESPUÉS · Antigravity propone, usuario aplica y re-verifica EN SU PowerShell · py_compile tras editar · años hardcodeados prohibidos · git destructivo prohibido · Python se edita en archivo, nunca en PowerShell · sin && · Antigravity NO cambia modelo/config sin aprobación · extracción guarda ambos outputs · limpiar pycache tras code changes · API keys SOLO en env vars (nunca hardcodeadas) · consenso = Score BD, nunca texto LLM · Claude backend = estándar · GATEs: diffs + py_compile antes de correr.

BACKLOG (opcional — NO bloquea producción)
Regenerar techs v1 desde backup (python generate_report_v2.py <tech>)
Modo "solo análisis" (saltar extracción si ya hay ≥5 pts)
Borrar archivos muertos de vistas ocultas (grep imports primero, cuando estable)
Batch mode (lista de techs → loop)
SimilarWeb API pagada ($100+/mes) — eliminaría anchors manuales
Docker/deploy Streamlit
Verificar git push final

COMANDOS BÁSICOS
Pipeline:        python generate_report_v2.py <tech>
Validación:      python test_backends.py claude <tech>
Frontend:        python -m streamlit run app.py
Fit manual:      cd C:\Users\roset\GLM && python persist_fit.py <tech>
Anchors:         editar custom_anchors.json (raíz de BASS)
Backup BD:       backup_historical_adoption.json (en git)

CIERRE
De un sistema con 20+ fixes que fallaba cada tech nueva → BASS v2.2: $0.06/tech, 5 minutos, análisis de consultoría senior, validación estadística integrada, escenarios, data lineage, frontend interactivo, BD limpida con backup.

Proyecto cerrado. La lección más valiosa (punto 10): "si cada fix crea un problema nuevo, la arquitectura está mal — rediseñar, no parchear."