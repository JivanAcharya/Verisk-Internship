from AdaptiveRagChatbot.create_graph import chatbot
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db,TokenDep,get_current_user
from app.models import User, ChatHistory, ChatSession  # assuming your model file is models.py
from app.schemas import QueryRequestSchema
from app.utils import rewrite_query


router = APIRouter(tags=["chatbot"],prefix ="/api/v1")
 

@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(request: QueryRequestSchema,
                    db: Session= Depends(get_db),                    
                    current_user : User = Depends(get_current_user)):
    """
    Create a new chat session for the user.
    """

    new_session = ChatSession(user_id = current_user.user_id)
    try:
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"session_id": new_session.session_id, }


@router.post("/sessions/{session_id}/messages" ,status_code=status.HTTP_200_OK)
async def answer_query(session_id :str,
                       request: QueryRequestSchema,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)): 
    """
    Answer user query using the adpative rag chatbot
    """
    try:
        session = db.query(ChatSession).filter_by(session_id = session_id, user_id = current_user.user_id).first()

        if not session:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or not authorized"
        )

        # Create the user message object
        user_message = ChatHistory(session_id = session_id,
                                   role = "user",
                                   content = request.query)

        # Add the user message to the session FIRST
        db.add(user_message)
        

        # update the session title for session history table if not set earlier
        if not session.title and request.query:
            session.title = request.query[:20] + "..."
           
        print(f"Session ID: {session.session_id}, Title : {session.title}")

        # retrieve last 5 chat messages for the session (this query is okay)
        chat_history = (db.query(ChatHistory)
                       .filter_by(session_id = session_id)
                       .order_by(ChatHistory.created_at.desc())
                       .limit(10) 
                       .all()
                       )

        #joining to a single string to pass the context
        chat_context = "\n".join(f"{msg.role.capitalize()}: {msg.content}" for msg in reversed(chat_history))

        print("\nChat context is :: ", chat_context)
        #rewriting the query basedo on chat history context and current query
        rewritten_query = rewrite_query(query = request.query, chat_context = chat_context)
        print("\n Rewritten Query: ", rewritten_query)

        inputs = {
            "question": rewritten_query
        }

        ai_response = chatbot.invoke(inputs)

        print(ai_response["question"],ai_response["generation"])

        # Create the AI message object
        ai_message = ChatHistory(
            session_id = session_id,
            role = "assistant",
            content = ai_response["generation"])

        # Add the AI message to the session
        db.add(ai_message)

        db.commit()

        db.refresh(user_message)
        db.refresh(ai_message)

        return {"session_id": session_id,
                "response": ai_response["generation"] }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", status_code=status.HTTP_200_OK)
async def get_chat_history(session_id : str,
                            db: Session= Depends(get_db),
                           current_user: User = Depends(get_current_user),
                           ):
    """
    Fetches all chat history entries for a specific user and session.
    """
    # Verify session belongs to the user (security check)
    session = db.query(ChatSession).filter_by(session_id=session_id, user_id=current_user.user_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or not authorized"
        )

    # Fetch chat messages in the session
    
    chat_history = (
        db.query(ChatHistory)
        .filter_by(session_id=session_id)
        .order_by(ChatHistory.created_at)
        .all()
    )
    
    if not chat_history:
        return []  ## hanlde this later

   
    formatted_messages = [{"role": msg.role, "content": msg.content, "timestamp": msg.created_at} for msg in chat_history]
    return {"session_id": session_id, "messages": formatted_messages}


@router.get("/sessions", status_code=status.HTTP_200_OK)
async def get_all_sessions(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Fetch all chat sessions for the user.
    """
    sessions = db.query(ChatSession).filter_by(user_id=current_user.user_id).all()
    
    if not sessions:
        return []
    
    session_list = [{"session_id": session.session_id, "created_at": session.created_at, "title":session.title} for session in sessions]
    return {"sessions": session_list}


@router.delete("/sessions/{session_id}", status_code=status.HTTP_200_OK)
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Delete a user session.
    """
    session = db.query(ChatSession).filter_by(
        session_id=session_id,
        user_id=current_user.user_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or not authorized"
        )

    try:
        db.delete(session)
        db.commit()
        return {"detail": "Session deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )
 

# @router.post("/query")
# async def query_endpoint(request: QueryRequestSchema,
#                          db: Session = Depends(get_db),
#                          current_user: User = Depends(get_current_user)):

#     try:
#         # retrieve the last 5 chat history for the user for the session_id
#         session = db.query(ChatSession).filter_by(session_id=request.session_id, user_id=current_user.user_id).first()
#         if not session:
#             print("Session not found for user, new session will be created")
#         chat_history = (db.query(ChatHistory)
#             .filter_by(session_id=request.session_id)
#             .order_by(ChatHistory.created_at
#             .desc())
#             .limit(5)
#             .all()
#             )

#         #join the chat history into a single string
#         chat_context = "\n".join(f"User: {chat.question}\nUniBro: {chat.answer}" for chat in chat_history)
        
#         rewritten_query = rewrite_query(query = request.query, chat_context = chat_context)

#         inputs = {
#             "question": rewritten_query
#         }
#         response = chatbot.invoke(inputs)

#         print(response["question"],response["generation"])

#         # Save the question and answer to the database
#         save_chat_history(user_id = current_user.user_id,
#                             session_id = request.session_id,
#                             question = response["question"], 
#                             answer = response["generation"],
#                             db= db)
        
#         return {"response": response["generation"]}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# def save_chat_history( user_id: int, session_id: int, question: str, answer: str,db: Session):
#     session_obj = db.query(ChatSession).filter_by(session_id=session_id, user_id=user_id).first()

#     # If session doesn't exist, create a new one
#     if not session_obj:
#         session_obj = ChatSession(
#             session_id=session_id, 
#             user_id=user_id
#         )
#         db.add(session_obj)
#         db.commit()
#         db.refresh(session_obj)  # Refresh to get updated values if needed

#     # Create new chat history entry
#     chat_entry = ChatHistory(
#         session_id=session_obj.session_id,
#         question=question,
#         answer=answer
#     )

#     # Add and commit
#     db.add(chat_entry)
#     db.commit()
#     db.refresh(chat_entry)

#     return chat_entry

