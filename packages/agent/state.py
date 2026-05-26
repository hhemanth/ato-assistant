from typing import TypedDict


class AgentState(TypedDict, total=False):
    messages: list[dict]       # [{"role": "user"|"assistant", "content": str}, ...]
    query: str                 # last user message, extracted for convenience
    category: str              # factual | calculation | personal_advice | out_of_scope
    confidence: float          # 0.0–1.0 from router
    reasoning: str             # one-sentence explanation, logged to LangSmith
    response: str              # full buffered response text, set before judge runs
    judge_scores: dict         # {"helpfulness": float, "correctness": float, "coherence": float}
    calculator_result: dict   # populated by calculator_node for "calculation" queries
