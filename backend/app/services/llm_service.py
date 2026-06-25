import os

from dotenv import load_dotenv
from openai import OpenAI

from backend.app.prompts import PYTHON_CODE_GENERATION_PROMPT
from backend.app.services.neo4j_service import get_graph_schema_prompt_context

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_python_code(
    user_query: str,
    catalog: str,
    schema: str,
    schema_context: dict,
    conversation_history: list | None = None,
    graph_schema_context: str | None = None,
):
    
    conversation_history = conversation_history or []

    history_text = "\n".join(
        [
            f"{msg['role']}: {msg.get('content')}"
            for msg in conversation_history
        ]
    )
    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": PYTHON_CODE_GENERATION_PROMPT,
            },
            {
                "role": "user",
                "content": f"""
                    Selected Databricks catalog:
                    {catalog}

                    Selected Databricks schema:
                    {schema}

                    Databricks schema context:
                    {schema_context}

                    Neo4j graph schema context:
                    {graph_schema_context}

                    Recent conversation:
                    {history_text}

                    Current user question:
                    {user_query}
                    """,
            },
        ],
    )

    return response.choices[0].message.content

def repair_python_code(
    original_code: str,
    error: str,
    user_query: str,
    catalog: str,
    schema: str,
    schema_context: dict,
    conversation_history: list | None = None,
    graph_schema_context: str | None = None,
):
    conversation_history = conversation_history or []

    history_text = "\n".join(
        f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
        for msg in conversation_history[-5:]
    )

    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": PYTHON_CODE_GENERATION_PROMPT,
            },
            {
                "role": "user",
                "content": f"""
The previous Python code failed.

Fix the code and return ONLY corrected executable Python code.

Selected Databricks catalog:
{catalog}

Selected Databricks schema:
{schema}

Databricks schema context:
{schema_context}

Neo4j graph schema context:
{graph_schema_context}

Recent conversation:
{history_text}

User question:
{user_query}

Failed code:
{original_code}

Execution error:
{error}
""",
            },
        ],
    )

    return response.choices[0].message.content