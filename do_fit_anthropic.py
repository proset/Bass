import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data.loaders import load_historical_data
from models.fit_models import fit_all_models
from data.ingestion import guardar_parametros_db

tech = 'anthropic'
df = load_historical_data(tech)
t_data = df['anio'].values
n_data = df['adopcion_acumulada'].values

fits = fit_all_models(t_data, n_data)
if fits:
    guardar_parametros_db(tech, fits)
    print("Fit completed.")
else:
    print("Fit failed.")
