import numpy as np
import pandas as pd
import logging
from config import get_conn, release_conn
from data.loaders import get_tecnologias_disponibles, load_historical_data
from data.ingestion import guardar_parametros_db
from models.fit_models import fit_all_models

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("DualMarketSolverCLI")

def main():
    logger.info("Iniciando el script CLI de optimización Dual Market Solver...")
    
    # Obtener tecnologías de la base de datos
    tecnologias = get_tecnologias_disponibles()
    
    if not tecnologias:
        logger.warning("No se encontraron tecnologías registradas en historical_adoption.")
        return

    logger.info(f"Se procesarán {len(tecnologias)} tecnologías en total.")

    for tech in tecnologias:
        logger.info(f"\n--- Procesando Tecnología: '{tech}' ---")
        
        # Cargar datos históricos
        df_tech = load_historical_data(tech)
        if df_tech.empty or len(df_tech) < 5:
            logger.warning(f"[{tech}] Datos insuficientes para modelado (mínimo 5 años). Saltando...")
            continue
            
        t_data = np.arange(len(df_tech))
        n_data = df_tech["adopcion_acumulada"].values
        
        logger.info(f"[{tech}] Ajustando los 7 modelos de difusión a la serie real...")
        fits = fit_all_models(t_data, n_data)
        
        if fits:
            logger.info(f"[{tech}] Guardando parámetros ajustados en la base de datos...")
            success = guardar_parametros_db(tech, fits)
            if success:
                logger.info(f"[{tech}] ¡Proceso completado exitosamente!")
                # Mostrar el modelo ganador
                best_model = None
                best_r2 = -np.inf
                for m, f in fits.items():
                    if f["r_cuadrado"] > best_r2:
                        best_r2 = f["r_cuadrado"]
                        best_model = m
                logger.info(f"[{tech}] Modelo recomendado: {best_model} (R² = {best_r2:.4f})")
            else:
                logger.error(f"[{tech}] Error al guardar los parámetros en la base de datos.")
        else:
            logger.error(f"[{tech}] No se pudo ajustar ningún modelo matemático.")

    logger.info("\nProceso global de optimización de curvas finalizado.")

if __name__ == "__main__":
    main()
