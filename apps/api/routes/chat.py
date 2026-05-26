"""
RAG chat endpoint: route → stream → judge.
"""
import asyncio
import json
import os
from collections.abc import AsyncIterator
from pathlib import Path

import anthropic
import voyageai
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from langsmith import traceable
from langsmith.wrappers import wrap_anthropic
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from supabase import create_client, Client

from graph import router_graph
from judge_graph import judge_graph

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

_anthropic = wrap_anthropic(anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"]))
_voyage = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])
_supabase: Client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

_MODEL = "claude-sonnet-4-6"
_EMBED_MODEL = "voyage-3-large"
_MAX_TOKENS = 1024
_TOP_K = 5

_PROMPTS = Path(__file__).parent.parent / "prompts"
_SYSTEM_PROMPT   = (_PROMPTS / "system.md").read_text()
_REFUSAL_PROMPT  = (_PROMPTS / "refusal.md").read_text()
_REDIRECT_PROMPT = (_PROMPTS / "out_of_scope.md").read_text()

_CALC_PLACEHOLDER = (
    "The tax calculator is coming soon. "
    "For now, the ATO has a free income tax estimator at "
    "https://www.ato.gov.au/calculators-and-tools/income-tax-estimator — "
    "it covers income tax, Medicare levy, and most offsets."
)

JUDGE_THRESHOLD = 0.6


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


def _format_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant ATO pages found for this query."
    parts = []
    for i, c in enumerate(chunks, 1):
        heading = " > ".join(c["heading_path"]) if c.get("heading_path") else ""
        parts.append(
            f"[{i}] {c['page_title']}\n"
            f"URL: {c['url']}\n"
            + (f"Section: {heading}\n" if heading else "")
            + f"\n{c['chunk_text']}"
        )
    return "\n\n---\n\n".join(parts)


@traceable(name="retrieve", metadata={"embed_model": _EMBED_MODEL})
async def _retrieve(query: str) -> list[dict]:
    embed_result = await asyncio.to_thread(
        lambda: _voyage.embed([query], model=_EMBED_MODEL, input_type="query")
    )
    embedding = embed_result.embeddings[0]
    response = await asyncio.to_thread(
        lambda: _supabase.rpc(
            "search_chunks_hybrid",
            {"query_embedding": embedding, "query_text": query, "match_count": _TOP_K},
        ).execute()
    )
    return response.data or []


@traceable(name="rag_generate", metadata={"model": _MODEL})
async def _rag_stream(messages: list[Message]) -> AsyncIterator[str]:
    query = next((m.content for m in reversed(messages) if m.role == "user"), "")
    chunks = await _retrieve(query)
    system = _SYSTEM_PROMPT.replace("{context}", _format_context(chunks))
    async with _anthropic.messages.stream(
        model=_MODEL,
        max_tokens=_MAX_TOKENS,
        system=system,
        messages=[{"role": m.role, "content": m.content} for m in messages],
    ) as stream:
        async for text in stream.text_stream:
            yield text


@traceable(name="refusal_generate", metadata={"model": _MODEL})
async def _refusal_stream(query: str) -> AsyncIterator[str]:
    async with _anthropic.messages.stream(
        model=_MODEL,
        max_tokens=512,
        system=_REFUSAL_PROMPT,
        messages=[{"role": "user", "content": query}],
    ) as stream:
        async for text in stream.text_stream:
            yield text


@traceable(name="redirect_generate", metadata={"model": _MODEL})
async def _redirect_stream(query: str) -> AsyncIterator[str]:
    async with _anthropic.messages.stream(
        model=_MODEL,
        max_tokens=256,
        system=_REDIRECT_PROMPT,
        messages=[{"role": "user", "content": query}],
    ) as stream:
        async for text in stream.text_stream:
            yield text


async def _stream_response(messages: list[Message]) -> AsyncIterator[str]:
    query = next((m.content for m in reversed(messages) if m.role == "user"), "")

    # Phase 1: route
    route_state = await router_graph.ainvoke(
        {"query": query, "messages": [{"role": m.role, "content": m.content} for m in messages]}
    )
    category: str = route_state["category"]

    # Select stream source based on category
    if category == "factual":
        source = _rag_stream(messages)
    elif category == "personal_advice":
        source = _refusal_stream(query)
    elif category == "out_of_scope":
        source = _redirect_stream(query)
    else:  # calculation — placeholder until Day 12
        async def _placeholder() -> AsyncIterator[str]:
            yield _CALC_PLACEHOLDER
        source = _placeholder()

    # Stream to client, buffer for judge
    buffer: list[str] = []
    async for token in source:
        yield token
        buffer.append(token)

    # Phase 2: judge (runs after stream completes)
    response_text = "".join(buffer)
    try:
        judge_state = await judge_graph.ainvoke(
            {"query": query, "response": response_text}
        )
        scores: dict = judge_state.get("judge_scores", {})
    except Exception:
        scores = {}

    if scores:
        avg = sum(scores.values()) / len(scores)
        if avg < JUDGE_THRESHOLD:
            yield (
                "\n\n> Note: I may not have full ATO coverage on this topic — "
                "check [ato.gov.au](https://ato.gov.au) directly."
            )
        yield f"\n__JUDGE__{json.dumps(scores)}__"


@router.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, body: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        _stream_response(body.messages),
        media_type="text/plain",
    )
