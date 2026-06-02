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

    if "query_databricks(" not in code:
        raise ValueError(
            "Generated code must use query_databricks()"
        )

    if "result" not in code:
        raise ValueError(
            "Generated code must assign result"
        )