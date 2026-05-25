"""
RAG chat endpoint: embed query → hybrid retrieve → generate with citations.
"""
import asyncio
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

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

_anthropic = wrap_anthropic(anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"]))
_voyage = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])
_supabase: Client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

_MODEL = "claude-sonnet-4-6"
_EMBED_MODEL = "voyage-3-large"
_MAX_TOKENS = 1024
_TOP_K = 5

_SYSTEM_PROMPT = (Path(__file__).parent.parent / "prompts" / "system.md").read_text()


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


@traceable(name="generate", metadata={"model": _MODEL})
async def _stream_response(messages: list[Message]) -> AsyncIterator[str]:
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


@router.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, body: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        _stream_response(body.messages),
        media_type="text/plain",
    )
