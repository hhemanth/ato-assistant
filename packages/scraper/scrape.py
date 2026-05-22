"""
Fetch ATO pages listed in target_urls.txt and upsert into ato_pages.
Run: uv run --directory packages/scraper python scrape.py
"""
import asyncio
import os
import re
from pathlib import Path

import httpx
import trafilatura
from dotenv import find_dotenv, load_dotenv
from supabase import create_client, Client

load_dotenv(find_dotenv())

SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 "
    "(ATO Assistant research tool; contact: hhemanth@gmail.com)"
)

URLS_FILE = Path(__file__).parent / "target_urls.txt"
MIN_CONTENT_CHARS = 200  # pages below this are hub/nav pages — skip


def _extract_title(html: str, fallback: str) -> str:
    m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
    if not m:
        return fallback
    title = m.group(1).strip()
    # Strip " | Australian Taxation Office" suffix ATO appends to every title
    return re.sub(r"\s*\|\s*Australian Taxation Office.*$", "", title).strip()


def _extract_last_modified(headers: httpx.Headers) -> str | None:
    return headers.get("last-modified")


def extract_page(html: str, url: str) -> tuple[str, str, str | None]:
    """Return (title, markdown, last_modified) from raw HTML and response headers."""
    title = _extract_title(html, url)
    markdown = trafilatura.extract(
        html,
        output_format="markdown",
        include_tables=True,
        include_links=False,
        favor_recall=True,
    ) or ""
    return title, markdown, None  # last_modified injected by caller


async def scrape_url(
    client: httpx.AsyncClient,
    supabase: Client,
    url: str,
) -> None:
    try:
        resp = await client.get(url, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        print(f"  SKIP  {url}: {exc}")
        return

    final_url = str(resp.url)
    title, markdown, _ = extract_page(resp.text, final_url)
    last_modified = _extract_last_modified(resp.headers)

    if len(markdown) < MIN_CONTENT_CHARS:
        print(f"  THIN  {final_url}: {len(markdown)} chars — hub page, skipping")
        return

    supabase.table("ato_pages").upsert(
        {
            "url": final_url,
            "title": title,
            "markdown": markdown,
            "last_modified": last_modified,
        },
        on_conflict="url",
    ).execute()
    print(f"  OK    {final_url} ({len(markdown)} chars)")


def load_urls() -> list[str]:
    return [
        line.strip()
        for line in URLS_FILE.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]


async def main() -> None:
    urls = load_urls()
    print(f"Scraping {len(urls)} URLs at 1 req/sec ...\n")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    headers = {"User-Agent": USER_AGENT}

    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        for i, url in enumerate(urls, 1):
            print(f"[{i:02d}/{len(urls)}]", end=" ")
            await scrape_url(client, supabase, url)
            if i < len(urls):
                await asyncio.sleep(1)

    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
