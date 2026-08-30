# Informe de Adopción: electric vehicles

# Informe de Adopción Tecnológica: Vehículos Eléctricos

---

## §1 Resumen Ejecutivo

El presente informe evalúa la trayectoria de adopción global de vehículos eléctricos (EV) mediante el ajuste de diez modelos de difusión tecnológica sobre la serie histórica disponible. El análisis identifica al modelo **Difusión Logística R&K** como el de mejor desempeño predictivo, evidenciando que la tecnología se encuentra en una **fase de crecimiento acelerado (exponencial-media)**, previa al punto de inflexión de saturación.

| Indicador | Valor |
|---|---|
| Modelo recomendado | Difusión Logística R&K |
| Bondad de ajuste (R²) | Ver tabla §4.2 |
| Error porcentual (MAPE) | Ver tabla §4.2 |
| Fase de adopción actual | Crecimiento acelerado |
| Horizonte de proyección | Hasta 2035 |

**NOTA DE FUENTE DE DATOS:** Los datos agregados de parque vehicular eléctrico provienen de estimaciones de organismos sectoriales (IEA y asociaciones afines), no de reportes corporativos individuales de fabricantes privados. Los fabricantes de EV no publican de forma consolidada y estandarizada sus cifras de unidades activas en circulación. Datos estimados. **Incertidumbre: media-alta.**

---

## §4.2 Recomendación de Modelo

| Modelo | R² | MAPE | Score |
|---|---|---|---|
| Difusión Logística R&K | Alto | Bajo | **Máximo** |
| Van den Bulte & Joshi | Alto | Bajo-medio | Alto |
| Dual Market | Alto | Bajo-medio | Alto |
| Muller & Yogev | Alto | Medio | Alto |
| Horsky & Simon | Alto | Medio | Alto |
| Bass Clásico | Alto | Medio-alto | Alto |
| Ladrón-de-Guevara & Putsis | Alto | Medio-alto | Alto |
| Gompertz | Alto | Medio-alto | Alto |
| Bass Generalizado (GBM) | Alto | Medio-alto | Medio-alto |
| Fourt & Woodlock | Bajo | Muy alto | Bajo |

**Justificación de selección:**

El modelo **Difusión Logística R&K** se recomienda por combinar el R² más alto del conjunto con el MAPE más reducido de todos los modelos evaluados, resultando en el Score compuesto superior. A diferencia de especificaciones como Bass Clásico o Ladrón-de-Guevara & Putsis —que replican exactamente los mismos valores de R² y MAPE, sugiriendo redundancia estructural entre ambos frente a estos datos—, el modelo logístico R&K captura de forma más precisa la curvatura reciente de la serie, particularmente la aceleración observada en los últimos periodos.

Modelos con estructura de doble segmento (Dual Market, Van den Bulte & Joshi) muestran desempeño casi idéntico entre sí (R² y MAPE prácticamente coincidentes), lo cual es consistente con que ambos incorporan mecanismos de imitación entre adoptantes tempranos y tardíos, pero no logran superar al modelo recomendado en error relativo.

El modelo **Fourt & Woodlock** debe descartarse explícitamente: su bajo R² y MAPE extremadamente elevado indican que su supuesto de coeficiente de innovación puro, sin componente de imitación social, no se ajusta a la dinámica observada en la adopción de EV, donde el efecto de imitación/red es determinante.

---

## §5 Análisis Cualitativo

### Fase de crecimiento

La serie histórica muestra una progresión con tasas de crecimiento interanual crecientes hasta los periodos más recientes, sin evidencia aún de desaceleración marcada. Esto posiciona a la tecnología en la **región media-ascendente de la curva en S**, es decir, en la fase donde el efecto de imitación (adopción impulsada por la observación de adoptantes previos) domina sobre el efecto de innovación (adopción autónoma por características intrínsecas del producto).

| Fase | Característica | Estado EV |
|---|---|---|
| Introducción | Adopción lenta, innovadores puros | Superada |
| Crecimiento temprano | Aceleración, entrada de mayoría temprana | Superada |
| Crecimiento acelerado | Máxima pendiente de adopción | **Actual** |
| Madurez/Saturación | Desaceleración hacia el techo de mercado | No alcanzada |

### Advertencias metodológicas

**Riesgo de sobreajuste:** Con una serie histórica de longitud reducida (menos de una decena de observaciones anuales, con un vacío en 2017), los modelos de alta parametrización —particularmente aquellos con múltiples segmentos de mercado (Dual Market, Van den Bulte & Joshi, GBM)— tienen mayor propensión a ajustar ruido idiosincrático en lugar de la señal estructural subyacente. La similitud casi perfecta en métricas entre pares de modelos (p. ej. Bass Clásico y Ladrón-de-Guevara & Putsis) es indicativa de que, con esta cantidad de datos, distintas formulaciones convergen a soluciones equivalentes, limitando la capacidad de diferenciación real entre estructuras teóricas.

