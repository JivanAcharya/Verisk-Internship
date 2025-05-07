from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base
import uuid

# Table to store individual chat session information only
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    session_id = Column(String(36), primary_key=True, default = lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)  
    title = Column(String, nullable = True)

    user = relationship("User", back_populates="chat_sessions")
    chat_history = relationship("ChatHistory", back_populates="session")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.session_id"))
    role = Column(String(50), nullable=False)  # for either 'user' or 'assistant'
    content = Column (String, nullable = False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow) 

    session = relationship("ChatSession", back_populates="chat_history")

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(200), index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

    chat_sessions = relationship("ChatSession", back_populates="user")

