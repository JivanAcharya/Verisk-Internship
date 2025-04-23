from AdaptiveRagChatbot.create_graph import chatbot
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db,TokenDep,get_current_user
from app.models import User, ChatHistory, ChatSession  # assuming your model file is models.py
from app.schemas import QueryRequestSchema
from app.utils import rewrite_query


router = APIRouter(tags=["chatbot"],prefix ="/api/v1")
 


@router.post("/query")
async def query_endpoint(request: QueryRequestSchema,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):

    try:
        # retrieve the last 5 chat history for the user for the session_id
        session = db.query(ChatSession).filter_by(session_id=request.session_id, user_id=current_user.user_id).first()
        if not session:
            print("Session not found for user, new session will be created")
        chat_history = (db.query(ChatHistory)
            .filter_by(session_id=request.session_id)
            .order_by(ChatHistory.created_at
            .desc())
            .limit(5)
            .all()
            )

        #join the chat history into a single string
        chat_context = "\n".join(f"User: {chat.question}\nUniBro: {chat.answer}" for chat in chat_history)
        
        rewritten_query = rewrite_query(query = request.query, chat_context = chat_context)

        inputs = {
            "question": rewritten_query
        }
        response = chatbot.invoke(inputs)

        print(response["question"],response["generation"])

        # Save the question and answer to the database
        save_chat_history(user_id = current_user.user_id,
                            session_id = request.session_id,
                            question = response["question"], 
                            answer = response["generation"],
                            db= db)
        
        return {"response": response["generation"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat-history/{session_id}")
async def get_chat_history(session_id : int,
                            db: Session= Depends(get_db),
                           current_user: User = Depends(get_current_user),
                           ):
    """
    Fetches all chat history entries for a specific user and session.
    """
    # Verify session belongs to the user (security check)
    session = db.query(ChatSession).filter_by(session_id=session_id, user_id=current_user.user_id).first()
    if not session:
        return [] 

    # Fetch chat messages in the session
    
    chat_entries = (
        db.query(ChatHistory)
        .filter_by(session_id=session_id)
        .order_by(ChatHistory.created_at)
        .all()
    )
    
    if not chat_entries:
        return []  ## hanlde exception later

    return [
        {
            "question": entry.question,
            "answer": entry.answer,
            "timestamp": entry.created_at
        }
        for entry in chat_entries
    ]

def save_chat_history( user_id: int, session_id: int, question: str, answer: str,db: Session):
    session_obj = db.query(ChatSession).filter_by(session_id=session_id, user_id=user_id).first()

    # If session doesn't exist, create a new one
    if not session_obj:
        session_obj = ChatSession(
            session_id=session_id, 
            user_id=user_id
        )
        db.add(session_obj)
        db.commit()
        db.refresh(session_obj)  # Refresh to get updated values if needed

    # Create new chat history entry
    chat_entry = ChatHistory(
        session_id=session_obj.session_id,
        question=question,
        answer=answer
    )

    # Add and commit
    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)

    return chat_entry

