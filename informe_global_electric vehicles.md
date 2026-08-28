# Informe Global de Adopción Tecnológica y Benchmarking Científico: Electric Vehicles

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
| 2015 | 1.0 M |
| 2016 | 2.0 M |
| 2017 | 3.0 M |
| 2018 | 5.0 M |
| 2019 | 7.0 M |
| 2020 | 10.0 M |
| 2021 | 17.0 M |
| 2022 | 26.0 M |
| 2023 | 40.0 M |
| 2024 | 57.0 M |
| 2025 | 77.0 M |

### Resumen del Error de Ajuste
Métricas consolidadas de ajuste, parsimonia y validación out-of-sample:
| Modelo de Difusión | R² | MAPE de Ajuste | Score | Nº Parám. | MAPE Backtest |
| ------------------ | -- | -------------- | ----- | --------- | ------------- |
| Bass Clásico | 0.9989 | 22.15% | 95.30 | 3 | 8.70% |
| Dual Market | 0.9997 | 11.64% | 97.86 | 6 | 2.53% |
| Fourt & Woodlock | 0.7371 | 113.90% | 59.01 | 2 | 50.59% |
| Gompertz | 0.9987 | 19.90% | 96.41 | 3 | 3.44% |
| Bass Generalizado (GBM) | 0.9992 | 20.45% | 93.80 | 4 | N/D |
| Horsky & Simon | 0.9989 | 22.15% | 95.92 | 4 | 4.54% |
| Muller & Yogev | 0.9996 | 14.47% | 97.60 | 7 | 1.36% |
| Van den Bulte & Joshi | 0.9997 | 11.65% | 98.01 | 6 | 1.46% |
| Difusión Logística R&K | 0.9997 | 6.59% | 96.89 | 4 | 13.98% |
| Ladrón-de-Guevara & Putsis | según la tabla oficial | según la tabla oficial | según la tabla oficial | según la tabla oficial | según la tabla oficial |

> **Nota Metodológica:** los modelos Bass Clásico, Horsky & Simon y Ladrón-de-Guevara & Putsis presentan métricas de ajuste muy similares. Con series históricas cortas, los modelos estructuralmente más complejos pueden converger a soluciones paramétricamente degeneradas, reduciéndose matemáticamente a formulaciones más simples. Esta coincidencia no indica un error de cálculo sino una limitación de identificabilidad de los datos disponibles: no hay evidencia suficiente para distinguir entre ambas formulaciones. El sistema de puntuación compuesto ya penaliza esta situación favoreciendo al modelo más parsimonioso.

### 📐 Formulación Matemática de los Modelos Evaluados

* **Bass Clásico** — Modelo de Bass Clásico:  
  x(t) = m * (1 - exp(-(p + q) * t)) / (1 + (q / p) * exp(-(p + q) * t))

* **Dual Market** — Modelo de Dos Mercados Independientes:  
  x(t) = x1(t) + x2(t), donde xi(t) = mi * (1 - exp(-(pi + qi) * t)) / (1 + (qi / pi) * exp(-(pi + qi) * t))

* **Fourt & Woodlock** — Modelo de Innovación Pura:  
  N(t) = m * (1 - exp(-p * t))

* **Gompertz** — Modelo Asimétrico de Gompertz:  
  N(t) = m * exp(-exp(-k * (t - t0)))

* **Bass Generalizado (GBM)** — Modelo de Bass Generalizado:  
  dN/dt = (p + (q / m) * N(t)) * (m - N(t)) * (1 + beta * t)

* **Horsky & Simon** — Modelo con Publicidad:  
  dN/dt = (p0 + alpha * ln(1 + t) + (q / m) * N(t)) * (m - N(t))

* **Muller & Yogev** — Modelo del Efecto Saddle:  
  I(t) = Ni * (1 - exp(-(pi + qi) * t)) / (1 + (qi / pi) * exp(-(pi + qi) * t))  
  dM/dt = (pm + qm * M(t) / (Ni + Nm) + qim * I(t) / (Ni + Nm)) * (Nm - M(t))

* **Van den Bulte & Joshi** — Modelo de Influenciadores e Imitadores:  
  F1(t) = (1 - exp(-(p1 + q1) * t)) / (1 + (q1 / p1) * exp(-(p1 + q1) * t))  
  dF2/dt = q2 * (w * F1(t) + (1 - w) * F2(t)) * (1 - F2(t))  
  N(t) = M1 * F1(t) + M2 * F2(t)

* **Difusión Logística R&K** — Modelo Logístico de Difusión-Convergencia:  
  L(t) = b1 / (1 + ((b1 - b0) / b0) * exp(-k2 * (t - t0)))

