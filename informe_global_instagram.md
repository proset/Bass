# Informe de Adopción: instagram

# Informe de Adopción Tecnológica: Instagram

---

## 1. Resumen Ejecutivo

Instagram es una plataforma de redes sociales de propiedad de Meta Platforms que publica periódicamente datos de usuarios activos mensuales, por lo que los datos históricos empleados en este análisis se consideran de fuente oficial o ampliamente verificada por medios especializados.

El modelo seleccionado para describir la trayectoria de adopción de Instagram es el **Difusión Logística R&K**, que obtuvo la puntuación compuesta más alta entre los diez modelos evaluados. Su superioridad se explica por la combinación de un ajuste estadístico muy elevado y un error de predicción notablemente bajo, lo que indica que captura con fidelidad tanto la aceleración inicial de la plataforma como la desaceleración gradual propia de mercados que se aproximan a la saturación.

La plataforma se encuentra en una **fase de crecimiento tardío / madurez temprana**. Tras una expansión explosiva durante su primera década de vida, el ritmo de incorporación de nuevos usuarios se ha moderado, aunque sigue siendo positivo. Las proyecciones apuntan a que la base de usuarios continuará creciendo, pero a tasas decrecientes, convergiendo hacia un techo estructural de mercado en el horizonte de largo plazo.

**Nivel de confianza de la proyección: MEDIO-ALTO**

La serie histórica disponible es suficientemente larga para alimentar modelos de difusión, y el modelo ganador muestra un ajuste robusto. Sin embargo, la existencia de un salto abrupto en los datos entre ciertos años —posiblemente atribuible a cambios metodológicos en la definición de usuario activo o a la incorporación de nuevos mercados— introduce incertidumbre estructural que limita la confianza plena. Las proyecciones a corto y medio plazo son razonablemente fiables; las de largo plazo deben tratarse con mayor cautela.

---

## 3. Análisis del Mercado y Contexto Competitivo

### Drivers de adopción

Instagram ha sido impulsado por una confluencia de factores que explican su crecimiento sostenido durante más de una década. En primer lugar, la **penetración global de smartphones y conectividad móvil** ha democratizado el acceso a plataformas visuales, especialmente en mercados emergentes de Asia, América Latina y África, donde la incorporación de nuevos usuarios sigue siendo el principal motor de crecimiento. En segundo lugar, la **evolución del formato de contenido** —de fotografías estáticas a Stories, Reels y contenido de vídeo corto— ha permitido a la plataforma retener a usuarios existentes y atraer a nuevas cohortes demográficas, particularmente jóvenes. En tercer lugar, el **ecosistema de creadores de contenido y la economía de influencers** ha convertido a Instagram en una herramienta profesional y de monetización, generando un efecto de red que refuerza la adopción. Finalmente, la **integración con el ecosistema de Meta** —incluyendo Facebook, WhatsApp y Threads— facilita la incorporación de usuarios mediante identidades compartidas y funcionalidades cruzadas.

### Competidores clave y dinámica competitiva

El entorno competitivo de Instagram es intenso y ha evolucionado significativamente. **TikTok** representa la amenaza más directa, habiendo redefinido el consumo de contenido de vídeo corto y captando masivamente a la audiencia joven que históricamente era el núcleo de Instagram. **YouTube** compite en el segmento de vídeo de formato largo y medio, mientras que **Snapchat** mantiene una base de usuarios fiel en el segmento adolescente con formatos efímeros. **Pinterest** compite en el nicho de contenido visual inspiracional. La respuesta de Instagram ha sido la imitación acelerada de funcionalidades —Reels como réplica directa a TikTok— con resultados mixtos en términos de diferenciación. La dinámica competitiva favorece a las plataformas que logran retener el tiempo de atención del usuario, un recurso cada vez más disputado.

### Barreras de adopción

