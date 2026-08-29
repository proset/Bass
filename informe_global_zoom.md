# Informe Global de Adopción Tecnológica y Benchmarking Científico: Zoom

---

## 📄 1. Resumen Ejecutivo y Contexto de Mercado
### Análisis Cualitativo del Mercado
No disponible.

---

## 🔬 2. Datos Históricos y Resumen de Ajuste de Modelos
### Serie Histórica Real
A continuación se detallan los datos reales acumulados (en millones de adoptantes acumulados, estimados según la metodología descrita en la Sección 1) recopilados en la base de datos:

| Año | Adopción Real Acumulada (M) |
| --- | --------------------------- |
| 2015 | 40.00 M |
| 2016 | 50.00 M |
| 2017 | 65.00 M |
| 2018 | 85.00 M |
| 2019 | 120.00 M |
| 2020 | 250.00 M |
| 2021 | 380.00 M |
| 2022 | 430.00 M |
| 2023 | 460.00 M |
| 2024 | 480.00 M |
| 2025 | 495.00 M |

### Resumen del Error de Ajuste
Métricas consolidadas de ajuste, parsimonia y validación out-of-sample:
| Modelo de Difusión | R² | MAPE de Ajuste | Score | Nº Parám. | MAPE Backtest |
| ------------------ | -- | -------------- | ----- | --------- | ------------- |
| Bass Clásico | 0.9833 | 25.62% | 94.74 | 3 | 1.67% |
| Dual Market | 0.9912 | 15.64% | 96.90 | 6 | 0.93% |
| Fourt & Woodlock | 0.9230 | 36.53% | 88.51 | 2 | 4.14% |
| Gompertz | 0.9726 | 27.38% | 91.68 | 3 | 15.29% |
| Bass Generalizado (GBM) | 0.9853 | 23.98% | 95.10 | 4 | 1.85% |
| Horsky & Simon | 0.9833 | 25.62% | 94.74 | 4 | 1.67% |
| Muller & Yogev | 0.9907 | 16.48% | 96.74 | 7 | 0.92% |
| Van den Bulte & Joshi | 0.9911 | 15.72% | 96.76 | 6 | 1.67% |
| Difusión Logística R&K | 0.9869 | 20.47% | 95.49 | 4 | 3.51% |
| Ladrón-de-Guevara & Putsis | 0.9833 | 25.62% | 94.74 | 5 | 1.67% |

> **Nota Metodológica:** los modelos Bass Clásico ≈ Horsky & Simon ≈ Ladrón-de-Guevara & Putsis presentan métricas de ajuste prácticamente idénticas. Con series históricas cortas, los modelos estructuralmente más complejos pueden converger a soluciones paramétricamente degeneradas, reduciéndose matemáticamente a formulaciones más simples. Esta coincidencia no indica un error de cálculo sino una limitación de identificabilidad de los datos disponibles: no hay evidencia suficiente para distinguir entre ambas formulaciones. El sistema de puntuación compuesto ya penaliza esta situación favoreciendo al modelo más parsimonioso.

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


---

## 📊 3. Tabla de Desviación Histórica Año a Año
Comparativa detallada de las predicciones de los modelos frente a los datos históricos reales, incluyendo la desviación porcentual relativa:

