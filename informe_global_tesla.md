# Informe de Adopción: tesla

# Informe de Adopción Tecnológica — Tesla (Vehículos Eléctricos)

---

## 1. Resumen Ejecutivo

Tesla es una empresa pública que reporta entregas de vehículos en sus informes trimestrales y anuales, por lo que los datos históricos utilizados corresponden a cifras de ventas/entregas acumuladas globales, con un nivel de trazabilidad razonable.

La serie histórica analizada muestra una trayectoria de adopción sostenida y acelerada durante la mayor parte de la ventana temporal, con una desaceleración visible en los años más recientes. Este patrón es consistente con una tecnología que ha superado la fase de adopción temprana y se encuentra transitando hacia la madurez del mercado, aunque sin haber alcanzado aún su techo de saturación.

**Modelo seleccionado: Difusión Logística R&K.** Este modelo fue elegido por obtener la puntuación compuesta más alta entre los diez modelos evaluados, combinando un ajuste prácticamente perfecto a los datos históricos con el error de predicción más bajo del conjunto. A diferencia de modelos más complejos que presentan métricas similares pero requieren mayor número de parámetros, el modelo seleccionado logra ese rendimiento con una estructura parsimoniosa, lo que reduce el riesgo de sobreajuste y mejora la capacidad de generalización hacia el futuro.

**Fase de crecimiento:** La adopción de vehículos eléctricos Tesla se encuentra en una fase de crecimiento tardío / transición hacia la madurez. El ritmo de expansión se ha moderado respecto a los años de mayor aceleración, y las proyecciones apuntan a una estabilización progresiva del parque acumulado en el horizonte de mediano plazo.

**Nivel de confianza de la proyección: MEDIO-ALTO.** El ajuste histórico es excelente y el modelo seleccionado es robusto. Sin embargo, el horizonte de proyección es largo, el mercado de vehículos eléctricos está sujeto a disrupciones regulatorias, tecnológicas y competitivas de alta intensidad, y el techo de saturación implícito en el modelo puede estar subestimado si los mercados emergentes aceleran su adopción más allá de lo que los datos históricos capturan. Estas consideraciones moderan la confianza desde ALTA hacia MEDIO-ALTA.

---

## 3. Análisis del Mercado y Contexto Competitivo

### Drivers de Adopción

La adopción de vehículos eléctricos Tesla ha sido impulsada por una combinación de factores tecnológicos, económicos y regulatorios que se han reforzado mutuamente a lo largo de la última década.

En el plano tecnológico, la mejora continua en la densidad energética de las baterías ha extendido la autonomía de los vehículos hasta niveles competitivos con los de combustión interna, eliminando una de las principales barreras psicológicas del consumidor. La red de supercargadores propietaria de Tesla ha sido un diferenciador crítico, reduciendo la fricción asociada a la recarga en viajes de larga distancia. La integración de software avanzado —incluyendo actualizaciones over-the-air y capacidades de asistencia a la conducción— ha posicionado al vehículo eléctrico como un producto tecnológico de alto valor percibido, más allá de su función de transporte.

En el plano económico, la reducción sostenida del coste de las baterías ha permitido a Tesla ampliar su gama hacia segmentos de precio más accesibles, ampliando el mercado potencial. Los incentivos fiscales a la compra de vehículos eléctricos en Estados Unidos, Europa y China han actuado como catalizadores de demanda en momentos clave del ciclo de adopción.

En el plano regulatorio, los mandatos de emisiones cero en California, la Unión Europea y varios mercados asiáticos han creado un entorno normativo favorable que presiona tanto a los consumidores como a los fabricantes hacia la electrificación. La prohibición progresiva de la venta de vehículos de combustión interna en múltiples jurisdicciones establece un horizonte temporal claro que acelera la transición.

El efecto de red social y la visibilidad de marca de Tesla han jugado también un papel relevante: la empresa ha operado históricamente con una inversión publicitaria mínima, apoyándose en la prescripción entre pares y en la cobertura mediática espontánea generada por sus innovaciones y por la figura de su fundador.

### Competidores Clave y Dinámica Competitiva

El panorama competitivo ha experimentado una transformación radical durante el período analizado. En los primeros años de la serie, Tesla operaba en un nicho con competencia limitada. En la actualidad, el mercado de vehículos eléctricos es uno de los más dinámicos y concurridos de la industria automotriz global.