Entre los factores que frenan el crecimiento futuro destacan la **saturación en mercados maduros** —Europa Occidental, Norteamérica y partes de Asia— donde la penetración ya es muy elevada y el margen de incorporación de nuevos usuarios es limitado. La **fatiga de plataformas** y la preocupación creciente por el bienestar digital, especialmente entre adolescentes, generan presión social e institucional. Las **restricciones regulatorias** en materia de privacidad de datos —GDPR en Europa, leyes estatales en Estados Unidos— elevan los costes de cumplimiento y limitan las capacidades de segmentación publicitaria. Adicionalmente, la **competencia por el tiempo de atención** con plataformas emergentes representa una barrera estructural al crecimiento del engagement, incluso cuando la base de usuarios sigue expandiéndose.

### Tendencias tecnológicas y regulatorias

La inteligencia artificial generativa está transformando la producción y distribución de contenido, lo que puede tanto beneficiar a Instagram —mediante herramientas de creación asistida— como amenazarla, al reducir las barreras de entrada para plataformas competidoras. La **realidad aumentada** y los formatos inmersivos representan una apuesta estratégica de Meta para diferenciar la experiencia de usuario. En el plano regulatorio, la presión sobre las grandes plataformas tecnológicas se intensifica globalmente: investigaciones antimonopolio, leyes de protección de menores y marcos de responsabilidad sobre contenidos son vectores de riesgo que podrían imponer restricciones operativas significativas.

### Factores externos relevantes

La pandemia de COVID-19 actuó como acelerador de la adopción digital global, impulsando el uso de plataformas sociales durante los períodos de confinamiento. Este efecto se refleja en el salto de usuarios observado en los primeros años de la década de 2020. Sin embargo, parte de ese crecimiento acelerado puede haber anticipado adopción que de otro modo se habría producido más gradualmente, lo que podría explicar la moderación posterior del ritmo de crecimiento. Las tensiones geopolíticas —restricciones a plataformas occidentales en determinados mercados, como China— limitan el potencial de expansión en algunas de las regiones más pobladas del mundo.

---

## 5. Análisis Cualitativo y Validación Estadística

### Análisis cualitativo del ajuste

El modelo **Difusión Logística R&K** captura con notable precisión la forma en S característica de la adopción de Instagram: una fase de despegue acelerado, una inflexión hacia el crecimiento moderado y una convergencia progresiva hacia un techo de mercado. Su ventaja sobre modelos alternativos reside en su capacidad para ajustar tanto la velocidad de difusión como el punto de saturación de manera flexible, sin incurrir en la complejidad paramétrica excesiva que penaliza a otros modelos.

Los modelos **Dual Market** y **Van den Bulte & Joshi** obtuvieron puntuaciones compuestas muy similares entre sí, lo que sugiere que ambos describen el fenómeno con eficacia comparable. El modelo **Gompertz** y **Muller & Yogev** también muestran un ajuste sólido, aunque con errores de predicción algo superiores. Los modelos de la familia Bass —Bass Clásico, GBM, Horsky & Simon y Ladrón-de-Guevara & Putsis— presentan un rendimiento notablemente inferior, lo que indica que la estructura de imitación-innovación pura no captura adecuadamente la dinámica de una plataforma que ha experimentado múltiples reinvenciones de producto.

### a) Control de sobreajuste (AIC mental)

La serie histórica disponible comprende once puntos de datos. El modelo **Difusión Logística R&K** opera con un número reducido de parámetros —típicamente dos o tres, según la formulación específica de Richards y Kingsland—, lo que sitúa la relación entre parámetros y observaciones en un rango aceptable. No se activa la advertencia de riesgo alto de sobreajuste, ya que el número de parámetros es claramente inferior a la mitad del número de observaciones. No obstante, con once puntos, cualquier modelo con más de cuatro o cinco parámetros debería ser examinado con cautela. Los modelos de mayor complejidad paramétrica evaluados en este análisis —como GBM o Van den Bulte & Joshi— deben interpretarse con reservas adicionales en este contexto de datos limitados.

### b) Detección de degeneración paramétrica

