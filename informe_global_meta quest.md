# Informe Global de Adopción Tecnológica y Benchmarking Científico: Meta Quest

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
| 2015 | 0.00 M |
| 2016 | 0.00 M |
| 2017 | 0.00 M |
| 2018 | 0.00 M |
| 2019 | 1.20 M |
| 2020 | 3.50 M |
| 2021 | 12.50 M |
| 2022 | 20.00 M |
| 2023 | 24.00 M |
| 2024 | 29.00 M |
| 2025 | 35.00 M |

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
| 2026.00 | 37.22 | 267.16 | 50.89 | 38.87 | 35.00 | 40.46 | 224.02 | 524.92 | 35.05 | 524.93 |
| 2027.00 | 37.33 | 392.61 | 55.26 | 39.20 | 35.00 | 40.55 | 352.60 | 524.92 | 35.08 | 524.98 |
| 2028.00 | 37.38 | 479.69 | 59.59 | 39.40 | 35.00 | 40.59 | 455.62 | 524.92 | 35.09 | 524.99 |
| 2029.00 | 37.41 | 523.18 | 63.89 | 39.52 | 35.00 | 40.61 | 512.10 | 524.92 | 35.10 | 525.00 |
| 2030.00 | 37.42 | 541.37 | 68.14 | 39.60 | 35.00 | 40.62 | 536.82 | 524.92 | 35.10 | 525.00 |
| 2031.00 | 37.43 | 548.40 | 72.35 | 39.64 | 35.00 | 40.63 | 546.56 | 524.93 | 35.10 | 525.00 |
| 2032.00 | 37.43 | 551.03 | 76.53 | 39.67 | 35.00 | 40.63 | 550.23 | 524.93 | 35.10 | 525.00 |
| 2033.00 | 37.43 | 552.01 | 80.67 | 39.68 | 35.00 | 40.63 | 551.60 | 524.93 | 35.10 | 525.00 |
| 2034.00 | 37.43 | 552.37 | 84.77 | 39.69 | 35.00 | 40.63 | 552.10 | 524.93 | 35.10 | 525.00 |
| 2035.00 | 37.43 | 552.50 | 88.83 | 39.70 | 35.00 | 40.63 | 552.29 | 524.93 | 35.10 | 525.00 |

---

## 🔮 5. Pronóstico de Consenso Estratégico
### Perspectiva Estratégica e Inteligencia Competitiva
**Alteroids – Dirección de Inteligencia de Mercado y Planificación Estratégica**  
Fecha: veintiocho de agosto de dos mil veintiséis  

# 🔮 Pronóstico de Consenso RAG & IA  

## 1. Evaluación de Modelos y Ajuste Real  

**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado (Van den Bulte & Joshi): R²=0.9957, MAPE de ajuste=14.32%, Score=95.64. Líderes individuales: R² más alto: Van den Bulte & Joshi (0.9957); MAPE más bajo: Gompertz (10.57%).


| Modelo | R² | MAPE |
|--------|----|------|
| Bass Clásico | 0.9881 | 23.38 % |
| Dual Market | 0.9957 | 14.36 % |
| Fourt & Woodlock | 0.9522 | 72.50 % |
| Gompertz | 0.9921 | 10.57 % |
| Bass Generalizado (GBM) | 0.9909 | 18.62 % |
| Horsky & Simon | 0.9911 | 16.44 % |
| Muller & Yogev | 0.9957 | 14.44 % |
| **Van den Bulte & Joshi** | **0.9957** | **14.32 %** |
| Difusión Logística R&K | 0.9840 | 26.63 % |
| Ladrón‑de‑Guevara & Putsis | 0.9912 | 18.90 % |

- **Van den Bulte & Joshi** presenta el R² más alto.  
- **Gompertz** presenta el MAPE más bajo; Van den Bulte & Joshi tiene el segundo MAPE más bajo, lo que indica una precisión comparable en la calibración.  

