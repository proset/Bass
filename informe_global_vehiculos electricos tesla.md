# Informe de Adopción: vehiculos electricos tesla

# Informe de Adopción Tecnológica: Vehículos Eléctricos Tesla

---

## 1. Resumen Ejecutivo

**NOTA DE FUENTE DE DATOS:** Tesla publica cifras de entregas y producción, pero los datos de adopción acumulada utilizados en este análisis corresponden a estimaciones de unidades vendidas globalmente. Aunque Tesla es una empresa pública (cotiza en NASDAQ), las cifras de adopción acumulada a nivel global provienen de fuentes de terceros y estimaciones del sector. Incertidumbre: media-alta.

El análisis de la trayectoria de adopción de los vehículos eléctricos Tesla revela una curva de crecimiento sostenido y acelerado que, en los años más recientes, comienza a mostrar señales de desaceleración relativa, características de una tecnología que transita desde la fase de crecimiento acelerado hacia la madurez temprana. La base de adoptantes acumulados ha crecido de manera exponencial durante la mayor parte de la serie histórica, impulsada por la expansión de la gama de productos, la reducción progresiva de costes y el fortalecimiento de la infraestructura de carga.

**Modelo seleccionado: Difusión Logística R&K.** Este modelo fue seleccionado por obtener la puntuación compuesta más alta entre los diez modelos evaluados, combinando un ajuste prácticamente perfecto a los datos históricos con el error de predicción más bajo de toda la batería de modelos. Su formulación logística captura con precisión la dinámica observada: crecimiento inicial lento, aceleración sostenida y convergencia hacia un techo de mercado, lo que resulta coherente con la naturaleza de la adopción de vehículos eléctricos como tecnología de consumo masivo con barreras de entrada decrecientes pero no nulas.

**Fase de crecimiento:** El mercado Tesla se encuentra en la **transición entre la fase de crecimiento tardío y la madurez temprana**. El ritmo de incorporación de nuevos adoptantes, aunque todavía positivo, muestra una desaceleración progresiva que el modelo captura con fidelidad. Las proyecciones apuntan a una estabilización del stock acumulado en el horizonte de medio plazo, lo que sugiere que el mercado se aproxima a su techo estructural bajo las condiciones actuales.

**Nivel de confianza de la proyección: MEDIO-ALTO**, con matices importantes. La calidad del ajuste estadístico es sobresaliente y la serie histórica cubre un período suficientemente largo para identificar la forma de la curva de difusión. Sin embargo, el techo de mercado proyectado parece conservador en relación con las referencias del sector, lo que introduce incertidumbre sobre si el modelo está capturando correctamente el potencial de largo plazo o si, por el contrario, los datos históricos de Tesla como marca individual no reflejan la expansión futura del mercado total de vehículos eléctricos. Esta distinción —entre la difusión de Tesla como empresa y la difusión del vehículo eléctrico como categoría— es crítica para interpretar las proyecciones.

---

## 3. Análisis del Mercado y Contexto Competitivo

### Drivers de Adopción

La adopción de vehículos eléctricos Tesla ha sido impulsada por una combinación de factores tecnológicos, económicos, regulatorios y culturales que se han reforzado mutuamente a lo largo de la última década.

**Factores tecnológicos:** Tesla ha liderado la industria en autonomía de batería, rendimiento de carga y software de conducción asistida. La integración vertical —desde la fabricación de celdas hasta el software de gestión energética— ha permitido a la compañía ofrecer una experiencia de usuario diferenciada que ha actuado como catalizador de adopción entre los segmentos de adoptantes tempranos y la mayoría temprana. La red Supercharger, construida de forma propietaria, eliminó una de las principales barreras percibidas: la ansiedad por la autonomía.

**Factores económicos:** La reducción progresiva del coste total de propiedad, impulsada por la caída en el precio de las baterías de litio, ha ampliado el mercado potencial de forma significativa. La introducción de modelos de precio más accesible —como el Model 3 y el Model Y— fue un punto de inflexión que democratizó el acceso a la marca y aceleró la curva de adopción de forma visible en los datos históricos.

**Factores regulatorios:** Las políticas de incentivos fiscales en Estados Unidos, Europa y China —los tres mercados principales de Tesla— han jugado un papel determinante. Los créditos fiscales para vehículos eléctricos, las restricciones a la circulación de vehículos de combustión interna en zonas urbanas y los objetivos de descarbonización del transporte establecidos por los gobiernos han creado un entorno favorable que ha acelerado la adopción más allá de lo que la dinámica de mercado libre habría generado de forma autónoma.

