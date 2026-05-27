# packages/agent/tests/test_verifier.py
"""
Unit tests for the citation verifier.
Parsing tests are pure (no API calls).
verify_response tests mock _check_snippet.
Run: uv run --directory packages/agent pytest tests/test_verifier.py -v
"""
import asyncio
from unittest.mock import AsyncMock, patch

from nodes.verifier import (
    VerificationSummary,
    _extract_citations,
    _extract_claim,
    _match_chunk,
    verify_response,
)


# ---------------------------------------------------------------------------
# _extract_citations
# ---------------------------------------------------------------------------

def test_extract_citations_single() -> None:
    response = (
        "The tax-free threshold is $18,200 [1].\n\n"
        "## Sources\n"
        "[1] Tax rates — https://www.ato.gov.au/tax-rates\n"
    )
    assert _extract_citations(response) == {1: "https://www.ato.gov.au/tax-rates"}


def test_extract_citations_multiple() -> None:
    response = (
        "Claim one [1]. Claim two [2].\n\n"
        "## Sources\n"
        "[1] Page A — https://www.ato.gov.au/a\n"
        "[2] Page B — https://www.ato.gov.au/b\n"
    )
    assert _extract_citations(response) == {
        1: "https://www.ato.gov.au/a",
        2: "https://www.ato.gov.au/b",
    }


def test_extract_citations_no_sources_section() -> None:
    assert _extract_citations("No sources here.") == {}


def test_extract_citations_empty_response() -> None:
    assert _extract_citations("") == {}


# ---------------------------------------------------------------------------
# _extract_claim
# ---------------------------------------------------------------------------

def test_extract_claim_found() -> None:
    response = "The tax-free threshold is $18,200 [1]. Other text."
    claim = _extract_claim(response, 1)
    assert "[1]" in claim
    assert "$18,200" in claim


def test_extract_claim_not_found() -> None:
    assert _extract_claim("No citation here.", 1) == ""


# ---------------------------------------------------------------------------
# _match_chunk
# ---------------------------------------------------------------------------

def test_match_chunk_found() -> None:
    chunks = [{"url": "https://www.ato.gov.au/tax-rates", "chunk_text": "rates info"}]
    result = _match_chunk("https://www.ato.gov.au/tax-rates", chunks)
    assert result is not None
    assert result["chunk_text"] == "rates info"


def test_match_chunk_not_found() -> None:
    chunks = [{"url": "https://www.ato.gov.au/other", "chunk_text": "other"}]
    assert _match_chunk("https://www.ato.gov.au/tax-rates", chunks) is None


def test_match_chunk_empty_list() -> None:
    assert _match_chunk("https://www.ato.gov.au/tax-rates", []) is None


# ---------------------------------------------------------------------------
# verify_response (mocks _check_snippet to avoid API calls)
# ---------------------------------------------------------------------------

def test_verify_response_all_verified() -> None:
    response = (
        "The tax-free threshold is $18,200 [1].\n\n"
        "## Sources\n"
        "[1] Tax rates — https://www.ato.gov.au/tax-rates\n"
    )
    chunks = [{"url": "https://www.ato.gov.au/tax-rates", "chunk_text": "threshold is $18,200"}]

    with patch("nodes.verifier._check_snippet", new=AsyncMock(return_value=True)):
        summary = asyncio.run(verify_response(response, chunks))

    assert summary.total_citations == 1
    assert summary.url_verified == 1
    assert summary.snippet_verified == 1


def test_verify_response_hallucinated_url() -> None:
    response = (
        "Claim [1].\n\n"
        "## Sources\n"
        "[1] Fake — https://www.ato.gov.au/does-not-exist\n"
    )
    chunks = [{"url": "https://www.ato.gov.au/real", "chunk_text": "real content"}]

    summary = asyncio.run(verify_response(response, chunks))

    assert summary.total_citations == 1
    assert summary.url_verified == 0
    assert summary.snippet_verified == 0


def test_verify_response_no_citations() -> None:
    summary = asyncio.run(verify_response("No citations.", []))
    assert summary.total_citations == 0
    assert summary.url_verified == 0
    assert summary.snippet_verified == 0


def test_verify_response_snippet_fails() -> None:
    response = (
        "Claim [1].\n\n"
        "## Sources\n"
        "[1] Page — https://www.ato.gov.au/page\n"
    )
    chunks = [{"url": "https://www.ato.gov.au/page", "chunk_text": "unrelated content"}]

    with patch("nodes.verifier._check_snippet", new=AsyncMock(return_value=False)):
        summary = asyncio.run(verify_response(response, chunks))

    assert summary.total_citations == 1
    assert summary.url_verified == 1
    assert summary.snippet_verified == 0
