from fastapi import FastAPI
from backend.app.routes.chats import router as chats_router
from backend.app.services.databricks_service import (
    test_connection,
    list_catalogs,
    list_schemas,
    list_tables,
    get_schema_context,
)
from pydantic import BaseModel
from backend.app.services.llm_service import generate_python_code

app = FastAPI(title="py-analytics-agent")

app.include_router(chats_router)


@app.get("/health")
def health():
    return {"status": "ok"}



@app.get("/databricks/test")
def databricks_test():
    return {
        "user": test_connection()
    }


@app.get("/databricks/catalogs")
def databricks_catalogs():
    return {
        "catalogs": list_catalogs()
    }

@app.get("/databricks/schemas")
def databricks_schemas(catalog: str):
    return {
        "catalog": catalog,
        "schemas": list_schemas(catalog),
    }

@app.get("/databricks/tables")
def databricks_tables(
    catalog: str,
    schema: str,
):
    return {
        "catalog": catalog,
        "schema": schema,
        "tables": list_tables(
            catalog,
            schema,
        ),
    }

@app.get("/databricks/schema-context")
def databricks_schema_context(
    catalog: str,
    schema: str,
):
    return get_schema_context(catalog, schema)

class GenerateCodeRequest(BaseModel):
    query: str
    catalog: str
    schema: str

@app.post("/agent/generate-code")
def agent_generate_code(payload: GenerateCodeRequest):
    schema_context = get_schema_context(
        payload.catalog,
        payload.schema,
    )

    code = generate_python_code(
        user_query=payload.query,
        catalog=payload.catalog,
        schema=payload.schema,
        schema_context=schema_context,
    )

    return {
        "code": code
    }