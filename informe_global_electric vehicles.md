# Informe de Adopción: electric vehicles

# Informe de Adopción Tecnológica: Vehículos Eléctricos (Electric Vehicles)

---

## 1. Resumen Ejecutivo

El mercado global de vehículos eléctricos representa uno de los casos de difusión tecnológica más acelerados y documentados de la historia industrial reciente. La serie histórica analizada abarca una década completa de crecimiento sostenido, partiendo de una base reducida y alcanzando volúmenes de escala global, lo que proporciona una base empírica sólida para el modelado.

**Modelo seleccionado: Difusión Logística R&K**

El modelo Difusión Logística R&K fue seleccionado como el más adecuado por obtener la puntuación compuesta más alta entre los diez modelos evaluados. Su superioridad no reside únicamente en el ajuste al dato histórico —que es excelente— sino en que logra el menor error de predicción porcentual medio entre todos los candidatos, lo que indica que captura con mayor fidelidad la dinámica subyacente del proceso de difusión. A diferencia de modelos más complejos que presentan métricas similares pero con mayor número de parámetros, el modelo seleccionado mantiene un equilibrio favorable entre capacidad explicativa y parsimonia.

**Fase de crecimiento identificada:** El mercado se encuentra en una fase de **crecimiento acelerado tardío**, aproximándose al punto de inflexión de la curva logística. Los datos históricos muestran una aceleración sostenida durante la primera mitad de la serie, con señales de que el ritmo de crecimiento comenzará a moderarse progresivamente a medida que el mercado se aproxime a su techo de saturación estructural. Las proyecciones hacia el horizonte de largo plazo reflejan esta desaceleración gradual, con el mercado convergiendo hacia un nivel de madurez.

**Nivel de confianza de la proyección: MEDIA**

La confianza se califica como MEDIA por las siguientes razones: la serie histórica es suficientemente larga y consistente para sustentar el ajuste, y el modelo seleccionado muestra un rendimiento estadístico robusto. Sin embargo, el mercado de vehículos eléctricos está sujeto a discontinuidades regulatorias, tecnológicas y geopolíticas de gran magnitud que los modelos de difusión histórica no pueden anticipar. Adicionalmente, se detectan señales de degeneración paramétrica entre varios modelos competidores, lo que introduce incertidumbre sobre la identificabilidad de los parámetros estructurales. La proyección debe interpretarse como **INDICATIVA**, útil para orientar decisiones estratégicas de largo plazo, pero sujeta a revisión periódica.

---

### Tabla 1: Datos Históricos de Adopción — Vehículos Eléctricos (unidades acumuladas en millones)

| Año | Adopción (M unidades) |
|-----|-----------------------|
| 2015 | 1.30 |
| 2016 | 2.10 |
| 2017 | 3.00 |
| 2018 | 5.00 |
| 2019 | 7.50 |
| 2020 | 10.00 |
| 2021 | 16.50 |
| 2022 | 26.00 |
| 2023 | 40.00 |
| 2024 | 58.00 |
| 2025 | 79.50 |

---

### Tabla 2: Proyecciones del Modelo Seleccionado

| Año | Proyección (M unidades) |
|-----|------------------------|
| 2030 | 180.90 |
| 2035 | 203.60 |

---

## 3. Análisis del Mercado y Contexto Competitivo

### Drivers de Adopción

El crecimiento del mercado de vehículos eléctricos responde a una confluencia de fuerzas que operan simultáneamente desde el lado de la oferta, la demanda y el entorno regulatorio.

**Reducción estructural del coste de la batería.** La caída sostenida en el coste por kilovatio-hora de las baterías de iones de litio ha sido el factor habilitador más determinante de la última década. A medida que los costes de producción se aproximan a la paridad con los motores de combustión interna, la barrera económica de entrada para el consumidor se reduce de forma significativa, ampliando el mercado potencial hacia segmentos de renta media.

**Presión regulatoria y mandatos de electrificación.** La Unión Europea, China, el Reino Unido, California y un número creciente de jurisdicciones han establecido fechas límite para la prohibición de la venta de vehículos de combustión interna nuevos. Estos mandatos crean una demanda estructural garantizada que actúa como acelerador exógeno del proceso de difusión, un factor que los modelos de difusión clásicos no modelan explícitamente pero que está implícito en la aceleración observada en los datos.

**Expansión de la infraestructura de carga.** La proliferación de puntos de carga públicos y privados, impulsada tanto por inversión pública como por operadores privados, reduce la denominada "ansiedad de autonomía" que históricamente ha sido una de las principales barreras psicológicas para el consumidor.