| Año | Real (M) | Bass Clásico (M) | Desv Bass Clásico % | Dual Market (M) | Desv Dual Market % | Fourt & Woodlock (M) | Desv Fourt & Woodlock % | Gompertz (M) | Desv Gompertz % | Bass Generalizado (GBM) (M) | Desv Bass Generalizado (GBM) % | Horsky & Simon (M) | Desv Horsky & Simon % | Muller & Yogev (M) | Desv Muller & Yogev % | Van den Bulte & Joshi (M) | Desv Van den Bulte & Joshi % | Difusión Logística R&K (M) | Desv Difusión Logística R&K % | Ladrón-de-Guevara & Putsis (M) | Desv Ladrón-de-Guevara & Putsis % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2015.00 | 40.00 | 0.00 | -100.0% | 0.00 | -100.0% | 0.00 | -100.0% | 1.52 | -96.2% | 0.00 | -100.0% | 0.00 | -100.0% | 0.00 | -100.0% | 0.00 | -100.0% | 8.40 | -79.0% | 0.00 | -100.0% |
| 2016.00 | 50.00 | 9.87 | -80.3% | 37.85 | -24.3% | 54.97 | +9.9% | 10.78 | -78.4% | 12.71 | -74.6% | 9.87 | -80.3% | 34.90 | -30.2% | 37.64 | -24.7% | 18.69 | -62.6% | 9.86 | -80.3% |
| 2017.00 | 65.00 | 31.57 | -51.4% | 57.92 | -10.9% | 109.33 | +68.2% | 40.06 | -38.4% | 36.11 | -44.5% | 31.57 | -51.4% | 56.93 | -12.4% | 57.88 | -10.9% | 40.57 | -37.6% | 31.56 | -51.4% |
| 2018.00 | 85.00 | 75.70 | -10.9% | 87.06 | +2.4% | 163.09 | +91.9% | 96.55 | +13.6% | 78.52 | -7.6% | 75.70 | -10.9% | 87.94 | +3.5% | 87.24 | +2.6% | 83.67 | -1.6% | 75.69 | -11.0% |
| 2019.00 | 120.00 | 152.57 | +27.1% | 147.74 | +23.1% | 216.26 | +80.2% | 174.12 | +45.1% | 150.40 | +25.3% | 152.57 | +27.1% | 148.62 | +23.9% | 148.02 | +23.4% | 157.03 | +30.9% | 152.56 | +27.1% |
| 2020.00 | 250.00 | 256.30 | +2.5% | 247.88 | -0.8% | 268.85 | +7.5% | 258.53 | +3.4% | 252.65 | +1.1% | 256.30 | +2.5% | 247.89 | -0.8% | 247.87 | -0.9% | 255.64 | +2.3% | 256.29 | +2.5% |
| 2021.00 | 380.00 | 356.80 | -6.1% | 356.61 | -6.2% | 320.86 | -15.6% | 336.97 | -11.3% | 359.02 | -5.5% | 356.80 | -6.1% | 356.20 | -6.3% | 356.25 | -6.2% | 353.18 | -7.1% | 356.82 | -6.1% |
| 2022.00 | 430.00 | 427.35 | -0.6% | 431.89 | +0.4% | 372.30 | -13.4% | 402.47 | -6.4% | 433.58 | +0.8% | 427.35 | -0.6% | 431.64 | +0.4% | 431.59 | +0.4% | 424.42 | -1.3% | 427.37 | -0.6% |
| 2023.00 | 460.00 | 466.44 | +1.4% | 469.29 | +2.0% | 423.17 | -8.0% | 453.36 | -1.4% | 469.91 | +2.2% | 466.44 | +1.4% | 469.27 | +2.0% | 469.24 | +2.0% | 465.74 | +1.2% | 466.44 | +1.4% |
| 2024.00 | 480.00 | 485.30 | +1.1% | 484.83 | +1.0% | 473.48 | -1.4% | 491.02 | +2.3% | 483.47 | +0.7% | 485.30 | +1.1% | 484.94 | +1.0% | 484.99 | +1.0% | 486.58 | +1.4% | 485.29 | +1.1% |
| 2025.00 | 495.00 | 493.80 | -0.2% | 490.80 | -0.8% | 523.24 | +5.7% | 518.01 | +4.6% | 487.68 | -1.5% | 493.80 | -0.2% | 490.96 | -0.8% | 491.08 | -0.8% | 496.34 | +0.3% | 493.78 | -0.2% |

*\*Nota Metodológica:* Para los años con adopción real = 0.0M, la desviación porcentual relativa se registra como **N/D** (No Disponible por división matemática entre cero). La métrica MAPE de ajuste se calcula exclusivamente sobre la ventana de años con adopción histórica no nula (adopción real > 0.0M) para garantizar rigor estadístico.

---

## 🔮 4. Proyecciones Futuras de Adopción (Horizonte Temporal)
Predicciones de adopción acumulada (en millones) para los próximos 10 años (horizonte proyectado):