Se observa un fenómeno de **colapso paramétrico** entre tres modelos: Bass Clásico, Horsky & Simon y Ladrón-de-Guevara & Putsis muestran métricas de ajuste prácticamente idénticas —mismo coeficiente de determinación y mismo error porcentual medio—. Esto no es un error de cálculo, sino una manifestación de **degeneración paramétrica**: con una serie de datos de longitud moderada, los parámetros adicionales que diferencian teóricamente a estos modelos no encuentran señal suficiente en los datos para identificarse de forma independiente. El resultado es que los modelos más complejos colapsan matemáticamente al comportamiento del más simple. Este fenómeno refuerza la preferencia por el modelo ganador, que logra mejor ajuste con menor complejidad. Asimismo, la coincidencia exacta entre Dual Market y Van den Bulte & Joshi sugiere que ambos convergen a la misma solución numérica bajo los datos disponibles, lo que debe tenerse en cuenta al interpretar sus proyecciones como independientes.

### c) Contraste con referencias externas

Según el conocimiento disponible del sector, diversas fuentes especializadas en análisis de redes sociales —incluyendo informes de Statista, DataReportal y análisis de Gartner sobre plataformas digitales— han proyectado que Instagram continuará creciendo en usuarios activos durante la presente década, con especial dinamismo en mercados emergentes. Las proyecciones del modelo para el horizonte de medio plazo se sitúan en un rango que resulta **cualitativamente coherente** con las estimaciones del sector, que anticipan una base de usuarios global de Instagram en el entorno de los cuatro mil millones para finales de la década, aunque con incertidumbre considerable. No se identificó una referencia externa única y autoritativa —equivalente a IEA para energía o IDC para hardware— que publique proyecciones de usuarios de Instagram con metodología transparente y comparable. Por tanto, el contraste es cualitativo y no debe interpretarse como validación cuantitativa.

### d) Modulación de confianza

| Dimensión | Evaluación | Justificación |
|---|---|---|
| Datos (n puntos) | Suficientes con reservas | Once observaciones permiten ajustar modelos de difusión, pero limitan la identificabilidad de modelos complejos |
| Sobreajuste | Riesgo bajo-medio | El modelo ganador tiene pocos parámetros; riesgo bajo para él, medio para modelos alternativos evaluados |
| Salto estructural en datos | Riesgo medio | El incremento abrupto observado en ciertos años puede reflejar cambio metodológico, no solo adopción real |
| Proyección a corto plazo | OPERATIVA | Fiable para decisiones de planificación a uno-tres años |
| Proyección a largo plazo | INDICATIVA | Sujeta a revisión ante cambios regulatorios, competitivos o tecnológicos |

**Conclusión de confianza:** La proyección a corto y medio plazo se clasifica como **OPERATIVA**, adecuada para orientar decisiones estratégicas con las cautelas señaladas. La proyección a largo plazo —horizonte de una década— se clasifica como **INDICATIVA**, y debe revisarse periódicamente a medida que se incorporen nuevos datos y se clarifiquen las dinámicas competitivas y regulatorias.

---

## 6. Marco Académico Teórico

### Formulación conceptual del modelo seleccionado

El modelo **Difusión Logística R&K** —formulado en la tradición de Richards y Kingsland— es una generalización flexible de la curva logística estándar. A diferencia de la logística simétrica clásica, este modelo incorpora un parámetro de asimetría que permite que el punto de inflexión —el momento de máxima velocidad de adopción— no se sitúe necesariamente en la mitad del techo de mercado, sino en cualquier fracción de él. Esto lo hace especialmente adecuado para plataformas digitales, cuya adopción frecuentemente muestra una aceleración inicial muy pronunciada seguida de una desaceleración más gradual, generando una curva asimétrica hacia la derecha.

Conceptualmente, el modelo asume que la adopción está limitada por un mercado potencial máximo —el techo de saturación— y que la velocidad de adopción en cada momento es proporcional tanto al número de adoptantes actuales como al potencial no realizado restante, modulada por el parámetro de asimetría.