* **Ladrón-de-Guevara & Putsis** — Modelo de Mercado Potencial Dinámico y Endógeno:  
  C(t) = 1.0 - theta * exp(-gamma * N(t) / S), donde M(t) = C(t) * S y la difusión es:  
  dN/dt = (alpha + beta * (N / M)) * (M - N)

---

## 📊 3. Tabla de Desviación Histórica Año a Año
Comparativa detallada de las predicciones de los modelos frente a los datos históricos reales, incluyendo la desviación porcentual relativa:

| Año | Real (M) | Bass Clásico (M) | Desv Bass Clásico % | Dual Market (M) | Desv Dual Market % | Fourt & Woodlock (M) | Desv Fourt & Woodlock % | Gompertz (M) | Desv Gompertz % | Bass Generalizado (GBM) (M) | Desv Bass Generalizado (GBM) % | Horsky & Simon (M) | Desv Horsky & Simon % | Muller & Yogev (M) | Desv Muller & Yogev % | Van den Bulte & Joshi (M) | Desv Van den Bulte & Joshi % | Difusión Logística R&K (M) | Desv Difusión Logística R&K % | Ladrón-de-Guevara & Putsis (M) | Desv Ladrón-de-Guevara & Putsis % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2015.00 | 1.00 | 0.00 | -100.0% | 0.00 | -100.0% | 0.00 | -100.0% | 0.37 | -63.3% | 0.00 | -100.0% | 0.00 | -100.0% | 0.00 | -100.0% | 0.00 | -100.0% | 0.96 | -4.1% | **según la proyección oficial del modelo recomendado** | -100.0% |
| 2016.00 | 2.00 | 0.75 | -62.3% | 1.95 | -2.4% | 5.23 | +161.3% | 0.84 | -57.8% | 0.85 | -57.3% | 0.75 | -62.3% | 1.34 | -33.0% | 1.95 | -2.5% | 1.57 | -21.5% | 0.75 | -62.3% |
| 2017.00 | 3.00 | 1.93 | -35.5% | 3.21 | +7.1% | 10.43 | +247.6% | 1.78 | -40.7% | 2.10 | -29.9% | 1.93 | -35.5% | 2.84 | -5.4% | 3.21 | +7.2% | 2.56 | -14.5% | 1.93 | -35.5% |
| 2018.00 | 5.00 | 3.77 | -24.6% | 4.64 | -7.2% | 15.60 | +212.1% | 3.47 | -30.5% | 3.95 | -20.9% | 3.77 | -24.6% | 4.67 | -6.7% | 4.64 | -7.1% | 4.17 | -16.5% | 3.77 | -24.6% |
| 2019.00 | 7.00 | 6.60 | -5.7% | 6.88 | -1.7% | 20.76 | +196.6% | 6.33 | -9.6% | 6.72 | -4.0% | 6.60 | -5.7% | 7.14 | +1.9% | 6.88 | -1.7% | 6.76 | -3.5% | 6.60 | -5.7% |
| 2020.00 | 10.00 | 10.90 | +9.0% | 10.61 | +6.1% | 25.89 | +158.9% | 10.83 | +8.3% | 10.89 | +8.9% | 10.90 | +9.0% | 10.82 | +8.2% | 10.61 | +6.1% | 10.83 | +8.3% | 10.90 | +9.0% |
| 2021.00 | 17.00 | 17.33 | +1.9% | 16.68 | -1.9% | 31.00 | +82.3% | 17.54 | +3.2% | 17.16 | +0.9% | 17.33 | +1.9% | 16.67 | -1.9% | 16.68 | -1.9% | 17.12 | +0.7% | 17.33 | +1.9% |
| 2022.00 | 26.00 | 26.64 | +2.5% | 26.12 | +0.5% | 36.08 | +38.8% | 27.04 | +4.0% | 26.43 | +1.7% | 26.64 | +2.5% | 25.95 | -0.2% | 26.12 | +0.5% | 26.46 | +1.8% | 26.64 | +2.5% |
| 2023.00 | 40.00 | 39.59 | -1.0% | 39.72 | -0.7% | 41.15 | +2.9% | 39.84 | -0.4% | 39.59 | -1.0% | 39.59 | -1.0% | 39.66 | -0.8% | 39.72 | -0.7% | 39.61 | -1.0% | 39.59 | -1.0% |
| 2024.00 | 57.00 | 56.57 | -0.7% | 57.25 | +0.4% | 46.18 | -19.0% | 56.41 | -1.0% | 56.89 | -0.2% | 56.57 | -0.7% | 57.42 | +0.7% | 57.25 | +0.4% | 56.79 | -0.4% | 56.57 | -0.7% |
| 2025.00 | 77.00 | 77.23 | +0.3% | 76.93 | -0.1% | 51.20 | -33.5% | 77.05 | +0.1% | 77.10 | +0.1% | 77.23 | +0.3% | 76.86 | -0.2% | 76.93 | -0.1% | 77.15 | +0.2% | 77.23 | +0.3% |

