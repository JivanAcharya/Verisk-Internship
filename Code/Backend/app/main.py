from fastapi import FastAPI
from app.models import Base
from app.db.session import engine

app = FastAPI()

#create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return{"message":"Welcome to Chatbot"}