import os

from dotenv import load_dotenv
from openai import OpenAI

from backend.app.prompts import PYTHON_CODE_GENERATION_PROMPT

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_python_code(
    user_query: str,
    catalog: str,
    schema: str,
    schema_context: dict,
    conversation_history: list | None = None,
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
                    Selected catalog:
                    {catalog}

                    Selected schema:
                    {schema}

                    Available schema context:
                    {schema_context}

                    Recent conversation:
                    {history_text}

                    Current user question:
                    {user_query}
                    """,
            },
        ],
    )

    return response.choices[0].message.content