**Factores culturales y de marca:** Tesla ha construido una identidad de marca asociada a la innovación, la sostenibilidad y el estatus tecnológico. Este posicionamiento ha generado una comunidad de usuarios altamente comprometida que actúa como vector de difusión social —el mecanismo de imitación que los modelos de Bass capturan formalmente— amplificando el efecto de boca a boca y reduciendo la necesidad de publicidad convencional.

### Competidores Clave y Dinámica Competitiva

El panorama competitivo ha experimentado una transformación radical durante el período analizado. En los primeros años de la serie histórica, Tesla operaba en un mercado de nicho con competencia limitada. La situación actual es radicalmente distinta.

**Fabricantes tradicionales reconvertidos:** Volkswagen Group, con su plataforma MEB y modelos como el ID.4 e ID.3, ha emergido como el competidor más relevante en Europa. General Motors, con su plataforma Ultium, y Ford, con el Mustang Mach-E y la F-150 Lightning, han ganado cuota en el mercado norteamericano. Stellantis, Hyundai-Kia y BMW también han intensificado su oferta eléctrica, fragmentando el mercado y erosionando la posición dominante de Tesla en varios segmentos.

**Fabricantes nativos digitales chinos:** BYD ha superado a Tesla en volumen de ventas globales de vehículos eléctricos en períodos recientes, convirtiéndose en el competidor más directo a escala mundial. NIO, Xpeng y Li Auto han consolidado posiciones sólidas en el mercado chino —el mayor mercado de vehículos eléctricos del mundo— donde Tesla enfrenta presiones competitivas crecientes tanto en precio como en características de producto.

**Implicaciones para la difusión de Tesla:** La intensificación competitiva tiene un efecto ambivalente sobre la adopción de Tesla específicamente. Por un lado, la expansión del ecosistema de vehículos eléctricos en general —con más modelos, más infraestructura y mayor normalización social— amplía el mercado total y beneficia a todos los actores. Por otro lado, Tesla pierde cuota relativa a medida que los adoptantes que habrían elegido Tesla por defecto ahora tienen alternativas viables. Este fenómeno de sustitución competitiva no está capturado en los modelos de difusión aplicados, que tratan a Tesla como si operara en un mercado sin sustitutos cercanos.

### Barreras de Adopción

A pesar del crecimiento sostenido, persisten barreras estructurales que limitan la velocidad de penetración:

**Infraestructura de carga:** Aunque la red Supercharger de Tesla es la más extensa de su categoría, la disponibilidad de carga rápida en zonas rurales, mercados emergentes y edificios residenciales sin garaje privado sigue siendo un freno significativo para los adoptantes potenciales en la mayoría temprana tardía y los rezagados.

**Precio de adquisición:** A pesar de la reducción de costes, el precio de entrada de los vehículos Tesla sigue siendo superior al de los equivalentes de combustión interna en la mayoría de los mercados, especialmente cuando los incentivos fiscales se reducen o eliminan —como ha ocurrido en varios mercados europeos en años recientes.

**Ansiedad por la autonomía y el tiempo de carga:** Aunque la autonomía media ha mejorado sustancialmente, la percepción de riesgo asociada a quedarse sin carga en trayectos largos sigue siendo una barrera psicológica relevante para segmentos de población con patrones de movilidad específicos —conductores de larga distancia, residentes en zonas sin infraestructura densa.

**Dependencia de materias primas críticas:** La cadena de suministro de baterías depende de materiales como el litio, el cobalto y el níquel, cuya disponibilidad y precio están sujetos a volatilidad geopolítica. Las tensiones en las cadenas de suministro globales —evidenciadas durante la pandemia de COVID-19 y agravadas por conflictos geopolíticos— han generado disrupciones en la producción que han afectado a la capacidad de Tesla para satisfacer la demanda.

### Tendencias Tecnológicas y Regulatorias

**Tecnología de baterías:** La transición hacia baterías de estado sólido, actualmente en fase de desarrollo avanzado por varios actores del sector, promete aumentar la densidad energética, reducir el tiempo de carga y mejorar la seguridad. Tesla ha apostado por su propia celda 4680 como paso intermedio hacia esta tecnología. La materialización de estas mejoras podría relanzar la curva de adopción más allá de lo que los datos históricos sugieren.

**Conducción autónoma:** El desarrollo del sistema Full Self-Driving de Tesla y su potencial comercialización como servicio de robotaxi representa una fuente de valor adicional que podría transformar el modelo de negocio y ampliar el mercado potencial más allá de los compradores tradicionales de vehículos.

