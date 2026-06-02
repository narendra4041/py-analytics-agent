from fastapi import FastAPI
from backend.app.routes.chats import router as chats_router
from backend.app.services.databricks_service import (
    test_connection,
    list_catalogs,
    list_schemas,
    list_tables,
    get_schema_context,
)
from backend.app.services.llm_service import (
    generate_python_code,
    repair_python_code,
)
from backend.app.sandbox.executor import execute_python_code
from backend.app.models import ExecuteCodeRequest, GenerateCodeRequest

from fastapi import Depends, HTTPException

from backend.app.auth import get_current_user_id
from backend.app.models import AgentChatRequest
from backend.app.routes.chats import (
    get_chat_by_id,
    get_recent_messages,
)
from backend.app.db.cosmos import messages_container
from uuid import uuid4
from datetime import datetime, timezone
from backend.app.storage.blob import upload_chart_base64
from backend.app.services.intent_service import classify_intent
from backend.app.safety import validate_generated_code

app = FastAPI(title="py-analytics-agent")

app.include_router(chats_router)


@app.get("/health")
def health():
    return {"status": "ok"}



@app.get("/databricks/test")
def databricks_test():
    return {
        "user": test_connection()
    }


@app.get("/databricks/catalogs")
def databricks_catalogs():
    return {
        "catalogs": list_catalogs()
    }

@app.get("/databricks/schemas")
def databricks_schemas(catalog: str):
    return {
        "catalog": catalog,
        "schemas": list_schemas(catalog),
    }

@app.get("/databricks/tables")
def databricks_tables(
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

@app.get("/databricks/schema-context")
def databricks_schema_context(
    catalog: str,
    schema: str,
):
    return get_schema_context(catalog, schema)


@app.post("/agent/generate-code")
def agent_generate_code(payload: GenerateCodeRequest):
    schema_context = get_schema_context(
        payload.catalog,
        payload.schema,
    )

    code = generate_python_code(
        user_query=payload.query,
        catalog=payload.catalog,
        schema=payload.schema,
        schema_context=schema_context,
    )

    return {
        "code": code
    }

@app.post("/agent/execute-code")
def agent_execute_code(payload: ExecuteCodeRequest):

    response = execute_python_code(
        payload.code
    )

    return response


@app.post("/agent/chat")
def agent_chat(
    payload: AgentChatRequest,
    user_id: str = Depends(get_current_user_id),
):
    chat = get_chat_by_id(
        chat_id=payload.chat_id,
        user_id=user_id,
    )

    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )

    user_message = {
        "id": str(uuid4()),
        "chat_id": payload.chat_id,
        "user_id": user_id,
        "role": "user",
        "content": payload.message,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    messages_container.create_item(user_message)
    
    conversation_history = get_recent_messages(
        chat_id=payload.chat_id,
        user_id=user_id,
        limit=10,
    )

    intent = classify_intent(
        message=payload.message,
        conversation_history=conversation_history,
    )

    assistant_result = None
    was_repaired = False

    if intent == "GENERAL":
        assistant_result = {
            "type": "text",
            "summary": "Hi, I can help you analyze your data, create tables, and generate charts."
        }

        assistant_message = {
            "id": str(uuid4()),
            "chat_id": payload.chat_id,
            "user_id": user_id,
            "role": "assistant",
            "content": assistant_result,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        messages_container.create_item(assistant_message)

        return {
            "chat_id": payload.chat_id,
            "intent": intent,
            "result": assistant_result,
            "execution_error": None,
        }

    schema_context = get_schema_context(
        chat["catalog"],
        chat["schema"],
    )

    code = generate_python_code(
        user_query=payload.message,
        catalog=chat["catalog"],
        schema=chat["schema"],
        schema_context=schema_context,
        conversation_history=conversation_history,
    )
    
    
    validate_generated_code(code)
    execution = execute_python_code(code)

    if execution["error"]:
        repaired_code = repair_python_code(
            original_code=code,
            error=execution["error"],
            user_query=payload.message,
            catalog=chat["catalog"],
            schema=chat["schema"],
            schema_context=schema_context,
            conversation_history=conversation_history,
        )

        repaired_execution = execute_python_code(repaired_code)
        was_repaired = True
        code = repaired_code
        validate_generated_code(repaired_code)
        execution = execute_python_code(repaired_code)

    if execution["results"]:
        assistant_result = execution["results"][0]["json"]

    if assistant_result is None and execution.get("chart_base64"):
        assistant_result = {
            "type": "chart",
            "summary": "Chart generated successfully",
            "chart_base64": execution["chart_base64"],
        }
    
    if (
        assistant_result
        and assistant_result.get("type") == "chart"
        and assistant_result.get("chart_base64")
    ):
        chart_url = upload_chart_base64(
            assistant_result["chart_base64"],
            payload.chat_id,
        )

        assistant_result["chart_url"] = chart_url
        assistant_result.pop("chart_base64", None)

    assistant_message = {
        "id": str(uuid4()),
        "chat_id": payload.chat_id,
        "user_id": user_id,
        "role": "assistant",
        "content": assistant_result,
        "generated_code": code,
        "execution": execution,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    messages_container.create_item(assistant_message)

    return {
        "chat_id": payload.chat_id,
        "code": code,
        "result": assistant_result,
        "execution_error": execution["error"],
        "was_repaired": was_repaired,
    }