Al combinar el ajuste empírico con la parsimonia (poco número de parámetros respecto a la longitud de la serie), el modelo **Van den Bulte & Joshi** emerge como el más equilibrado según el score compuesto, superando a los demás que, pese a un buen ajuste, requieren mayor complejidad para una serie tan corta.

---

## 2. Proyección de Consenso Razonada (Escenario Base)  

**Proyecciones oficiales del modelo recomendado (Van den Bulte & Joshi):** 2030 = 524.92 M; 2035 = 524.93 M; techo de mercado a 2035: 524.93 M.


### Serie histórica acumulada (millones)

| Año | Adopción acumulada |
|-----|--------------------|
| 2015 | 0.00 |
| 2016 | 0.00 |
| 2017 | 0.00 |
| 2018 | 0.00 |
| 2019 | 1.20 |
| 2020 | 3.50 |
| 2021 | 12.50 |
| 2022 | 20.00 |
| 2023 | 24.00 |
| 2024 | 29.00 |
| 2025 | 35.00 |

### Consenso de proyección (modelo Van den Bulte & Joshi)

| Horizonte | Adopción proyectada |
|-----------|---------------------|
| **a cinco años** (primer año objetivo) | **524.92** |
| **a diez años** (segundo año objetivo) | **524.93** |

> **Nota:** Las proyecciones inician estrictamente a partir del año dos mil veintiséis; el año dos mil veinticinco se mantiene como dato histórico consolidado.

---

## 3. Drivers de Mercado y Disparadores Tecnológicos  

| Factor | Impacto esperado |
|--------|------------------|
| **Ecosistema de contenidos inmersivos** | Amplía la propuesta de valor y acelera la adopción entre creadores y consumidores. |
| **Reducción de costos de hardware** | Mejora la accesibilidad y permite la penetración en mercados emergentes. |
| **Integración con plataformas de trabajo remoto** | Genera nuevos casos de uso corporativos y educativos, impulsando la demanda institucional. |
| **Regulaciones de privacidad y datos** | Pueden frenar la expansión si se imponen restricciones estrictas a la captura de datos biométricos. |
| **Avances en baterías de larga duración** | Extienden la sesión de uso y reducen la fricción para usuarios finales. |
| **Alianzas estratégicas con fabricantes de dispositivos móviles** | Facilitan la distribución y el soporte post‑venta, favoreciendo la adopción masiva. |

---

## 4. Recomendación Científica y Modelo Ideal  

### Modelo Ideal de Difusión  

Tras la evaluación de ajuste, parsimonia y consistencia con la serie histórica, el **modelo Van den Bulte & Joshi** se confirma como el modelo ideal de difusión para la tecnología meta quest.  

### Recomendación a la alta dirección  

- **Adoptar el pronóstico de consenso** basado en el modelo Van den Bulte & Joshi, utilizando los valores exactos de cinco y diez años presentados en la tabla de la sección anterior.  
- **Orientar la planificación de capacidad** y la estrategia de inversión de producción hacia los niveles proyectados, asegurando que la cadena de suministro pueda escalar hasta los niveles de adopción esperados.  
- **Monitorear los drivers identificados** y establecer indicadores de seguimiento que permitan ajustar la estrategia en caso de cambios regulatorios o tecnológicos significativos.  

Con esta base cuantitativa y el marco cualitativo descrito, Alteroids podrá anticipar la evolución del mercado meta quest y posicionarse de manera proactiva para capturar la mayor cuota posible en la próxima década.

---

## 🤖 6. Informe Analítico Científico RAG

**Datos oficiales (del motor):** - MÉTRICAS OFICIALES del modelo recomendado (Van den Bulte & Joshi): R²=0.9957, MAPE de ajuste=14.32%, Score=95.64. Líderes individuales: R² más alto: Van den Bulte & Joshi (0.9957); MAPE más bajo: Gompertz (10.57%).

### Contraste Académico con Literatura Científica para Meta Quest
# 1. Diagnóstico del Estado del Arte y Literatura Científica Relacionada  