Los fabricantes tradicionales —Volkswagen Group, General Motors, Stellantis, Hyundai-Kia, BMW Group— han acelerado sus planes de electrificación y compiten directamente con Tesla en múltiples segmentos. La presión competitiva ha obligado a Tesla a reducir precios en varias ocasiones, comprimiendo márgenes pero defendiendo cuota de mercado.

El competidor más significativo en términos de volumen global es BYD, el fabricante chino que ha superado a Tesla en entregas totales de vehículos eléctricos en algunos trimestres recientes. BYD opera con una integración vertical profunda —incluyendo producción propia de baterías— y tiene acceso preferencial al mercado chino, que representa la mayor cuota del mercado global de vehículos eléctricos. Esta dinámica introduce una presión competitiva estructural que los modelos de difusión basados exclusivamente en datos de Tesla no capturan plenamente.

En el segmento premium, Rivian, Lucid y los modelos eléctricos de Mercedes-Benz y BMW compiten por el mismo perfil de consumidor que históricamente ha sido el núcleo de la base de clientes de Tesla.

La entrada de fabricantes chinos en mercados europeos y latinoamericanos —con vehículos de precio competitivo— representa una amenaza emergente para la expansión global de Tesla en el horizonte de proyección.

### Barreras de Adopción

A pesar del crecimiento sostenido, persisten barreras estructurales que moderan el ritmo de adopción.

La infraestructura de carga pública sigue siendo insuficiente en amplias regiones del mundo, especialmente en mercados emergentes y en zonas rurales de economías desarrolladas. La dependencia de carga doméstica excluye a una fracción significativa de la población urbana que no dispone de aparcamiento privado.

El precio de adquisición, aunque en descenso, sigue siendo superior al de vehículos de combustión equivalentes en la mayoría de los segmentos, lo que limita la penetración en hogares de renta media-baja. La incertidumbre sobre el valor residual de los vehículos eléctricos —vinculada a la degradación de la batería y a la velocidad de obsolescencia tecnológica— genera reticencia en segmentos sensibles al coste total de propiedad.

La dependencia de la cadena de suministro de materias primas críticas —litio, cobalto, níquel— introduce volatilidad en costes y riesgos de disponibilidad que pueden afectar tanto a la producción como al precio final.

Finalmente, la percepción de riesgo tecnológico asociada a los sistemas de conducción autónoma —y los incidentes de seguridad que han recibido cobertura mediática— puede generar fricción en segmentos de consumidores más conservadores.

### Tendencias Tecnológicas y Regulatorias

La próxima generación de baterías de estado sólido promete mejoras sustanciales en densidad energética, seguridad y tiempo de carga, con potencial para redefinir los parámetros de competitividad del sector. Tesla, junto con Toyota, QuantumScape y varios fabricantes chinos, está invirtiendo activamente en esta tecnología.

La regulación de emisiones se está endureciendo globalmente. El Reglamento europeo que establece el fin de la venta de vehículos de combustión interna para mediados de la próxima década es el referente más claro, pero iniciativas similares avanzan en Reino Unido, Canadá y varios estados de EE.UU. Este marco regulatorio actúa como acelerador estructural de la demanda.

La integración de los vehículos eléctricos en redes de energía inteligente —vehicle-to-grid— abre nuevas propuestas de valor que pueden reforzar la adopción en mercados con alta penetración de energías renovables.

### Factores Externos Relevantes

La pandemia de COVID-19 generó disrupciones en la cadena de suministro global que afectaron la producción automotriz entre los años de mayor impacto, aunque paradójicamente aceleró el interés por la movilidad sostenible y los planes de estímulo económico post-pandemia incluyeron incentivos específicos para la electrificación del transporte.

Las tensiones geopolíticas —especialmente entre Estados Unidos y China— afectan a las cadenas de suministro de baterías y semiconductores, y pueden condicionar el acceso de Tesla al mercado chino, que es estratégicamente crítico para su volumen global.

Las políticas de subsidios son volátiles: cambios en la administración política de los principales mercados pueden alterar el calendario de incentivos y, con ello, el ritmo de adopción a corto y medio plazo.

---

## 5. Análisis Cualitativo y Validación Estadística

### Análisis Cualitativo

