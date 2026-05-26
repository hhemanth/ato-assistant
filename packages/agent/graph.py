"""
router_graph: START → router_node → END (for factual/personal_advice/out_of_scope)
              START → router_node → calculator_node → END (for calculation)
"""
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from langgraph.graph import StateGraph, START, END

from nodes.router import router_node
from nodes.calculator_node import calculator_node
from state import AgentState


def _route(state: AgentState) -> str:
    return state.get("category", "factual")


def _build() -> object:
    g: StateGraph = StateGraph(AgentState)
    g.add_node("router", router_node)
    g.add_node("calculator", calculator_node)
    g.add_edge(START, "router")
    g.add_conditional_edges(
        "router",
        _route,
        {
            "factual": END,
            "personal_advice": END,
            "out_of_scope": END,
            "calculation": "calculator",
        },
    )
    g.add_edge("calculator", END)
    return g.compile()


router_graph = _build()
