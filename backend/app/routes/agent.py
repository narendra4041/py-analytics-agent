from uuid import uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from backend.app.auth import get_current_user_id
from backend.app.models import AgentChatRequest

from backend.app.db.cosmos import messages_container

from backend.app.routes.chats import (
    get_chat_by_id,
    get_recent_messages,
)

from backend.app.services.intent_service import classify_intent

from backend.app.services.databricks_service import (
    get_schema_context,
)

from backend.app.services.llm_service import (
    generate_python_code,
    repair_python_code,
)

from backend.app.sandbox.executor import execute_python_code

from backend.app.storage.blob import upload_chart_base64

from backend.app.safety import validate_generated_code
from backend.app.services.neo4j_service import get_graph_schema_prompt_context

router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)

@router.post("/chat")
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

    graph_schema_context = get_graph_schema_prompt_context()

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
        graph_schema_context=graph_schema_context,
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
            graph_schema_context=graph_schema_context,
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
        chart_artifact = upload_chart_base64(
            assistant_result["chart_base64"],
            payload.chat_id,
        )

        assistant_result["blob_name"] = chart_artifact["blob_name"]
        assistant_result.pop("chart_url", None)
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

    response_result = assistant_result.copy()

    if (
        response_result.get("type") == "chart"
        and response_result.get("blob_name")
    ):
        response_result["chart_url"] = chart_artifact["chart_url"]

    return {
        "chat_id": payload.chat_id,
        "code": code,
        "result": response_result,
        "execution_error": execution["error"],
        "was_repaired": was_repaired,
    }