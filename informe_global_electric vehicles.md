# Informe de Adopción: electric vehicles

# INFORME DE ADOPCIÓN TECNOLÓGICA
## Vehículos Eléctricos (*Electric Vehicles* — EV)

---

# §1 RESUMEN EJECUTIVO

El mercado global de vehículos eléctricos representa uno de los fenómenos de difusión tecnológica más acelerados registrados en la historia industrial reciente. El análisis cubre una ventana temporal de once años y aplica un conjunto de diez modelos de difusión para caracterizar la trayectoria de adopción, identificar la fase de crecimiento actual y proyectar el comportamiento futuro del mercado.

El modelo seleccionado como óptimo es el **Dual Market**, que obtiene la puntuación compuesta más alta del conjunto evaluado. Este modelo captura una dinámica estructural que los modelos de mercado único no pueden representar adecuadamente: la coexistencia de dos segmentos de adoptantes con velocidades de difusión, sensibilidades al precio y horizontes de decisión sustancialmente distintos —el segmento de consumidores particulares y el segmento de flotas comerciales e institucionales—, cuya interacción genera el patrón de crecimiento observado.

Los resultados del ajuste revelan una polarización clara entre modelos de alto rendimiento y modelos inadecuados para este conjunto de datos. La gran mayoría de los modelos alcanzan coeficientes de determinación superiores a **0.99**, lo que indica que la serie histórica sigue una trayectoria suave y bien estructurada, favorable para el ajuste paramétrico. Sin embargo, el error porcentual absoluto medio (MAPE) discrimina con mayor precisión entre modelos, revelando diferencias sustanciales en la capacidad predictiva local.

Las proyecciones del modelo recomendado sitúan el mercado global en torno a los **~100 millones** de unidades acumuladas hacia el año 2030, con una estabilización prácticamente completa hacia 2035, lo que sugiere que el mercado se aproxima a su techo de saturación dentro del horizonte de proyección analizado. Esta conclusión debe interpretarse con cautela, dado que el potencial de mercado total (*market potential*, parámetro M) es sensible a supuestos sobre infraestructura de carga, paridad de costes con vehículos de combustión interna y marcos regulatorios nacionales.

| Dimensión | Hallazgo principal |
|---|---|
| Período analizado | Once años de datos históricos |
| Modelos evaluados | Diez modelos de difusión |
| Modelo recomendado | Dual Market |
| Score del modelo recomendado | 97.09 / 100 |
| Fase de adopción actual | Crecimiento tardío / inicio de saturación |
| Proyección horizonte medio | ~100 millones de unidades |
| Proyección horizonte largo | ~101 millones de unidades (saturación) |
| Nivel de confianza general | Moderado-alto, con advertencias específicas |

---

# §5 ANÁLISIS CUALITATIVO

## 5.1 Caracterización de la Trayectoria de Adopción

La serie histórica de vehículos eléctricos exhibe un perfil de crecimiento que, a simple vista, podría clasificarse como exponencial puro. Sin embargo, un examen más cuidadoso revela que la tasa de crecimiento interanual, aunque sostenida, muestra señales incipientes de moderación en los últimos períodos registrados. Este comportamiento es precisamente el que distingue una curva sigmoidea en su fase de inflexión tardía de una curva exponencial sin techo.

| Período | Comportamiento cualitativo dominante |
|---|---|
| Inicio de la serie — año 3 | Despegue lento; adoptantes innovadores y entusiastas tecnológicos |
| Año 3 — año 7 | Aceleración sostenida; entrada de mayoría temprana; reducción de costes de batería |
| Año 7 — año 9 | Crecimiento máximo en términos absolutos; efecto de imitación dominante |
| Año 9 — año 11 | Moderación de la tasa relativa; señales de aproximación al punto de inflexión |
| Horizonte proyectado | Desaceleración progresiva hacia la saturación del mercado potencial |

