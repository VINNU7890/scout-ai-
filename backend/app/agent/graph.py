from __future__ import annotations

import logging

from langgraph.graph import END, START, StateGraph

from backend.app.agent.nodes.analyst import analyst_node
from backend.app.agent.nodes.doc_researcher import doc_researcher_node
from backend.app.agent.nodes.planner import planner_node
from backend.app.agent.nodes.verifier import verifier_node
from backend.app.agent.nodes.web_researcher import web_researcher_node
from backend.app.agent.nodes.writer import writer_node
from backend.app.agent.state import ResearchState

logger = logging.getLogger("scoutai.agent.graph")


def should_revise_or_end(state: ResearchState) -> str:
    """Conditional router from verifier node."""
    verification = state.get("verification")
    revision_count = state.get("revision_count", 0)

    # If verification failed and we haven't revised yet, route back to writer once
    if verification and not verification.passed and revision_count <= 1:
        logger.info(
            f"Verifier rejected report. Routing back to writer (revision #{revision_count})"
        )
        return "writer"

    return END


def create_research_graph() -> StateGraph:
    """Constructs and returns the LangGraph research state graph."""
    builder = StateGraph(ResearchState)

    # Register nodes
    builder.add_node("planner", planner_node)
    builder.add_node("web_researcher", web_researcher_node)
    builder.add_node("doc_researcher", doc_researcher_node)
    builder.add_node("analyst", analyst_node)
    builder.add_node("writer", writer_node)
    builder.add_node("verifier", verifier_node)

    # Define edges: START -> planner -> [web || doc] -> analyst -> writer -> verifier -> (writer | END)
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "web_researcher")
    builder.add_edge("planner", "doc_researcher")
    builder.add_edge("web_researcher", "analyst")
    builder.add_edge("doc_researcher", "analyst")
    builder.add_edge("analyst", "writer")
    builder.add_edge("writer", "verifier")

    # Conditional edge from verifier
    builder.add_conditional_edges(
        "verifier",
        should_revise_or_end,
        {
            "writer": "writer",
            END: END,
        },
    )

    return builder


def compile_research_graph():
    """Compiles the StateGraph into an executable graph application."""
    graph = create_research_graph()
    return graph.compile()
