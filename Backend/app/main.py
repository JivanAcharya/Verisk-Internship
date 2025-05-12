from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ✅ Add this
from app.models import Base
from app.db.session import engine
from app.api.routes import auth, chat, sop_review
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

# ✅ Add this: CORS setup
origins = [
    "http://127.0.0.1:5173",  
    "http://localhost:5173",  
    "http://127.0.0.1:80",  
    "http://localhost:80", 
    "http://frontend:80",
    "http://backend:80",
    "http://backend:443",
    "http://frontend:5173",
    "http://localhost",       # Optional for safety
]

app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,            # List of frontend origins
    allow_credentials=True,
    allow_methods=["*"],              
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to Chatbot"}

# Include API routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(sop_review.router)
