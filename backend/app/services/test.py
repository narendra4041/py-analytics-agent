from pprint import pprint

from backend.app.services.neo4j_service import (
    verify_neo4j_connection,
    query_neo4j,
    get_graph_schema_context,
)


verify_neo4j_connection()
print("Neo4j connectivity verified.")

df = query_neo4j("""
MATCH (n)
RETURN labels(n) AS labels, count(*) AS count
LIMIT 10
""")

print("\nNode counts:")
print(df)

schema_context = get_graph_schema_context()

print("\nRelationship counts:")
pprint(schema_context["relationship_counts"])

print("\nRelationship patterns:")
pprint(schema_context["relationship_patterns"][:10])

print("\nNode properties sample:")
pprint(schema_context["node_properties"][:20])