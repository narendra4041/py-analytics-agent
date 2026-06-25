import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase


ENV_PATH = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=True,
)


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if value is None or value.strip() == "":
        raise ValueError(f"Missing required environment variable: {name}")

    return value.strip()


NEO4J_URI = get_required_env("NEO4J_URI")
NEO4J_USERNAME = get_required_env("NEO4J_USERNAME")
NEO4J_PASSWORD = get_required_env("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j").strip()


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
)


def verify_neo4j_connection() -> None:
    driver.verify_connectivity()


def run_cypher(
    cypher: str,
    parameters: dict | None = None,
) -> list[dict]:
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(cypher, parameters or {})
        return [record.data() for record in result]


def query_neo4j(cypher: str) -> pd.DataFrame:
    records = run_cypher(cypher)
    return pd.DataFrame(records)


def get_graph_schema_context() -> dict:
    node_counts = run_cypher("""
    MATCH (n)
    UNWIND labels(n) AS label
    RETURN
        label,
        count(*) AS count
    ORDER BY count DESC
    """)

    relationship_counts = run_cypher("""
    MATCH ()-[r]->()
    RETURN
        type(r) AS relationship_type,
        count(*) AS count
    ORDER BY count DESC
    """)

    relationship_patterns = run_cypher("""
    MATCH (source)-[r]->(target)
    RETURN
        labels(source) AS source_labels,
        type(r) AS relationship_type,
        labels(target) AS target_labels,
        count(*) AS count
    ORDER BY count DESC
    LIMIT 100
    """)

    node_properties = run_cypher("""
    CALL db.schema.nodeTypeProperties()
    YIELD nodeLabels, propertyName, propertyTypes, mandatory
    RETURN
        nodeLabels,
        propertyName,
        propertyTypes,
        mandatory
    ORDER BY nodeLabels, propertyName
    """)

    relationship_properties = run_cypher("""
    CALL db.schema.relTypeProperties()
    YIELD relType, propertyName, propertyTypes, mandatory
    RETURN
        relType,
        propertyName,
        propertyTypes,
        mandatory
    ORDER BY relType, propertyName
    """)

    return {
        "database": NEO4J_DATABASE,
        "node_counts": node_counts,
        "relationship_counts": relationship_counts,
        "relationship_patterns": relationship_patterns,
        "node_properties": node_properties,
        "relationship_properties": relationship_properties,
    }

def get_graph_schema_prompt_context() -> str:
    context = get_graph_schema_context()

    lines = []

    lines.append("Node labels and counts:")
    for item in context["node_counts"]:
        lines.append(f"- {item['label']}: {item['count']} nodes")

    lines.append("\nRelationship types and counts:")
    for item in context["relationship_counts"]:
        lines.append(
            f"- {item['relationship_type']}: {item['count']} relationships"
        )

    lines.append("\nRelationship patterns:")
    for item in context["relationship_patterns"][:50]:
        source = ":".join(item["source_labels"])
        target = ":".join(item["target_labels"])
        rel = item["relationship_type"]
        count = item["count"]

        lines.append(
            f"- ({source})-[:{rel}]->({target})  count={count}"
        )

    lines.append("\nNode properties:")
    for item in context["node_properties"]:
        labels = ":".join(item["nodeLabels"])
        prop = item["propertyName"]
        types = ", ".join(item["propertyTypes"])
        mandatory = item["mandatory"]

        lines.append(
            f"- {labels}.{prop}: {types}, mandatory={mandatory}"
        )

    lines.append("\nRelationship properties:")
    for item in context["relationship_properties"]:
        rel = item["relType"]
        prop = item["propertyName"]
        types = ", ".join(item["propertyTypes"])
        mandatory = item["mandatory"]

        lines.append(
            f"- {rel}.{prop}: {types}, mandatory={mandatory}"
        )

    return "\n".join(lines)