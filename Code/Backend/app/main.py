from fastapi import FastAPI
from fastapi import APIRouter
from app.models import Base
from app.db.session import engine
from app.api.routes import auth
from app.core.config import settings
# from app.api

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

#create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return{"message":"Welcome to Chatbot"}



app.include_router(auth.router)