La moderación observada en los últimos períodos no debe interpretarse como una señal de debilidad del mercado, sino como el comportamiento esperado de cualquier proceso de difusión que se aproxima a su techo estructural. El mercado de vehículos eléctricos no está contrayéndose; está madurando.

## 5.2 Factores Cualitativos que Explican la Dinámica Observada

La trayectoria de adopción no puede explicarse exclusivamente mediante parámetros matemáticos. Existen fuerzas estructurales que han actuado como aceleradores o frenos en distintos momentos del período analizado:

### 5.2.1 Aceleradores de la Difusión

| Factor acelerador | Mecanismo de influencia |
|---|---|
| Reducción del coste de baterías de iones de litio | Disminuye la barrera económica de entrada para el adoptante medio |
| Mandatos regulatorios de emisiones cero | Genera demanda inducida en segmentos de flotas y mercados regulados |
| Expansión de infraestructura de carga | Reduce la ansiedad de autonomía (*range anxiety*), principal freno conductual |
| Efecto de imitación social | Los adoptantes tempranos visibles aceleran la decisión de la mayoría |
| Ampliación de la oferta de modelos | Permite la segmentación por precio, tamaño y uso, captando nuevos perfiles |
| Incentivos fiscales y subsidios directos | Comprimen el tiempo de recuperación de la inversión inicial |

### 5.2.2 Frenos y Resistencias Estructurales

| Factor de resistencia | Mecanismo de influencia |
|---|---|
| Heterogeneidad de infraestructura entre regiones | Crea mercados de adopción asimétrica que distorsionan los agregados globales |
| Dependencia de cadenas de suministro de minerales críticos | Introduce volatilidad en costes y disponibilidad de unidades |
| Tiempo de carga vs. repostaje convencional | Persiste como fricción conductual en segmentos de uso intensivo |
| Incertidumbre sobre valor residual | Frena la adopción en segmentos sensibles al coste total de propiedad |
| Retirada o reducción de subsidios en mercados maduros | Puede generar caídas temporales de demanda en mercados específicos |

## 5.3 Segmentación del Mercado y Dualidad Estructural

La selección del modelo Dual Market no es arbitraria: responde a una realidad empírica observable en los datos. El mercado global de vehículos eléctricos no es homogéneo. Coexisten al menos dos dinámicas de adopción con lógicas distintas:

| Dimensión | Segmento de consumidores particulares | Segmento de flotas y mercado institucional |
|---|---|---|
| Motor de adopción principal | Preferencia individual, identidad, incentivos fiscales | Coste total de propiedad, regulación, ESG corporativo |
| Velocidad de decisión | Lenta; ciclo de compra de varios años | Más rápida en contextos regulados; decisión centralizada |
| Sensibilidad al precio | Alta en segmentos medios y bajos | Moderada; prima el TCO sobre el precio de adquisición |
| Efecto de imitación | Fuerte; influencia social y visibilidad del producto | Débil; decisión técnica y financiera |
| Contribución al agregado global | Dominante en volumen | Creciente; especialmente en transporte urbano y logística |

Esta dualidad explica por qué los modelos de mercado único, aunque alcanzan ajustes estadísticos elevados, cometen errores sistemáticos en determinados subperíodos: están promediando dos dinámicas que no deberían promediarse.

## 5.4 Fase de Crecimiento Actual

Con base en el análisis conjunto de la trayectoria histórica, los parámetros estimados por el modelo recomendado y las señales cualitativas del mercado, el mercado global de vehículos eléctricos se encuentra actualmente en la **fase de crecimiento tardío**, aproximándose al punto de inflexión de la curva sigmoidea.

| Fase de la curva de difusión | Características definitorias | ¿Aplica al mercado EV actual? |
|---|---|---|
| Introducción | Adoptantes innovadores; crecimiento lento; alta incertidumbre | No — superada |
| Crecimiento temprano | Aceleración; entrada de mayoría temprana; efecto imitación creciente | No — superada |
| Crecimiento tardío | Tasas absolutas máximas; moderación relativa; mayoría tardía entrando | **Sí — fase actual** |
| Saturación | Desaceleración marcada; mercado de reposición dominante; rezagados | Próxima — horizonte 2028-2032 |
| Madurez | Crecimiento nulo o negativo en nuevos adoptantes; mercado estabilizado | Proyectada — post-2033 |