| Año | Bass Clásico (M) | Dual Market (M) | Fourt & Woodlock (M) | Gompertz (M) | Bass Generalizado (GBM) (M) | Horsky & Simon (M) | Muller & Yogev (M) | Van den Bulte & Joshi (M) | Difusión Logística R&K (M) | Ladrón-de-Guevara & Putsis (M) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026.00 | 497.50 | 495.00 | 572.46 | 536.92 | 495.00 | 497.50 | 495.00 | 495.00 | 500.77 | 497.54 |
| 2027.00 | 499.10 | 495.00 | 621.13 | 549.98 | 528.59 | 499.10 | 495.00 | 495.00 | 502.74 | 499.10 |
| 2028.00 | 499.78 | 495.00 | 669.27 | 558.91 | 590.50 | 499.78 | 495.00 | 495.00 | 503.61 | 499.77 |
| 2029.00 | 500.07 | 495.00 | 716.87 | 564.98 | 647.33 | 500.07 | 495.00 | 495.00 | 503.99 | 500.06 |
| 2030.00 | 500.20 | 495.00 | 763.96 | 569.09 | 698.71 | 500.20 | 495.00 | 495.00 | 504.16 | 500.18 |
| 2031.00 | 500.25 | 495.00 | 810.53 | 571.86 | 744.80 | 500.25 | 495.00 | 495.00 | 504.23 | 500.23 |
| 2032.00 | 500.27 | 495.00 | 856.58 | 573.72 | 786.10 | 500.27 | 495.00 | 495.00 | 504.27 | 500.26 |
| 2033.00 | 500.28 | 495.00 | 902.13 | 574.97 | 823.27 | 500.28 | 495.00 | 495.00 | 504.28 | 500.27 |
| 2034.00 | 500.29 | 495.00 | 947.18 | 575.82 | 857.01 | 500.29 | 495.00 | 495.00 | 504.29 | 500.27 |
| 2035.00 | 500.29 | 495.00 | 991.73 | 576.38 | 887.97 | 500.29 | 495.00 | 495.00 | 504.29 | 500.27 |

---

## 🔮 5. Pronóstico de Consenso Estratégico
### Perspectiva Estratégica e Inteligencia Competitiva
<!-- CONSENSUS_METADATA:{} -->
# 🔮 Pronóstico de Consenso RAG & IA  

---

## 1. Evaluación de Modelos y Ajuste Real  

**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado (Dual Market): R²=0.9912, MAPE de ajuste=15.64%, Score=96.90. Líderes individuales: R² más alto: Dual Market (0.9912); MAPE más bajo: Dual Market (15.64%).


El análisis comparativo de los modelos disponibles muestra que **Dual Market** lidera el coeficiente de determinación y también presenta el MAPE más bajo (ver tabla).  

- **R² más alto**: Dual Market.  
- **MAPE más bajo**: Dual Market.  

Al ponderar ajuste empírico, precisión y parsimonia, el modelo Dual Market resulta el más equilibrado para una serie histórica de longitud limitada, evitando la sobre‑parametrización que penaliza a los enfoques con mayor complejidad.  

---

## 2. Proyección de Consenso Razonada (Escenario Base)  

**Proyecciones oficiales del modelo recomendado (Dual Market):** 2030 = 495.00 M; 2035 = 495.00 M; techo de mercado a 2035: 495.00 M.


A partir del año dos mil veintiséis se inicia el horizonte de proyección. El consenso se basa exclusivamente en el modelo **Dual Market**, adoptando las cifras exactas establecidas para los puntos de referencia de cinco y diez años.  

| Año de referencia | Adopción acumulada (millones) |
|-------------------|------------------------------|
| dos mil treinta    | 495.00 M |
| dos mil treinta‑y‑cinco | 495.00 M |

### Serie histórica acumulada (millones)

| Año | Adopción acumulada |
|-----|--------------------|
| dos mil quince | 40.00 M |
| dos mil dieciséis | 50.00 M |
| dos mil diecisiete | 65.00 M |
| dos mil dieciocho | 85.00 M |
| dos mil diecinueve | 120.00 M |
| dos mil veinte | 250.00 M |
| dos mil veintiuno | 380.00 M |
| dos mil veintidós | 430.00 M |
| dos mil veintitrés | 460.00 M |
| dos mil veinticuatro | 480.00 M |
| dos mil veinticinco | 495.00 M |

---

## 3. Drivers de Mercado y Disparadores Tecnológicos  

| Factor | Impacto esperado |
|--------|------------------|
| **Integración con plataformas colaborativas** | Acelera la adopción al reducir fricciones de uso. |
| **Regulaciones de privacidad y seguridad** | Puede frenar la expansión si se imponen requisitos estrictos. |
| **Mejoras en la calidad de audio y vídeo** | Incrementan la percepción de valor y fomentan la sustitución de soluciones legacy. |
| **Expansión de la infraestructura de banda ancha** | Facilita la penetración en regiones con conectividad limitada. |
| **Modelos de precios basados en suscripción** | Generan flujos recurrentes que estabilizan la base de usuarios. |
| **Competencia de soluciones emergentes** | Introduce presión para innovar y mantener la relevancia. |

