import os
from collections.abc import AsyncIterator

import anthropic
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()

_client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 1024


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


async def _stream_tokens(messages: list[Message]) -> AsyncIterator[str]:
    async with _client.messages.stream(
        model=_MODEL,
        max_tokens=_MAX_TOKENS,
        messages=[{"role": m.role, "content": m.content} for m in messages],
    ) as stream:
        async for text in stream.text_stream:
            yield text


@router.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        _stream_tokens(request.messages),
        media_type="text/plain",
    )
