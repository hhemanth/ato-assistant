"""
Router node: classifies a query into factual | calculation | personal_advice | out_of_scope.
Uses claude-haiku-4-5-20251001 for fast, cheap classification.
"""
import json
import os
import re
from pathlib import Path

import anthropic
from pydantic import BaseModel
from typing import Literal

from state import AgentState

_MODEL = "claude-haiku-4-5-20251001"
_PROMPT = (Path(__file__).parent.parent / "prompts" / "router.md").read_text()
_CLIENT: anthropic.AsyncAnthropic | None = None


def _client() -> anthropic.AsyncAnthropic:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _CLIENT


class RoutingDecision(BaseModel):
    category: Literal["factual", "calculation", "personal_advice", "out_of_scope"]
    confidence: float
    reasoning: str


def _parse_decision(text: str) -> RoutingDecision:
    """Extract JSON from model response, tolerating minor whitespace/markdown."""
    # Strip markdown code fences if present
    text = re.sub(r"```json?\s*|\s*```", "", text).strip()
    return RoutingDecision.model_validate_json(text)


async def router_node(state: AgentState) -> dict:
    query = state["query"]

    response = await _client().messages.create(
        model=_MODEL,
        max_tokens=256,
        system=_PROMPT,
        messages=[{"role": "user", "content": query}],
    )

    decision = _parse_decision(response.content[0].text)

    return {
        "category": decision.category,
        "confidence": decision.confidence,
        "reasoning": decision.reasoning,
    }