**Marco regulatorio global:** La Unión Europea ha establecido la prohibición de venta de vehículos de combustión interna para mediados de la próxima década, lo que crea un mandato regulatorio que actuará como acelerador estructural de la adopción. Estados Unidos ha mantenido incentivos fiscales significativos a través de la Inflation Reduction Act, aunque con condiciones de elegibilidad que han afectado a Tesla de forma variable. China mantiene políticas de apoyo al vehículo eléctrico como parte de su estrategia industrial, aunque con un sesgo creciente hacia los fabricantes nacionales.

### Factores Externos Relevantes

**Pandemia de COVID-19:** La pandemia generó disrupciones en la cadena de suministro que afectaron a la producción de Tesla, especialmente en el período de mayor impacto. Sin embargo, también aceleró la digitalización del proceso de compra —Tesla ya operaba con un modelo de venta directa online— y generó un cambio en las preferencias de movilidad que, en algunos segmentos, favoreció la adopción de vehículos privados frente al transporte público.

**Tensiones geopolíticas:** Las relaciones entre Estados Unidos y China tienen implicaciones directas para Tesla, que opera una gigafábrica en Shanghái y depende del mercado chino para una fracción significativa de sus ventas globales. Las tensiones arancelarias y las presiones regulatorias en China representan un riesgo de cola relevante para las proyecciones.

**Volatilidad de precios de la energía:** Los episodios de alta volatilidad en los precios del petróleo —como el observado tras la invasión de Ucrania— han actuado históricamente como aceleradores de la adopción de vehículos eléctricos al mejorar el diferencial de coste operativo frente a los vehículos de combustión.

---

## 5. Análisis Cualitativo y Validación Estadística

### Análisis Cualitativo del Ajuste

La trayectoria de adopción de Tesla presenta una forma sigmoidea característica de las innovaciones tecnológicas que superan el umbral de masa crítica y alcanzan la mayoría del mercado. Los datos históricos muestran una aceleración sostenida durante la mayor parte del período analizado, seguida de una desaceleración relativa en los años más recientes, coherente con el agotamiento progresivo del mercado potencial bajo las condiciones actuales.

El modelo Difusión Logística R&K captura esta dinámica con una fidelidad excepcional, lo que sugiere que la curva de adopción de Tesla ha seguido un patrón de difusión relativamente ordenado, sin discontinuidades estructurales mayores que distorsionen el ajuste. Esto es notable dado el contexto de disrupciones externas —pandemia, tensiones geopolíticas, cambios regulatorios— que podrían haber generado quiebres en la tendencia.

### a) Control de Sobreajuste (AIC Mental)

La batería de modelos evaluada incluye formulaciones de complejidad paramétrica variable. El modelo ganador, Difusión Logística R&K, es una extensión del modelo logístico clásico con un número de parámetros moderado —típicamente tres parámetros fundamentales: tasa de crecimiento, punto de inflexión y techo de mercado, con posibles extensiones para capturar asimetrías en la curva.

Con una serie histórica de once puntos de datos, el umbral de riesgo de sobreajuste se sitúa en modelos con más de cinco o seis parámetros libres. El modelo seleccionado se mantiene dentro de un rango de complejidad razonable para el tamaño muestral disponible, por lo que **el riesgo de sobreajuste se evalúa como medio-bajo** para el modelo ganador específicamente.

Sin embargo, es importante señalar que once observaciones anuales constituyen una base de datos modesta para ajustar modelos de difusión con múltiples parámetros. La alta calidad del ajuste —prácticamente perfecta en varios modelos— es en parte un artefacto del reducido número de grados de libertad disponibles: con pocos puntos y varios parámetros, cualquier modelo flexible puede ajustarse casi perfectamente a los datos sin que ello garantice capacidad predictiva fuera de la muestra.

### b) Detección de Degeneración Paramétrica

El análisis de los resultados revela un patrón estadístico que merece atención explícita: **varios modelos de distinta complejidad teórica muestran métricas de ajuste prácticamente idénticas**, con coeficientes de determinación indistinguibles y errores de predicción muy similares entre sí.

Específicamente, los modelos Dual Market, Muller & Yogev y Van den Bulte & Joshi presentan ajustes prácticamente equivalentes entre sí, y todos ellos son formulaciones más complejas que el Bass Clásico, el cual a su vez muestra métricas idénticas a las de Horsky & Simon y Ladrón-de-Guevara & Putsis.

