import getpass
import os

def _set_env(var:str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Enter {var}: ")

_set_env("TAVILY_API_KEY")
_set_env("GROQ_API_KEY")

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq

#set embeddings
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

docs = TextLoader("top_uni_detailed.txt").load()

#tiktoken based text splitter for openai baseed models
# text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=200)  

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs_splits = text_splitter.split_documents(docs)
vector_store = Chroma.from_documents(documents = docs_splits, embedding = embeddings)
retriever = vector_store.as_retriever()




### Router
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate

from pydantic import BaseModel, Field

#defining data model for llm output
class RouteQuery(BaseModel):
    """Route a uer query to the most relevant datasource."""

    datasource : Literal["vectorstore","web_search"] = Field(
        ...,
        description="Given a user question choose to route it to a vectorstore or web search."
    )


## LLM with function call
llm = ChatGroq(model = "llama-3.3-70b-versatile", temperature=0)
structured_llm_router = llm.with_structured_output(RouteQuery)

## Prompt
system = """You are an expert at routing a user question to a vectorstore or web search.
The vectorstore contains only the documents related to universities in United States.
Use the vectorstore for questions on these topics. Otherwise, use web-search."""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}")
    ]
)

question_router = route_prompt | structured_llm_router

# print(
#     question_router.invoke(
#         {"question": "Who will the Bears draft first in the NFL draft?"}
#     )
# )


## Retrieval grader
class GradeDocument(BaseModel):
    """Binary score for relevance check on retireved documents."""
    binary_score :str = Field(
        description="Document are relevant to the question, 'yes' or 'no'"
    )

llm = ChatGroq(model = "llama-3.3-70b-versatile", temperature=0)
structured_llm_grader = llm.with_structured_output(GradeDocument)

# Prompt
system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
    If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
    It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
    ]
)

retrieval_grader = grade_prompt | structured_llm_grader
# question = "universities in boston"
# docs = retriever.invoke(question)
# doc_text = docs[0].page_content

# print(retrieval_grader.invoke({"question": question,"document": doc_text }))


## Generate
from langchain import hub
from langchain_core.output_parsers import StrOutputParser

#prompt
prompt = hub.pull("rlm/rag-prompt")

# LLM
llm = ChatGroq(model = "llama-3.3-70b-versatile", temperature=0)
# Post - processsing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

#chain
rag_chain = prompt | llm | StrOutputParser()

# generation = rag_chain.invoke({"context":docs, "question":question})
# print(generation)


## Halucination garader
class GradeHalucination(BaseModel):
    """Binary score for hallucination present in generated answer."""
    binary_score :str = Field(
        description="Answer in grounded in the facts, 'yes' or 'no'"
    )

#LLM with funcin call
llm = ChatGroq(model = "llama-3.3-70b-versatile", temperature=0)
structured_llm_halucination_grader = llm.with_structured_output(GradeHalucination)

# Prompt
system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
     Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""
hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
    ]
)

hallucination_grader = hallucination_prompt | structured_llm_halucination_grader
# hallucination_grader.invoke({"documents":docs, "generation": generation})
# print(hallucination_grader)


## Answer Grader

class GradeAnswer(BaseModel):
    """Binary score to assess asnwer addresses question."""
    binary_score :str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

#LLM with function call
llm = ChatGroq(model = "llama-3.3-70b-versatile", temperature=0)
structured_llm_answer_grader = llm.with_structured_output(GradeAnswer)


# Prompt
system = """You are a grader assessing whether an answer addresses / resolves a question \n 
     Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""
answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
    ]
)

answer_grader = answer_prompt | structured_llm_answer_grader
# answer_grader.invoke({"question": question, "generation": generation})
# print(answer_grader)


### Question Re-writer

# LLM
llm = ChatGroq(model = "llama-3.3-70b-versatile", temperature=0)

# Prompt
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

question_rewriter = re_write_prompt | llm | StrOutputParser()
# question_rewriter.invoke({"question": question})

### Web search
from langchain_community.tools.tavily_search import TavilySearchResults

web_search_tool = TavilySearchResults(k=3)



## Graph construction

# Define graph state

from typing import List
from typing_extensions import TypedDict

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
    """

    question: str
    generation: str
    documents: List[str]