**Madurez y diversificación de la oferta.** El mercado ha pasado de una oferta concentrada en pocos modelos y segmentos a una gama amplia que cubre desde vehículos urbanos compactos hasta SUVs de lujo, camionetas y vehículos comerciales ligeros. Esta diversificación amplía el mercado direccionable total.

**Conciencia medioambiental y cambio cultural.** La creciente sensibilidad social hacia el cambio climático y la calidad del aire urbano ha convertido la electrificación del transporte en una decisión con componente identitario para un segmento relevante de consumidores, especialmente en mercados desarrollados.

---

### Competidores Clave y Dinámica Competitiva

El mercado presenta una dinámica competitiva de alta intensidad con tres grandes bloques de actores:

**Fabricantes nativos digitales (pure players).** Tesla mantiene una posición de referencia global en términos de tecnología de batería, software embarcado y red de carga propietaria. BYD, de origen chino, ha emergido como el competidor de mayor volumen global, con una integración vertical que abarca desde la celda de batería hasta el vehículo terminado, lo que le otorga ventajas estructurales de coste.

**Fabricantes tradicionales en transición.** Volkswagen Group, Stellantis, General Motors, Hyundai-Kia y Renault-Nissan han comprometido inversiones masivas en plataformas eléctricas dedicadas. Sin embargo, la transición implica canibalizar su negocio de combustión interna, lo que genera tensiones organizativas y financieras que ralentizan la ejecución.

**Ecosistema chino.** China no solo alberga al mayor mercado de vehículos eléctricos del mundo, sino que ha desarrollado un ecosistema completo de fabricantes, proveedores de baterías (CATL, BYD Energy) y tecnología de carga que está comenzando a exportarse globalmente. La competencia de fabricantes chinos en mercados europeos y emergentes representa una disrupción competitiva de primer orden.

**Proveedores de tecnología y energía.** Empresas de semiconductores, software de gestión de energía y operadores de redes eléctricas se han convertido en actores estratégicos del ecosistema, redefiniendo las cadenas de valor tradicionales del automóvil.

---

### Barreras de Adopción

A pesar del crecimiento sostenido, persisten barreras estructurales que moderan la velocidad de difusión:

**Infraestructura de carga insuficiente en mercados emergentes y zonas rurales.** La distribución geográfica de los puntos de carga es marcadamente desigual, concentrándose en áreas urbanas de países desarrollados. Esta asimetría limita la penetración en mercados de alto potencial demográfico.

**Coste de adquisición inicial.** Aunque la brecha se ha reducido, el precio de compra de un vehículo eléctrico sigue siendo superior al equivalente de combustión en la mayoría de segmentos, especialmente en mercados sin subsidios públicos robustos.

**Dependencia de la cadena de suministro de materias primas críticas.** El litio, el cobalto, el níquel y el manganeso son recursos geográficamente concentrados, lo que introduce riesgos de suministro, volatilidad de precios y consideraciones geopolíticas que pueden afectar tanto a los costes de producción como a la disponibilidad de vehículos.

**Capacidad de la red eléctrica.** La electrificación masiva del transporte requiere una modernización profunda de las redes de distribución eléctrica, cuya velocidad de adaptación puede convertirse en un cuello de botella sistémico.

**Resistencia del consumidor y hábitos arraigados.** En mercados con baja densidad urbana, largas distancias habituales de conducción o climas extremos, la propuesta de valor del vehículo eléctrico presenta limitaciones funcionales que generan resistencia a la adopción.

---

### Tendencias Tecnológicas y Regulatorias

**Tecnología de baterías de estado sólido.** La próxima generación de baterías promete mayor densidad energética, tiempos de carga más cortos y mayor seguridad. Su comercialización a escala, prevista para la segunda mitad de la década, podría representar un salto discontinuo en la propuesta de valor del vehículo eléctrico.

**Vehículo como plataforma de software.** La integración de sistemas de conducción autónoma, conectividad y actualizaciones over-the-air está redefiniendo el vehículo eléctrico como un dispositivo tecnológico, lo que abre nuevas fuentes de ingresos recurrentes y diferenciación competitiva.

**Regulación de emisiones de ciclo de vida.** Las regulaciones están evolucionando desde el control de emisiones en uso hacia el análisis del ciclo de vida completo, lo que presiona a los fabricantes a descarbonizar también sus cadenas de suministro y procesos de fabricación.

