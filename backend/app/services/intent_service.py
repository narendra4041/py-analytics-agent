import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def classify_intent(
    message: str,
    conversation_history: list | None = None,
) -> str:
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
                "content": """
You classify user messages for a data analytics chat agent.

Return ONLY one word:

ANALYTICS
or
GENERAL

ANALYTICS means:
- user asks about data
- user asks for metrics
- user asks for a chart
- user asks for a table
- user asks to query/analyze records
- user asks a follow-up about previous analysis

GENERAL means:
- greetings
- thanks
- casual conversation
- asks what the assistant can do
- non-data questions
""",
            },
            {
                "role": "user",
                "content": f"""
Previous conversation:
{history_text}

Current message:
{message}
""",
            },
        ],
    )

    intent = response.choices[0].message.content.strip().upper()

    if intent not in {"ANALYTICS", "GENERAL"}:
        return "GENERAL"

    return intent