from fastapi import APIRouter

from backend.app.services.neo4j_service import (
    verify_neo4j_connection,
    get_graph_schema_context,
)

router = APIRouter(
    prefix="/neo4j",
    tags=["Neo4j"],
)


@router.get("/health")
def neo4j_health():
    verify_neo4j_connection()
    return {"status": "ok"}


@router.get("/schema-context")
def neo4j_schema_context():
    return get_graph_schema_context()