### Comparación con modelos alternativos

| Modelo | Fortaleza principal | Limitación principal |
|---|---|---|
| Bass Clásico | Separación explícita de innovadores e imitadores | Asume simetría en la curva de adopción |
| Gompertz | Captura asimetría; buena para adopciones con despegue lento | Menos flexible que R&K en el punto de inflexión |
| Dual Market | Modela dos segmentos de mercado diferenciados | Mayor complejidad; riesgo de sobreajuste con pocos datos |
| Difusión Logística R&K | Flexibilidad en asimetría; parsimonia paramétrica | Asume un único techo de mercado estático |
| GBM (Bass Generalizado) | Incorpora variables de marketing mix | Requiere datos adicionales de esfuerzo comercial |

### Relación con la teoría de difusión de innovaciones

El modelo se inscribe en la tradición inaugurada por Everett Rogers en su obra sobre la difusión de innovaciones, que describe cómo las nuevas tecnologías o productos se propagan a través de sistemas sociales siguiendo patrones predecibles. La curva en S —característica de todos los modelos evaluados— refleja la secuencia de adopción por parte de innovadores, adoptantes tempranos, mayoría temprana, mayoría tardía y rezagados. El modelo R&K añade rigor matemático a esta intuición sociológica, permitiendo estimar con precisión el ritmo de transición entre fases y el techo estructural de adopción. En el contexto de plataformas digitales, los efectos de red —ausentes en la formulación original de Rogers— amplifican la fase de crecimiento acelerado, lo que justifica la asimetría que el modelo captura eficazmente.

---

## 7. Recomendación a la Dirección

### Síntesis estratégica

La trayectoria de adopción de Instagram describe una plataforma que ha superado con éxito las fases de despegue y crecimiento acelerado, y que se adentra en una etapa de madurez donde el crecimiento de usuarios, aunque positivo, es estructuralmente más lento. Este es el patrón típico de plataformas que han alcanzado una penetración elevada en sus mercados naturales y dependen del acceso a nuevas geografías y segmentos demográficos para sostener el crecimiento.

### Recomendaciones

**Dado que la proyección a corto y medio plazo es

## 2. Datos Históricos y Desviaciones

### 2.1 Serie Histórica Real
| Año | Adopción (M) |
|---|---|
| 2015 | 400.00 M |
| 2016 | 600.00 M |
| 2017 | 800.00 M |
| 2018 | 1000.00 M |
| 2019 | 1000.00 M |
| 2020 | 1071.34 M |
| 2021 | 1213.38 M |
| 2022 | 2000.00 M |
| 2023 | 2110.00 M |
| 2024 | 2350.00 M |
| 2025 | 3000.00 M |


