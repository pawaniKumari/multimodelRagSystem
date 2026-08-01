import psycopg2
from psycopg2.extras import RealDictCursor
from src.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def get_db_connection():
    """Establishes and returns a database connection."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def execute_query(query: str, params: tuple = ()):
    """Executes a query and returns results as a list of dictionaries."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if cur.description:  # If query returns data
                results = cur.fetchall()
            else:
                conn.commit()
                results = None
            return results
    finally:
        conn.close()