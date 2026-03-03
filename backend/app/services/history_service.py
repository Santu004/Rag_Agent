from sqlalchemy.orm import Session
from typing import List

from backend.app.models.chat_history import ChatHistory


def save_chat_history(
    db: Session,
    session_id: str,
    user_message: str,
    ai_message: str
) -> ChatHistory:
    """
    Save a single chat interaction to the database.
    """
    chat = ChatHistory(
        session_id=session_id,
        user_message=user_message,
        ai_message=ai_message,
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


def get_chat_history(
    db: Session,
    session_id: str,
    limit: int = 20
) -> List[ChatHistory]:
    """
    Fetch chat history for a given session_id.
    """
    return (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.timestamp.asc())
        .limit(limit)
        .all()
    )
