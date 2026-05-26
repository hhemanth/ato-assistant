"""
Calculator node: extracts income params from query using Haiku 4.5, then
calls the pure Python tax calculator. No LLM math — LLM only extracts params.
"""
import json
import os
import re

import anthropic

from state import AgentState
from tools.tax_calculator import TaxInput, calculate

_MODEL = "claude-haiku-4-5-20251001"
_CLIENT: anthropic.AsyncAnthropic | None = None

_EXTRACT_PROMPT = """\
Extract tax calculation parameters from the user's query. Return ONLY a JSON object.

{
  "income": <number, annual gross income in AUD, required>,
  "financial_year": <"2025-26" or "2026-27", default "2025-26">,
  "has_help_debt": <true or false, default false>,
  "has_private_hospital_cover": <true or false, default false>
}

Rules:
- income: required. If not stated, return {"error": "no_income"} instead.
- financial_year: "2026-27" only if user says "next year", "2026-27", or "FY27". Otherwise "2025-26".
- has_help_debt: true if user mentions HECS, HELP, student debt/loan.
- has_private_hospital_cover: true if user mentions private health, PHI, hospital cover.
"""


def _client() -> anthropic.AsyncAnthropic:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _CLIENT


def _parse_params(text: str) -> dict:
    text = re.sub(r"```json?\s*|\s*```", "", text).strip()
    return json.loads(text)


async def calculator_node(state: AgentState) -> dict:
    query = state["query"]

    response = await _client().messages.create(
        model=_MODEL,
        max_tokens=128,
        system=_EXTRACT_PROMPT,
        messages=[{"role": "user", "content": query}],
    )

    params = _parse_params(response.content[0].text)

    if "error" in params:
        return {
            "calculator_result": {
                "error": "I could not find an income amount in your question. "
                         "Could you rephrase? For example: \"I earned $85,000 — what's my tax?\""
            }
        }

    try:
        inp = TaxInput(**params)
        result = calculate(inp)
        return {"calculator_result": result.model_dump()}
    except Exception as exc:
        return {"calculator_result": {"error": f"Could not compute: {exc}"}}
