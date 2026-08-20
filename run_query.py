import sys
sys.path.append(r"C:\Users\roset\Bass")
from config import get_conn, release_conn

conn = get_conn()
cursor = conn.cursor()
cursor.execute("""
    SELECT tecnologia, COUNT(*) FILTER (WHERE anio = 2026) AS filas_2026
    FROM historical_adoption GROUP BY tecnologia
    HAVING COUNT(*) FILTER (WHERE anio = 2026) > 0 ORDER BY 1;
""")
rows = cursor.fetchall()
for r in rows:
    print(f"Tech: {r[0]}, Filas 2026: {r[1]}")
cursor.close()
release_conn(conn)
