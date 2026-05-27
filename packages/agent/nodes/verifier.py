"""
Citation verifier: checks each [N] citation in a RAG response against retrieved chunks.
"""
import asyncio
import json
import os
import re
from pathlib import Path
from typing import Optional

import anthropic
from pydantic import BaseModel

_PROMPT = (Path(__file__).parent.parent / "prompts" / "verifier.md").read_text()
_MODEL = "claude-haiku-4-5-20251001"
_CLIENT: anthropic.AsyncAnthropic | None = None


def _client() -> anthropic.AsyncAnthropic:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _CLIENT


class VerificationSummary(BaseModel):
    total_citations: int
    url_verified: int       # URL matched a retrieved chunk
    snippet_verified: int   # Haiku confirmed snippet supports claim


def _extract_citations(response_text: str) -> dict[int, str]:
    """Return {citation_number: url} parsed from the ## Sources section."""
    citations: dict[int, str] = {}
    match = re.search(r"## Sources\n(.*?)(?:\n\n|\Z)", response_text, re.DOTALL)
    if not match:
        return citations
    for line in match.group(1).splitlines():
        m = re.match(r"\[(\d+)\]\s+.*?[—–-]\s+(https?://[^\s]+)", line)
        if m:
            citations[int(m.group(1))] = m.group(2).rstrip(".,;)")
    return citations


def _extract_claim(response_text: str, citation_num: int) -> str:
    """Extract the sentence containing [N] from the response body (before ## Sources).

    Handles both inline citations ("rate is 2% [1].") and trailing citations ("rate is 2%. [1]").
    """
    body = response_text.split("## Sources")[0]
    # Match sentence ending with [N] (trailing citation) or [N] inside sentence
    pattern = rf"[^.!?\n]*(?:\[{citation_num}\][^.!?\n]*[.!?]|[^.!?\n]*[.!?]\s*\[{citation_num}\])"
    m = re.search(pattern, body)
    return m.group(0).strip() if m else ""


def _match_chunk(url: str, chunks: list[dict]) -> Optional[dict]:
    """Return the chunk matching url, or None if not found."""
    for chunk in chunks:
        if chunk.get("url") == url:
            return chunk
    return None


async def _check_snippet(claim: str, chunk_text: str) -> bool:
    """Ask Haiku whether chunk_text directly supports claim."""
    response = await _client().messages.create(
        model=_MODEL,
        max_tokens=128,
        system=_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Claim: {claim}\n\nSource snippet: {chunk_text}",
        }],
    )
    raw = re.sub(r"```json?\s*|\s*```", "", response.content[0].text).strip()
    try:
        return bool(json.loads(raw).get("supports_claim", False))
    except (json.JSONDecodeError, AttributeError):
        return False


async def verify_response(response_text: str, chunks: list[dict]) -> VerificationSummary:
    """Verify all [N] citations in a RAG response against retrieved chunks."""
    citations = _extract_citations(response_text)
    total = len(citations)

    if total == 0:
        return VerificationSummary(total_citations=0, url_verified=0, snippet_verified=0)

    url_verified = 0
    snippet_tasks: list = []

    for num, url in citations.items():
        chunk = _match_chunk(url, chunks)
        if chunk is None:
            continue  # hallucinated URL
        url_verified += 1
        claim = _extract_claim(response_text, num)
        snippet_tasks.append(_check_snippet(claim, chunk["chunk_text"]))

    results = await asyncio.gather(*snippet_tasks, return_exceptions=True)
    snippet_verified = sum(1 for r in results if r is True)

    return VerificationSummary(
        total_citations=total,
        url_verified=url_verified,
        snippet_verified=snippet_verified,
    )