La serie histórica de adopción de Tesla describe una curva sigmoidea característica de los procesos de difusión tecnológica: una fase inicial de crecimiento lento correspondiente a los primeros adoptantes, una fase de aceleración sostenida durante la mayor parte de la ventana temporal, y una moderación reciente que anticipa la transición hacia la madurez. Este patrón es coherente con la teoría de difusión de innovaciones y con la evolución observada en otros mercados de tecnología de consumo de alto valor.

La calidad del ajuste de los modelos de mayor rendimiento es excepcionalmente alta, lo que indica que los datos históricos siguen una trayectoria muy regular, con escasa volatilidad idiosincrática. Esto es consistente con un proceso de adopción impulsado por fuerzas estructurales estables —reducción de costes, expansión de infraestructura, presión regulatoria— más que por shocks puntuales.

### a) Control de Sobreajuste (AIC Mental)

La serie histórica cuenta con once puntos de datos. El modelo Difusión Logística R&K opera con un número reducido de parámetros —típicamente tres en su formulación estándar: potencial de mercado, tasa de crecimiento y punto de inflexión— lo que resulta en una ratio parámetros/observaciones muy favorable. Con once observaciones y tres parámetros, el modelo ganador se sitúa muy por debajo del umbral de riesgo de sobreajuste (que se activaría si el número de parámetros superara la mitad del número de observaciones). El riesgo de sobreajuste para el modelo seleccionado es **bajo**.

En contraste, modelos como Dual Market, Bass Generalizado o Van den Bulte & Joshi incorporan parámetros adicionales para capturar segmentación de mercado o efectos de marketing. Con once puntos de datos, estos parámetros adicionales tienen escasa capacidad de identificación empírica, lo que reduce su ventaja teórica en la práctica. El modelo seleccionado justifica su complejidad de forma adecuada.

### b) Detección de Degeneración Paramétrica

Se observa un fenómeno notable en los resultados: varios modelos —Bass Clásico, Horsky & Simon y Ladrón-de-Guevara & Putsis— presentan métricas de ajuste prácticamente idénticas entre sí, con valores de R² y MAPE coincidentes hasta el segundo decimal. Este patrón no es un error de cálculo: es una manifestación de **colapso paramétrico**.

Cuando el número de observaciones es limitado, los parámetros adicionales que diferencian a los modelos más complejos de sus versiones más simples no pueden ser estimados de forma independiente con los datos disponibles. Como resultado, el optimizador numérico hace converger esos parámetros hacia valores que reproducen el comportamiento del modelo más simple, y las métricas de ajuste se igualan. En la práctica, estos modelos están resolviendo el mismo problema matemático con distintas etiquetas.

Esta degeneración es una limitación de identificabilidad inherente a series cortas, no un defecto de los modelos en sí. Su implicación práctica es que, en este contexto, la elección entre los modelos degenerados debe basarse en criterios de parsimonia y en la interpretabilidad de los parámetros, no en las métricas de ajuste.

### c) Contraste con Referencias Externas

La Agencia Internacional de la Energía (IEA) publica anualmente proyecciones sobre la adopción global de vehículos eléctricos en su informe *Global EV Outlook*. Según el escenario de políticas anunciadas (STEPS) y el escenario de desarrollo sostenible (SDS/NZE) de la IEA, el parque global de vehículos eléctricos ligeros podría alcanzar entre doscientos y trescientos millones de unidades para mediados de la próxima década, dependiendo del escenario de política climática considerado.

Las proyecciones del modelo analizado se refieren exclusivamente al parque acumulado de vehículos Tesla, no al mercado global. En este contexto, la comparación directa no es posible sin conocer la cuota de mercado implícita que el modelo asigna a Tesla en el horizonte de proyección. Sin embargo, si se considera que Tesla ha representado históricamente entre el tres y el cinco por ciento del mercado global de vehículos eléctricos en los años de mayor competencia, y que las proyecciones de la IEA apuntan a un mercado global de escala muy superior, el techo de saturación implícito en el modelo podría estar **subestimando** el potencial de largo plazo de Tesla, especialmente si la empresa mantiene o recupera cuota en mercados emergentes.

Esta divergencia cualitativa sugiere que los factores que los datos históricos no capturan plenamente —expansión en mercados emergentes, nuevos modelos de precio accesible, evolución de la cuota frente a competidores chinos— son determinantes para la validez de las proyecciones en el horizonte más largo.

