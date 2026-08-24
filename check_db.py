from config import get_conn
from psycopg2.extras import RealDictCursor
c = get_conn()
cur = c.cursor(cursor_factory=RealDictCursor)
cur.execute("SELECT anio, adopcion_acumulada, source, is_estimate FROM historical_adoption WHERE tecnologia='netflix' ORDER BY anio")
rows = cur.fetchall()
if not rows:
    print("No hay datos de Netflix en la BD.")
for r in rows:
    source = (r['source'] or 'N/A')[:60]
    print(f"{r['anio']}: {r['adopcion_acumulada']}M (Est: {r['is_estimate']}) - {source}")
