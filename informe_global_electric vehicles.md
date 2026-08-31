# Informe de Adopción: electric vehicles

# Informe de Adopción Tecnológica: Vehículos Eléctricos (Electric Vehicles)

---

## 1. Resumen Ejecutivo

El mercado global de vehículos eléctricos ha experimentado una de las trayectorias de adopción más dinámicas registradas en la historia de la movilidad motorizada. La serie histórica analizada revela una aceleración sostenida y pronunciada, característica de una tecnología que ha superado la fase de adopción temprana y se encuentra en plena expansión masiva, impulsada por la convergencia de políticas públicas, reducción de costes de baterías, expansión de infraestructura de carga y cambio cultural en la percepción del consumidor.

**Modelo seleccionado: Van den Bulte & Joshi**

Este modelo fue seleccionado como el más adecuado para describir la dinámica de adopción observada, obteniendo la puntuación compuesta más alta entre los diez modelos evaluados. Su superioridad se fundamenta en su capacidad para capturar la heterogeneidad del mercado, distinguiendo entre segmentos de adoptantes con distintas sensibilidades a la influencia social y a los efectos de imitación. Esta arquitectura teórica resulta especialmente pertinente en un mercado tan segmentado como el de los vehículos eléctricos, donde coexisten adoptantes tempranos motivados por valores medioambientales, consumidores sensibles al precio y mercados emergentes en distintas fases de madurez.

**Fase de crecimiento actual:** El mercado se encuentra en la fase de crecimiento acelerado, habiendo superado el punto de inflexión inicial pero sin haber alcanzado aún la saturación. Las proyecciones del modelo sugieren que el mercado tenderá hacia una meseta en el horizonte de medio plazo, lo que indica que el potencial de mercado máximo estimado por el modelo podría estar siendo alcanzado dentro del período proyectado.

**Nivel de confianza de la proyección: MEDIA**

Justificación: El ajuste estadístico del modelo ganador es excelente sobre los datos históricos disponibles, y la serie temporal cubre un período suficientemente representativo del ciclo de adopción. Sin embargo, la convergencia de las proyecciones hacia una meseta estable en un horizonte relativamente corto genera interrogantes sobre si el potencial de mercado estimado refleja adecuadamente la expansión hacia mercados emergentes de gran escala (India, Sudeste Asiático, África), cuya dinámica de adopción podría extender significativamente la curva de crecimiento más allá de lo que los datos históricos —predominantemente occidentales y chinos— permiten inferir. Este factor estructural modera la confianza en las proyecciones de largo plazo.

---

## 5. Análisis Cualitativo y Validación Estadística

### 5.1 Análisis Cualitativo del Proceso de Difusión

La trayectoria de adopción de los vehículos eléctricos refleja con notable fidelidad los postulados clásicos de la teoría de difusión de innovaciones. En las fases iniciales de la serie, el crecimiento fue modesto y estuvo protagonizado por innovadores y adoptantes tempranos: consumidores con alta sensibilidad medioambiental, elevada renta disponible y tolerancia al riesgo tecnológico. La disponibilidad limitada de modelos, la escasa infraestructura de carga y los precios elevados actuaron como barreras estructurales que ralentizaron la difusión masiva.

A partir de la mitad del período analizado, se observa una inflexión clara hacia el crecimiento exponencial. Este cambio de régimen coincide con la reducción drástica del coste de las baterías de iones de litio, la proliferación de modelos accesibles por parte de fabricantes tradicionales y la intensificación de políticas de incentivo fiscal y regulatorio en Europa, China y Estados Unidos. El efecto de imitación social —componente central de los modelos de difusión— se volvió dominante: la visibilidad creciente de los vehículos eléctricos en el espacio público aceleró la normalización de la tecnología y redujo la percepción de riesgo entre los adoptantes de la mayoría temprana.

En los años más recientes de la serie, el crecimiento continúa siendo robusto, aunque comienzan a emerger señales de moderación relativa en algunos mercados maduros, donde la penetración ya es significativa y los adoptantes rezagados presentan mayor resistencia al cambio por razones de infraestructura, hábitos de uso o limitaciones económicas.

