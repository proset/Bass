# Informe Global de Adopción Tecnológica y Benchmarking Científico: Meta Quest

---

## 📄 1. Resumen Ejecutivo y Contexto de Mercado
### Análisis Cualitativo del Mercado


---

## 🔬 2. Datos Históricos y Resumen de Ajuste de Modelos
### Serie Histórica Real
A continuación se detallan los datos reales acumulados (en millones de adoptantes acumulados, estimados según la metodología descrita en la Sección 1) recopilados en la base de datos:

| Año | Adopción Real Acumulada (M) |
| --- | --------------------------- |
| 2015 | 0.0 M |
| 2016 | 0.0 M |
| 2017 | 0.0 M |
| 2018 | 0.0 M |
| 2019 | 1.2 M |
| 2020 | 3.5 M |
| 2021 | 12.5 M |
| 2022 | 20.0 M |
| 2023 | 24.0 M |
| 2024 | 29.0 M |
| 2025 | 35.0 M |

### Resumen del Error de Ajuste
Métricas consolidadas de ajuste, parsimonia y validación out-of-sample:
| Modelo de Difusión | R² | MAPE de Ajuste | Score | Nº Parám. | MAPE Backtest |
| ------------------ | -- | -------------- | ----- | --------- | ------------- |
| Bass Clásico | 0.9881 | 23.38% | 93.75 | 3 | 12.78% |
| Dual Market | 0.9957 | 14.36% | 95.63 | 6 | 12.78% |
| Fourt & Woodlock | 0.9522 | 72.50% | 84.25 | 2 | 10.19% |
| Gompertz | 0.9921 | 10.57% | 95.27 | 3 | 17.27% |
| Bass Generalizado (GBM) | 0.9909 | 18.62% | 93.13 | 4 | 22.95% |
| Horsky & Simon | 0.9911 | 16.44% | 94.51 | 4 | 15.97% |
| Muller & Yogev | 0.9957 | 14.44% | 95.50 | 7 | 13.56% |
| Van den Bulte & Joshi | 0.9957 | 14.32% | 95.64 | 6 | 12.78% |
| Difusión Logística R&K | 0.9840 | 26.63% | 94.04 | 4 | 5.66% |
| Ladrón-de-Guevara & Putsis | 0.9912 | 18.90% | 93.67 | 5 | 19.20% |

### 📐 Formulación Matemática de los Modelos Evaluados

* **Bass Clásico** — Modelo de Bass Clásico:
  x(t) = m * (1 - exp(-(p + q) * t)) / (1 + (q / p) * exp(-(p + q) * t))

* **Dual Market (Roset & Canals)** — Modelo de Dos Mercados Independientes:
  x(t) = x1(t) + x2(t), donde x1 y x2 son modelos clásicos de Bass independientes:
  xi(t) = mi * (1 - exp(-(pi + qi) * t)) / (1 + (qi / pi) * exp(-(pi + qi) * t))

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
| 2015.00 | 0.00 | 0.00 | N/D | 0.00 | N/D | 0.00 | N/D | 0.12 | N/D | 0.00 | N/D | 0.00 | N/D | 0.00 | N/D | 0.00 | N/D | 0.98 | N/D | 0.00 | N/D |
| 2016.00 | 0.00 | 2.04 | N/D | 1.62 | N/D | 4.84 | N/D | 1.24 | N/D | 1.68 | N/D | 1.54 | N/D | 1.62 | N/D | 1.62 | N/D | 2.34 | N/D | 1.77 | N/D |
| 2017.00 | 0.00 | 5.66 | N/D | 5.31 | N/D | 9.64 | N/D | 4.96 | N/D | 5.84 | N/D | 5.63 | N/D | 5.32 | N/D | 5.31 | N/D | 5.31 | N/D | 5.54 | N/D |
| 2018.00 | 0.00 | 11.25 | N/D | 11.75 | N/D | 14.40 | N/D | 11.38 | N/D | 11.71 | N/D | 11.57 | N/D | 11.75 | N/D | 11.75 | N/D | 10.79 | N/D | 11.48 | N/D |
| 2019.00 | 1.20 | 18.30 | +1424.6% | 19.10 | +1491.6% | 19.11 | +1492.2% | 18.74 | +1461.7% | 18.28 | +1423.2% | 18.38 | +1431.4% | 19.08 | +1490.2% | 19.10 | +1491.7% | 18.43 | +1435.6% | 18.42 | +1434.6% |
| 2020.00 | 3.50 | 25.18 | +619.5% | 24.72 | +606.3% | 23.77 | +579.2% | 25.29 | +622.6% | 24.63 | +603.8% | 24.87 | +610.7% | 24.70 | +605.9% | 24.72 | +606.2% | 25.75 | +635.7% | 24.91 | +611.6% |
| 2021.00 | 12.50 | 30.44 | +143.5% | 28.99 | +131.9% | 28.40 | +127.2% | 30.28 | +142.3% | 30.10 | +140.8% | 30.21 | +141.7% | 29.02 | +132.1% | 28.98 | +131.9% | 30.64 | +145.1% | 30.18 | +141.5% |
| 2022.00 | 20.00 | 33.75 | +68.7% | 34.95 | +74.8% | 32.98 | +64.9% | 33.74 | +68.7% | 34.35 | +71.7% | 34.11 | +70.5% | 34.94 | +74.7% | 34.96 | +74.8% | 33.16 | +65.8% | 34.13 | +70.6% |
| 2023.00 | 24.00 | 35.58 | +48.2% | 48.43 | +101.8% | 37.52 | +56.3% | 36.01 | +50.0% | 37.37 | +55.7% | 36.71 | +52.9% | 47.73 | +98.9% | 48.44 | +101.8% | 34.30 | +42.9% | 36.93 | +53.9% |
| 2024.00 | 29.00 | 36.52 | +25.9% | 81.06 | +179.5% | 42.02 | +44.9% | 37.44 | +29.1% | 39.34 | +35.6% | 38.34 | +32.2% | 77.41 | +166.9% | 81.10 | +179.7% | 34.78 | +19.9% | 38.86 | +34.0% |
| 2025.00 | 35.00 | 36.99 | +5.7% | 151.42 | +332.6% | 46.47 | +32.8% | 38.33 | +9.5% | 40.52 | +15.8% | 39.32 | +12.3% | 139.96 | +299.9% | 151.51 | +332.9% | 34.97 | -0.1% | 40.16 | +14.8% |

*\*Nota Metodológica:* Para los años con adopción real = 0.0M, la desviación porcentual relativa se registra como **N/D** (No Disponible por división matemática entre cero). La métrica MAPE de ajuste se calcula exclusivamente sobre la ventana de años con adopción histórica no nula (adopción real > 0.0M) para garantizar rigor estadístico.

---

## 🔮 4. Proyecciones Futuras de Adopción (Horizonte Temporal)
Predicciones de adopción acumulada (en millones) para los próximos 10 años (horizonte proyectado):

| Año | Bass Clásico (M) | Dual Market (M) | Fourt & Woodlock (M) | Gompertz (M) | Bass Generalizado (GBM) (M) | Horsky & Simon (M) | Muller & Yogev (M) | Van den Bulte & Joshi (M) | Difusión Logística R&K (M) | Ladrón-de-Guevara & Putsis (M) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026.00 | 37.22 | 267.16 | 50.89 | 38.87 | 41.18 | 39.89 | 244.72 | 267.29 | 35.05 | 41.03 |
| 2027.00 | 37.33 | 392.61 | 55.26 | 39.20 | 41.52 | 40.22 |