import os
import logging
import toml
import psycopg2
from psycopg2 import pool as pg_pool

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("BassConfig")

# ==========================================
# Carga de Parámetros de Base de Datos y APIs
# ==========================================
conn_params = {}
GEMINI_API_KEY = None

# Intentar cargar desde Streamlit secrets.toml
try:
    import streamlit as st
    if "postgres" in st.secrets:
        conn_params = st.secrets["postgres"]
    if "gemini" in st.secrets:
        GEMINI_API_KEY = st.secrets["gemini"].get("api_key") or st.secrets.get("gemini_api_key")
except Exception:
    pass

# Si no está en streamlit, intentar cargar desde toml directo
if not conn_params or not GEMINI_API_KEY:
    try:
        secrets_path = os.path.join(".streamlit", "secrets.toml")
        if os.path.exists(secrets_path):
            secrets = toml.load(secrets_path)
            if not conn_params and "postgres" in secrets:
                conn_params = secrets["postgres"]
            if not GEMINI_API_KEY and "gemini" in secrets:
                GEMINI_API_KEY = secrets["gemini"].get("api_key") or secrets.get("gemini_api_key")
    except Exception as e:
        logger.warning(f"No se pudo cargar secrets.toml directamente: {e}")

# Fallback a variables de entorno (prioritario para despliegue en contenedores/CI)
PG_HOST = os.environ.get("PG_HOST") or conn_params.get("host") or os.environ.get("DB_HOST") or os.environ.get("POSTGRES_HOST")
PG_DATABASE = os.environ.get("PG_DATABASE") or conn_params.get("database") or os.environ.get("DB_NAME") or os.environ.get("POSTGRES_DATABASE") or "postgres"
PG_USER = os.environ.get("PG_USER") or conn_params.get("user") or os.environ.get("DB_USER") or os.environ.get("POSTGRES_USER")
PG_PASSWORD = os.environ.get("PG_PASSWORD") or conn_params.get("password") or os.environ.get("DB_PASSWORD") or os.environ.get("POSTGRES_PASSWORD")

env_port = os.environ.get("PG_PORT") or conn_params.get("port") or os.environ.get("DB_PORT") or os.environ.get("POSTGRES_PORT")
PG_PORT = int(env_port) if env_port else 6543

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or GEMINI_API_KEY

conn_dict = {
    "host": PG_HOST,
    "database": PG_DATABASE,
    "user": PG_USER,
    "password": PG_PASSWORD,
    "port": PG_PORT
}

# ==========================================
# Constantes de Modelos de Gemini
# ==========================================
GEMINI_PRIMARY = "gemini-2.5-flash"
GEMINI_FALLBACKS = ["gemini-1.5-flash", "gemini-1.5-pro"]
EMBEDDING_MODEL = "models/gemini-embedding-001"

# ==========================================
# Connection Pool (Thread-safe)
# ==========================================
_pool = None

def get_pool():
    global _pool
    if _pool is None:
        try:
            _pool = pg_pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=15,
                connect_timeout=10,
                **conn_dict
            )
            logger.info("ThreadedConnectionPool de PostgreSQL inicializado correctamente.")
        except Exception as e:
            logger.error(f"Error inicializando Connection Pool: {e}")
            raise
    return _pool

def get_conn():
    """
    Obtiene una conexión del pool.
    Realiza una verificación ping rápida para asegurar que la conexión esté viva.
    """
    try:
        pool = get_pool()
        db_conn = pool.getconn()
        db_conn.autocommit = True
        
        # Ping check
        try:
            with db_conn.cursor() as cur:
                cur.execute("SELECT 1")
        except Exception:
            logger.warning("Conexión muerta detectada en el pool, reemplazando...")
            try:
                pool.putconn(db_conn, close=True)
            except Exception:
                pass
            db_conn = pool.getconn()
            db_conn.autocommit = True
        return db_conn
    except Exception as e:
        logger.error(f"Error obteniendo conexión del pool: {e}. Activando fallback de conexión directa.")
        try:
            direct_conn = psycopg2.connect(connect_timeout=10, **conn_dict)
            direct_conn.autocommit = True
            return direct_conn
        except Exception as direct_e:
            logger.critical(f"Fallo crítico: No se pudo conectar a la base de datos tampoco de forma directa: {direct_e}")
            raise

def release_conn(db_conn):
    """Devuelve de forma segura la conexión al pool."""
    if db_conn is None:
        return
    try:
        pool = get_pool()
        pool.putconn(db_conn)
    except Exception as e:
        logger.warning(f"No se pudo devolver la conexión al pool (cerrándola directamente): {e}")
        try:
            db_conn.close()
        except Exception:
            pass
