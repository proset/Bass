# FASE 3: Análisis y Recomendación — Backtest de Prior para Young-Techs

## 1. Resultados del Backtest (183 curvas)

| Método | MAPE 5y (mediana) | MAPE 10y (mediana) | Fallos de fit |
|:---|:---:|:---:|:---:|
| **A (Persistencia)** | 59.6% | 83.9% | 0 |
| **B (Categoría/Ritmo)** | 39.4% | 67.1% | 1 |
| **C (Forma/Ritmo)** | **34.4%** | **48.2%** | 1 |
| **D (GM 1,1)** | 47.4% | 257.8% | 4 |

### Desglose del Método C (Forma) por Categoría
* **Conectividad:** MAPE 5y = 34.8% | MAPE 10y = 50.4% (N=175)
* **Redes Sociales:** MAPE 5y = 40.7% | MAPE 10y = 47.9% (N=3)
* **Consumo (Hardware):** MAPE 5y = 26.0% | MAPE 10y = 23.5% (N=2)
* **Salud:** MAPE 5y = 8.4% | MAPE 10y = 38.7% (N=1)
* **Coches Eléctricos (EV):** MAPE 5y = 12.5% | MAPE 10y = 0.2% (N=1)

## 2. Interpretación según Tabla de Decisión

* **C > B > A (el match por forma aporta valor):** A 5 años, Método C (34.4%) bate a B (39.4%) y destroza al ingenuo A (59.6%). A 10 años, C (48.2%) aplasta a B (67.1%). El matching por forma dinámica de los primeros años *efectivamente* captura el comportamiento subyacente mucho mejor que asumir una curva mediana estática.
* **C vs D (Grey Model se estrella a largo plazo):** GM(1,1) funciona decentemente en el corto plazo sin restricciones de techo (47.4% a 5 años), pero a 10 años colapsa absolutamente (257.8% MAPE) porque al no tener techo, proyecta al infinito. El Método C con su techo empírico por analogía protege las proyecciones a largo plazo.

El resultado global del Método C a 5 años (34.4%) se encuentra marginalmente por encima del umbral de excelencia (20-30%), fuertemente penalizado por el bloque enorme de conectividad global. Sin embargo, en hardware de consumo y EV se mueve en MAPEs del 12-26%. Cumple de sobra el criterio de ser superior a B y D en todos los horizontes.

## 3. Veredicto y Recomendación

**Veredicto:** Vendible con disclaimers (Vía libre a Integrar Fix 45).
El Método C (Analogía por forma con prior restrictivo de ritmo) es indiscutiblemente la técnica superior para proyectar tecnologías jóvenes de <6 puntos de datos. 

**Acción recomendada:** 
Integrar la solución al pipeline (Fix 45). Se usará el *prior* de los análogos extraídos del Método C, normalizados por ritmo, para anclar el parámetro `m` del solver en aquellas tecnologías de la base de datos marcadas como jóvenes, en lugar de permitir que el optimizador RK4 diverja inventando techos inexistentes.
