from sqlalchemy.orm import Session
from app.db.session import get_db
import app.models.models as models
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.core.config import settings
import os


