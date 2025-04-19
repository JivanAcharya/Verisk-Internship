from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class QuerySchema(BaseModel):
    query:str
    thread_id: str = "default_session"

class ChatHistorySchema(BaseModel):
    session_id : str
    user_message : str
    bot_response : str

class UserLoginSchema(BaseModel):
    email : EmailStr
    password : str

class UserBaseSchema(BaseModel):
    username: str
    email: EmailStr

class UserRegisterSchema(UserBaseSchema):
    password: str = Field(..., min_length=8, description="password must be at least 8 characters long")
    # confirm_password: str

class Message(BaseModel):
    message : str

class Token(BaseModel):
    access_token:str | None = None
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    user_id: int
    exp: Optional[int] = None