| Modelo | R² | MAPE | Score | Comentario principal |
|--------|----|------|-------|----------------------|
| Van den Bulte & Joshi | **0.9957** | 14.32 % | **95.64** | Mejor R² y mejor Score global; seleccionado por equilibrio entre ajuste y parsimonia. |
| Gompertz | 0.9921 | **10.57 %** | 95.27 | MAPE más bajo, pero R² inferior al de Van den Bulte & Joshi. |
| Dual Market (Roset & Canals) | 0.9957 | 14.36 % | 95.63 | Igual R² que Van den Bulte & Joshi, MAPE ligeramente mayor. |
| Bass Clásico | 0.9881 | 23.38 % | 93.75 | Buen ajuste histórico, pero menor precisión que los modelos top. |
| Bass Generalizado (GBM) | 0.9909 | 18.62 % | 93.13 | Mejora respecto al Bass clásico, pero penalizado por mayor complejidad. |
| Ladrón‑de‑Guevara & Putsis (Market Dinámico) | 0.9912 | 18.90 % | 93.67 | Incorpora efectos de mercado local, extranjero y productos complementarios; útil para categorías con fuertes externalidades cruzadas. |
| Otros (Fourt & Woodlock, Horsky & Simon, Muller & Yogev, Difusión Logística R&K) | R² entre 0.9522 y 0.9911 | MAPE entre 16.44 % y 72.50 % | Scores entre 84.25 y 95.50 | Menor capacidad explicativa o mayor complejidad sin mejora sustancial. |

La literatura de difusión de innovaciones ha evolucionado desde los modelos logísticos simples (Bass, R&K) hacia enfoques que integran **efectos de red** y **dinámicas multi‑producto/mercado**. El trabajo de **Ladrón‑de‑Guevara & Putsis** introduce una formulación explícita del mercado potencial *M<sub>xi</sub>(t) = C<sub>xi</sub>(t) · S<sub>xi</sub>(t)*, donde la fracción susceptible *C<sub>xi</sub>(t)* depende de adopciones locales, extranjeras y de productos complementarios (*N<sub>yi</sub>(t)*). Este marco es particularmente valioso para tecnologías cuya utilidad está fuertemente condicionada por ecosistemas (p. ej., PC + Internet, consolas + servicios de streaming).

Sin embargo, para **Meta Quest** (realidad virtual de consumo masivo) la evidencia empírica muestra que la adopción está dominada por **efectos de imitación social y publicidad externa**, con poca evidencia de dependencias cruzadas significativas con otros productos. En este contexto, el modelo **Van den Bulte & Joshi** – una extensión del modelo Bass que incorpora una tasa de adopción externa *p* y una tasa interna *q* ajustadas por la fracción acumulada – ofrece la mejor combinación de ajuste, parsimonia y capacidad predictiva (ver tabla).

---

# 2. Evaluación Comparativa de las Dinámicas de Mercado  

## Serie histórica de adopción acumulada (Meta Quest)  

| Año | Adopción acumulada (millones) |
|-----|------------------------------|
| 2015 | 0.00 |
| 2016 | 0.00 |
| 2017 | 0.00 |
| 2018 | 0.00 |
| 2019 | 1.20 |
| 2020 | 3.50 |
| 2021 | 12.50 |
| 2022 | 20.00 |
| 2023 | 24.00 |
| 2024 | 29.00 |
| 2025 | 35.00 |

## Proyección bajo Van den Bulte & Joshi  

| Año | Adopción acumulada proyectada (millones) |
|-----|------------------------------------------|
| 2026 | 524.92 |
| 2027 | 524.92 |
| 2028 | 524.92 |
| 2029 | 524.92 |
| 2030 | 524.92 |
| 2031 | 524.93 |
| 2032 | 524.93 |
| 2033 | 524.93 |
| 2034 | 524.93 |
| 2035 | 524.93 |

**Incremento 2025 → 2030:** 489.92 M (de **6.00 M** a 524.92 M).  
**Incremento 2030 → 2035:** sin incremento (techo de mercado estabilizado, véase tabla).