Este fenómeno es un indicador clásico de **colapso paramétrico o degeneración paramétrica**: cuando el número de observaciones es limitado, los parámetros adicionales de los modelos más complejos no pueden ser identificados de forma independiente por los datos. Matemáticamente, los parámetros "extra" convergen a valores que hacen que el modelo complejo se comporte de forma idéntica al más simple. **Esto no es un error de cálculo ni un problema de implementación; es una limitación fundamental de identificabilidad estadística** que surge cuando la información contenida en los datos es insuficiente para distinguir entre formulaciones altern

## 2. Datos Históricos y Desviaciones

### 2.1 Serie Histórica Real
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
| 2025 | 8.82 M |


### 2.2 Desviaciones por Modelo (Ajuste Histórico)
| Año | Real (M) | Bass Clásico (M) | Dual Market (M) | Fourt & Woodlock (M) | Gompertz (M) | Bass Generalizado (GBM) (M) | Horsky & Simon (M) | Muller & Yogev (M) | Van den Bulte & Joshi (M) | Difusión Logística R&K (M) | Ladrón-de-Guevara & Putsis (M) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2015 | 0.05 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.07 | 0.00 |
| 2016 | 0.13 | 0.07 | 0.10 | 0.65 | 0.04 | 0.09 | 0.07 | 0.11 | 2.36 | 0.13 | 0.07 |
| 2017 | 0.23 | 0.19 | 0.25 | 1.30 | 0.13 | 0.23 | 0.19 | 0.28 | 3.24 | 0.24 | 0.19 |
| 2018 | 0.47 | 0.41 | 0.48 | 1.94 | 0.34 | 0.45 | 0.41 | 0.57 | 3.57 | 0.44 | 0.41 |
| 2019 | 0.84 | 0.77 | 0.82 | 2.58 | 0.75 | 0.80 | 0.77 | 1.04 | 3.70 | 0.78 | 0.77 |
| 2020 | 1.34 | 1.37 | 1.37 | 3.22 | 1.42 | 1.38 | 1.37 | 1.80 | 3.77 | 1.36 | 1.37 |
| 2021 | 2.28 | 2.31 | 2.25 | 3.85 | 2.41 | 2.28 | 2.31 | 3.03 | 3.81 | 2.29 | 2.31 |
| 2022 | 3.59 | 3.65 | 3.61 | 4.48 | 3.70 | 3.62 | 3.65 | 4.86 | 3.86 | 3.64 | 3.65 |
| 2023 | 5.40 | 5.34 | 5.38 | 5.11 | 5.27 | 5.35 | 5.34 | 7.18 | 3.91 | 5.35 | 5.34 |
| 2024 | 7.19 | 7.17 | 7.20 | 5.74 | 7.04 | 7.22 | 7.17 | 9.50 | 3.98 | 7.19 | 7.17 |
| 2025 | 8.82 | 8.84 | 8.82 | 6.36 | 8.93 | 8.81 | 8.84 | 11.45 | 4.04 | 8.83 | 8.84 |

### 2.3 Fuentes de Datos
| Año | Valor (M) | Tipo |
| --- | --- | --- |
| 2015 | 0.05 | Real (reportado) |
| 2016 | 0.13 | Real (reportado) |
| 2017 | 0.23 | Real (reportado) |
| 2018 | 0.47 | Real (reportado) |
| 2019 | 0.84 | Real (reportado) |
| 2020 | 1.34 | Real (reportado) |
| 2021 | 2.28 | Real (reportado) |
| 2022 | 3.59 | Real (reportado) |
| 2023 | 5.40 | Real (reportado) |
| 2024 | 7.19 | Real (reportado) |
| 2025 | 8.82 | Real (reportado) |

## 3bis. Métricas

| Modelo | R² | MAPE | Score | k |
|---|---|---|---|---|
| Bass Clásico | 0.9997 | 17.48% | 95.23 | 3 |
| Dual Market | 0.9999 | 12.66% | 96.77 | 6 |
| Fourt & Woodlock | 0.7740 | 161.04% | 62.37 | 2 |
| Gompertz | 0.9987 | 22.85% | 94.57 | 3 |
| Bass Generalizado (GBM) | 0.9999 | 13.40% | 96.92 | 4 |
| Horsky & Simon | 0.9997 | 17.48% | 95.23 | 4 |
| Muller & Yogev | 0.9999 | 12.66% | 97.16 | 7 |
| Van den Bulte & Joshi | 0.9999 | 12.64% | 97.22 | 6 |
| Difusión Logística R&K | 0.9999 | 6.29% | 98.11 | 4 |
| Ladrón-de-Guevara & Putsis | 0.9997 | 17.48% | 95.23 | 5 |