**Escasez de datos:** La ausencia del valor correspondiente a 2017 y la corta longitud total de la serie constituyen una limitación relevante. Las proyecciones a mediano-largo plazo (2030, 2035) dependen críticamente del techo de mercado (parámetro de saturación) estimado, el cual es el parámetro más sensible a errores en muestras pequeñas. Se recomienda tratar las proyecciones de largo plazo como **escenarios direccionales**, no como pronósticos puntuales de alta certeza.

**Sensibilidad estructural:** El modelo logístico R&K asume simetría en la curva de adopción alrededor del punto de inflexión; si la adopción real de EV presenta asimetrías (por ejemplo, por shocks regulatorios, subsidios o restricciones de suministro de materias primas), el modelo podría subestimar o sobreestimar la velocidad de aproximación a la saturación.

---

## §6 Marco Teórico

Los modelos de difusión tecnológica aplicados parten del marco general de **difusión de innovaciones**, en el que la tasa de adopción en el tiempo se modela como función de dos componentes: un coeficiente de innovación (adopción independiente de la presión social) y un coeficiente de imitación (adopción mediada por el contacto con adoptantes previos).

| Familia de modelo | Mecanismo central | Supuesto clave |
|---|---|---|
| Bass Clásico / Generalizado | Innovación + imitación combinadas | Mercado homogéneo, techo fijo (o variable en GBM) |
| Fourt & Woodlock | Innovación pura | Sin efecto de imitación |
| Gompertz / Logística R&K | Curva en S paramétrica | Simetría o asimetría controlada de la curva |
| Dual Market / Van den Bulte & Joshi | Segmentación de mercado | Coexistencia de submercados con dinámicas propias |
| Horsky & Simon / Muller & Yogev | Factores de utilidad/precio | Incorporan variables económicas explícitas |
| Ladrón-de-Guevara & Putsis | Generalización competitiva | Interacción entre múltiples tecnologías/generaciones |

El modelo **Logístico R&K**, en particular, extiende la curva logística clásica incorporando flexibilidad adicional en la forma de la curva de adopción, lo que le permite capturar asimetrías en la velocidad de aproximación a la saturación —una característica especialmente relevante en mercados como el de EV, donde factores exógenos (política pública, costos de batería, infraestructura de carga) pueden acelerar o retrasar la fase de madurez de forma no simétrica respecto a la fase de crecimiento.

Este marco teórico sustenta por qué, ante series con inflexión de crecimiento reciente y aceleración sostenida como la del EV, los modelos con mayor flexibilidad en la forma de la curva (Logística R&K) superan en desempeño a los modelos de innovación pura (Fourt & Woodlock) y igualan o superan a los modelos de segmentación de mercado, sin incurrir en la complejidad paramétrica adicional que estos últimos requieren.

## 2. Datos Históricos

| Año | Adopción (M) |
|---|---|
| 2015 | 1.26 M |
| 2016 | 2.00 M |
| 2018 | 5.10 M |
| 2019 | 7.20 M |
| 2020 | 10.00 M |
| 2021 | 16.50 M |
| 2022 | 26.00 M |
| 2023 | 40.00 M |
| 2024 | 58.00 M |


## 3. Métricas

| Modelo | R² | MAPE | Score | k |
|---|---|---|---|---|
| Bass Clásico | 0.9980 | 22.45% | 95.86 | 3 |
| Dual Market | 0.9994 | 12.18% | 95.29 | 6 |
| Fourt & Woodlock | 0.7282 | 84.14% | 60.70 | 2 |
| Gompertz | 0.9963 | 24.39% | 94.10 | 3 |
| Bass Generalizado (GBM) | 0.9982 | 21.85% | 93.32 | 4 |
| Horsky & Simon | 0.9980 | 22.84% | 95.58 | 4 |
| Muller & Yogev | 0.9992 | 15.20% | 96.07 | 7 |
| Van den Bulte & Joshi | 0.9994 | 12.17% | 95.30 | 6 |
| Difusión Logística R&K | 0.9994 | 6.82% | 98.57 | 4 |
| Ladrón-de-Guevara & Putsis | 0.9980 | 22.45% | 95.86 | 5 |


## 4. Proyecciones

| Año | Difusión Logística R&K (M) |
|---|---|
| 2025 | 58.18 M |
| 2026 | 82.74 M |
| 2027 | 112.43 M |
| 2028 | 144.96 M |
| 2029 | 177.01 M |
| 2030 | 205.41 M |
| 2031 | 228.34 M |
| 2032 | 245.48 M |
| 2033 | 257.57 M |
| 2034 | 265.76 M |


**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado (Difusión Logística R&K): R²=0.9994, MAPE=6.82%, Score=98.57.

### 📐 Formulación Matemática

## (Fórmulas...)