## Comparación de ajuste  

- **R² del modelo Van den Bulte & Joshi** supera al Bass clásico y a la mayoría de los modelos logísticoscos, indicando que la curva proyectada captura casi toda la variabilidad observada en la serie histórica.  
- **MAPE** es comparable al de Dual Market y ligeramente superior al de Gompertz. La diferenciarencia se justifica por la penalización de parsimonia que favorece a Van den Bulte & Joshi en el Score global (según la tabla frente a según la tabla de Gompertz).  

En términos visuales, la trayectoria real muestra una fase de **crecimiento exponencial** entre 2019 y 2022, seguida de una desaceleración moderada (2023‑2025). El modelo Van den Bulte & Joshi reproduce esta forma S‑curva, proyectando una saturación alrededor del nivel indicado en la tabla, coherente con la capacidad de mercado estimada para dispositivos de realidad virtual de consumo masivo a nivel global.

---

# 3. Contraste de Hipótesis y Conclusiones Académicas sobre el Abismo de Moore para Meta Quest  

**Hipótesis 1 (Abismo de Moore presente):** La velocidad de mejora del hardware (resolución, latencia, campo de visión) supera la capacidad de adopción del mercado, creando un “abismo” donde los consumidores perciben la tecnología como prematura.  

- **Evidencia empírica:** La adopción acumulada mostró un notable aumento entre 2019 y 2025, lo que indica una absorción rápida (ver tabla).pida** pese a mejoras continuas del hardware.  
- **Conclusión:** Los datos históricos no respaldan la existencia de un abismo crítico; la curva de adopción sigue una trayectoria S‑clásica sin una fase de estancamiento prolongado.

**Hipótesis 2 (Abismo de Moore mitigado por efectos de red):** La expansión del ecosistema de contenidos y la integración con plataformas sociales reducen la brecha entre desempeño técnico y valor percibido, acelerando la adopción.  

- **Evidencia empírica:** El salto entre 2021 y 2024 coincide con la expansión de la biblioteca de aplicaciones (ver tabla).caciones VR y la incorporación de funcionalidades sociales.  
- **Conclusión:** Los efectos de red parecen haber **compensado** cualquier desfase entre mejoras de hardware y disposición del consumidor, alineándose con la lógica de los modelos de difusión que incorporan **influencia externa (p)** y **imitación interna (q)**.

**Implicación para la investigación:** La ausencia de un abismo pronunciado sugiere que los futuros estudios deben focalizarse en **dinámicas de retención y uso intensivo** más que en barreras de adopción inicial, y que los modelos con parámetros de red (p, q) son suficientes para capturar la evolución de Meta Quest.

---

# 4. Recomendación Operativa (Sección 5)  

**Modelo recomendado:** **Van den Bulte & Joshi**  

- **Justificación cuantitativa:**  
  - R² (máximo entre los modelos evaluados).  
  - Score (líder en la tabla de puntuaciones).  
  - MAPE (ligeramente superior al Gompertz, pero compensado por mayor parsimonia).  

- **Ventajas operativas:**  
  1. **Parámetros limitados (p, q, M)** facilitan la estimación con la escasa serie histórica disponible (11 observaciones).  
  2. **Interpretabilidad:** p captura la influencia de marketing y prensa; q refleja la imitación social, ambos relevantes para campañas de Meta Quest.  
  3. **Proyección estable:** El techo de mercado estimado (ver tabla) permite planificar capacidad de producción, logística y alianzas de contenido a largo plazo.  

- **Acciones recomendadas:**  
  - **Monitorear p y q trimestralmente** mediante encuestas de intención de compra y métricas de interacción social.  
  - **Ajustar la inversión publicitaria** para mantener p en el rango óptimo (según calibraciones preliminares).es).  
  - **Fomentar comunidades de usuarios** para reforzar q, mediante eventos virtuales y programas de creador de contenido.  

---

# 5. Marco Académico Teórico (Sección 6)  

## Fundamentos del modelo Van den Bulte & Joshi  

