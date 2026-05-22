"""
Embed ato_chunks rows that have no embedding yet using Voyage voyage-3-large.
Safe to re-run: only processes rows where embedding IS NULL.
Run: uv run --directory packages/scraper python embed.py
"""
import os

import voyageai
from dotenv import find_dotenv, load_dotenv
from supabase import create_client, Client

load_dotenv(find_dotenv())

SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]
VOYAGE_API_KEY: str = os.environ["VOYAGE_API_KEY"]

MODEL = "voyage-3-large"
BATCH_SIZE = 128  # Voyage's recommended maximum


def fetch_unembedded(supabase: Client) -> list[dict]:
    return (
        supabase.table("ato_chunks")
        .select("id, chunk_text")
        .is_("embedding", "null")
        .execute()
        .data
    )


def embed_batch(
    voyage: voyageai.Client,
    batch: list[dict],
) -> list[dict]:
    texts = [c["chunk_text"] for c in batch]
    result = voyage.embed(texts, model=MODEL, input_type="document")
    return [
        {"id": batch[i]["id"], "embedding": result.embeddings[i]}
        for i in range(len(batch))
    ]


def main() -> None:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    voyage = voyageai.Client(api_key=VOYAGE_API_KEY)

    chunks = fetch_unembedded(supabase)
    if not chunks:
        print("No unembedded chunks found. Run chunk.py first.")
        return

    print(f"Embedding {len(chunks)} chunks in batches of {BATCH_SIZE} ...\n")

    total = 0
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        rows = embed_batch(voyage, batch)
        for row in rows:
            supabase.table("ato_chunks").update({"embedding": row["embedding"]}).eq("id", row["id"]).execute()
        total += len(rows)
        print(f"  Batch {i // BATCH_SIZE + 1}: {len(rows)} chunks embedded (total: {total})")

    print(f"\nDone. {total} chunks now have embeddings.")


if __name__ == "__main__":
    main()