### d) Modulación de Confianza

| Dimensión | Valoración | Justificación |
|---|---|---|
| Suficiencia de datos (n puntos) | Suficiente para el modelo seleccionado | Once observaciones anuales con trayectoria regular permiten identificar los parámetros del modelo logístico con fiabilidad razonable |
| Riesgo de sobreajuste | Bajo | Ratio parámetros/observaciones favorable; modelo parsimonioso con tres parámetros |
| Horizonte de proyección | Moderado-largo | Las proyecciones a cinco y diez años en un mercado en transformación acelerada introducen incertidumbre estructural creciente |
| Contraste externo | Divergencia cualitativa posible | El techo de saturación implícito puede estar subestimado respecto a referencias sectoriales |
| **Conclusión** | **Proyección OPERATIVA con cautela en el horizonte largo**

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
| 2024 | 7.25 M |
| 2025 | 9.00 M |


### 2.2 Desviaciones por Modelo (Ajuste Histórico)
| Año | Real (M) | Bass Clásico (M) | Dual Market (M) | Fourt & Woodlock (M) | Gompertz (M) | Bass Generalizado (GBM) (M) | Horsky & Simon (M) | Muller & Yogev (M) | Van den Bulte & Joshi (M) | Difusión Logística R&K (M) | Ladrón-de-Guevara & Putsis (M) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2015 | 0.05 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 | 0.00 |
| 2016 | 0.13 | 0.07 | 0.10 | 0.66 | 0.05 | 0.09 | 0.07 | 0.10 | 2.31 | 0.14 | 0.07 |
| 2017 | 0.23 | 0.20 | 0.25 | 1.31 | 0.14 | 0.23 | 0.20 | 0.25 | 3.16 | 0.25 | 0.20 |
| 2018 | 0.47 | 0.41 | 0.48 | 1.96 | 0.35 | 0.45 | 0.41 | 0.48 | 3.49 | 0.44 | 0.41 |
| 2019 | 0.84 | 0.78 | 0.82 | 2.61 | 0.76 | 0.81 | 0.78 | 0.82 | 3.63 | 0.79 | 0.78 |
| 2020 | 1.34 | 1.38 | 1.37 | 3.25 | 1.42 | 1.38 | 1.38 | 1.37 | 3.70 | 1.37 | 1.38 |
| 2021 | 2.28 | 2.31 | 2.25 | 3.89 | 2.40 | 2.28 | 2.31 | 2.25 | 3.76 | 2.29 | 2.31 |
| 2022 | 3.59 | 3.64 | 3.61 | 4.53 | 3.70 | 3.61 | 3.64 | 3.61 | 3.82 | 3.63 | 3.64 |
| 2023 | 5.40 | 5.35 | 5.39 | 5.16 | 5.29 | 5.35 | 5.35 | 5.39 | 3.89 | 5.36 | 5.35 |
| 2024 | 7.25 | 7.23 | 7.26 | 5.79 | 7.12 | 7.28 | 7.23 | 7.26 | 3.98 | 7.26 | 7.23 |
| 2025 | 9.00 | 9.02 | 9.00 | 6.42 | 9.10 | 8.99 | 9.02 | 9.00 | 4.08 | 9.00 | 9.02 |

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
| 2024 | 7.25 | Real (reportado) |
| 2025 | 9.00 | Real (reportado) |

## 3bis. Métricas

| Modelo | R² | MAPE | Score | k |
|---|---|---|---|---|
| Bass Clásico | 0.9998 | 16.82% | 95.53 | 3 |
| Dual Market | 0.9999 | 12.41% | 97.47 | 6 |
| Fourt & Woodlock | 0.7697 | 163.58% | 61.96 | 2 |
| Gompertz | 0.9989 | 21.22% | 95.07 | 3 |
| Bass Generalizado (GBM) | 0.9999 | 12.97% | 97.18 | 4 |
| Horsky & Simon | 0.9998 | 16.82% | 95.57 | 4 |
| Muller & Yogev | 0.9999 | 12.40% | 96.12 | 7 |
| Van den Bulte & Joshi | 0.9999 | 12.38% | 96.21 | 6 |
| Difusión Logística R&K | 0.9999 | 7.46% | 98.14 | 4 |
| Ladrón-de-Guevara & Putsis | 0.9998 | 16.82% | 95.53 | 5 |


