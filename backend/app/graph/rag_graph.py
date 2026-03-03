from typing import TypedDict

from langgraph.graph import StateGraph, END

from backend.app.rag.chain import get_rag_chain


# 🔹 Define graph state
class RAGState(TypedDict):
    question: str
    answer: str


# 🔹 RAG Node
def rag_node(state: RAGState) -> RAGState:
    """
    Executes the RAG chain.
    """
    rag_chain = get_rag_chain()
    response = rag_chain.invoke(state["question"])

    return {
        "question": state["question"],
        "answer": response,
    }


# 🔹 Build Graph
def build_rag_graph():
    graph = StateGraph(RAGState)

    # Add nodes
    graph.add_node("rag", rag_node)

    # Define edges
    graph.set_entry_point("rag")
    graph.add_edge("rag", END)

    # Compile graph
    return graph.compile()


# Singleton graph instance
rag_graph = build_rag_graph()
