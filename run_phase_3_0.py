import sys
sys.path.append(r"C:\Users\roset\Bass")
from config import get_conn, release_conn

conn = get_conn()
cursor = conn.cursor()

cursor.execute("""
    ALTER TABLE model_parameters
      ADD COLUMN IF NOT EXISTS mape_ajuste double precision,
      ADD COLUMN IF NOT EXISTS mape_backtest double precision,
      ADD COLUMN IF NOT EXISTS score double precision,
      ADD COLUMN IF NOT EXISTS n_params integer;
""")
conn.commit()

cursor.close()
release_conn(conn)
