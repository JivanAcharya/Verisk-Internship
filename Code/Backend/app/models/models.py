from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from . import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(200), index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

    # Added reverse relationship for GeneralChatHistory
    general_chat_history = relationship("ChatHistory", back_populates="user")


class ChatHistory(Base):
    __tablename__ = "general_chat_history"
    session_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="general_chat_history")
