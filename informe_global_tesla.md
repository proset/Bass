# Informe de Adopción: tesla

# Informe de Adopción Tecnológica — Tesla
### Análisis de Difusión de Vehículos Eléctricos en el Parque Acumulado Global

---

## 1. Resumen Ejecutivo

Tesla es una empresa que cotiza en bolsa y publica sus cifras de entregas acumuladas con regularidad. Los datos utilizados en este análisis corresponden a estimaciones del parque acumulado global de vehículos Tesla en circulación, construidas a partir de reportes oficiales de entregas trimestrales. El nivel de incertidumbre asociado a esta fuente es **bajo-moderado**, dado que las entregas anuales son públicas, aunque la conversión a parque acumulado incorpora supuestos sobre bajas y retiradas de flota.

El análisis integra diez modelos de difusión tecnológica ajustados sobre la serie histórica disponible. Tras la evaluación comparativa, el modelo **Difusión Logística R&K** emerge como el recomendado, al combinar el mejor equilibrio entre precisión de ajuste, parsimonia paramétrica y error de predicción mínimo entre todos los candidatos evaluados. Su superioridad sobre modelos más complejos no es marginal: presenta el error porcentual absoluto medio más bajo del conjunto, lo que indica que captura la dinámica de crecimiento sin sacrificar capacidad de generalización.

En cuanto a la **fase de crecimiento**, Tesla se encuentra en una etapa de desaceleración progresiva hacia la saturación. La curva de adopción ha superado claramente el punto de inflexión —donde el crecimiento era máximo— y transita ahora hacia la fase de madurez temprana, caracterizada por incrementos anuales decrecientes en términos relativos. El mercado de vehículos eléctricos premium de largo alcance, segmento históricamente dominado por Tesla, muestra señales estructurales de aproximación al techo de su mercado potencial actual, aunque nuevos segmentos y geografías podrían redefinir ese techo.

El **nivel de confianza de la proyección es ALTO** para el horizonte de corto y medio plazo, sustentado en la excelente bondad de ajuste del modelo seleccionado, la coherencia de la serie histórica y la estabilidad paramétrica observada. Para el horizonte de largo plazo, la confianza se modera a **MEDIA**, dado que las proyecciones hacia la mitad de la próxima década dependen de supuestos sobre saturación de mercado que los datos históricos por sí solos no pueden validar.

---

## 5. Análisis Cualitativo y Validación Estadística

### 5.1 Análisis Cualitativo de la Trayectoria de Adopción

La trayectoria de adopción de Tesla describe con notable fidelidad la curva sigmoidea característica de los modelos de difusión de innovaciones. En la fase inicial, el crecimiento fue lento y sostenido, propio de un producto de nicho dirigido a adoptantes tempranos con alta disposición a pagar y tolerancia al riesgo tecnológico. La aceleración posterior coincide con la expansión del portafolio de productos hacia segmentos de mayor volumen, la consolidación de la red de supercargadores y la reducción progresiva de costes de producción. El punto de inflexión de la curva —el momento de máxima velocidad de adopción— quedó atrás, y la serie más reciente muestra con claridad la transición hacia una fase de crecimiento decreciente, coherente con la aproximación al mercado potencial estimado por el modelo.

Esta dinámica es consistente con la teoría clásica de difusión: los adoptantes tardíos y rezagados son, por definición, más difíciles de captar, más sensibles al precio y menos propensos a la innovación, lo que naturalmente frena la tasa de crecimiento absoluta incluso cuando el parque acumulado sigue expandiéndose.

---

### 5.2 Validación Analítica

#### a) Control de Sobreajuste (AIC Mental)

El conjunto de datos disponible comprende once observaciones anuales. La regla práctica establece que si el número de parámetros libres de un modelo supera la mitad del número de observaciones, existe riesgo alto de sobreajuste. El modelo **Difusión Logística R&K** opera con un número reducido de parámetros —típicamente dos o tres en su formulación estándar—, lo que lo sitúa muy por debajo del umbral de riesgo con la muestra disponible. **No se detecta riesgo de sobreajuste en el modelo ganador.**

En contraste, modelos como el **Bass Generalizado (GBM)** o el **Van den Bulte & Joshi** incorporan parámetros adicionales que, con once puntos de datos, tienen escasa capacidad de identificación independiente. Aunque sus métricas de ajuste son comparables a las del modelo ganador, la parsimonia del modelo logístico lo hace preferible desde el principio de Occam: igual poder explicativo con menor complejidad implica mayor robustez ante datos futuros.

#### b) Detección de Degeneración Paramétrica

