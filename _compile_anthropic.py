from data.loaders import load_historical_data, load_model_parameters
from ai.analysis import generar_consenso_pronostico_ia
from data.ingestion import guardar_consenso_forecast
from data.report_compiler import compilar_informe_global
from config import get_conn, release_conn

tech = 'anthropic'

# Regenerar consenso con el nuevo prompt que preselecciona el modelo
df = load_historical_data(tech)
params = load_model_parameters(tech)
conn = get_conn(); cur = conn.cursor()
cur.execute("SELECT analisis FROM qualitative_analysis WHERE LOWER(TRIM(tecnologia))=%s", (tech,))
row = cur.fetchone(); analisis = row[0] if row else ''
cur.close(); release_conn(conn)

print("Regenerando consenso con modelo preseleccionado...")
consenso = generar_consenso_pronostico_ia(tech, df, params, analisis)
guardar_consenso_forecast(tech, consenso)
print("Consenso guardado. Compilando informe...")

try:
    compilar_informe_global(tech)
    print("GATE: True ✅")
except Exception as e:
    msg = str(e)
    if 'Blockers' in msg:
        import re
        for b in re.findall(r'"([^"]+)"', msg):
            print(f"BLOCKER: {b[:130]}")
    else:
        print(f"ERROR: {msg[:300]}")