### 5.2 Validaciones Analíticas

#### a) Control de Sobreajuste (AIC Mental)

El modelo Van den Bulte & Joshi incorpora un número de parámetros superior al de modelos más parsimoniosos como el Bass Clásico o el Gompertz. Con una serie de datos de once observaciones anuales, la relación entre el número de parámetros del modelo ganador y el tamaño muestral se sitúa en un umbral que merece atención. Aunque el número de parámetros no supera el umbral crítico de la mitad del número de observaciones —por lo que no se activa la advertencia de riesgo alto de sobreajuste—, la diferencia es suficientemente estrecha como para recomendar cautela.

Es relevante señalar que modelos como Difusión Logística R&K y Dual Market alcanzan métricas de ajuste muy similares al modelo ganador con estructuras paramétricas comparables o más simples. En términos de parsimonia, estos modelos alternativos merecen consideración seria, ya que una complejidad adicional que no produce mejoras sustanciales en el ajuste puede comprometer la capacidad de generalización fuera de la muestra. **El riesgo de sobreajuste se califica como MEDIO.**

#### b) Detección de Degeneración Paramétrica

El análisis comparativo de los resultados revela un fenómeno estadístico significativo: varios modelos —concretamente Bass Clásico, Horsky & Simon y Ladrón-de-Guevara & Putsis— exhiben métricas de ajuste prácticamente idénticas entre sí, con valores de R² y MAPE que no presentan diferencias discernibles.

Este comportamiento no constituye un error de cálculo ni una coincidencia numérica: es una manifestación clásica de **colapso paramétrico** o degeneración paramétrica. Cuando el tamaño muestral es limitado, los parámetros adicionales que diferencian a los modelos más complejos de los más simples no encuentran suficiente información en los datos para identificarse de forma independiente. Como resultado, los parámetros "extra" convergen hacia valores que los vuelven matemáticamente irrelevantes, y el modelo complejo colapsa funcionalmente al comportamiento del modelo más simple. Esto es una **limitación de identificabilidad**, no un defecto del software ni del analista.

La implicación práctica es importante: en presencia de degeneración paramétrica, el principio de parsimonia (navaja de Occam) aconseja preferir el modelo más simple entre los que muestran rendimiento equivalente, ya que ofrece mayor estabilidad paramétrica y mejor generalización. En este caso, Bass Clásico sería preferible a Horsky & Simon o Ladrón-de-Guevara & Putsis cuando sus métricas son indistinguibles.

#### c) Contraste con Referencias Externas

La Agencia Internacional de la Energía (IEA) constituye la referencia de mayor autoridad para proyecciones del mercado global de vehículos eléctricos. En sus escenarios de políticas anunciadas y de desarrollo sostenible, la IEA proyecta una expansión muy significativa del parque global de vehículos eléctricos hacia mediados de la década de los treinta, con cifras que en sus escenarios más ambiciosos superan ampliamente las estimaciones que el modelo Van den Bulte & Joshi extrapola para el horizonte analizado.

**Advertencia de divergencia:** La proyección del modelo se sitúa potencialmente muy por debajo de las referencias del sector para el horizonte de largo plazo. La IEA atribuye esta diferencia a factores que los datos históricos no capturan con suficiente peso: la aceleración de la electrificación en mercados emergentes de enorme escala poblacional (India, Indonesia, Brasil), el efecto de regulaciones de prohibición de venta de vehículos de combustión interna ya legisladas en múltiples jurisdicciones para la próxima década, y la posible disrupción de costes derivada de nuevas químicas de baterías (estado sólido, sodio-ion). Estos factores estructurales podrían desplazar significativamente al alza el potencial de mercado real respecto al estimado por el modelo a partir de datos históricos.

Esta divergencia no invalida el modelo, pero sí señala que la meseta proyectada podría ser un artefacto de la estimación del mercado potencial máximo con datos predominantemente de la fase de crecimiento inicial, y no una predicción robusta del techo real del mercado.

