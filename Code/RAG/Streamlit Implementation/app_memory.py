import uuid
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from psycopg_pool import ConnectionPool 
import psycopg
from dotenv import load_dotenv

load_dotenv()

DB_URI = os.getenv("DATABASE_URL")
app = FastAPI()

# Database setup
pool = ConnectionPool(conninfo=DB_URI, max_size=20, kwargs={"autocommit": True})

def setup_database():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    bot_response TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS session_id_idx ON chat_history(session_id)")
    print("Database Setup Complete")
setup_database()

# Initialize model and embeddings
llm = init_chat_model("llama-3.3-70b-versatile", model_provider="groq")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
CHROMA_PERSIST_DIR = "chroma_db"

# Load or create vector store
if os.path.exists(CHROMA_PERSIST_DIR):
    vector_store = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embeddings)
else:
    loader = TextLoader("top_uni_detailed.txt")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
    all_splits = text_splitter.split_documents(docs)
    vector_store = Chroma.from_documents(all_splits, embeddings, persist_directory=CHROMA_PERSIST_DIR)

# Retrieve relevant documents
def retrieve_documents(query: str):
    retrieved_docs = vector_store.similarity_search(query, k=3)
    serialized_docs =  "\n\n".join(f"\nContent: {doc.page_content}" for doc in retrieved_docs)
    # print("\n Retrieved Docs are : ", retrieved_docs)
    return serialized_docs
# Get chat history
def get_chat_history(session_id, limit=5):
    with pool.connection() as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute("""
                SELECT user_message, bot_response 
                FROM chat_history 
                WHERE session_id = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
            """, (session_id, limit))
            return cur.fetchall()

# Store chat history
def store_chat_history(session_id, user_message, bot_response):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO chat_history (session_id, user_message, bot_response)
                VALUES (%s, %s, %s)
            """, (session_id, user_message, bot_response))
            print("Chat history stored")

# Generate response
def generate_response(user_input, session_id):
    chat_history = get_chat_history(session_id)
    # print("\n Chat History is : ", chat_history)
    chat_context = "\n".join(f"User: {chat['user_message']}\nUniBro: {chat['bot_response']}" for chat in chat_history)
    # print("\n Chat context is :: ", chat_context)

    ## for query rewriting
    query_template = ChatPromptTemplate.from_messages([
        ("system",
          "You are query rewriting specialist for University Question and Answering RAG application."
          " From the input of previous chat histroy and the human input, generate a short concise query for RAG application."),
        ("system", "STRICTLY RESPOND WITH THE FINAL QUERY ONLY, NO ADDITIONAL TEXT AND PREAMBLE."),
        ("system", f"Previous Chat History (for context, if relevant):\n{chat_context}"),
        ("human", "{input}")
    ])
    
    query = query_template.format(input= user_input)
    response = llm.invoke(query)
    new_query = response.content
    retrieved_content = retrieve_documents(new_query)

    print("\n\n User input is ", user_input)
    print("\n\nQuery is", query)
    print("\n\nNew query based on previous chat history : ", new_query)
    print("\n\nRetreieved content based on new query : ", retrieved_content)

    ##final prompt for the LLM using the new written query
    prompt_template = ChatPromptTemplate.from_messages([
    ("system", 
     "You are UniBro, an AI consultant specializing in U.S. university admissions. "
     "Your responses must be strictly based on the retrieved information—do not rely on external or general knowledge. "
     "Maintain accuracy, clarity, and conciseness while ensuring relevance to the user's previous chat history."
     "Never start your response with 'Based on the retrieved information', as this is already implied."
    ),
    # ("system", f"Previous Chat History (for context, if relevant):\n{chat_context}"),
    ("system", f"Retrieved Information (use this exclusively for answering):\n{retrieved_content}"),
    ("human", "{input}")
])
    prompt = prompt_template.format(input=new_query)
    response = llm.invoke(prompt)
    return response.content

# Request model
class QueryRequest(BaseModel):
    query: str
    thread_id: str = "default_session"

# API endpoint
@app.post("/query")
async def query_endpoint(request: QueryRequest):
    try:
        response = generate_response(request.query, request.thread_id)
        store_chat_history(request.thread_id, request.query, response)
        return {"response": response, "session_id": request.thread_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
