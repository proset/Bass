# ESTADO DEL PROYECTO BASS/GLM — 05/09/2026 (FINAL — v2.3 + Analogical Forecast + Benchmarking Mixto)

## RESUMEN EJECUTIVO
BASS está COMPLETO y validado de extremo a extremo: sistema autónomo ($0.10-0.15/análisis) que proyecta la adopción de CUALQUIER tecnología por tres rutas según sus datos (fit directo / analogía / espera honesta), compara tecnologías maduras con jóvenes en benchmarking mixto con confianza degradada, y nunca presenta ficción como proyección. El requisito original del SaaS ("dar una previsión sobre chatgpt") está cumplido: proyección por analogía con ±34% de error declarado, validada por backtest leave-one-out.

## ARQUITECTURA FINAL (3 rutas + comparación mixta)
```text
python generate_report_v2.py <tech>

EXTRACCIÓN (Gemini+Grounding, $0.02)
    ↓
CASCADA v2.3 (gate determinista → Claude juez → re-extracción quirúrgica con retry → rollback de invariantes → veredicto)
    ↓
┌─ MADURO (≥6 pts reales) ──→ fit GLM: 10 modelos compiten, backtest
│                              anti-sobreajuste, solver verificado
│                              (Fix 40-43 + test permanente Fix 42)
├─ YOUNG (3-5 pts) ─────────→ ANALOGICAL FORECAST (Fix 45-49):
│                              Claude clasifica (categoría/mercado_M/ritmo)
│                              → match por forma+ritmo vs catálogo de 191
│                              curvas (36 explosivas: WhatsApp/Facebook/...)
│                              → prior de techo p25/p50/p75 de los análogos
│                              → fit logístico con m FIJADO (2 params)
│                              → informe con ±34%/±48% declarado (backtest)
│                              → persistido como "Analogical_Forecast" en BD
├─ MUY JOVEN (<3 pts) ──────→ "DATOS INSUFICIENTES para analogía:
│                              mínimo 3 puntos, reintentar con más historial"
└─ BASURA/MUERTA ───────────→ INSERVIBLE honesto (sora, métrica rara)
    ↓
CLAUDE-ANALISTA (informe: 4 validaciones, confianza modulada)
```

## FRONTEND (Streamlit, 3 pestañas):
- 📈 Proyecciones — consenso por Score BD + multiselect modelos (analíticas o RK4 verificadas)
- 📊 Comparativa MIXTA (Fix 50) — maduras (fit) + jóvenes (analogía escenario base) EN LA MISMA comparación: métricas N/D-analogía, confianza truncada a TENTATIVA si hay analogía, asimetría explícita, prohibición de ganadores de precisión entre clases
- 📄 Informe Global
- Sidebar: carga inteligente + CSV + manual + eliminar (conservados)

## EL BACKTEST QUE VALIDÓ LA ANALOGÍA (FASE 1-3 del experimento)
| Método | MAPE 5y | MAPE 10y |
|---|---|---|
| C. Forma+ritmo (implementado) | 34.4% | 48.2% |
| B. Categoría | 39.4% | 67.1% |
| A. Persistencia | 59.6% | 83.9% |
| D. GM(1,1) | 47.4% | 257.8% (sin techo) |

Catálogo: 191 curvas OWID (por país) + redes sociales (MAU público) + hardware de consumo. Clasificador de ritmo calibrado (explosiva >5x año5/año2). Leave-one-out estricto. El match por forma derrotó incluso a la clasificación equivocada de Claude (anthropic clasificada "otra" aún matcheó Snapchat/WhatsApp/Facebook — la matemática es más robusta que la semántica).

## VALIDACIÓN COMPLETA (todas las rutas, evidencia en git)
| Ruta | Techs validadas |
|---|---|
| MADURO | tesla, instagram, EV-chinos, ozempic, coches-hibridos-toyota, midjourney |
| YOUNG→ANALOGÍA | chatgpt, gemini, anthropic, perplexity (WhatsApp/FB en análogos) |
| MUY JOVEN | grok, claude-code ("reintentar con más historial") |
| INSERVIBLE | sora (muerto), toyota (métrica indeterminada) |
| MIXTO (Fix 50) | EV vs anthropic vs chatgpt: TENTATIVA, inconmensurabilidad (usuarios vs coches) detectada por Claude, sin "líder indiscutible" |