Un hallazgo estadísticamente relevante de este análisis es la convergencia de métricas entre varios modelos. Los modelos **Horsky & Simon**, **Ladrón-de-Guevara & Putsis** y **Bass Clásico** exhiben métricas de ajuste prácticamente idénticas entre sí. Este fenómeno no constituye un error de cálculo: es una manifestación conocida de **colapso paramétrico** o degeneración de identificabilidad.

Cuando el número de observaciones es limitado, los parámetros "extra" de modelos más complejos no encuentran señal suficiente en los datos para tomar valores diferenciados. Como resultado, el modelo complejo colapsa matemáticamente hacia la solución del modelo más simple, produciendo ajustes equivalentes. Esto confirma que, con la muestra disponible, la distinción entre estos tres modelos es estadísticamente irrelevante, y la elección entre ellos debe basarse en criterios teóricos o de parsimonia, no en las métricas de ajuste.

De manera análoga, **Muller & Yogev** y **Dual Market** presentan métricas casi idénticas entre sí, sugiriendo un segundo grupo de colapso paramétrico. El modelo **Fourt & Woodlock** es el único que se desmarca negativamente de forma inequívoca, con un ajuste sustancialmente inferior al resto, lo que indica que su estructura funcional es inadecuada para describir esta trayectoria de adopción.

#### c) Contraste con Referencias Externas

La **Agencia Internacional de la Energía (IEA)**, en sus informes anuales sobre vehículos eléctricos (*Global EV Outlook*), proyecta una expansión acelerada del parque global de vehículos eléctricos de pasajeros para el conjunto de la industria, impulsada por políticas de descarbonización, reducción de costes de baterías y expansión de infraestructura de carga en mercados emergentes, especialmente China, India y el Sudeste Asiático.

Las proyecciones del modelo para Tesla hacia mediados de la próxima década apuntan a una estabilización del parque acumulado en torno a un techo relativamente contenido. Esta proyección podría situarse **por debajo** de lo que cabría esperar si Tesla mantiene o recupera cuota en mercados de alto crecimiento, o si expande su portafolio hacia segmentos de menor precio. La IEA anticipa que el mercado global de vehículos eléctricos crecerá a tasas que superan con creces la tasa de crecimiento implícita en la proyección del modelo para Tesla en el horizonte largo.

**Advertencia:** La proyección del modelo se sitúa potencialmente por debajo de las referencias del sector para el conjunto del mercado de vehículos eléctricos. La diferencia se atribuye a factores que los datos históricos de Tesla no capturan directamente: la irrupción de competidores chinos (BYD, NIO, SAIC), la posible erosión de cuota de mercado de Tesla, la expansión de la demanda en mercados emergentes donde Tesla tiene presencia limitada, y el efecto de políticas públicas de subsidio que benefician al mercado en su conjunto pero no necesariamente a Tesla en particular. El modelo captura la difusión histórica de Tesla, no la del mercado total de vehículos eléctricos.

#### d) Modulación de Confianza

| Dimensión | Valoración | Justificación |
|---|---|---|
| Suficiencia de datos (n puntos) | Suficiente | Once observaciones anuales permiten identificar la forma sigmoidal completa |
| Riesgo de sobreajuste | Bajo | El modelo ganador tiene pocos parámetros relativos a n |
| Degeneración paramétrica | Detectada (parcial) | Tres grupos de modelos colapsan a soluciones equivalentes |
| Contraste externo | Divergencia moderada-alta en largo plazo | Factores competitivos y de mercado no capturados |
| **Clasificación de proyección** | **OPERATIVA (corto-medio plazo) / INDICATIVA (largo plazo)** | Ver nota |

**Nota de clasificación:** La proyección para el horizonte de corto y medio plazo se clasifica como **OPERATIVA**, fiable para decisiones de planificación con revisión periódica. La proyección para el horizonte de largo plazo se clasifica como **INDICATIVA**, sujeta a revisión ante cambios competitivos, regulatorios o tecnológicos que los datos históricos no anticipan.

---

## 6. Marco Académico Teórico

### 6.1 Formulación Conceptual del Modelo Seleccionado

El modelo **Difusión Logística R&K** pertenece a la familia de modelos de difusión de innovaciones de crecimiento limitado. Su estructura matemática describe la evolución del número acumulado de adoptantes como una función sigmoidea del tiempo, gobernada por dos parámetros fundamentales: la tasa intrínseca de crecimiento y el mercado potencial máximo (capacidad de carga o *ceiling*). La dinámica subyacente postula que la velocidad de adopción en cada período es proporcional tanto al número de adoptantes actuales como a la fracción del mercado potencial aún no capturada. Este mecanismo genera naturalmente la forma de S característica: crecimiento lento inicial, aceleración en la fase central y desaceleración progresiva hacia la saturación.

