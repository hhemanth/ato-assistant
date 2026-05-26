"""
Integration tests for the router node.
Requires: ANTHROPIC_API_KEY env var.
Run: uv run --directory packages/agent pytest tests/test_router.py -v
"""
import asyncio
import os
import pytest
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from nodes.router import router_node
from state import AgentState

# 5 queries per category — router must get ≥ 18/20 correct
CASES: list[tuple[str, str]] = [
    # factual
    ("What is the Medicare levy rate?", "factual"),
    ("What are the income tax brackets for 2024-25?", "factual"),
    ("What is the CGT discount for assets held over 12 months?", "factual"),
    ("When is the lodgment deadline for individual tax returns?", "factual"),
    ("What expenses can I claim for working from home?", "factual"),
    # calculation
    ("I earned $85,000 this year. How much income tax will I owe?", "calculation"),
    ("My income is $120,000. What is my Medicare levy surcharge?", "calculation"),
    ("I sold shares for $50,000 that I bought for $30,000 two years ago. What is my capital gain?", "calculation"),
    ("I worked from home 200 days. Using the fixed rate method, what can I claim?", "calculation"),
    ("My taxable income is $40,000. Do I qualify for the low income tax offset and how much?", "calculation"),
    # personal_advice
    ("Should I salary sacrifice into super or invest in ETFs?", "personal_advice"),
    ("Is it worth getting private health insurance to avoid the Medicare levy surcharge?", "personal_advice"),
    ("Should I set up a company or operate as a sole trader?", "personal_advice"),
    ("Would it be better for me to use the actual cost or fixed rate method for WFH?", "personal_advice"),
    ("Should I lodge my own tax return or use a tax agent?", "personal_advice"),
    # out_of_scope
    ("What is the current RBA interest rate?", "out_of_scope"),
    ("Can you recommend a good accountant in Sydney?", "out_of_scope"),
    ("How do I apply for a passport?", "out_of_scope"),
    ("What are the best ETFs to invest in right now?", "out_of_scope"),
    ("Tell me a joke about accountants.", "out_of_scope"),
]


@pytest.mark.parametrize("query,expected", CASES)
def test_router_classifies_correctly(query: str, expected: str) -> None:
    state: AgentState = {"query": query, "messages": []}
    result = asyncio.run(router_node(state))
    assert result["category"] == expected, (
        f"Query: {query!r}\n"
        f"Expected: {expected}\n"
        f"Got: {result['category']} (confidence={result['confidence']:.2f})\n"
        f"Reasoning: {result['reasoning']}"
    )


def test_router_returns_confidence_and_reasoning() -> None:
    state: AgentState = {"query": "What is the tax-free threshold?", "messages": []}
    result = asyncio.run(router_node(state))
    assert "category" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert 0.0 <= result["confidence"] <= 1.0
    assert len(result["reasoning"]) > 0
