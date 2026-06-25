BLOCKED_PATTERNS = [
    "os.system",
    "subprocess",
    "eval(",
    "exec(",
    "open(",
    "socket",
    "requests.",
    "httpx.",
    "urllib",
    "shutil",
    "pathlib",
    "glob",
    "__import__",
    "importlib",
    "pip install",
    "sql.connect",
    "databricks.sql",
    "client_secret",
    "access_token",
]


def validate_generated_code(code: str) -> None:
    lowered = code.lower()

    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in lowered:
            raise ValueError(
                f"Blocked unsafe code pattern: {pattern}"
            )

    has_databricks = "query_databricks(" in code
    has_neo4j = "query_neo4j(" in code

    if not has_databricks and not has_neo4j:
        raise ValueError(
            "Generated code must use query_databricks() or query_neo4j()."
        )
    if "result" not in code:
        raise ValueError(
            "Generated code must assign result"
        )