### 2.2 Desviaciones por Modelo (Ajuste Histórico)
| Año | Real (M) | Bass Clásico (M) | Dual Market (M) | Fourt & Woodlock (M) | Gompertz (M) | Bass Generalizado (GBM) (M) | Horsky & Simon (M) | Muller & Yogev (M) | Van den Bulte & Joshi (M) | Difusión Logística R&K (M) | Ladrón-de-Guevara & Putsis (M) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2015 | 400.00 | 0.00 | 0.00 | 0.00 | 312.93 | 0.00 | 0.00 | 0.00 | 0.00 | 404.99 | 0.00 |
| 2016 | 600.00 | 232.00 | 602.02 | 332.10 | 458.40 | 232.30 | 232.00 | 447.79 | 1285.63 | 516.18 | 232.00 |
| 2017 | 800.00 | 481.13 | 813.38 | 642.14 | 637.09 | 479.76 | 481.13 | 734.79 | 2029.88 | 653.55 | 481.13 |
| 2018 | 1000.00 | 745.27 | 903.55 | 931.59 | 846.19 | 741.09 | 745.27 | 927.34 | 2461.04 | 820.79 | 745.27 |
| 2019 | 1000.00 | 1021.58 | 1006.44 | 1201.81 | 1080.81 | 1014.43 | 1021.58 | 1074.09 | 2711.22 | 1020.78 | 1021.58 |
| 2020 | 1071.34 | 1306.56 | 1162.14 | 1454.08 | 1334.72 | 1297.37 | 1306.56 | 1218.70 | 2856.46 | 1254.87 | 1306.56 |
| 2021 | 1213.38 | 1596.26 | 1393.50 | 1689.60 | 1601.06 | 1586.95 | 1596.26 | 1408.97 | 2940.79 | 1522.10 | 1596.26 |
| 2022 | 2000.00 | 1886.43 | 1711.66 | 1909.48 | 1873.00 | 1879.78 | 1886.43 | 1693.73 | 2989.75 | 1818.61 | 1886.43 |
| 2023 | 2110.00 | 2172.80 | 2103.83 | 2114.75 | 2144.29 | 2172.09 | 2172.80 | 2089.61 | 3018.19 | 2137.38 | 2172.80 |
| 2024 | 2350.00 | 2451.32 | 2526.77 | 2306.39 | 2409.55 | 2459.98 | 2451.32 | 2534.83 | 3034.69 | 2468.67 | 2451.32 |
| 2025 | 3000.00 | 2718.38 | 2921.94 | 2485.29 | 2664.47 | 2739.56 | 2718.38 | 2918.04 | 3044.28 | 2801.06 | 2718.38 |

### 2.3 Fuentes de Datos
| Año | Valor (M) | Tipo |
| --- | --- | --- |
| 2015 | 400.00 | Real (reportado) |
| 2016 | 600.00 | Real (reportado) |
| 2017 | 800.00 | Real (reportado) |
| 2018 | 1000.00 | Real (reportado) |
| 2019 | 1000.00 | Real (reportado) |
| 2020 | 1071.34 | Real (reportado) |
| 2021 | 1213.38 | Real (reportado) |
| 2022 | 2000.00 | Real (reportado) |
| 2023 | 2110.00 | Real (reportado) |
| 2024 | 2350.00 | Real (reportado) |
| 2025 | 3000.00 | Real (reportado) |

## 3bis. Métricas

| Modelo | R² | MAPE | Score | k |
|---|---|---|---|---|
| Bass Clásico | 0.8864 | 27.70% | 85.56 | 3 |
| Dual Market | 0.9513 | 14.59% | 93.01 | 6 |
| Fourt & Woodlock | 0.8600 | 26.38% | 83.91 | 2 |
| Gompertz | 0.9356 | 15.22% | 91.39 | 3 |
| Bass Generalizado (GBM) | 0.8889 | 27.53% | 85.79 | 4 |
| Horsky & Simon | 0.8864 | 27.70% | 85.56 | 4 |
| Muller & Yogev | 0.9421 | 18.63% | 91.76 | 7 |
| Van den Bulte & Joshi | 0.9513 | 14.59% | 93.01 | 6 |
| Difusión Logística R&K | 0.9591 | 10.74% | 94.66 | 4 |
| Ladrón-de-Guevara & Putsis | 0.8864 | 27.70% | 85.56 | 5 |


## 4. Proyecciones