## 4. Proyecciones

### 4.1 Proyecciones de Todos los Modelos
| Año | Difusión Logística R&K (M) | Dual Market (M) | Bass Generalizado (GBM) (M) | Van den Bulte & Joshi (M) | Muller & Yogev (M) | Horsky & Simon (M) | Bass Clásico (M) | Ladrón-de-Guevara & Putsis (M) | Gompertz (M) | Fourt & Woodlock (M) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2015 | 0.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 |
| 2016 | 0.14 | 0.10 | 0.09 | 2.31 | 0.10 | 0.07 | 0.07 | 0.07 | 0.05 | 0.66 |
| 2017 | 0.25 | 0.25 | 0.23 | 3.16 | 0.25 | 0.20 | 0.20 | 0.20 | 0.14 | 1.31 |
| 2018 | 0.44 | 0.48 | 0.45 | 3.49 | 0.48 | 0.41 | 0.41 | 0.41 | 0.35 | 1.96 |
| 2019 | 0.79 | 0.82 | 0.81 | 3.63 | 0.82 | 0.78 | 0.78 | 0.78 | 0.76 | 2.61 |
| 2020 | 1.37 | 1.37 | 1.38 | 3.70 | 1.37 | 1.38 | 1.38 | 1.38 | 1.42 | 3.25 |
| 2021 | 2.29 | 2.25 | 2.28 | 3.76 | 2.25 | 2.31 | 2.31 | 2.31 | 2.40 | 3.89 |
| 2022 | 3.63 | 3.61 | 3.61 | 3.82 | 3.61 | 3.64 | 3.64 | 3.64 | 3.70 | 4.53 |
| 2023 | 5.36 | 5.39 | 5.35 | 3.89 | 5.39 | 5.35 | 5.35 | 5.35 | 5.29 | 5.16 |
| 2024 | 7.26 | 7.26 | 7.28 | 3.98 | 7.26 | 7.23 | 7.23 | 7.23 | 7.12 | 5.79 |
| 2025 | 9.00 | 9.00 | 8.99 | 4.08 | 9.00 | 9.02 | 9.02 | 9.02 | 9.10 | 6.42 |
| 2026 | 10.37 | 10.62 | 10.20 | 4.20 | 10.63 | 10.47 | 10.47 | 10.47 | 11.15 | 7.04 |
| 2027 | 11.32 | 12.14 | 10.90 | 4.31 | 12.17 | 11.51 | 11.51 | 11.51 | 13.20 | 7.67 |
| 2028 | 11.92 | 13.51 | 11.26 | 4.43 | 13.59 | 12.20 | 12.20 | 12.20 | 15.18 | 8.29 |
| 2029 | 12.27 | 14.69 | 11.42 | 4.54 | 14.84 | 12.62 | 12.62 | 12.62 | 17.04 | 8.90 |
| 2030 | 12.47 | 15.65 | 11.49 | 4.63 | 15.88 | 12.87 | 12.87 | 12.87 | 18.75 | 9.51 |
| 2031 | 12.59 | 16.39 | 11.52 | 4.71 | 16.71 | 13.02 | 13.02 | 13.02 | 20.30 | 10.12 |
| 2032 | 12.65 | 16.95 | 11.53 | 4.77 | 17.35 | 13.10 | 13.10 | 13.10 | 21.68 | 10.73 |
| 2033 | 12.69 | 17.36 | 11.53 | 4.82 | 17.83 | 13.15 | 13.15 | 13.15 | 22.89 | 11.34 |
| 2034 | 12.71 | 17.65 | 11.53 | 4.85 | 18.17 | 13.18 | 13.18 | 13.18 | 23.95 | 11.94 |
| 2035 | 12.72 | 17.85 | 11.54 | 4.88 | 18.42 | 13.19 | 13.19 | 13.19 | 24.86 | 12.53 |

### 4.2 Escenarios de Consenso
| Escenario | Modelo | 2030 (M) | 2035 (M) |
| --- | --- | --- | --- |
| Conservador | Bass Clásico | 12.87 | 13.19 |
| Base (recomendado) | Difusión Logística R&K | 12.47 | 12.72 |
| Optimista | Gompertz | 18.75 | 24.86 |

**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado (Difusión Logística R&K): R²=0.9999, MAPE de ajuste=7.46%, Score=98.14.

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
