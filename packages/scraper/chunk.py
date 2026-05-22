"""
Split ato_pages markdown into ~500-token chunks with heading context.
Deletes and re-inserts chunks for every page on each run (idempotent).
Run: uv run --directory packages/scraper python chunk.py
"""
import os
import re

import tiktoken
from dotenv import find_dotenv, load_dotenv
from supabase import create_client, Client

load_dotenv(find_dotenv())

SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]

CHUNK_TOKENS = 500
OVERLAP_TOKENS = 50
ENCODER = tiktoken.get_encoding("cl100k_base")

HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$")


def _tokens(text: str) -> list[int]:
    return ENCODER.encode(text)


def _detokenize(tokens: list[int]) -> str:
    return ENCODER.decode(tokens)


def _update_heading_path(line: str, current: list[str]) -> list[str]:
    m = HEADING_RE.match(line.rstrip())
    if not m:
        return current
    level = len(m.group(1))           # 1, 2, or 3
    text = m.group(2).strip()
    # Keep ancestors, replace at this level and drop deeper levels
    return (current[: level - 1] + [text])


def chunk_markdown(markdown: str) -> list[dict]:
    """
    Walk markdown line-by-line, accumulate tokens, and emit chunks.
    Each chunk carries the heading_path active at the start of that chunk.
    """
    chunks: list[dict] = []
    heading_path: list[str] = []
    buffer: list[int] = []
    chunk_heading: list[str] = []   # heading_path at the start of current buffer
    chunk_index = 0

    def _flush() -> None:
        nonlocal chunk_index
        text = _detokenize(buffer).strip()
        if not text:
            return
        chunks.append({
            "chunk_index": chunk_index,
            "heading_path": chunk_heading.copy(),
            "chunk_text": text,
        })
        chunk_index += 1

    for line in markdown.splitlines(keepends=True):
        new_path = _update_heading_path(line, heading_path)
        if new_path != heading_path:
            heading_path = new_path

        line_tokens = _tokens(line)

        if len(buffer) + len(line_tokens) > CHUNK_TOKENS:
            _flush()
            # Carry overlap from the end of the previous buffer into the next chunk
            overlap = buffer[-OVERLAP_TOKENS:] if buffer else []
            buffer = overlap + line_tokens
            chunk_heading = heading_path.copy()
        else:
            if not buffer:
                chunk_heading = heading_path.copy()
            buffer.extend(line_tokens)

    _flush()
    return chunks


def process_page(supabase: Client, page: dict) -> int:
    page_id = page["id"]
    chunks = chunk_markdown(page["markdown"])

    # Replace all existing chunks for this page (idempotent re-run)
    supabase.table("ato_chunks").delete().eq("page_id", page_id).execute()

    if not chunks:
        return 0

    rows = [
        {
            "page_id": page_id,
            "url": page["url"],
            "page_title": page["title"],
            "chunk_index": c["chunk_index"],
            "heading_path": c["heading_path"],
            "chunk_text": c["chunk_text"],
        }
        for c in chunks
    ]
    supabase.table("ato_chunks").insert(rows).execute()
    return len(chunks)


def main() -> None:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    pages = (
        supabase.table("ato_pages")
        .select("id, url, title, markdown")
        .execute()
        .data
    )
    print(f"Chunking {len(pages)} pages ...\n")

    total_chunks = 0
    for page in pages:
        n = process_page(supabase, page)
        total_chunks += n
        print(f"  {page['url']}")
        print(f"    → {n} chunks")

    print(f"\nDone. {total_chunks} total chunks across {len(pages)} pages.")


if __name__ == "__main__":
    main()