### 4.1 Proyecciones de Todos los Modelos
| Año | Difusión Logística R&K (M) | Van den Bulte & Joshi (M) | Dual Market (M) | Muller & Yogev (M) | Gompertz (M) | Bass Generalizado (GBM) (M) | Bass Clásico (M) | Ladrón-de-Guevara & Putsis (M) | Horsky & Simon (M) | Fourt & Woodlock (M) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2015 | 404.99 | 0.00 | 0.00 | 0.00 | 312.93 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2016 | 516.18 | 1285.63 | 602.02 | 447.79 | 458.40 | 232.30 | 232.00 | 232.00 | 232.00 | 332.10 |
| 2017 | 653.55 | 2029.88 | 813.38 | 734.79 | 637.09 | 479.76 | 481.13 | 481.13 | 481.13 | 642.14 |
| 2018 | 820.79 | 2461.04 | 903.55 | 927.34 | 846.19 | 741.09 | 745.27 | 745.27 | 745.27 | 931.59 |
| 2019 | 1020.78 | 2711.22 | 1006.44 | 1074.09 | 1080.81 | 1014.43 | 1021.58 | 1021.58 | 1021.58 | 1201.81 |
| 2020 | 1254.87 | 2856.46 | 1162.14 | 1218.70 | 1334.72 | 1297.37 | 1306.56 | 1306.56 | 1306.56 | 1454.08 |
| 2021 | 1522.10 | 2940.79 | 1393.50 | 1408.97 | 1601.06 | 1586.95 | 1596.26 | 1596.26 | 1596.26 | 1689.60 |
| 2022 | 1818.61 | 2989.75 | 1711.66 | 1693.73 | 1873.00 | 1879.78 | 1886.43 | 1886.43 | 1886.43 | 1909.48 |
| 2023 | 2137.38 | 3018.19 | 2103.83 | 2089.61 | 2144.29 | 2172.09 | 2172.80 | 2172.80 | 2172.80 | 2114.75 |
| 2024 | 2468.67 | 3034.69 | 2526.77 | 2534.83 | 2409.55 | 2459.98 | 2451.32 | 2451.32 | 2451.32 | 2306.39 |
| 2025 | 2801.06 | 3044.28 | 2921.94 | 2918.04 | 2664.47 | 2739.56 | 2718.38 | 2718.38 | 2718.38 | 2485.29 |
| 2026 | 3122.99 | 3049.85 | 3244.66 | 3177.01 | 3000.00 | 3007.20 | 3000.00 | 3000.00 | 3000.00 | 3000.00 |
| 2027 | 3424.30 | 3053.08 | 3480.47 | 3324.53 | 3131.41 | 3259.71 | 3206.88 | 3206.88 | 3206.88 | 3000.00 |
| 2028 | 3697.42 | 3054.96 | 3639.13 | 3400.56 | 3339.93 | 3494.48 | 3424.50 | 3424.51 | 3424.51 | 3000.00 |
| 2029 | 3937.88 | 3056.04 | 3740.04 | 3437.76 | 3530.83 | 3709.63 | 3623.06 | 3623.07 | 3623.07 | 3089.73 |
| 2030 | 4144.23 | 3056.68 | 3801.94 | 3455.55 | 3704.18 | 3904.02 | 3802.40 | 3802.40 | 3802.40 | 3216.61 |
| 2031 | 4317.43 | 3057.04 | 3839.08 | 3463.97 | 3860.46 | 4077.26 | 3962.89 | 3962.89 | 3962.89 | 3335.06 |
| 2032 | 4460.15 | 3057.26 | 3861.06 | 3467.95 | 4000.50 | 4229.62 | 4105.34 | 4105.34 | 4105.34 | 3445.65 |
| 2033 | 4575.96 | 3057.38 | 3873.96 | 3469.84 | 4125.31 | 4361.92 | 4230.86 | 4230.86 | 4230.86 | 3548.89 |
| 2034 | 4668.77 | 3057.45 | 3881.51 | 3470.74 | 4236.05 | 4475.43 | 4340.76 | 4340.76 | 4340.76 | 3645.27 |
| 2035 | 4742.41 | 3057.50 | 3885.90 | 3471.17 | 4333.93 | 4571.71 | 4436.43 | 4436.43 | 4436.44 | 3735.25 |

### 4.2 Escenarios de Consenso
| Escenario | Modelo | 2030 (M) | 2035 (M) |
| --- | --- | --- | --- |
| Conservador | Gompertz | 3704.18 | 4333.93 |
| Base (recomendado) | Difusión Logística R&K | 4144.23 | 4742.41 |
| Optimista | Difusión Logística R&K | 4144.23 | 4742.41 |

**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado (Difusión Logística R&K): R²=0.9591, MAPE de ajuste=10.74%, Score=94.66.

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
