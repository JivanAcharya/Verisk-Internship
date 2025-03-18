from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from llm_config import llm
#data model to return the route
class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource"""
    datasource: Literal["vectorstore","professor_search","general_query"] = Field(
        ..., description="Given a user query choose to route it to the vectorstore or professor search or general query route"
    )

structured_llm_router = llm.with_structured_output(RouteQuery)

## Prompt to handle routing
system = """You are an expert at routing a user question to a vectorstore or professor search or general query routes.
Vectorstore contains only the documents related to universities in United States but not about the professors, use it for university queries.
. For queries related to professors or faculty use professor search.
Otherwise, use the general query route."""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",system),
        ("human","{question}")
    ]
)


question_router = route_prompt | structured_llm_router
