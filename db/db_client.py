import psycopg2
from pgvector.psycopg2 import register_vector
from shared import config
import psycopg2.extras
from psycopg2 import sql
from shared import logger

log = logger.get_logger(__name__)

conn = None
def initdb():
    global conn
    log.info("Connecting to database...")
    print(config.get('DB_NAME'));
    DATABASE = {
        'dbname': config.get('PG_DATABASE'),
        'user': config.get('PG_USER'),
        'password': config.get('PG_PASSWORD'),
        'host': config.get('PG_HOST'),
        'port': config.get('PG_PORT')
    }


    conn = psycopg2.connect(**DATABASE)
    conn.cursor().execute('CREATE EXTENSION IF NOT EXISTS vector')
    register_vector(conn)
    log.info("Connected to database...")



def get_conn():
    return conn
def drop_table(table_name):
    """Drop the given table if it exists."""
    try:
        cursor = conn.cursor()

        cursor.execute(f"""
            DROP TABLE IF EXISTS {table_name};
        """)

        conn.commit()
        cursor.close()

        log.info(f"Table {table_name} dropped successfully!")
    except Exception as e:
        log.error(f"Error dropping table: {e}")
def check_table_exists(table_name):
    """Check if the given table exists in the database."""
    try:
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_name='{table_name}'
            );
        """)

        result = cursor.fetchone()[0]
        cursor.close()

        return result
    except Exception as e:
        print(f"Error: {e}")
        return False

def commit():
    get_conn().commit()

def close():
    get_conn().close()


def table_has_records(table_name):
    """Check if the given table has any records."""
    try:
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT EXISTS (
                SELECT 1 FROM {table_name} LIMIT 1
            );
        """)

        # Fetch the result, which will be True if there's at least one record
        has_records = cursor.fetchone()[0]
        cursor.close()

        return has_records
    except Exception as e:
        print(f"Error: {e}")
        return False  # Return False if there's an error



def remove_table(table_name):
    """Remove all tables from the database."""
    try:
        conn = get_conn()
        cursor = conn.cursor()

        # SQL command to drop the specified table
        drop_query = sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(sql.Identifier(table_name))

        cursor.execute(drop_query)
        conn.commit()
        cursor.close()

        print(f"Table {table_name} has been dropped successfully.")
    except Exception as e:
        print(f"Error dropping table {table_name}: {e}")

