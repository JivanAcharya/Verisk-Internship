from langgraph.graph import START, END, StateGraph
from .graph_setup import (GraphState,
                         professor_search,
                         web_search,
                         professor_search_from_json,
                         format_search_results,
                         general_query, 
                         retrieve,generate,
                         decide_to_generate,
                         route_question,
                         route_professor_query,
                         route_json_results, 
                         grade_documents,
                         grade_generations,
                         transform_query)

workflow = StateGraph(GraphState)

#define nodes

workflow.add_node("professor_search", professor_search)
workflow.add_node("web_search", web_search)
workflow.add_node("professor_search_from_json", professor_search_from_json)
workflow.add_node("format_search_results", format_search_results)
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

workflow.add_conditional_edges(
    "professor_search",
    route_professor_query,
    {
        "json_data": "professor_search_from_json",
        "web_search": "web_search",
    }
)


workflow.add_edge("retrieve","grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    }
)

workflow.add_edge("transform_query", "web_search")
workflow.add_conditional_edges(
    "generate",
    grade_generations,
    {
        "hallucination": "generate",
        "useful": END,
        "not useful": "transform_query",
    }
)
workflow.add_conditional_edges(
    "professor_search_from_json",
     route_json_results,
     {
         "not found" : "web_search",
         "found data": "format_search_results"
    }
)
workflow.add_edge("web_search", "format_search_results")
workflow.add_edge("format_search_results", END)
workflow.add_edge("general_query", END)

chatbot = workflow.compile()