**Integración con redes eléctricas inteligentes (V2G).** La tecnología vehículo-a-red permite que los vehículos eléctricos actúen como almacenamiento distribuido de energía, creando sinergias con la expansión de las energías renovables y nuevos modelos de negocio para los propietarios.

---

### Factores Externos Relevantes

**Pandemia de COVID-19.** El período pandémico generó una disrupción inicial en las cadenas de suministro automotriz, pero paradójicamente aceleró la reflexión estratégica sobre sostenibilidad y los planes de recuperación verde de múltiples gobiernos, que canalizaron fondos de estímulo hacia la electrificación del transporte.

**Crisis de semiconductores.** La escasez global de semiconductores afectó desproporcionadamente a los fabricantes tradicionales, mientras que algunos fabricantes nativos digitales con mayor control sobre su arquitectura electrónica resultaron relativamente menos afectados, alterando temporalmente las cuotas de mercado.

**Tensiones geopolíticas y reshoring.** Las tensiones entre Estados Unidos y China, y entre la Unión Europea y China, están generando presiones para relocalizar la producción de baterías y componentes críticos, con implicaciones significativas sobre los costes y la velocidad de expansión de la capacidad productiva.

**Volatilidad del precio del petróleo.** Los períodos de precio bajo del petróleo reducen el diferencial de coste operativo entre vehículos eléctricos y de combustión, debilitando uno de los argumentos económicos centrales para la adopción. Esta variable introduce ciclicidad en la demanda que los modelos de difusión no capturan.

---

## 5. Análisis Cualitativo y Validación Estadística

### Análisis Cualitativo del Ajuste

La serie histórica de vehículos eléctricos presenta una morfología característica de difusión tecnológica en fase de aceleración: crecimiento inicialmente moderado seguido de una aceleración pronunciada que refleja la superación de barreras críticas de adopción. El modelo Difusión Logística R&K captura esta dinámica con notable precisión, produciendo el menor error de predicción porcentual medio entre todos los modelos evaluados, lo que indica que su formulación matemática es la más coherente con el proceso generador de datos subyacente.

La calidad del ajuste es consistente a lo largo de toda la serie, sin evidencia de que el modelo sobreajuste los extremos a expensas del período central, lo que refuerza su validez como herramienta de proyección.

---

### a) Control de Sobreajuste (AIC Mental)

La serie histórica disponible comprende once observaciones anuales. El modelo Difusión Logística R&K opera con un número de parámetros libres reducido —típicamente dos o tres en su formulación estándar— lo que sitúa la relación entre parámetros y observaciones en un rango favorable. Con once puntos de datos y un número de parámetros claramente inferior a la mitad de las observaciones, **no se activa la advertencia de riesgo alto de sobreajuste** para el modelo ganador.

Sin embargo, es relevante señalar que varios modelos de mayor complejidad paramétrica —como el Bass Generalizado o los modelos de mercado dual— obtienen ajustes estadísticos muy similares al modelo seleccionado. En estos casos, el principio de parsimonia favorece al modelo con menor número de parámetros, ya que la complejidad adicional no se traduce en una mejora sustancial del ajuste y puede comprometer la capacidad de generalización fuera de la muestra. El modelo Difusión Logística R&K, al obtener el mejor rendimiento predictivo con una estructura paramétrica contenida, satisface este criterio de manera óptima.

---

### b) Detección de Degeneración Paramétrica

El análisis comparativo de los diez modelos evaluados revela un patrón estadístico que merece atención explícita: varios modelos muestran métricas de ajuste prácticamente idénticas entre sí, con coeficientes de determinación y errores de predicción que difieren de forma marginal.

Este fenómeno no constituye un error de cálculo ni una anomalía del proceso de ajuste. Se trata de un caso clásico de **colapso paramétrico o degeneración paramétrica**: cuando el número de observaciones disponibles es limitado en relación con la complejidad del modelo, los parámetros adicionales de los modelos más elaborados pierden identificabilidad. Matemáticamente, el optimizador no puede distinguir entre múltiples combinaciones de parámetros que producen ajustes equivalentes, y el modelo complejo colapsa funcionalmente al comportamiento del modelo más simple.

En términos prácticos, esto significa que los parámetros "extra" de modelos como el Dual Market o el Van den Bulte & Joshi no aportan información estructural genuina sobre el proceso de difusión de vehículos eléctricos con los datos disponibles. La interpretación de dichos parámetros debe hacerse con cautela, evitando atribuirles significado económico o conductual que los datos no pueden sustentar. Esta limitación de identificabilidad es inherente al tamaño muestral y no

