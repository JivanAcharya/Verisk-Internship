import streamlit as st
import uuid
import os
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import MessagesState, StateGraph
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
graph_builder = StateGraph(MessagesState)


load_dotenv()
DB_URI = os.getenv("DATABASE_URL")

# Initialize database connection pool
# connection_kwargs = {"autocommit": True, "prepare_threshold": 0}

# pool = ConnectionPool(conninfo=DB_URI, max_size=20, kwargs=connection_kwargs)
# checkpointer = PostgresSaver(pool)
# checkpointer.setup()
llm = init_chat_model("llama-3.1-8b-instant", model_provider="groq")
CHROMA_PERSIST_DIR = "chroma_db"

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Check if Chroma DB exists, if so, load it
if os.path.exists(CHROMA_PERSIST_DIR):
    print("Loading existing Chroma database...")
    vector_store = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embeddings)
else:
    print("Creating new Chroma database...")
    
    # Load documents
    loader = TextLoader("expanded_descriptions.txt")
    docs = loader.load()
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=500)
    all_splits = text_splitter.split_documents(docs)
    
    # Initialize vector store and add documents
    vector_store = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embeddings)
    vector_store.add_documents(documents=all_splits)
    
    # Save to disk
    vector_store.persist()

print("Chroma vector store is ready!")
@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


# Generate an AIMessage that may include a tool-call to be sent.
def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
   
    return {"messages": [response]}


# execute the retrieval.
tools = ToolNode([retrieve])


#g enerate a response using the retrieved content.
def generate(state: MessagesState):
    """Generate answer."""
    
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "You are 'UniBro' a universities consultant for United States "
        "You only answer the queries realted to universities in America"
        "You should reinforce that you only reply to queries related to universities in America"
        "Use only the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "Always try to ask open ended queries after answering."
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    response = llm.invoke(prompt)
    return {"messages": [response]}

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

graph = graph_builder.compile()

# Streamlit UI
st.set_page_config(page_title="RAG Chat", layout="wide")

# Session state for managing chat history and thread IDs
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

# Sidebar for managing chat sessions
st.sidebar.title("Chat Sessions")
if st.sidebar.button("New Chat"):
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.chat_sessions[st.session_state.thread_id] = []

# Display previous chat sessions
for thread in st.session_state.chat_sessions.keys():
    if st.sidebar.button(f"Session {thread[:8]}"):
        st.session_state.thread_id = thread

# Main chat interface
st.title("RAG-Powered Chatbot")
st.write("Ask a question, and the AI will retrieve relevant information.")

# Display chat history
thread_id = st.session_state.thread_id
if thread_id not in st.session_state.chat_sessions:
    st.session_state.chat_sessions[thread_id] = []

for entry in st.session_state.chat_sessions[thread_id]:
    with st.chat_message("user"):
        st.write(entry["user"])
    with st.chat_message("assistant"):
        st.write(entry["assistant"])

# User input
user_input = st.chat_input("Type your message...")
if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    
    # Invoke the RAG agent
    config = {"configurable": {"thread_id": thread_id}}
    res = graph.invoke({"messages": [{"role": "user", "content": user_input}]}, config)
    
    response = res['messages'][-1].content
    with st.chat_message("assistant"):
        st.write(response)
    
    # Store chat history
    st.session_state.chat_sessions[thread_id].append({"user": user_input, "assistant": response})
