from AdaptiveRagChatbot.create_graph import chatbot
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db,TokenDep,get_current_user
from app.models import User
from app.schemas import QueryRequestSchema


router = APIRouter(tags=["chatbot"],prefix ="/api/v1")
 


@router.post("/query")
async def query_endpoint(request: QueryRequestSchema,  db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # print(current_user)

    try:
        inputs = {
            "question": request.query
        }
        response = chatbot.invoke(inputs)

        print(response["question"],response["generation"])

        return {"response": response["generation"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

