import os
import pandas as pd

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


def query_databricks(query: str) -> pd.DataFrame:
    conn = sql.connect(
        server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME"),
        http_path=os.getenv("DATABRICKS_HTTP_PATH"),
        credentials_provider=get_credentials_provider,
    )

    try:
        return pd.read_sql(query, conn)
    finally:
        conn.close()