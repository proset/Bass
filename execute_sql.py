import os
import toml
import psycopg2

def main():
    secrets = toml.load(os.path.join(".streamlit", "secrets.toml"))
    conn_params = secrets["postgres"]
    
    conn = psycopg2.connect(
        host=conn_params["host"],
        database=conn_params["database"],
        user=conn_params["user"],
        password=conn_params["password"],
        port=conn_params.get("port", 6543)
    )
    conn.autocommit = True
    
    with open("supabase_schema.sql", "r", encoding="utf-8") as f:
        sql = f.read()
        
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        print("Esquema SQL ejecutado correctamente.")
    except Exception as e:
        print(f"Error ejecutando SQL: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
