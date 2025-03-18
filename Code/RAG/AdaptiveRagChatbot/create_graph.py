from langgraph.graph import START, END, StateGraph
from graph_setup import GraphState, professor_search,general_query, retrieve,generate,decide_to_generate,route_question, grade_documents,grade_generations,transform_query

workflow = StateGraph(GraphState)

#define nodes

workflow.add_node("professor_search", professor_search)
workflow.add_node("retrieve",retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("generate", generate)
workflow.add_node("general_query", general_query)
workflow.add_node("transform_query", transform_query)

#build graph
workflow.add_conditional_edges(
    START,
    route_question,
    {
        "professor_search": "professor_search",
        "vectorstore": "retrieve",
        "general_query": "general_query",
    }
)

workflow.add_edge("professor_search", "generate")
workflow.add_edge("retrieve","grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    }
)

workflow.add_edge("transform_query", "retrieve")
workflow.add_conditional_edges(
    "generate",
    grade_generations,
    {
        "not supported": "generate",
        "useful": END,
        "not useful": "transform_query",
    }
)
workflow.add_edge("general_query", END)

app = workflow.compile()