#Graph FLOW

from langchain.schema import Document

def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("--RETRIEVE--")
    question = state["question"]

    #retrieval
    documents = retriever.invoke(question)
    return{"documents": documents, "question": question}

def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {"documents": documents, "question": question, "generation": generation}

def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """
    print("--CHECK DOCUMENT RELEVANCE TO QUESTION--")
    question = state["question"]
    documents = state["documents"]

    filtered_docs = []
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue
    return {"documents": filtered_docs, "question": question}

def transform_query(state):
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    print("---TRANSFORM QUERY---")
    question = state["question"]
    documents = state["documents"]

    # Re-write question
    better_question = question_rewriter.invoke({"question": question})
    return {"documents": documents, "question": better_question}


def web_search(state):
    """
    Web search based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """

    print("---WEB SEARCH---")
    question = state["question"]

    # Web search
    docs = web_search_tool.invoke({"query": question})
    print("DEBUG: Web search results:", docs)

    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content=web_results)

    return {"documents": web_results, "question": question}


### Edges ###
# from print import print


def route_question(state):
    """
    Route question to web search or RAG.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION---")
    question = state["question"]
    source = question_router.invoke({"question": question})
    if source.datasource == "web_search":
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "web_search"
    elif source.datasource == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
        return "vectorstore"
    

def decide_to_generate(state):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    print("---ASSESS GRADED DOCUMENTS---")
    state["question"]
    filtered_documents = state["documents"]

    if not filtered_documents:
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print(
            "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
        )
        return "transform_query"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"
    

def grade_generation_v_documents_and_question(state):
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """

    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )
    grade = score.binary_score

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score.binary_score
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"
    

from langgraph.graph import END, StateGraph, START

workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("web_search", web_search)  # web search
workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("grade_documents", grade_documents)  # grade documents
workflow.add_node("generate", generate)  # generatae
workflow.add_node("transform_query", transform_query)  # transform_query

# Build graph
workflow.add_conditional_edges(
    START,
    route_question,
    {
        "web_search": "web_search",
        "vectorstore": "retrieve",
    },
)
workflow.add_edge("web_search", "generate")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)
workflow.add_edge("transform_query", "retrieve")
workflow.add_conditional_edges(
    "generate",
    grade_generation_v_documents_and_question,
    {
        "not supported": "generate",
        "useful": END,
        "not useful": "transform_query",
    },
)

# Compile
app = workflow.compile()

# Run
# inputs = {
#     "question": "What courses are offered at Harvard University?"
# }
# for output in app.stream(inputs):
#     for key, value in output.items():
#         # Node
#         print(f"Node '{key}':")
#         # Optional: print full state at each node
#         # print.print(value["keys"], indent=2, width=80, depth=None)
#     print("\n---\n")

# # Final generation
# print(value["generation"])



##for history based adaptive rag
from psycopg_pool import ConnectionPool 
import psycopg
DB_URI = os.getenv("DATABASE_URL")

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


chat_history = get_chat_history("client_2")
    # print("\n Chat History is : ", chat_history)
chat_context = "\n".join(f"User: {chat['user_message']}\nUniBro: {chat['bot_response']}" for chat in chat_history)

query_template = ChatPromptTemplate.from_messages([
    ("system",
        "You are query rewriting specialist for University Question and Answering RAG application."
        " From the input of previous chat histroy and the human input, generate a short concise query for RAG application."),
    ("system", "STRICTLY RESPOND WITH THE FINAL QUERY ONLY, NO ADDITIONAL TEXT AND PREAMBLE."),
    ("system", f"Previous Chat History (for context, if relevant):\n{chat_context}"),
    ("human", "{input}")
])

user_input = "What courses are offered at Harvard University?"
query = query_template.format(input= user_input)
response = llm.invoke(query)
new_query = response.content

inputs = {
    "question": new_query
}

resp = app.invoke(inputs)
user_message, bot_response = resp['question'], resp["generation"]
store_chat_history("client_2", user_message, bot_response)
print(resp['question'], resp["generation"])

from IPython.display import Image, display

display(Image(app.get_graph().draw_mermaid_png()))