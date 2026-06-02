from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from backend.app.auth import get_current_user_id
from backend.app.db.cosmos import (
    chat_sessions_container,
    messages_container,
)
from backend.app.models import (
    ChatSessionCreate,
    MessageCreate,
)

router = APIRouter(tags=["Chats"])


@router.post("/chats")
def create_chat(
    payload: ChatSessionCreate,
    user_id: str = Depends(get_current_user_id),
):
    chat = {
        "id": str(uuid4()),
        "user_id": user_id,
        "title": payload.title,
        "catalog": payload.catalog,
        "schema": payload.schema,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    chat_sessions_container.create_item(chat)
    return chat


@router.get("/chats")
def get_chats(
    user_id: str = Depends(get_current_user_id),
):
    query = """
    SELECT * FROM c
    WHERE c.user_id = @user_id
    ORDER BY c.created_at DESC
    """

    return list(
        chat_sessions_container.query_items(
            query=query,
            parameters=[{"name": "@user_id", "value": user_id}],
            partition_key=user_id,
        )
    )


@router.post("/chats/{chat_id}/messages")
def create_message(
    chat_id: str,
    payload: MessageCreate,
    user_id: str = Depends(get_current_user_id),
):
    message = {
        "id": str(uuid4()),
        "chat_id": chat_id,
        "user_id": user_id,
        "role": payload.role,
        "content": payload.content,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    messages_container.create_item(message)
    return message


@router.get("/chats/{chat_id}/messages")
def get_messages(
    chat_id: str,
    user_id: str = Depends(get_current_user_id),
):
    chat = get_chat_by_id(
        chat_id=chat_id,
        user_id=user_id,
    )

    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found",
        )

    query = """
    SELECT * FROM c
    WHERE c.chat_id = @chat_id
    AND c.user_id = @user_id
    ORDER BY c.created_at ASC
    """

    return list(
        messages_container.query_items(
            query=query,
            parameters=[
                {"name": "@chat_id", "value": chat_id},
                {"name": "@user_id", "value": user_id},
            ],
            partition_key=chat_id,
        )
    )

def get_chat_by_id(chat_id: str, user_id: str):
    query = """
    SELECT * FROM c
    WHERE c.id = @chat_id
    AND c.user_id = @user_id
    """

    items = list(
        chat_sessions_container.query_items(
            query=query,
            parameters=[
                {"name": "@chat_id", "value": chat_id},
                {"name": "@user_id", "value": user_id},
            ],
            partition_key=user_id,
        )
    )

    if not items:
        return None

    return items[0]

def get_recent_messages(chat_id: str, user_id: str, limit: int = 10):
    query = """
    SELECT * FROM c
    WHERE c.chat_id = @chat_id
    AND c.user_id = @user_id
    ORDER BY c.created_at DESC
    """

    items = list(
        messages_container.query_items(
            query=query,
            parameters=[
                {"name": "@chat_id", "value": chat_id},
                {"name": "@user_id", "value": user_id},
            ],
            partition_key=chat_id,
        )
    )

    items = items[:limit]

    return list(reversed(items))