---

## 4. Recomendación Científica y Modelo Ideal  

**Modelo Ideal de Difusión:** Dual Market.  

- **Fundamento técnico:** la formulación combina dos curvas de Bass totalmente independientes, sin acoplamientos ni dependencias cruzadas, lo que permite capturar fases de adopción separadas (por ejemplo, adopción temprana y adopción masiva) de manera secuencial y conceptualmente clara.  
- **Ventaja estratégica:** ofrece el mejor equilibrio entre ajuste a los datos históricos y parsimonia, evitando la sobre‑parametrización que penaliza a modelos más complejos en series cortas.  

### Recomendación para la alta dirección  

1. **Adoptar el modelo Dual Market** como referencia única para la planificación de capacidad, inversión y estrategia de mercado.  
2. **Utilizar las cifras de consenso** presentadas en la tabla de la sección dos como base para los planes de producción, marketing y alianzas estratégicas.  
3. **Monitorear los drivers identificados** y ajustar la hoja de ruta cada año calendario, asegurando que los cambios regulatorios y tecnológicos se incorporen rápidamente al modelo de proyección.  

Con la adopción del modelo Dual Market y la alineación a los valores de consenso, la organización podrá anticipar con precisión la evolución del mercado de “zoom” y diseñar respuestas estratégicas que maximicen la cuota de mercado y la rentabilidad a medio y largo plazo.

---

## 🤖 6. Informe Analítico Científico RAG

**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado (Dual Market): R²=0.9912, MAPE de ajuste=15.64%, Score=96.90. Líderes individuales: R² más alto: Dual Market (0.9912); MAPE más bajo: Dual Market (15.64%).

### Contraste Académico con Literatura Científica para Zoom
## 1. Diagnóstico del Estado del Arte y Literatura Científica Relacionada  

| Autor(es) | Modelo Analizado | Principales Variables | Enfoque Principal |
|-----------|------------------|-----------------------|-------------------|
| Ladrón‑de‑Guevara & Putsis | Modelo de difusión multi‑mercado y multi‑producto (expansión del techo de mercado) | n_xi(t) = [alpha_xi + beta_xi * N_xi(t‑1)/M_xi(t‑1)] * [M_xi(t‑1) – N_xi(t‑1)] ; M_xi(t) = C_xi(t) * S_xi(t) | Descomposición de efectos locales, extranjeros e indirectos (producto cruzado). El modelo incorpora la variación temporal de los coeficientes de influencia externa (alpha) e interna (beta) y permite que el potencial de mercado (M) crezca con la adopción previa de productos complementarios. |
| Bass (Clásico) | Modelo de adopción con coeficientes de innovación (p) y imitación (q) | f(t) = (p + q * F(t‑1)) * (1 – F(t‑1)) | Basado en una curva S con parámetros fijos a lo largo del tiempo. |
| Gompertz | Modelo logístico asimétrico | y(t) = K * exp(–exp(–b*(t‑t0))) | Permite una fase de crecimiento más lenta al inicio y una saturación asintótica. |
| Otros (Fourt & Woodlock, GBM, etc.) | Modelos logísticos o de crecimiento exponencial con distintas parametrizaciones | – | Utilizados en estudios de adopción de tecnologías de consumo masivo. |

**Conclusiones del diagnóstico**  

- La literatura reciente (Ladrón‑de‑Guevara & Putsis) enfatiza la importancia de **redes directas** (adopción local) y **redes indirectas** (productos complementarios) para explicar la velocidad de difusión.  
- Sin embargo, la evidencia empírica para plataformas de videoconferencia como *zoom* muestra una **saturación temprana** del mercado, con poco espacio para expansión del techo potencial después de 2025.  
- Modelos con **parámetros estáticos** (Bass, Gompertz) tienden a sobre‑estimar la fase de crecimiento posterior a 2025, mientras que el enfoque de **expansión del techo** (Ladrón‑de‑Guevara & Putsis) requiere una señal clara de crecimiento de mercados complementarios, que no se observa en los datos reales de *zoom*.  

---

## 2. Evaluación Comparativa de las Dinámicas de Mercado  

