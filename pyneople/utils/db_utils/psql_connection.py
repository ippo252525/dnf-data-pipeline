import psycopg2
from pyneople.config.config import Settings
from contextlib import contextmanager

@contextmanager
def psql_connection():
    """
    with psql_connection() as conn:
    """
    conn = psycopg2.connect(
        dbname=Settings.POSTGRES_DB,
        user=Settings.POSTGRES_USER,
        password=Settings.POSTGRES_PASSWORD,
        host=Settings.POSTGRES_HOST,
        port=Settings.POSTGRES_PORT
    ) 
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()