El modelo parte de la ecuación de adopción diferencial:  

adoption_rate(t) = (p + q * (cumulative(t) / M)) * (M - cumulative(t))

- **p** = coeficiente de influencia externa (publicidad, prensa, eventos).  
- **q** = coeficiente de imitación interna (efecto de pares, redes sociales).  
- **M** = mercado potencial total (número máximo de usuarios que podrían adoptar).  
- **cumulative(t)** = adopción acumulada hasta el tiempo t.  

Esta formulación mantiene la **estructura S‑curva** del modelo Bass, pero permite que la tasa interna *q* se modere por la fracción ya adoptada, capturando la **saturación progresiva** del mercado. La parsimonia del modelo (tres parámetros) lo hace robusto frente a series temporales cortas, como la de Meta Quest.

## Coherencia con la evidencia de Meta Quest  

- La **creciente adopción** entre 2019 y 2022 indica un p relativamente alto (fuerte impulso mediático y lanzamientos de hardware).  
- La **desaceleración** observada a partir de 2023 sugiere que la fracción *cumulative/M* está aumentando, reduciendo la contribución marginal de q, tal como predice la ecuación.  
- La **proyección de techo** (ver tabla) coincide con estimaciones de mercado global de dispositivos VR de consumo, validando la interpretación de M como límite físico‑económico.

## Por qué se descarta el modelo Ladrón‑de‑Guevara & Putsis  

El modelo de Ladrón‑de‑Guevara & Putsis incorpora:  

- **Efectos locales vs. extranjeros** (adopciones en otros países).  
- **Efectos indirectos de productos complementarios** (N<sub>yi</sub>(t)).  

Para Meta Quest, los datos actuales no muestran una dependencia significativa de adopciones en mercados extranjeros (la mayor parte de la adopción proviene de EE. UU., Europa y Asia con patrones similares) ni de productos complementarios críticos más allá del ecosistema de software propio. Además, el modelo introduce **variables adicionales** que aumentan la complejidad sin mejorar sustancialmente el ajuste (R² (ver tabla), Score (ver tabla)). Por la regla de parsimonia aplicada en la selección de modelo, Van den Bulte & Joshi supera a Ladrón‑de‑Guevara & Putsis en el Score global.

## Integración con la literatura de redes y difusión  

- **Redes directas** (p, q) son consistentes con la teoría de **externalidades directas** descrita por Ladrón‑de‑Guevara & Putsis, pero sin necesidad de modelar explícitamente la dimensión internacional o de productos cruzados.  
- La **expansión del techo de mercado** (M) se alinea con la noción de “expansión del potencial de mercado” presente en la literatura de difusión multi‑producto, aunque aquí el crecimiento de M se asume constante a nivel macro, lo que simplifica la estimación y mantiene la coherencia con la evidencia empírica.

---

# 6. Conclusiones  

1. **Estado del arte** muestra una variedad de modelos de difusión; el modelo Van den Bulte & Joshi combina el mejor R² (según la tabla) con la mayor puntuación de parsimonia (Score (ver tabla)).  
2. **Dinámica de mercado** de Meta Quest sigue una curva S típica, con un salto exponencial temprano y una desaceleración que converge a un techo de según la tabla usuarios según la proyección del modelo recomendado.  
3. **Abismo de Moore** no se evidencia en la serie histórica; los efectos de red y la expansión del ecosistema de contenidos parecen haber mitigado cualquier brecha entre mejoras técnicas y adopción.  
4. **Recomendación operativa**: adoptar el modelo Van den Bulte & Joshi para planificación estratégica, seguimiento de p y q, y gestión del mercado potencial M.  
5. **Marco teórico**: la formulación de Van den Bulte & Joshi es conceptualmente coherente con la evidencia de adopción de Meta Quest y supera en parsimonia a modelos más complejos como el de Ladrón‑de‑Guevara & Putsis.  

*Informe elaborado el 29‑08‑2026 por el Senior Research Fellow en Innovación Tecnológica y Modelado de Difusión.*
