from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from llm_config import llm
## Query rewriter
class RewriteQuery(BaseModel):
    """Rewrite a user query to a more specific question."""
    query:str = Field(
        ..., description="Rewritten query"
    )
structured_llm_query_rewriter = llm.with_structured_output(RewriteQuery)
system = """You a question re-writer that converts an input question to a better version that is optimized \n 
     for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
re_write_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        (
            "human",
            "Here is the initial question: \n\n {question} \n Formulate an improved question.",
        ),
    ]
)

question_rewriter = re_write_prompt | structured_llm_query_rewriter



