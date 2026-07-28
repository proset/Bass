import pandas as pd
import logging
from psycopg2.extras import DictCursor, RealDictCursor
from config import get_conn, release_conn

logger = logging.getLogger("BassLoaders")

def normalize_tech_name(tech):
    """Normaliza el nombre de la tecnología: trim y minúsculas."""
    if not tech:
        return ""
    return tech.strip().lower()

def get_tecnologias_disponibles():
    """Obtiene la lista de nombres de tecnologías disponibles en la base de datos (únicas, ordenadas y en minúsculas)."""
    db_conn = get_conn()
    try:
        query = "SELECT DISTINCT tecnologia FROM historical_adoption"
        df = pd.read_sql(query, db_conn)
        if df.empty:
            return ["inteligencia artificial"]
        # Filtrar duplicados eliminando espacios y forzando minúsculas
        unique_techs = sorted(list(set(t.strip().lower() for t in df['tecnologia'].tolist() if t)))
        if not unique_techs:
            return ["inteligencia artificial"]
        return unique_techs
    except Exception as e:
        logger.error(f"Error cargando tecnologías disponibles: {e}")
        return ["inteligencia artificial"]
    finally:
        release_conn(db_conn)

def load_historical_data(tech):
    """Carga los datos históricos para una tecnología dada (case-insensitive)."""
    tech_norm = normalize_tech_name(tech)
    db_conn = get_conn()
    try:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM historical_adoption WHERE LOWER(TRIM(tecnologia)) = %s ORDER BY anio",
                (tech_norm,)
            )
            rows = cur.fetchall()
        return pd.DataFrame(rows) if rows else pd.DataFrame()
    except Exception as e:
        logger.error(f"Error cargando datos históricos para '{tech}': {e}")
        return pd.DataFrame()
    finally:
        release_conn(db_conn)

def load_model_parameters(tech):
    """Carga los parámetros estimados de los modelos para una tecnología dada (case-insensitive)."""
    tech_norm = normalize_tech_name(tech)
    db_conn = get_conn()
    try:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM model_parameters WHERE LOWER(TRIM(tecnologia)) = %s",
                (tech_norm,)
            )
            rows = cur.fetchall()
        if not rows:
            return {}
        return {row["modelo_tipo"]: dict(row) for row in rows}
    except Exception as e:
        logger.error(f"Error cargando parámetros de modelos para '{tech}': {e}")
        return {}
    finally:
        release_conn(db_conn)

def load_qualitative_analysis(tech):
    """Carga el análisis cualitativo en formato markdown para una tecnología dada (case-insensitive)."""
    tech_norm = normalize_tech_name(tech)
    db_conn = get_conn()
    try:
        with db_conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT analisis FROM qualitative_analysis WHERE LOWER(TRIM(tecnologia)) = %s", (tech_norm,))
            row = cur.fetchone()
        if row:
            return row["analisis"]
    except Exception as e:
        logger.error(f"Error cargando análisis cualitativo: {e}")
    finally:
        release_conn(db_conn)
    return None

def load_consenso_forecast(tech):
    """Carga el pronóstico de consenso en formato markdown para una tecnología dada (case-insensitive)."""
    tech_norm = normalize_tech_name(tech)
    db_conn = get_conn()
    try:
        with db_conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT consenso FROM consensus_forecast WHERE LOWER(TRIM(tecnologia)) = %s", (tech_norm,))
            row = cur.fetchone()
        if row:
            return row["consenso"]
    except Exception as e:
        logger.error(f"Error cargando pronóstico de consenso: {e}")
    finally:
        release_conn(db_conn)
    return None
