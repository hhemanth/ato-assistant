"""
router_graph: START → router_node → END
Returns AgentState with category, confidence, reasoning populated.
"""
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from langgraph.graph import StateGraph, START, END

from nodes.router import router_node
from state import AgentState


def _build() -> object:
    g: StateGraph = StateGraph(AgentState)
    g.add_node("router", router_node)
    g.add_edge(START, "router")
    g.add_edge("router", END)
    return g.compile()


router_graph = _build()