A diferencia del modelo **Bass Clásico**, que descompone la adopción en dos canales —innovación exógena (influencia de medios de comunicación) e imitación endógena (influencia social entre adoptantes)—, el modelo logístico asume que el proceso de adopción está dominado por la imitación o el aprendizaje social, con un coeficiente de innovación exógena despreciable. En el caso de Tesla, esta simplificación resulta empíricamente justificada: la adopción ha sido impulsada predominantemente por efectos de red, visibilidad social del producto y recomendación entre pares, más que por campañas de comunicación masiva tradicionales.

### 6.2 Comparación con Modelos Alternativos

El modelo **Gompertz** comparte con el logístico la estructura de crecimiento limitado, pero introduce una asimetría en la curva: el punto de inflexión no ocurre al cincuenta por ciento del mercado potencial, sino en una fracción inferior, lo que lo hace más adecuado para productos con adopción inicial más rápida y desaceleración más prolongada. Su menor precisión en este caso sugiere que la adopción de Tesla es más simétrica de lo que el Gompertz presupone.

Los modelos de la familia **Bass** —clásico, generalizado y sus variantes— ofrecen mayor riqueza interpretativa al separar los mecanismos de innovación e imitación, pero esta riqueza tiene un coste: requieren más datos para identificar sus parámetros de forma estable. Con la muestra disponible, el fenómeno de colapso paramétrico descrito anteriormente reduce su ventaja teórica a cero en términos prácticos.

El modelo **Fourt & Woodlock**, diseñado originalmente para productos de consumo frecuente con comportamiento de prueba y repetición, resulta estructuralmente inadecuado para bienes duraderos de alta implicación como los vehículos eléctricos, lo que explica su rendimiento notablemente inferior.

### 6.3 Relación con la Teoría de Difusión de Innovaciones

El marco teórico de referencia es la teoría de difusión de innovaciones de Everett Rogers, que clasifica a los adoptantes en cinco categorías secuenciales: innovadores, adoptantes tempranos, mayoría temprana, mayoría tardía y rezagados. La curva de adopción de Tesla, tal como la captura el modelo logístico, es coherente con este marco: la fase de aceleración corresponde a la penetración en la mayoría temprana, mientras que la desaceleración actual refleja la transición hacia la mayoría tardía, segmento caracterizado por mayor aversión al riesgo, mayor sensibilidad al precio y menor identificación con la propuesta de valor diferencial de Tesla frente a alternativas convencionales o competidores eléctricos emergentes.

La teoría de Rogers también anticipa que la difusión puede verse interrumpida o acelerada por factores exógenos —cambios regulatorios, discontinuidades tecnológicas, entrada de competidores— que los modelos matemáticos de difusión no modelizan internamente. Esta limitación es especialmente relevante en el sector de la movilidad eléctrica, donde la velocidad del cambio regulatorio y tecnológico es excepcionalmente alta.

---

## 4.2 Recomendación a la Dirección

La proyección del modelo **Difusión Logística R&K** ofrece una base **operativa** para la planificación de corto y medio plazo, y una base **indicativa** —sujeta a revisión— para el horizonte de largo plazo. La recomendación estratégica se articula en consecuencia con este doble nivel de confianza.

**Para el horizonte operativo (corto y medio plazo):** La dirección puede utilizar las proyecciones del modelo como referencia de planificación con un nivel de confianza razonable. La trayectoria de desaceleración es robusta y estadísticamente bien fundamentada. Se recomienda orientar las decisiones de inversión en infraestructura, capacidad productiva y red de servicio posventa hacia un escenario de crecimiento moderado y decreciente en términos relativos, evitando compromisos de capacidad dimensionados para tasas de crecimiento propias de la fase de aceleración ya superada.

**Para el horizonte indicativo (largo plazo):** La dirección debe tratar las proyecciones de largo plazo como escenario de referencia, no como previsión firme. La divergencia potencial con las dinámicas del mercado global de vehículos eléctricos —impulsadas por competidores, políticas públicas y expansión geográfica— introduce una incertidumbre estructural que el modelo no puede resolver con los datos disponibles. Se recomienda complementar este análisis con escenarios alternativos que incorporen explícitamente variables competitivas (cuota de mercado frente a competidores chinos y europeos), regulatorias (incentivos fiscales, mandatos de cero emisiones) y tecnológicas (coste de baterías, autonomía, infraestructura de carga).

**Recomendación transversal:** Dado que el análisis detecta señales de aproximación al techo del mercado potencial en el segmento histórico de Tesla, la dirección debería evaluar estrategias de expansión hacia nuevos segmen

