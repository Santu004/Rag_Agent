from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from backend.app.core.database import get_db
from backend.app.models.chat_history import ChatHistory
from backend.app.graph.rag_graph import rag_graph
from backend.app.services.history_service import (
    save_chat_history,
    get_chat_history,
)

# =====================================================
# Router Configuration
# =====================================================

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

# =====================================================
# Pydantic Schemas (Request / Response)
# =====================================================

class ChatRequest(BaseModel):
    """
    Request body for chat endpoint.
    Represents a single user query.
    """
    session_id: str
    question: str


class ChatResponse(BaseModel):
    """
    Response body for chat endpoint.
    Contains the AI-generated answer.
    """
    answer: str


class ChatHistoryItem(BaseModel):
    """
    Single chat message formatted
    for frontend (Streamlit).
    """
    role: str
    content: str


# =====================================================
# Chat Endpoint (RAG Interaction)
# =====================================================

@router.post("/", response_model=ChatResponse)
def chat_endpoint(
    payload: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Handle a chat interaction with the RAG agent.

    Flow:
    1. Validate user input
    2. Invoke LangGraph-based RAG agent
    3. Persist user + assistant messages to PostgreSQL
    4. Return assistant response
    """

    # Basic validation
    if not payload.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        # Invoke LangGraph RAG workflow
        result = rag_graph.invoke(
            {"question": payload.question}
        )

        answer: str = result["answer"]

        # Persist chat history
        save_chat_history(
            db=db,
            session_id=payload.session_id,
            user_message=payload.question,
            ai_message=answer,
        )

        return ChatResponse(answer=answer)

    except Exception as e:
        # Fail-safe error handling
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# Fetch Chat History (Per Thread)
# =====================================================

@router.get(
    "/history/{session_id}",
    response_model=List[ChatHistoryItem]
)
def get_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Fetch full chat history for a given session (thread).

    Behavior:
    - Messages are returned in chronological order
    - Output format is frontend (Streamlit) friendly
    """

    history = get_chat_history(db, session_id)

    messages: List[ChatHistoryItem] = []

    for item in history:
        messages.append(
            ChatHistoryItem(
                role="user",
                content=item.user_message
            )
        )
        messages.append(
            ChatHistoryItem(
                role="assistant",
                content=item.ai_message
            )
        )

    return messages


# =====================================================
# Clear Chat History (Per Thread)
# =====================================================

@router.delete("/history/{session_id}")
def clear_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete all chat messages for a specific session (thread).

    Behavior:
    - Deletes ONLY rows matching the given session_id
    - Other threads remain untouched
    - Used by frontend 'Clear Chat' button
    """

    deleted_rows = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .delete()
    )

    db.commit()

    return {
        "status": "success",
        "deleted_messages": deleted_rows
    }


# =====================================================
# List All Threads
# =====================================================

@router.get("/threads")
def list_threads(
    db: Session = Depends(get_db)
):
    """
    Return all distinct chat threads (session_ids).

    Purpose:
    - Used by frontend to show thread list
    - Enables thread switching
    """

    rows = (
        db.query(ChatHistory.session_id)
        .distinct()
        .order_by(ChatHistory.session_id.desc())
        .all()
    )

    # rows is a list of tuples → extract values
    return [row[0] for row in rows]

# =====================================================
# Delete Threads
# =====================================================

@router.delete("/thread/{session_id}")
def delete_thread(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an entire thread.

    This removes:
    - All chat messages for the session_id
    - Effectively deletes the thread itself
    """

    deleted_rows = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .delete()
    )

    db.commit()

    return {
        "status": "success",
        "deleted_messages": deleted_rows
    }
