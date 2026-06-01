import os

from databricks import sql
from databricks.sdk.core import Config, oauth_service_principal
from dotenv import load_dotenv

load_dotenv()


def get_credentials_provider():
    config = Config(
        host=f"https://{os.getenv('DATABRICKS_SERVER_HOSTNAME')}",
        client_id=os.getenv("DATABRICKS_CLIENT_ID"),
        client_secret=os.getenv("DATABRICKS_CLIENT_SECRET"),
    )

    return oauth_service_principal(config)


def get_connection():
    return sql.connect(
        server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME"),
        http_path=os.getenv("DATABRICKS_HTTP_PATH"),
        credentials_provider=get_credentials_provider,
    )


def test_connection():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT current_user()")
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row[0]

def list_catalogs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SHOW CATALOGS")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [row[0] for row in rows]

def list_schemas(catalog: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"SHOW SCHEMAS IN {catalog}")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [row[0] for row in rows]

def list_tables(catalog: str, schema: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"SHOW TABLES IN {catalog}.{schema}"
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [row[1] for row in rows]

def get_schema_context(catalog: str, schema: str):
    conn = get_connection()
    cursor = conn.cursor()

    query = f"""
    SELECT
        table_name,
        column_name,
        data_type,
        comment
    FROM {catalog}.information_schema.columns
    WHERE table_schema = '{schema}'
    ORDER BY table_name, ordinal_position
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    tables = {}

    for table_name, column_name, data_type, comment in rows:
        tables.setdefault(table_name, []).append({
            "column": column_name,
            "type": data_type,
            "comment": comment,
        })

    return {
        "catalog": catalog,
        "schema": schema,
        "tables": tables,
    }