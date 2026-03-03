from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from backend.app.core.database import Base


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(String(100), index=True, nullable=False)

    user_message = Column(Text, nullable=False)

    ai_message = Column(Text, nullable=False)

    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
