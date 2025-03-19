from typing import List
from typing_extensions import TypedDict

from retriever_setup import retriever 
from llm_config import llm
from graders import retrieval_grader, hallucination_grader,answer_grader
from query_rewriter import question_rewriter
from professor_web_search import web_search_tool, professor_search_json
from routes import question_router,professor_search_router,json_results_router


class GraphState(TypedDict):
    """
    Represents the state of the graph
    
    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
    """

    question: str
    generation:str
    documents: List[str]


## Graph Flow
from langchain.schema import Document

def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("\n RETRIEVE")
    question = state['question']

    documents = retriever.invoke(question)
    return{"documents": documents,"question":question}


##Generator
from langchain import hub
from langchain_core.output_parsers import StrOutputParser

# def get_chain():
#     """
#     Returns the rag chain
#     """
#     prompt = hub.pull("rlm/rag-prompt")

#     rag_chain = prompt | llm | StrOutputParser()
#     return rag_chain

prompt = hub.pull("rlm/rag-prompt")

rag_chain = prompt | llm | StrOutputParser()

def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """

    print("\n GENERATE")
    question = state['question']
    documents = state['documents']

    #RAG Generation
    
    generation = rag_chain.invoke({"context":documents, "question": question})
    return {"documents": documents, "question": question, "generation": generation}

def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """
    print("\n Check Document relevance to question")
    question = state["question"]
    documents = state["documents"]

    filtered_docs = []
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score
        if grade == "yes":
            print("\n Document is relevant")
            filtered_docs.append(d)
        else:
            print("\nDocument is not relevant to the question")
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
    print("\n Transform Query")
    question = state["question"]
    documents = state["documents"]

    #rewrite query
    new_question = question_rewriter.invoke({"question": question})
    return {"documents": documents, "question": new_question}

def professor_search(state):
    """
    Search professors in the web with re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """
    return {"question": state["question"]}


def web_search(state):
    print("\n Professor Web Search")
    question = state["question"]

    #web search
    docs = web_search_tool.invoke({"query":question})

    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content = web_results)

    return{"documents":web_results, "question":question}

def professor_search_from_json(state):
    """
    Search for professors in the json data with re-phrased question.
    
    Args:
        state (dict): The current graph state
        
    Returns:
        state (dict): Updates documents key with appended json results
    """
    print("\n Professor Search from JSON")
    question = state["question"]
    
    #json search
    json_results = professor_search_json(question)
    
    return{"documents":json_results, "question":question}

def format_search_results(state):
    """
    Format the search results for display to the user
    
    Args:
        state (dict): The current graph state
    
    Returns:
        state (dict): Update generation with the formatted search results
    """
    question = state['question']
    documents = state['documents']
    print("\n Format Search Results")
    resp = llm.invoke(f"""For the question by the user :: {question} \n
                        The results of web search are {documents}. \n Now give the answer only addressing the user question from the retrieved web search document
                        \n NO PREAMBLE AND EXTRA TEXTS""")
    return {"question":question, "generation":resp.content}

def general_query(state):
    """
    Respond to general query of the user 
    
    Args:
        state (dict): The current graph state
    
    Returns:
        state (dict):Update generation with the responded generated answer
    """
    question = state['question']
    print("\n General Query")
    resp = llm.invoke(question)
    return {"question":question, "generation":resp.content}



### Conditional edges

def route_question(state):
    """
    Route question to professor search or vectorstore or general query.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """
    print("\n Route Question")
    question = state["question"]

    source = question_router.invoke({"question": question})
    print("\n SOURCE:"+source.datasource)
    if source.datasource == "vectorstore":
        return "vectorstore"
    elif source.datasource == "professor_search":
        return "professor_search"
    else:
        return "general_query"
    
## routes for professor search
def route_professor_query(state):
    """
    Route question to json_data or web_search for professor query .

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """
    print("\n Route Professor Query")
    question = state["question"]
    source = professor_search_router.invoke({"question": question})
    print("\n SOURCE:"+source.datasource)
    if source.datasource == "json_data":
        return "json_data"
    else:
        return "web_search"

def route_json_results(state):
    print("\n Route according to JSON Results")
    question = state["question"]
    documents = state["documents"]
    source = json_results_router.invoke({"question":question,"documents": documents})
    print("\n SOURCE:"+source.datasource)
    if source.datasource == "web_search":
        return "not found"
    else: 
        return "found data"

def decide_to_generate(state):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    print("\n Assess graded documents")
    state["question"]
    filtered_documents = state["documents"]

    if not filtered_documents:
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print(
            "\nDecision: All docs not relevant, transform query"
        )
        return "transform_query"
    else:
        # We have relevant documents, so generate answer
        print("\nDecision: Generate answer")
        return "generate"
    
def grade_generations(state):
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """
    print("\n Check hallucinations")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]
    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )
    grade = score.binary_score
    if grade == "yes":
        print("\n Generation is grounded in the documents")
        print("\n Grade generation vs question")
        score = answer_grader.invoke(
            {"question": question, "generation": generation}
        )   
        grade = score.binary_score
        if grade == "yes":
            print("\n Decision: Generation answers the question")
            return "useful"
        else:
            print("\n Decision: Generation does not addreess question")
            return "not useful"
    else:
        print("\n Generation is not grounded in the documents, Retry...")
        return "hallucination"