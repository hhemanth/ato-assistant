"""
Judge node: scores a (query, response) pair using claude-haiku-4-5-20251001.
Returns helpfulness, correctness, and coherence scores in [0.0, 1.0].
"""
import json
import os
import re
from pathlib import Path

import anthropic

from state import AgentState

_MODEL = "claude-haiku-4-5-20251001"
_CLIENT: anthropic.AsyncAnthropic | None = None

_JUDGE_PROMPT = """\
You are an evaluator for an Australian Taxation Office (ATO) information assistant.

Given a user question and the assistant's response, score the response on three dimensions.
Return ONLY a JSON object with float scores from 0.0 to 1.0. No markdown, no explanation.

{
  "helpfulness": <0.0–1.0>,
  "correctness": <0.0–1.0>,
  "coherence": <0.0–1.0>
}

Scoring guide:
- helpfulness: Does the response actually address what the user asked? 1.0 = fully addresses the question, 0.0 = ignores it.
- correctness: Is the information factually accurate for Australian tax rules? 1.0 = accurate and well-grounded, 0.0 = incorrect or misleading.
- coherence: Is the response well-structured and easy to follow? 1.0 = clear and logically organised, 0.0 = confusing or incoherent.
"""


def _client() -> anthropic.AsyncAnthropic:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _CLIENT


def _parse_scores(text: str) -> dict[str, float]:
    text = re.sub(r"```json?\s*|\s*```", "", text).strip()
    raw = json.loads(text)
    return {
        "helpfulness": float(raw["helpfulness"]),
        "correctness": float(raw["correctness"]),
        "coherence": float(raw["coherence"]),
    }


async def judge_node(state: AgentState) -> dict:
    query = state["query"]
    response = state["response"]

    result = await _client().messages.create(
        model=_MODEL,
        max_tokens=128,
        system=_JUDGE_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Question: {query}\n\nResponse: {response}",
            }
        ],
    )

    scores = _parse_scores(result.content[0].text)
    return {"judge_scores": scores}