Esta clasificación tiene implicaciones estratégicas directas: las empresas que aún compiten por cuota de mercado en nuevos adoptantes tienen una ventana temporal limitada antes de que el mercado transite hacia una lógica de reposición y fidelización.

---

# §6 MARCO TEÓRICO

## 6.1 Fundamentos de los Modelos de Difusión de Innovaciones

Los modelos de difusión de innovaciones parten de un supuesto central: la adopción de una tecnología en una población no ocurre de forma instantánea ni aleatoria, sino que sigue un proceso social estructurado en el que la información, la imitación y las características del adoptante interactúan para producir patrones predecibles en el tiempo.

La arquitectura teórica común a todos los modelos evaluados puede describirse mediante tres componentes fundamentales:

| Componente | Descripción conceptual | Parámetro asociado |
|---|---|---|
| Mercado potencial | Número máximo de adoptantes posibles dado el entorno | M (o N) |
| Efecto innovación | Adopción impulsada por exposición externa (publicidad, regulación) | p (coeficiente de innovación) |
| Efecto imitación | Adopción impulsada por contacto con adoptantes previos | q (coeficiente de imitación) |

La tensión entre el efecto innovación y el efecto imitación determina la forma de la curva: cuando la imitación domina sobre la innovación, la curva es más pronunciada y el despegue más tardío pero más acelerado. Cuando la innovación domina, el crecimiento es más gradual y sostenido desde el inicio.

## 6.2 Descripción de los Modelos Evaluados

### Modelo Bass Clásico
Es el modelo fundacional del campo. Asume un mercado homogéneo con dos tipos de adoptantes: innovadores (influenciados por comunicación masiva) e imitadores (influenciados por el boca a boca). Su elegancia reside en la parsimonia: tres parámetros (M, p, q) capturan la dinámica esencial. Su limitación principal es precisamente esa parsimonia: no puede representar heterogeneidad de mercado ni efectos de variables externas.

### Modelo Dual Market
Extiende la lógica del Bass Clásico reconociendo que el mercado total está compuesto por dos submercados con parámetros de difusión distintos. Cada submercado tiene su propio potencial, su propio coeficiente de innovación y su propio coeficiente de imitación. El agregado observado es la suma de dos procesos de difusión simultáneos pero asíncronos. Este modelo es teóricamente superior cuando existe evidencia empírica o conceptual de segmentación estructural del mercado.

### Modelo Fourt & Woodlock
Diseñado originalmente para bienes de consumo de alta frecuencia de compra (*frequently purchased consumer goods*). Asume que la adopción es proporcional al mercado no penetrado en cada período, sin efecto de imitación explícito. Su inadecuación para el mercado EV —reflejada en el ajuste más bajo del conjunto— es teóricamente coherente: los vehículos eléctricos son bienes de compra infrecuente con fuerte efecto de imitación social, exactamente lo opuesto al perfil para el que este modelo fue concebido.

### Modelo Gompertz
Basado en la función de Gompertz, produce una curva sigmoidea asimétrica: el crecimiento alcanza su máximo antes del punto medio de saturación y la desaceleración posterior es más gradual. Es apropiado cuando los adoptantes tempranos son desproporcionadamente más numerosos que los tardíos. Ofrece buen ajuste global pero puede subestimar el crecimiento en fases intermedias.

### Modelo Bass Generalizado (GBM)
Incorpora variables de marketing mix (precio, publicidad, distribución) como moduladores de los coeficientes de difusión. Permite que p y q varíen en el tiempo en función de decisiones estratégicas observables. Su mayor complejidad paramétrica puede ser una ventaja cuando se dispone de datos de variables de control, pero introduce riesgo de sobreajuste cuando esos datos son escasos o aproximados.

