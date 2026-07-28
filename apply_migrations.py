import os
import toml
import psycopg2

def main():
    print("Iniciando la aplicación de migraciones de base de datos...")
    try:
        secrets = toml.load(os.path.join(".streamlit", "secrets.toml"))
        conn_params = secrets["postgres"]
    except Exception as e:
        print(f"Error leyendo secrets.toml: {e}")
        return

    try:
        conn = psycopg2.connect(
            host=conn_params["host"],
            database=conn_params["database"],
            user=conn_params["user"],
            password=conn_params["password"],
            port=conn_params.get("port", 6543)
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 1. Alterar columnas a DOUBLE PRECISION
        print("Alterando columnas a DOUBLE PRECISION en historical_adoption...")
        cursor.execute("ALTER TABLE historical_adoption ALTER COLUMN adopcion_acumulada TYPE DOUBLE PRECISION;")
        cursor.execute("ALTER TABLE historical_adoption ALTER COLUMN adopcion_anual TYPE DOUBLE PRECISION;")
        
        # 2. Agregar created_at y updated_at
        print("Agregando created_at y updated_at a historical_adoption...")
        cursor.execute("ALTER TABLE historical_adoption ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now();")
        cursor.execute("ALTER TABLE historical_adoption ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();")
        
        # 3. Crear índice HNSW en pgvector
        print("Creando índice HNSW de similitud de coseno en papers_embeddings...")
        # Nota: La extensión HNSW requiere vector_cosine_ops o similar y está disponible en pgvector v0.5.0+
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS papers_embeddings_hnsw_idx ON papers_embeddings USING hnsw (vector_embedding vector_cosine_ops);")
            print("Índice HNSW creado correctamente.")
        except Exception as idx_err:
            print(f"Advertencia: No se pudo crear el índice HNSW: {idx_err}. Intentando con IVFFlat de respaldo...")
            cursor.execute("CREATE INDEX IF NOT EXISTS papers_embeddings_ivfflat_idx ON papers_embeddings USING ivfflat (vector_embedding vector_cosine_ops) WITH (lists = 100);")
            print("Índice IVFFlat creado como alternativa.")
            
        print("Migraciones ejecutadas exitosamente en la base de datos.")
        cursor.close()
        conn.close()
    except Exception as err:
        print(f"Error ejecutando las migraciones: {err}")

if __name__ == "__main__":
    main()
