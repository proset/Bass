import sys
sys.path.append(r"C:\Users\roset\Bass")
from config import get_conn, release_conn

conn = get_conn()
cursor = conn.cursor()

# Phase A2
cursor.execute("""
    ALTER TABLE historical_adoption
      ADD COLUMN IF NOT EXISTS source text,
      ADD COLUMN IF NOT EXISTS source_date date,
      ADD COLUMN IF NOT EXISTS metric_type text,
      ADD COLUMN IF NOT EXISTS is_estimate boolean DEFAULT false;
""")

# Phase A3
cursor.execute("DELETE FROM historical_adoption WHERE tecnologia = 'chatgpt' AND anio = 2026;")

# Phase A4
queries = [
    "UPDATE historical_adoption SET source='Pre-lanzamiento', metric_type='WAU', is_estimate=false WHERE tecnologia='chatgpt' AND anio=2021;",
    "UPDATE historical_adoption SET source='Estimación terceros (Similarweb/UBS) — sin primaria', source_date='2022-12-31', metric_type='WAU', is_estimate=true WHERE tecnologia='chatgpt' AND anio=2022;",
    "UPDATE historical_adoption SET source='Estimación terceros — sin primaria', source_date='2023-12-31', metric_type='WAU', is_estimate=true WHERE tecnologia='chatgpt' AND anio=2023;",
    "UPDATE historical_adoption SET source='Reportado por medios citando a OpenAI (dic-2024); primaria no localizada', source_date='2024-12-31', metric_type='WAU', is_estimate=true WHERE tecnologia='chatgpt' AND anio=2024;",
    "UPDATE historical_adoption SET source='Estimación sin verificación (rango agregadores 700-800M)', source_date='2025-12-31', metric_type='WAU', is_estimate=true WHERE tecnologia='chatgpt' AND anio=2025;"
]
for q in queries:
    cursor.execute(q)

conn.commit()

# Phase A5
cursor.execute("SELECT anio, adopcion_acumulada, source, is_estimate FROM historical_adoption WHERE tecnologia='chatgpt' ORDER BY anio;")
rows = cursor.fetchall()
col_names = [desc[0] for desc in cursor.description]

print("--- RESULTADO A5 ---")
for r in rows:
    print({col_names[i]: r[i] for i in range(len(col_names))})

cursor.close()
release_conn(conn)
