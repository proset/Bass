# Informe de Adopción: toyota

## DATOS INSUFICIENTES PARA PROYECCIÓN

Este informe no incluye proyecciones de adopción porque la calidad de los datos disponibles no permite un ajuste fiable.

### Serie disponible
| Año | Adopción (M) |
|---|---|
| 2015 | 10.10 M |
| 2016 | 20.30 M |
| 2017 | 30.80 M |
| 2018 | 41.40 M |
| 2019 | 51.80 M |
| 2020 | 61.80 M |
| 2021 | 72.10 M |
| 2022 | 82.70 M |
| 2023 | 93.80 M |
| 2024 | 104.80 M |
| 2025 | 116.10 M |

### Motivo
Toyota es una empresa activa y relevante, pero esta serie es inservible porque la métrica subyacente es completamente indeterminada y no corresponde a ningún indicador tecnológico público conocido de la compañía. El crecimiento perfectamente lineal de ~10M por año durante 11 años consecutivos, sin ninguna perturbación por COVID, crisis de semiconductores ni cambios de mercado, es una señal inequívoca de datos sintéticos o interpolados artificialmente. Ninguna métrica real de Toyota —vehículos vendidos, electrificados acumulados, usuarios conectados, descargas de app— produce esta forma ni estos valores desde 2015.

### Qué haría falta
- Serie histórica más larga (mínimo 4-6 puntos con datos verificados)
- Métrica consistente entre años (MAU, usuarios, unidades — sin mezclar)
- Si la empresa no publica datos: añadir valores verificados a custom_anchors.json

### Cuándo reintentar
Re-ejecuta el pipeline cuando dispongas de más historial o anchors verificados: los productos jóvenes acumulan un punto de datos por año.