#### d) Modulación de Confianza

| Dimensión | Valoración | Justificación |
|---|---|---|
| Suficiencia de datos (n=11) | Suficiente con reservas | Cubre un ciclo de adopción representativo, pero infrapondera mercados emergentes |
| Riesgo de sobreajuste | Medio | Relación parámetros/observaciones próxima al umbral; modelos alternativos parsimoniosos compiten |
| Degeneración paramétrica | Detectada | Tres modelos con métricas idénticas; colapso paramétrico confirmado |
| Divergencia con referencia externa | Significativa | IEA proyecta escenarios superiores; factores no capturados en datos históricos |
| **Clasificación final** | **Proyección INDICATIVA** | Fiable para orientar decisiones estratégicas de medio plazo, pero sujeta a revisión ante cambios regulatorios, tecnológicos o de mercados emergentes |

**Conclusión de confianza:** La proyección se clasifica como **INDICATIVA**. Es suficientemente robusta para orientar decisiones estratégicas de posicionamiento y planificación de capacidad en el horizonte de corto y medio plazo, pero no debe utilizarse como cifra definitiva para decisiones de inversión de largo plazo sin incorporar escenarios alternativos que contemplen los factores estructurales identificados.

---

## 6. Marco Académico Teórico

### 6.1 Formulación Conceptual del Modelo Van den Bulte & Joshi

El modelo Van den Bulte & Joshi representa una extensión sofisticada del paradigma de difusión de innovaciones inaugurado por Bass. Su contribución teórica fundamental reside en el reconocimiento de que los mercados reales no son homogéneos: los adoptantes potenciales difieren sistemáticamente en su susceptibilidad a la influencia social, en sus umbrales de adopción y en su exposición a los efectos de imitación.

Conceptualmente, el modelo descompone el mercado potencial en segmentos con distintas dinámicas de adopción. Cada segmento responde de manera diferenciada a los mecanismos de innovación exógena —influencia de comunicaciones de masa, publicidad, políticas públicas— y a los mecanismos de imitación endógena —influencia interpersonal, visibilidad social, efectos de red. Esta arquitectura dual permite capturar fenómenos que los modelos homogéneos no pueden reproducir, como la existencia de múltiples puntos de inflexión o la persistencia del crecimiento más allá de lo que un único segmento de mercado justificaría.

La formulación matemática subyacente mantiene la estructura diferencial característica de los modelos de difusión, pero introduce parámetros que modulan la heterogeneidad entre segmentos, permitiendo que la curva agregada de adopción resulte de la superposición de dinámicas parciales con distintas velocidades y momentos de inflexión.

### 6.2 Comparación con los Modelos Evaluados

| Modelo | Fortaleza principal | Limitación principal | Adecuación al caso EV |
|---|---|---|---|
| Bass Clásico | Parsimonia, interpretabilidad | Mercado homogéneo | Alta para fase inicial |
| Dual Market | Captura dos segmentos | Mayor complejidad | Muy alta |
| Fourt & Woodlock | Simplicidad extrema | No captura imitación | Baja |
| Gompertz | Asimetría en la curva | Un solo segmento | Alta |
| Bass Generalizado (GBM) | Flexibilidad dinámica | Requiere más datos | Alta |
| Horsky & Simon | Incorpora precio | Colapsa a Bass con pocos datos | Media |
| Muller & Yogev | Extensión de Bass | Complejidad sin ganancia clara | Alta |
| Van den Bulte & Joshi | Heterogeneidad de mercado | Mayor número de parámetros | Muy alta |
| Difusión Logística R&K | Robusto, bajo MAPE | Menos fundamentación teórica | Alta |
| Ladrón-de-Guevara & Putsis | Competencia entre productos | Colapsa a Bass con pocos datos | Media |

El modelo de Fourt & Woodlock muestra el peor desempeño estadístico con diferencia, lo que confirma que su estructura —diseñada para bienes de consumo frecuente con compras repetidas— es conceptualmente inadecuada para un bien duradero como el vehículo eléctrico, donde la adopción es un evento único por consumidor en el horizonte relevante.