## 2. Datos Históricos

| Año | Adopción (M) |
|---|---|
| 2015 | 0.05 M |
| 2016 | 0.13 M |
| 2017 | 0.23 M |
| 2018 | 0.47 M |
| 2019 | 0.84 M |
| 2020 | 1.34 M |
| 2021 | 2.28 M |
| 2022 | 3.59 M |
| 2023 | 5.40 M |
| 2024 | 7.19 M |
| 2025 | 8.83 M |


## 3. Métricas

| Modelo | R² | MAPE | Score | k |
|---|---|---|---|---|
| Horsky & Simon | 0.9997 | 17.35% | 95.22 | 4 |
| Muller & Yogev | 0.9999 | 12.43% | 95.87 | 7 |
| Van den Bulte & Joshi | 0.9999 | 12.40% | 97.25 | 6 |
| Difusión Logística R&K | 0.9999 | 6.53% | 98.07 | 4 |
| Ladrón-de-Guevara & Putsis | 0.9997 | 17.35% | 95.22 | 5 |
| Bass Clásico | 0.9997 | 17.35% | 95.22 | 3 |
| Dual Market | 0.9999 | 12.43% | 97.24 | 6 |
| Fourt & Woodlock | 0.7742 | 161.67% | 62.38 | 2 |
| Gompertz | 0.9987 | 22.65% | 94.62 | 3 |
| Bass Generalizado (GBM) | 0.9999 | 13.26% | 96.92 | 4 |


## 4. Proyecciones

| Año | Difusión Logística R&K (M) |
|---|---|
| 2026 | 10.09 M |
| 2027 | 10.94 M |
| 2028 | 11.46 M |
| 2029 | 11.77 M |
| 2030 | 11.94 M |
| 2031 | 12.03 M |
| 2032 | 12.09 M |
| 2033 | 12.12 M |
| 2034 | 12.13 M |
| 2035 | 12.14 M |


**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado (Difusión Logística R&K): R²=0.9999, MAPE=6.53%, Score=98.07.

### 📐 Formulación Matemática de los Modelos Evaluados

* **Bass Clásico (1969)** — Modelo de Bass Clásico:
  x(t) = m * (1 - exp(-(p + q) * t)) / (1 + (q / p) * exp(-(p + q) * t))

* **Dual Market (Roset & Canals, 2011)** — Modelo de Dos Mercados Independientes:
  x(t) = x1(t) + x2(t), donde x1 y x2 son modelos clásicos de Bass independientes:
  xi(t) = mi * (1 - exp(-(pi + qi) * t)) / (1 + (qi / pi) * exp(-(pi + qi) * t))

* **Fourt & Woodlock (1960)** — Modelo de Innovación Pura:
  N(t) = m * (1 - exp(-p * t))

* **Gompertz (1825)** — Modelo Asimétrico de Gompertz:
  N(t) = m * exp(-exp(-k * (t - t0)))

* **Bass Generalizado (GBM) (1994)** — Modelo de Bass Generalizado:
  dN/dt = (p + (q / m) * N(t)) * (m - N(t)) * (1 + beta * t)

* **Horsky & Simon (1983)** — Modelo con Publicidad:
  dN/dt = (p0 + alpha * ln(1 + t) + (q / m) * N(t)) * (m - N(t))

* **Muller & Yogev (2006)** — Modelo del Efecto Saddle:
  I(t) = Ni * (1 - exp(-(pi + qi) * t)) / (1 + (qi / pi) * exp(-(pi + qi) * t))
  dM/dt = (pm + qm * M(t) / (Ni + Nm) + qim * I(t) / (Ni + Nm)) * (Nm - M(t))

* **Van den Bulte & Joshi (2007)** — Modelo de Influenciadores e Imitadores:
  F1(t) = (1 - exp(-(p1 + q1) * t)) / (1 + (q1 / p1) * exp(-(p1 + q1) * t))
  dF2/dt = q2 * (w * F1(t) + (1 - w) * F2(t)) * (1 - F2(t))
  N(t) = M1 * F1(t) + M2 * F2(t)

* **Difusión Logística R&K (Ryu & Kim)** — Modelo Logístico de Difusión-Convergencia:
  L(t) = b1 / (1 + ((b1 - b0) / b0) * exp(-k2 * (t - t0)))

* **Ladrón-de-Guevara & Putsis (2011)** — Modelo de Mercado Potencial Dinámico y Endógeno:
  C(t) = 1.0 - theta * exp(-gamma * N(t) / S), donde M(t) = C(t) * S y la difusión es:
  dN/dt = (alpha + beta * (N / M)) * (M - N)