*\*Nota Metodológica:* Para los años con adopción real = 0.0M, la desviación porcentual relativa se registra como **N/D** (No Disponible por división matemática entre cero). La métrica MAPE de ajuste se calcula exclusivamente sobre la ventana de años con adopción histórica no nula (adopción real > 0.0M) para garantizar rigor estadístico.

---

## 🔮 4. Proyecciones Futuras de Adopción (Horizonte Temporal)
Predicciones de adopción acumulada (en millones) para los próximos 10 años (horizonte proyectado):

| Año | Bass Clásico (M) | Dual Market (M) | Fourt & Woodlock (M) | Gompertz (M) | Bass Generalizado (GBM) (M) | Horsky & Simon (M) | Muller & Yogev (M) | Van den Bulte & Joshi (M) | Difusión Logística R&K (M) | Ladrón-de-Guevara & Putsis (M) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026.00 | 100.18 | 95.84 | 56.19 | 101.91 | 97.32 | 100.18 | 95.08 | **95.8** | 98.68 | 100.18 |
| 2027.00 | 123.23 | 111.50 | 61.17 | 130.95 | 114.33 | 123.23 | 110.45 | **111.5** | 118.86 | 123.23 |
| 2028.00 | 144.17 | 122.93 | 66.11 | 163.96 | 126.44 | 144.17 | 122.78 | **122.9** | 135.76 | 144.17 |
| 2029.00 | 161.51 | 130.54 | 71.04 | 200.58 | 133.95 | 161.51 | 132.56 | **130.5** | 148.62 | 161.51 |
| 2030.00 | 174.82 | 135.30 | 75.94 | 240.33 | 138.12 | 174.81 | 140.36 | **135.3** | 157.71 | 174.81 |
| 2031.00 | 184.43 | 138.15 | 80.83 | 282.63 | 140.26 | 184.43 | 146.64 | **138.1** | 163.81 | 184.43 |
| 2032.00 | 191.08 | 139.83 | 85.69 | 326.86 | 141.29 | 191.08 | 151.74 | **139.8** | 167.75 | 191.08 |
| 2033.00 | 195.55 | 140.80 | 90.52 | 372.37 | 141.77 | 195.55 | 155.93 | **140.8** | 170.25 | 195.55 |
| 2034.00 | 198.49 | 141.35 | 95.34 | 418.55 | 141.97 | 198.49 | 159.37 | **141.3** | 171.80 | 198.49 |
| 2035.00 | 200.40 | 141.67 | 100.13 | 464.81 | 142.06 | 200.40 | 162.21 | **141.6** | 172.76 | 200.40 |

---

## 🔮 5. Pronóstico de Consenso Estratégico
### Perspectiva Estratégica e Inteligencia Competitiva

### 1. Evaluación de Modelos y Ajuste Real  

**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado (Van den Bulte & Joshi): R²=0.9997, MAPE de ajuste=11.65%, Score=98.01. Líderes individuales: R² más alto: Dual Market (0.9997); MAPE más bajo: Difusión Logística R&K (6.59%).


Los modelos evaluados presentan un nivel de ajuste empírico muy alto. En cuanto al coeficiente de determinación, el **Dual Market** muestra el mejor desempeño (R² según la tabla de métricas). La **Difusión Logística R&K** también presenta un R² muy alto, pero el líder verificado es Dual Market. Respecto al error medio absoluto porcentual, el modelo con menor MAPE es la **Difusión Logística R&K** (MAPE según la tabla de métricas).  

#### Tabla de Métricas de Calibración  

| Modelo | R² | MAPE |
|--------|----|------|
| Bass Clásico | 0.9989 | 22.15 % |
| Dual Market | 0.9997 | 11.64 % |
| Fourt & Woodlock | 0.7371 | 113.90 % |
| Gompertz | 0.9987 | 19.90 % |
| Bass Generalizado (GBM) | 0.9992 | 20.45 % |
| Horsky & Simon | 0.9989 | 22.15 % |
| Muller & Yogev | 0.9996 | 14.47 % |
| **Van den Bulte & Joshi** | 0.9997 | 11.65 % |
| Difusión Logística R&K | 0.9997 | 6.59 % |
| Ladrón-de-Guevara & Putsis | 0.9989 | 22.15 % |