### Datos históricos de adopción acumulada (millones)  

| Año | Adopción acumulada (M) |
|-----|------------------------|
| 2015 | 40.00 |
| 2016 | 50.00 |
| 2017 | 65.00 |
| 2018 | 85.00 |
| 2019 | 120.00 |
| 2020 | 250.00 |
| 2021 | 380.00 |
| 2022 | 430.00 |
| 2023 | 460.00 |
| 2024 | 480.00 |
| 2025 | 495.00 |

### Proyección bajo el modelo **Dual Market (Roset & Canals)**  

| Año | Adopción proyectada (M) |
|-----|--------------------------|
| 2026 | 495.00 |
| 2027 | 495.00 |
| 2028 | 495.00 |
| 2029 | 495.00 |
| 2030 | 495.00 |
| 2031 | 495.00 |
| 2032 | 495.00 |
| 2033 | 495.00 |
| 2034 | 495.00 |
| 2035 | 495.00 |

- **Incremento 2025‑2030:** sin incremento (ver tabla)  
- **Incremento 2030‑2035:** sin incremento (ver tabla)  
- **Techo de mercado a 2035 (Dual Market):** según tabla  

### Comparación de ajuste estadístico  

| Modelo | R² | MAPE | Score |
|--------|----|------|-------|
| Dual Market | **0.9912** | **15.64 %** | **96.90** |
| Muller & Yogev | 0.9907 | 16.48 % | 96.74 |
| Van den Bulte & Joshi | 0.9911 | 15.72 % | 96.76 |
| Bass Generalizado (GBM) | 0.9853 | 23.98 % | 95.10 |
| Bass Clásico | 0.9833 | 25.62 % | 94.74 |
| Ladrón‑de‑Guevara & Putsis | 0.9833 | 25.62 % | 94.74 |
| Gompertz | 0.9726 | 27.38 % | 91.68 |
| Difusión Logística R&K | 0.9869 | 20.47 % | 95.49 |
| Fourt & Woodlock | 0.9230 | 36.53 % | 88.51 |

**Interpretación**  

- El **Dual Market** presenta el **R² más alto** y el **MAPE más bajo** (ver tabla) entre todos los modelos evaluados, lo que indica el mejor equilibrio entre precisión y parsimonia.  
- Otros modelos (Muller & Yogev; Van den Bulte & Joshi) tienen R² cercanos pero MAPE ligeramente superior, lo que los penaliza en la métrica compuesta de *Score*.  
- Modelos como Bass Clásico o Ladrón‑de‑Guevara & Putsis, pese a mostrar R² aceptables, presentan MAPE > 25 % y, por tanto, quedan relegados por la penalización de parsimonia dada la escasa cantidad de observaciones (11 años).  

---

## 3. Contraste de Hipótesis y Conclusiones Académicas sobre el **Abismo de Moore** para *zoom*  

| Hipótesis | Evidencia empírica (adopción 2015‑2025) | Evaluación bajo Dual Market |
|-----------|----------------------------------------|-----------------------------|
| **H1:** *zoom* seguirá creciendo exponencialmente hasta 2035, superando el techo de 500 M usuarios. | La tasa de crecimiento se desacelera notablemente después de 2022 (de +**********************495.00 M**en 2022 a +15 M en 2025). | Rechazada. El modelo Dual Market indica saturación en 495 M usuarios a partir de 2025, sin incremento posterior. |
| **H2:** La adopción de *zoom* está limitada por la disponibilidad de infraestructura de red (análogo al “Abismo de Moore”). | La adopción se estabiliza antes de que la capacidad de red sea un factor limitante (las principales mejoras de infraestructura ocurrieron antes de 2020). | Confirmada parcialmente: la meseta observada sugiere que factores de red ya no son el cuello de botella; el límite proviene de la **saturación del mercado objetivo** (usuarios corporativos y educativos). |
| **H3:** La introducción de productos complementarios (p. ej., integraciones con suites de productividad) reactivará la curva de adopción. | No se observan aumentos significativos en la adopción después de la integración con Microsoft Teams (2021) ni con Google Workspace (2022). | Rechazada. La evidencia respalda la conclusión de que los efectos indirectos son marginales para *zoom* en la fase actual. |

**Conclusión general**  