### Modelo Horsky & Simon
Introduce explícitamente el precio como variable explicativa del coeficiente de innovación, reconociendo que la disposición a ser adoptante temprano es función decreciente del precio. Es particularmente relevante en mercados donde la reducción de costes ha sido un motor documentado de la adopción, como ocurre con las baterías de iones de litio en el mercado EV.

### Modelo Muller & Yogev
Extiende el marco de Bass para incorporar la heterogeneidad de los adoptantes en términos de su utilidad percibida del producto. Reconoce que distintos segmentos de la población tienen umbrales de adopción distintos y que el proceso de difusión es, en parte, un proceso de superación secuencial de esos umbrales. Ofrece un ajuste muy competitivo en este análisis.

### Modelo Van den Bulte & Joshi
Incorpora efectos de estatus social y señalización en el proceso de adopción. Reconoce que parte de la utilidad de adoptar una tecnología proviene de la distinción social que confiere al adoptante temprano, y que esta utilidad disminuye a medida que la tecnología se masifica. Es teóricamente relevante para el mercado EV, donde la señalización de valores ambientales y estatus tecnológico ha sido documentada como motivador de adopción temprana.

### Modelo Difusión Logística R&K
Variante del modelo logístico estándar con parametrización alternativa que permite mayor flexibilidad en la forma de la curva. Asume simetría en la curva de adopción alrededor del punto de inflexión. Ofrece buen ajuste y es computacionalmente robusto, aunque su supuesto de simetría puede ser restrictivo.

### Modelo Ladrón-de-Guevara & Putsis
Extiende el marco de Bass para mercados con competencia entre tecnologías alternativas o entre generaciones sucesivas de un mismo producto. Incorpora efectos de sustitución y complementariedad entre productos. Su aplicación al mercado EV es conceptualmente válida dado que los vehículos eléctricos

## 2. Datos Históricos

| Año | Adopción (M) |
|---|---|
| 2015 | 1.26 M |
| 2016 | 2.00 M |
| 2017 | 3.10 M |
| 2018 | 5.00 M |
| 2019 | 7.20 M |
| 2020 | 10.00 M |
| 2021 | 16.25 M |
| 2022 | 26.00 M |
| 2023 | 40.00 M |
| 2024 | 58.00 M |
| 2025 | 74.00 M |


## 3. Métricas

| Modelo | R² | MAPE | Score | k |
|---|---|---|---|---|
| Bass Clásico | 0.9978 | 25.30% | 94.45 | 3 |
| Dual Market | 0.9997 | 11.65% | 97.09 | 6 |
| Fourt & Woodlock | 0.7434 | 110.86% | 59.47 | 2 |
| Gompertz | 0.9971 | 20.46% | 96.27 | 3 |
| Bass Generalizado (GBM) | 0.9984 | 23.41% | 92.87 | 4 |
| Horsky & Simon | 0.9978 | 25.30% | 95.21 | 4 |
| Muller & Yogev | 0.9996 | 12.20% | 96.46 | 7 |
| Van den Bulte & Joshi | 0.9997 | 11.77% | 96.97 | 6 |
| Difusión Logística R&K | 0.9988 | 13.55% | 95.55 | 4 |
| Ladrón-de-Guevara & Putsis | 0.9978 | 25.30% | 94.45 | 5 |


## 4. Proyecciones

| Año | Dual Market (M) |
|---|---|
| 2026 | 85.94 M |
| 2027 | 93.16 M |
| 2028 | 97.07 M |
| 2029 | 99.07 M |
| 2030 | 100.05 M |
| 2031 | 100.53 M |
| 2032 | 100.77 M |
| 2033 | 100.88 M |
| 2034 | 100.94 M |
| 2035 | 100.97 M |


**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado (Dual Market): R²=0.9997, MAPE=11.65%, Score=97.09.

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
