import os
from src.database import get_db_connection

def initialize_database():
    """Executes schema.sql to setup tables and extensions."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
            conn.commit()
            print("Successfully initialized PostgreSQL database schema and pgvector extension.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_database()