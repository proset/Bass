# Informe de Adopción: coches  toyota

## DATOS INSUFICIENTES PARA PROYECCIÓN

Este informe no incluye proyecciones de adopción porque la calidad de los datos disponibles no permite un ajuste fiable.

### Serie disponible
| Año | Adopción (M) |
|---|---|
| 2016 | 1.20 M |
| 2017 | 3.50 M |
| 2018 | 8.00 M |
| 2019 | 15.60 M |
| 2020 | 28.90 M |
| 2021 | 45.20 M |
| 2022 | 62.40 M |
| 2023 | 78.10 M |
| 2024 | 91.50 M |
| 2025 | 102.00 M |

### Motivo
La serie es fundamentalmente inservible porque la métrica subyacente es irreconocible e incompatible con cualquier dato conocido de Toyota: ni ventas anuales (~10M/año), ni acumulado histórico (>200M unidades desde los años 50), ni parque circulante activo (~100-150M globales, pero alcanzado hace décadas, no en 2024). Los valores parecen extraídos de una fuente que mezcla o malinterpreta completamente la métrica, posiblemente confundiendo 'coches Toyota' con algún servicio digital específico (app, plataforma conectada) sin etiquetar correctamente. No hay forma de corregir la serie sin identificar primero qué métrica real se está midiendo.

### Qué haría falta
- Serie histórica más larga (mínimo 4-6 puntos con datos verificados)
- Métrica consistente entre años (MAU, usuarios, unidades — sin mezclar)
- Si la empresa no publica datos: añadir valores verificados a custom_anchors.json

### Cuándo reintentar
Re-ejecuta el pipeline cuando dispongas de más historial o anchors verificados: los productos jóvenes acumulan un punto de datos por año.
