"""
judge_graph: START → judge_node → END
Expects state["query"] and state["response"] to be populated.
Returns state with judge_scores populated.
"""
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from langgraph.graph import StateGraph, START, END

from nodes.judge import judge_node
from state import AgentState


def _build() -> object:
    g: StateGraph = StateGraph(AgentState)
    g.add_node("judge", judge_node)
    g.add_edge(START, "judge")
    g.add_edge("judge", END)
    return g.compile()


judge_graph = _build()
