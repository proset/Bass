import sys
import os
sys.path.append(r"C:\Users\roset\Bass")
from config import get_conn

def check_reports():
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT tecnologia FROM historical_adoption WHERE tecnologia LIKE '%chat%' OR tecnologia LIKE '%openai%';")
    techs = cur.fetchall()
    print("Technologies matching 'chat' or 'openai':", techs)
    
    # Try to find where the report is stored. There might be a table for qualitative analysis or global report
    # Let's list all tables in the public schema
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    tables = [r[0] for r in cur.fetchall()]
    print("Tables:", tables)
    
    if 'analisis_cualitativo' in tables:
        cur.execute("SELECT tecnologia FROM analisis_cualitativo WHERE tecnologia LIKE '%chat%' OR tecnologia LIKE '%openai%';")
        print("analisis_cualitativo for:", cur.fetchall())
        
    if 'consenso_forecast' in tables:
        cur.execute("SELECT tecnologia FROM consenso_forecast WHERE tecnologia LIKE '%chat%' OR tecnologia LIKE '%openai%';")
        print("consenso_forecast for:", cur.fetchall())
        
    # Is there an informe_global table?
    if 'informe_global' in tables:
        cur.execute("SELECT tecnologia FROM informe_global WHERE tecnologia LIKE '%chat%' OR tecnologia LIKE '%openai%';")
        print("informe_global for:", cur.fetchall())
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_reports()
