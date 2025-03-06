import uuid
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import ToolNode
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import MessagesState, StateGraph
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv

load_dotenv()
DB_URI = os.getenv("DATABASE_URL")

app = FastAPI()

connection_kwargs = {"autocommit": True, "prepare_threshold": 0}

pool = ConnectionPool(conninfo=DB_URI, max_size=20, kwargs=connection_kwargs)
checkpointer = PostgresSaver(pool)
checkpointer.setup()



# Initialize model and embeddings
llm = init_chat_model("llama-3.1-8b-instant", model_provider="groq")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")


CHROMA_PERSIST_DIR = "chroma_db"
# checking if chroma already exists or not
if os.path.exists(CHROMA_PERSIST_DIR):
     vector_store = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embeddings)
else:
    loader = TextLoader("university_data.txt")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)

    # for persistence passing persist_directory
    vector_store = Chroma.from_documents(documents=all_splits, embedding=embeddings, persist_directory=CHROMA_PERSIST_DIR)
    print("Chroma DB ready")


# RAG Tool for retrieval
@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""

    print("retrieve called")

    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    print("\n",serialized,retrieved_docs)
    return serialized, retrieved_docs

def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    print("query or respond called")
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
   
    return {"messages": [response]}


# execute the retrieval.
tools = ToolNode([retrieve])

# Generate response from the LLM using the retrieved documents
def generate(state: MessagesState):
    """Generate answer using retrieved content."""
    print("generate called")
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "You are 'UniBro', an AI-powered university admissions consultant specializing in U.S. universities. "
        "Your goal is to provide accurate, concise, and well-structured answers based strictly on the retrieved documents. "
        "Do not generate answers from general knowledge—only use the given context. If the retrieved information is insufficient, state that explicitly.\n\n"
        
        "**Instructions:**\n"
        "- Answer questions concisely in **three sentences or fewer**.\n"
        "- If multiple relevant answers exist, list them clearly using bullet points or numbering.\n"
        "- If a university or program is mentioned, provide key details like location, ranking, notable programs, or admissions requirements (if available).\n"
        "- If you do not know the answer, say: 'I do not have information on that topic based on the provided documents.'\n\n"
        "If possible ask open ended questions?"
        "**Retrieved Context:**\n"
        f"{docs_content}"
    )

    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # invoking the llm with the context and prompt
    response = llm.invoke(prompt)
    print("\n",[response])
    return {"messages": [response]}


# Building and compiling the graph
graph_builder = StateGraph(MessagesState)
from langgraph.graph import END
from langgraph.prebuilt import ToolNode, tools_condition

graph_builder.add_node(query_or_respond)
graph_builder.add_node(tools)
graph_builder.add_node(generate)

graph_builder.set_entry_point("query_or_respond")
graph_builder.add_conditional_edges(
    "query_or_respond",
    tools_condition,
    {END: END, "tools": "tools"},
)
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)

graph = graph_builder.compile(checkpointer=checkpointer)

DEFAULT_CONFIG = {"configurable": {"thread_id": "user2"}}



## Request Model For api
class QueryRequest(BaseModel):
    query: str

#   query endpoint to recieve user query and repsond with the answer
@app.post("/query")
async def query_endpoint(request: QueryRequest):
    try:
        user_input = request.query
        print("User query received:", user_input)

        res = graph.invoke({"messages": [{"role": "user", "content": user_input}]}, DEFAULT_CONFIG)

        print("Graph output:", res)
        response = res['messages'][-1].content
        return {"response": response}
    
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