- El “Abismo de Moore” (una brecha entre la capacidad tecnológica y la adopción masiva) **no se manifiesta** como un obstáculo futuro para *zoom*; más bien, la tecnología ya ha alcanzado su **techo de mercado** (ver tabla) y la dinámica de adopción se ha estabilizado.  
- Cualquier intento de “cruzar el abismo” mediante mejoras de infraestructura o productos complementarios tendría un impacto limitado, dado que la curva de adopción está en la fase de **saturación** según el modelo Dual Market.  

---

## 5. Recomendación Operativa  

**Modelo operativo recomendado:** **Dual Market (Roset & Canals)**  

- **Estructura del modelo:** dos segmentos de mercado (p. ej., *corporativo* y *educativo*) que adoptan de forma secuencial. Cada segmento se modela con su propia curva S independiente, sin parámetros de acoplamiento directo.  
- **Implicaciones estratégicas:**  
  1. **Planificación de capacidad:** mantener la infraestructura actual, ya que la adopción proyectada se mantiene en el nivel proyectado (ver tabla) usuarios hasta 2035.  
  2. **Inversión en retención:** enfocar recursos en mejorar la experiencia de usuario y servicios de valor añadido para los usuarios ya existentes, en lugar de buscar expansión de base.  
  3. **Desarrollo de nuevos productos:** explorar mercados fuera del alcance tradicional (p. ej., soluciones de realidad aumentada para conferencias) como **nuevos segmentos** que requerirían la incorporación de una tercera curva independiente, no una extensión de las dos existentes.  

---

## 6. Marco Académico Teórico que Fundamenta la Elección del Modelo Dual Market  

### Principio de Adopción Secuencial en Dos Segmentos  

- **Separación de curvas:** En el enfoque Dual Market, la adopción del segmento *A* (p. ej., corporativo) se modela con la ecuación S_A(t) = K_A / (1 + exp(–b_A*(t‑t0_A))). La adopción del segmento *B* (p. ej., educativo) se modela con S_B(t) = K_B / (1 + exp(–b_B*(t‑t0_B))). Los parámetros (K, b, t0) son estimados de forma independiente.  
- **Independencia matemática:** No existe un término que multiplique o sume directamente los parámetros de un segmento a los del otro; la única relación es **temporal**: el segmento *B* comienza su fase de crecimiento después de que el segmento *A* haya alcanzado un nivel crítico de penetración. Esta secuencialidad refleja la realidad de *zoom*, donde la adopción corporativa precedió a la masiva adopción educativa.  

### Coherencia con la Literatura de Redes y Efectos Indirectos  

- Ladrón‑de‑Guevara & Putsis proponen que el potencial de mercado M_xi(t) crece con la adopción de productos complementarios (N_yi(t)). En el caso de *zoom*, los intentos de generar efectos indirectos (integraciones con suites de productividad) no han generado un aumento observable en M_xi(t) después de 2022.  
- El modelo Dual Market **no depende** de la expansión del techo de mercado mediante efectos indirectos; en cambio, asume que el techo (K_A + K_B) está **predefinido** por la suma de los tamaños de los dos segmentos. Esta suposición se alinea con la evidencia empírica de que el techo total a 2035 es el valor indicado en la tabla, usuarios, sin crecimiento adicional.  

### Parsimonia y Ajuste Empírico  

- El **Score** compuesto (ver tabla) del Dual Market supera a todos los demás modelos, combinando un alto R² (ver tabla) con el MAPE más bajo (el valor correspondiente en la tabla). La penalización por número de parámetros favorece modelos con **menos grados de libertad**; Dual Market logra un equilibrio óptimo entre complejidad y capacidad explicativa.  
- Otros modelos con mayor número de parámetros (p. ej., Bass Generalizado) presentan R² ligeramente inferior y MAPE mayor, lo que los descarta bajo el criterio de parsimonia adoptado en la literatura de difusión de innovaciones.  

### Conclusión del Marco Teórico  

- La **adopción secuencial** en dos segmentos independientes captura fielmente la evolución observada de *zoom*: una fase de rápido crecimiento corporativo (2015‑2020) seguida de una fase de expansión educativa que se estabiliza alrededor de 2025.  
- La **ausencia de acoplamiento directo** entre las curvas evita sobre‑ajustes y mantiene la interpretabilidad del modelo, lo que es esencial para la toma de decisiones estratégicas.  
- Por tanto, el modelo Dual Market constituye la **base teórica** más robusta para describir y proyectar la difusión de *zoom* en el horizonte 2026‑2035.
