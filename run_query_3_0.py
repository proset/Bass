import sys
sys.path.append(r"C:\Users\roset\Bass")
from config import get_conn, release_conn

conn = get_conn()
cursor = conn.cursor()

cursor.execute("""
    SELECT modelo_tipo, score, n_params, mape_ajuste, mape_backtest
    FROM model_parameters WHERE tecnologia='chatgpt' ORDER BY score DESC;
""")
rows = cursor.fetchall()
for r in rows:
    print(r)

cursor.close()
release_conn(conn)