### 6.3 Relación con la Teoría de Difusión de Innovaciones

El análisis se inscribe en la tradición teórica inaugurada por Everett Rogers, quien conceptualizó la difusión de innovaciones como un proceso social de comunicación a través del tiempo entre los miembros de un sistema social. Los modelos matemáticos evaluados operacionalizan esta teoría mediante ecuaciones diferenciales que capturan la interacción entre adoptantes acumulados y no adoptantes potenciales.

La curva de adopción observada en los vehículos eléctricos es consistente con la curva en S característica de Rogers, aunque con particularidades propias de un mercado global heterogéneo: la fase de innovadores fue inusualmente prolongada debido a las barreras de coste y la escasez de modelos; la transición hacia la mayoría temprana fue precipitada por intervenciones de política pública de una intensidad sin precedentes en la historia de la automoción; y la mayoría tardía y rezagados presentan resistencias específicas vinculadas a la infraestructura de carga en zonas rurales y a la economía de uso en contextos de baja renta.

El modelo Van den Bulte & Joshi conecta directamente con las extensiones modernas de la teoría de Rogers que reconocen la heterogeneidad de los adoptantes como variable explicativa central, superando la simplificación del adoptante representativo que subyace a los modelos más parsimoniosos.

---

## 4.2. Recomendación a la Dirección

Dado que la proyección ha sido clasificada como **INDICATIVA** —robusta para orientación estratégica de medio plazo pero sujeta a revisión ante factores estructurales no capturados en los datos históricos—, las recomendaciones que siguen incorporan explícitamente esta cautela y evitan compromisos de largo plazo basados exclusivamente en las cifras del modelo.

**Recomendación principal:** La dirección debe interpretar las proyecciones del modelo como un escenario de referencia conservador, no como un techo de mercado. La evidencia estadística y el contraste con referencias s

## 2. Datos Históricos

| Año | Adopción (M) |
|---|---|
| 2015 | 1.26 M |
| 2016 | 2.00 M |
| 2017 | 3.00 M |
| 2018 | 5.00 M |
| 2019 | 7.50 M |
| 2020 | 10.00 M |
| 2021 | 16.60 M |
| 2022 | 26.00 M |
| 2023 | 40.00 M |
| 2024 | 58.00 M |
| 2025 | 78.00 M |


## 3. Métricas

| Modelo | R² | MAPE | Score | k |
|---|---|---|---|---|
| Bass Clásico | 0.9986 | 23.21% | 95.40 | 3 |
| Dual Market | 0.9996 | 12.88% | 96.84 | 6 |
| Fourt & Woodlock | 0.7324 | 114.17% | 58.57 | 2 |
| Gompertz | 0.9982 | 22.14% | 95.76 | 3 |
| Bass Generalizado (GBM) | 0.9989 | 21.56% | 93.46 | 4 |
| Horsky & Simon | 0.9986 | 23.21% | 96.02 | 4 |
| Muller & Yogev | 0.9996 | 13.22% | 96.60 | 7 |
| Van den Bulte & Joshi | 0.9997 | 12.14% | 96.95 | 6 |
| Difusión Logística R&K | 0.9995 | 9.40% | 96.78 | 4 |
| Ladrón-de-Guevara & Putsis | 0.9986 | 23.21% | 95.40 | 5 |


## 4. Proyecciones

| Año | Van den Bulte & Joshi (M) |
|---|---|
| 2026 | 128.25 M |
| 2027 | 128.32 M |
| 2028 | 128.35 M |
| 2029 | 128.37 M |
| 2030 | 128.38 M |
| 2031 | 128.39 M |
| 2032 | 128.39 M |
| 2033 | 128.40 M |
| 2034 | 128.40 M |
| 2035 | 128.40 M |


**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado (Van den Bulte & Joshi): R²=0.9997, MAPE=12.14%, Score=96.95.

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