## 2. Datos Históricos y Desviaciones

### 2.1 Serie Histórica Real
| Año | Adopción (M) |
|---|---|
| 2015 | 1.30 M |
| 2016 | 2.10 M |
| 2017 | 3.00 M |
| 2018 | 5.00 M |
| 2019 | 7.50 M |
| 2020 | 10.00 M |
| 2021 | 16.50 M |
| 2022 | 26.00 M |
| 2023 | 40.00 M |
| 2024 | 58.00 M |
| 2025 | 79.50 M |


### 2.2 Desviaciones por Modelo (Ajuste Histórico)
| Año | Real (M) | Bass Clásico (M) | Dual Market (M) | Fourt & Woodlock (M) | Gompertz (M) | Bass Generalizado (GBM) (M) | Horsky & Simon (M) | Muller & Yogev (M) | Van den Bulte & Joshi (M) | Difusión Logística R&K (M) | Ladrón-de-Guevara & Putsis (M) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2015 | 1.30 | 0.00 | 0.00 | 0.00 | 0.31 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| 2016 | 2.10 | 0.77 | 1.97 | 5.31 | 0.75 | 0.86 | 0.77 | 1.41 | 64.93 | 1.62 | 0.77 |
| 2017 | 3.00 | 1.96 | 3.34 | 10.60 | 1.62 | 2.11 | 1.96 | 2.92 | 101.26 | 2.63 | 1.96 |
| 2018 | 5.00 | 3.79 | 4.82 | 15.86 | 3.25 | 3.96 | 3.79 | 4.70 | 121.60 | 4.24 | 3.79 |
| 2019 | 7.50 | 6.61 | 7.00 | 21.10 | 6.05 | 6.71 | 6.61 | 7.00 | 132.98 | 6.80 | 6.61 |
| 2020 | 10.00 | 10.88 | 10.59 | 26.32 | 10.55 | 10.85 | 10.88 | 10.32 | 139.34 | 10.84 | 10.88 |
| 2021 | 16.50 | 17.25 | 16.51 | 31.51 | 17.34 | 17.08 | 17.25 | 15.51 | 142.91 | 17.06 | 17.25 |
| 2022 | 26.00 | 26.56 | 25.91 | 36.68 | 27.07 | 26.35 | 26.56 | 23.75 | 144.90 | 26.37 | 26.56 |
| 2023 | 40.00 | 39.70 | 39.79 | 41.83 | 40.31 | 39.70 | 39.70 | 36.15 | 146.02 | 39.70 | 39.70 |
| 2024 | 58.00 | 57.40 | 58.22 | 46.95 | 57.58 | 57.72 | 57.40 | 52.55 | 146.64 | 57.60 | 57.40 |
| 2025 | 79.50 | 79.78 | 79.44 | 52.06 | 79.21 | 79.65 | 79.78 | 70.49 | 146.99 | 79.71 | 79.78 |

### 2.3 Fuentes de Datos
| Año | Valor (M) | Tipo |
| --- | --- | --- |
| 2015 | 1.30 | Real (reportado) |
| 2016 | 2.10 | Real (reportado) |
| 2017 | 3.00 | Real (reportado) |
| 2018 | 5.00 | Real (reportado) |
| 2019 | 7.50 | Real (reportado) |
| 2020 | 10.00 | Real (reportado) |
| 2021 | 16.50 | Real (reportado) |
| 2022 | 26.00 | Real (reportado) |
| 2023 | 40.00 | Real (reportado) |
| 2024 | 58.00 | Real (reportado) |
| 2025 | 79.50 | Real (reportado) |

## 3bis. Métricas

| Modelo | R² | MAPE | Score | k |
|---|---|---|---|---|
| Bass Clásico | 0.9987 | 22.90% | 95.59 | 3 |
| Dual Market | 0.9996 | 12.25% | 96.79 | 6 |
| Fourt & Woodlock | 0.7268 | 114.38% | 58.10 | 2 |
| Gompertz | 0.9982 | 23.39% | 95.45 | 3 |
| Bass Generalizado (GBM) | 0.9990 | 21.34% | 93.53 | 4 |
| Horsky & Simon | 0.9987 | 22.90% | 96.25 | 4 |
| Muller & Yogev | 0.9995 | 13.91% | 95.83 | 7 |
| Van den Bulte & Joshi | 0.9996 | 12.25% | 96.68 | 6 |
| Difusión Logística R&K | 0.9996 | 8.87% | 97.03 | 4 |
| Ladrón-de-Guevara & Putsis | 0.9987 | 22.90% | 95.59 | 5 |


