"""
Judge node: scores a (query, response) pair using nvidia/nemotron-4-340b-reward.
Scores are extracted from logprobs and normalised to 0–1 via sigmoid.
"""
import math
import os

from openai import AsyncOpenAI

from state import AgentState

_MODEL = "nvidia/nemotron-4-340b-reward"
_BASE_URL = "https://integrate.api.nvidia.com/v1"
_ATTRIBUTES = ("helpfulness", "correctness", "coherence")
_CLIENT: AsyncOpenAI | None = None


def _client() -> AsyncOpenAI:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = AsyncOpenAI(
            base_url=_BASE_URL,
            api_key=os.environ["NVIDIA_API_KEY"],
        )
    return _CLIENT


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


async def judge_node(state: AgentState) -> dict:
    query = state["query"]
    response = state["response"]

    result = await _client().chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "user", "content": query},
            {"role": "assistant", "content": response},
        ],
        logprobs=True,
    )

    raw_scores: dict[str, float] = {}
    logprobs_content = result.choices[0].logprobs.content or []
    for item in logprobs_content:
        if item.token in _ATTRIBUTES:
            raw_scores[item.token] = item.logprob

    scores = {attr: _sigmoid(raw_scores.get(attr, 0.0)) for attr in _ATTRIBUTES}

    return {"judge_scores": scores}
