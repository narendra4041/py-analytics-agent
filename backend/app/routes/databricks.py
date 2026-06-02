from fastapi import APIRouter

from backend.app.services.databricks_service import (
    list_catalogs,
    list_schemas,
    list_tables,
)

router = APIRouter(
    prefix="/databricks",
    tags=["Databricks"],
)


@router.get("/catalogs")
def get_catalogs():
    return {
        "catalogs": list_catalogs()
    }


@router.get("/schemas")
def get_schemas(catalog: str):
    return {
        "catalog": catalog,
        "schemas": list_schemas(catalog),
    }


@router.get("/tables")
def get_tables(
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