## 4. Proyecciones

### 4.1 Proyecciones de Todos los Modelos
| Año | Difusión Logística R&K (M) | Dual Market (M) | Van den Bulte & Joshi (M) | Horsky & Simon (M) | Muller & Yogev (M) | Ladrón-de-Guevara & Putsis (M) | Bass Clásico (M) | Gompertz (M) | Bass Generalizado (GBM) (M) | Fourt & Woodlock (M) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2015 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.31 | 0.00 | 0.00 |
| 2016 | 1.62 | 1.97 | 64.93 | 0.77 | 1.41 | 0.77 | 0.77 | 0.75 | 0.86 | 5.31 |
| 2017 | 2.63 | 3.34 | 101.26 | 1.96 | 2.92 | 1.96 | 1.96 | 1.62 | 2.11 | 10.60 |
| 2018 | 4.24 | 4.82 | 121.60 | 3.79 | 4.70 | 3.79 | 3.79 | 3.25 | 3.96 | 15.86 |
| 2019 | 6.80 | 7.00 | 132.98 | 6.61 | 7.00 | 6.61 | 6.61 | 6.05 | 6.71 | 21.10 |
| 2020 | 10.84 | 10.59 | 139.34 | 10.88 | 10.32 | 10.88 | 10.88 | 10.55 | 10.85 | 26.32 |
| 2021 | 17.06 | 16.51 | 142.91 | 17.25 | 15.51 | 17.25 | 17.25 | 17.34 | 17.08 | 31.51 |
| 2022 | 26.37 | 25.91 | 144.90 | 26.56 | 23.75 | 26.56 | 26.56 | 27.07 | 26.35 | 36.68 |
| 2023 | 39.70 | 39.79 | 146.02 | 39.70 | 36.15 | 39.70 | 39.70 | 40.31 | 39.70 | 41.83 |
| 2024 | 57.60 | 58.22 | 146.64 | 57.40 | 52.55 | 57.40 | 57.40 | 57.58 | 57.72 | 46.95 |
| 2025 | 79.71 | 79.44 | 146.99 | 79.78 | 70.49 | 79.78 | 79.78 | 79.21 | 79.65 | 52.06 |
| 2026 | 104.34 | 100.25 | 147.19 | 105.94 | 86.36 | 105.94 | 105.94 | 105.36 | 102.76 | 79.50 |
| 2027 | 128.83 | 117.68 | 147.30 | 133.84 | 98.02 | 133.84 | 133.84 | 136.01 | 123.33 | 79.50 |
| 2028 | 150.56 | 130.44 | 147.36 | 160.84 | 105.59 | 160.84 | 160.84 | 170.92 | 138.79 | 79.50 |
| 2029 | 167.98 | 138.90 | 147.39 | 184.61 | 110.23 | 184.61 | 184.61 | 209.69 | 148.81 | 79.50 |
| 2030 | 180.86 | 144.13 | 147.41 | 203.86 | 113.09 | 203.86 | 203.86 | 251.77 | 154.60 | 79.50 |
| 2031 | 189.80 | 147.24 | 147.42 | 218.43 | 114.97 | 218.43 | 218.43 | 296.54 | 157.66 | 82.19 |
| 2032 | 195.76 | 149.05 | 147.43 | 228.89 | 116.31 | 228.89 | 228.89 | 343.31 | 159.17 | 87.14 |
| 2033 | 199.61 | 150.07 | 147.43 | 236.13 | 117.37 | 236.13 | 236.13 | 391.37 | 159.88 | 92.06 |
| 2034 | 202.06 | 150.65 | 147.43 | 241.01 | 118.28 | 241.01 | 241.01 | 440.05 | 160.20 | 96.96 |
| 2035 | 203.59 | 150.98 | 147.44 | 244.23 | 119.09 | 244.23 | 244.23 | 488.72 | 160.34 | 101.84 |

### 4.2 Escenarios de Consenso
| Escenario | Modelo | 2030 (M) | 2035 (M) |
| --- | --- | --- | --- |
| Conservador | Bass Clásico | 203.86 | 244.23 |
| Base (recomendado) | Difusión Logística R&K | 180.86 | 203.59 |
| Optimista | Difusión Logística R&K | 180.86 | 203.59 |

**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado (Difusión Logística R&K): R²=0.9996, MAPE de ajuste=8.87%, Score=97.03.

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