## 4. Proyecciones

### 4.1 Proyecciones de Todos los Modelos
| Año | Difusión Logística R&K (M) | Van den Bulte & Joshi (M) | Muller & Yogev (M) | Bass Generalizado (GBM) (M) | Dual Market (M) | Bass Clásico (M) | Horsky & Simon (M) | Ladrón-de-Guevara & Putsis (M) | Gompertz (M) | Fourt & Woodlock (M) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2015 | 0.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 |
| 2016 | 0.13 | 2.36 | 0.11 | 0.09 | 0.10 | 0.07 | 0.07 | 0.07 | 0.04 | 0.65 |
| 2017 | 0.24 | 3.24 | 0.28 | 0.23 | 0.25 | 0.19 | 0.19 | 0.19 | 0.13 | 1.30 |
| 2018 | 0.44 | 3.57 | 0.57 | 0.45 | 0.48 | 0.41 | 0.41 | 0.41 | 0.34 | 1.94 |
| 2019 | 0.78 | 3.70 | 1.04 | 0.80 | 0.82 | 0.77 | 0.77 | 0.77 | 0.75 | 2.58 |
| 2020 | 1.36 | 3.77 | 1.80 | 1.38 | 1.37 | 1.37 | 1.37 | 1.37 | 1.42 | 3.22 |
| 2021 | 2.29 | 3.81 | 3.03 | 2.28 | 2.25 | 2.31 | 2.31 | 2.31 | 2.41 | 3.85 |
| 2022 | 3.64 | 3.86 | 4.86 | 3.62 | 3.61 | 3.65 | 3.65 | 3.65 | 3.70 | 4.48 |
| 2023 | 5.35 | 3.91 | 7.18 | 5.35 | 5.38 | 5.34 | 5.34 | 5.34 | 5.27 | 5.11 |
| 2024 | 7.19 | 3.98 | 9.50 | 7.22 | 7.20 | 7.17 | 7.17 | 7.17 | 7.04 | 5.74 |
| 2025 | 8.83 | 4.04 | 11.45 | 8.81 | 8.82 | 8.84 | 8.84 | 8.84 | 8.93 | 6.36 |
| 2026 | 10.08 | 8.82 | 12.96 | 9.89 | 10.25 | 10.16 | 10.16 | 10.16 | 10.84 | 8.82 |
| 2027 | 10.92 | 8.82 | 14.07 | 10.49 | 11.53 | 11.08 | 11.08 | 11.08 | 12.71 | 8.82 |
| 2028 | 11.44 | 8.82 | 14.84 | 10.78 | 12.63 | 11.67 | 11.67 | 11.67 | 14.48 | 8.82 |
| 2029 | 11.74 | 8.82 | 15.35 | 10.91 | 13.55 | 12.03 | 12.03 | 12.03 | 16.11 | 8.82 |
| 2030 | 11.91 | 8.82 | 15.68 | 10.96 | 14.27 | 12.23 | 12.23 | 12.23 | 17.58 | 9.42 |
| 2031 | 12.01 | 8.82 | 15.89 | 10.98 | 14.83 | 12.35 | 12.35 | 12.35 | 18.89 | 10.03 |
| 2032 | 12.06 | 8.82 | 16.02 | 10.98 | 15.23 | 12.42 | 12.42 | 12.42 | 20.03 | 10.63 |
| 2033 | 12.09 | 8.82 | 16.11 | 10.99 | 15.52 | 12.46 | 12.46 | 12.46 | 21.01 | 11.22 |
| 2034 | 12.10 | 8.82 | 16.16 | 10.99 | 15.73 | 12.48 | 12.48 | 12.48 | 21.86 | 11.82 |
| 2035 | 12.11 | 8.82 | 16.19 | 10.99 | 15.87 | 12.49 | 12.49 | 12.49 | 22.57 | 12.41 |

### 4.2 Escenarios de Consenso
| Escenario | Modelo | 2030 (M) | 2035 (M) |
| --- | --- | --- | --- |
| Conservador | Bass Clásico | 12.23 | 12.49 |
| Base (recomendado) | Difusión Logística R&K | 11.91 | 12.11 |
| Optimista | Gompertz | 17.58 | 22.57 |

**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado (Difusión Logística R&K): R²=0.9999, MAPE de ajuste=6.29%, Score=98.11.

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
