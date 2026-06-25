from e2b import Template

template = (
    Template()
    .from_template("code-interpreter-v1")
    .pip_install([
        "databricks-sql-connector",
        "databricks-sdk",
        "pandas",
        "numpy",
        "matplotlib",
        "neo4j",
    ])
)