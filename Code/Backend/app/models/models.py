from enum import Enum
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Column, Integer, String, ForeignKey,DateTime, Boolean
from sqlalchemy.orm import relationship
from . import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer,primary_key=True,autoincrement=True, index = True)
    name = Column(String(200), unique = True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    modified_at = Column(DateTime, nullable=False)

    items = relationship("Item", back_populates="user")

class GeneralChatHistory(Base):
    __tablename__ = "general_chat_history"
    session_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User",back_populates="general_chat_history")