## HISTORIA (5 días, 3 arquitecturas)
| Versión | Qué era | Fin |
|---|---|---|
| v1 (Groq loop) | 20+ fixes, 70% fiabilidad, whack-a-mole | Reemplazada — "si cada fix crea un problema, la arquitectura está mal" |
| v2.2 (3 roles) | Gemini busca / GLM calcula / Claude escribe | Base vigente |
| v2.3 | Cascada de verificación de datos | Vigente |
| Fix 40-43 | "Dos matemáticas" cerrada: monotonicidad interna, 3 modelos más a RK4, test permanente | Vigente |
| Fix 45-50 | Analogical Forecast + young-techs + benchmarking mixto | Vigente |

## LECCIONES CRÍTICAS (todas pagadas con evidencia)
- LLM correcto por rol: buscar ≠ calcular ≠ escribir (Gemini/GLM/Claude).
- El fit SIEMPRE en Python — LLM-matemática no es reproducible.
- Aproximaciones analíticas de modelos acoplados = ficción (4 bugs de la misma familia) → solver es la verdad, analítica solo si la reproduce exactamente (test permanente lo garantiza).
- La cascada: frescura (Gemini) × plausibilidad (Claude) cruzadas = precisión.
- Invariantes primero: corrección que rompe la serie se revierte.
- El floor de monotonicidad contra el dato real congela proyecciones — la monotonicidad es INTERNA del modelo.
- Con <6 puntos el techo es matemáticamente indeterminado → la analogía (36 curvas explosivas) es la solución validada (34.4% MAPE).
- El match por forma es más robusto que la clasificación semántica.
- Una comparación nunca es más fuerte que su dato más débil (regla del mínimo + truncado a TENTATIVA con analogía).
- Métricas incomparables (usuarios vs coches) → Claude declara inconmensurabilidad y se niega al ganador — el producto ES esa honestidad.
- Errores de red en re-extracción: retry (grok quedó sin corregir por un WinError 10054 no manejado).
- Anchors de custom_anchors.json deben aplicar como capa FINAL (la re-extracción puede pisarlos — bug abierto).

## COMPONENTES CLAVE
- `generate_report_v2.py` — pipeline 3 rutas (cascada + analogía + fit)
- `models/analogical_forecast.py` — match forma/ritmo, prior, fit m-fijado
- `models/analytical_projections.py` — 5 analíticas exactas + 5 RK4 verificados
- `tests/test_analytical_vs_solver.py` — invariante permanente (Fix 42)
- `data/catalog/curves.json` — 191 curvas (36 explosivas)
- `catalog_builder_v2.py` — constructor + clasificador de ritmo
- `ui/tab_benchmarking.py` — comparativa mixta con asimetría
- `custom_anchors.json` — datos verificados por humanos (pendiente capa final)
- `backup_historical_adoption.json` — backup pre-limpieza

## BACKLOG (nada bloquea producción)
- BUG ABIERTO: anchors pisables por re-extracción (aplicar como capa final)
- MAPE_backtest en tabla §3bis + peso en Score (16.12% hoy invisible)
- Ponderación del tramo reciente en la selección de ganador
- Regla anti-marca en extracción (toyota vs coches-hibridos-toyota)
- Fix escenarios (Conservador ≤ Base ≤ Optimista — invertidos en varios)
- Verificación de mejora en re-extracción (instagram empeoró una vez)
- Categorías finas del clasificador de analogía (compensado por el match)
- Regenerar informes v1 (Netflix, Spotify...) desde backup
- Batch mode / Docker / deploy / git push de cierre

## COMANDOS
- Pipeline: `python generate_report_v2.py <tech>`
- Benchmarking mixto: UI Streamlit → Comparativa (fit + analogía juntas)
- Validación: `python test_backends.py claude <tech>`
- Test invariante: `python tests/test_analytical_vs_solver.py`
- Frontend: `python -m streamlit run app.py`
- Anchors: `custom_orders.json` — editar valores verificados
- Catálogo: `data/catalog/curves.json` (rebuild: `catalog_builder_v2.py`)

## CIERRE
De "no puede predecir chatgpt" (invendible) a: chatgpt proyectado por analogía con 36 curvas explosivas, ±34% declarado, comparado contra techs maduras con Claude declarando la inconmensurabilidad y negándose a declarar un ganador.

El producto no promete predicciones perfectas — promete: proyección estadística cuando los datos lo permiten, analogía validada cuando no, espera honesta cuando aún no hay nada, y la frontera entre las tres siempre visible. ESE es el SaaS defendible.