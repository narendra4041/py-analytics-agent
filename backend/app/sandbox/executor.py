import os

from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox

load_dotenv()


RUNTIME_CODE = """
import os
import pandas as pd

from databricks import sql
from databricks.sdk.core import Config, oauth_service_principal


def get_credentials_provider():
    config = Config(
        host=f"https://{os.environ['DATABRICKS_SERVER_HOSTNAME']}",
        client_id=os.environ["DATABRICKS_CLIENT_ID"],
        client_secret=os.environ["DATABRICKS_CLIENT_SECRET"],
    )
    return oauth_service_principal(config)


def query_databricks(query: str) -> pd.DataFrame:
    conn = sql.connect(
        server_hostname=os.environ["DATABRICKS_SERVER_HOSTNAME"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        credentials_provider=get_credentials_provider,
    )

    try:
        return pd.read_sql(query, conn)
    finally:
        conn.close()
"""


def execute_python_code(code: str):
    full_code = (
        RUNTIME_CODE
        + "\n\n"
        + code
        + "\n\n"
        + "result"
    )

    with Sandbox.create(
        "py-analytics-agent",
        envs={
            "DATABRICKS_SERVER_HOSTNAME": os.getenv("DATABRICKS_SERVER_HOSTNAME"),
            "DATABRICKS_HTTP_PATH": os.getenv("DATABRICKS_HTTP_PATH"),
            "DATABRICKS_CLIENT_ID": os.getenv("DATABRICKS_CLIENT_ID"),
            "DATABRICKS_CLIENT_SECRET": os.getenv("DATABRICKS_CLIENT_SECRET"),
        }
    ) as sandbox:
        execution = sandbox.run_code(full_code)
        chart_base64 = None

        try:
            file_content = sandbox.files.read("/home/user/output.png", format="bytes")
            import base64
            chart_base64 = base64.b64encode(file_content).decode("utf-8")
        except Exception:
            chart_base64 = None

    
    return {
        "text": execution.text,
        "results": [
            {
                "text": r.text,
                "json": r.json,
            }
            for r in execution.results
        ],
        "logs": {
            "stdout": execution.logs.stdout,
            "stderr": execution.logs.stderr,
        },
        "error": str(execution.error) if execution.error else None,
        "chart_base64": chart_base64,
    }