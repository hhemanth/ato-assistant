"""
Spider ATO hub pages to discover net-new leaf URLs.
BFS crawl from 24 hub pages to depth 2. Writes discovered_urls.txt.

Run: uv run --directory packages/scraper python spider.py
Then review discovered_urls.txt, prune junk, and run:
  uv run --directory packages/scraper python scrape.py --urls-file discovered_urls.txt
"""
import asyncio
import os
from collections import deque
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from dotenv import find_dotenv, load_dotenv
from supabase import create_client, Client

load_dotenv(find_dotenv())

SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]

ATO_HOST = "www.ato.gov.au"
MAX_DEPTH = 2
MAX_FETCHES = 400
OUTPUT_FILE = Path(__file__).parent / "discovered_urls.txt"
URLS_FILE = Path(__file__).parent / "target_urls.txt"

HUB_PAGES: list[str] = [
    # Individuals & Families — Income & Deductions
    "https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/income-you-must-declare",
    "https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/deductions-you-can-claim",
    "https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/tax-offsets",
    # Individuals & Families — Employment & Life Events
    "https://www.ato.gov.au/individuals-and-families/jobs-and-employment-types",
    "https://www.ato.gov.au/individuals-and-families/coming-to-australia-or-going-overseas",
    "https://www.ato.gov.au/individuals-and-families/your-tax-return",
    # Investments & Assets
    "https://www.ato.gov.au/individuals-and-families/investments-and-assets/capital-gains-tax",
    "https://www.ato.gov.au/individuals-and-families/investments-and-assets/property-and-land/residential-rental-properties",
    "https://www.ato.gov.au/individuals-and-families/investments-and-assets/shares-funds-and-trusts",
    "https://www.ato.gov.au/individuals-and-families/investments-and-assets/crypto-asset-investments",
    # Super, Medicare, HELP
    "https://www.ato.gov.au/individuals-and-families/super-for-individuals-and-families/super",
    "https://www.ato.gov.au/individuals-and-families/medicare-and-private-health-insurance",
    "https://www.ato.gov.au/individuals-and-families/study-and-training-support-loans",
    # Business / Sole Trader (currently zero coverage)
    "https://www.ato.gov.au/businesses-and-organisations/gst",
    "https://www.ato.gov.au/businesses-and-organisations/business-activity-statements-bas",
    "https://www.ato.gov.au/businesses-and-organisations/income-deductions-and-concessions",
    "https://www.ato.gov.au/businesses-and-organisations/starting-registering-or-closing-a-business",
    "https://www.ato.gov.au/businesses-and-organisations/employer-obligations",
    "https://www.ato.gov.au/businesses-and-organisations/super-for-employers",
    "https://www.ato.gov.au/businesses-and-organisations/income-deductions-and-concessions/sharing-economy-and-tax",
    # Rates, Forms & Other
    "https://www.ato.gov.au/tax-rates-and-codes",
    "https://www.ato.gov.au/tax-rates-and-codes/key-superannuation-rates-and-thresholds",
    "https://www.ato.gov.au/forms-and-instructions",
    "https://www.ato.gov.au/not-for-profit",
]

# URL path fragments that indicate non-content pages
EXCLUDE_PATH_FRAGMENTS: list[str] = [
    "/legal/",
    "/about-ato/",
    "/media-centre/",
    "/news/",
    "/calculators-and-tools/",
    "/sitemap/",
    "/search/",
    "/contact-us/",
    "/online-services/",
    "/media-releases/",
    "/speeches/",
    "/corporate/",
    "/law-and-legislation/",
    "/legal-database/",
    "/ato-community/",
]

EXCLUDE_EXTENSIONS: frozenset[str] = frozenset(
    {".pdf", ".doc", ".docx", ".xlsx", ".xls", ".zip", ".csv", ".json"}
)

BROWSER_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-AU,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "From": "hhemanth@gmail.com",
}


def normalise(url: str) -> str:
    """Canonicalise to https://www.ato.gov.au<path> (no fragment, no trailing slash)."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") or "/"
    return f"https://{ATO_HOST}{path}"


def should_include(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.netloc not in (ATO_HOST, "ato.gov.au"):
        return False
    if parsed.fragment or parsed.query:
        return False
    path = parsed.path.lower()
    _, ext = os.path.splitext(path)
    if ext in EXCLUDE_EXTENSIONS:
        return False
    return not any(frag in path for frag in EXCLUDE_PATH_FRAGMENTS)


def extract_links(html: str, base_url: str) -> set[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: set[str] = set()
    for a in soup.find_all("a", href=True):
        full = urljoin(base_url, a["href"])
        norm = normalise(full)
        if should_include(norm):
            links.add(norm)
    return links


def load_existing_urls() -> set[str]:
    if not URLS_FILE.exists():
        return set()
    return {
        line.strip()
        for line in URLS_FILE.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }


def load_indexed_urls(supabase: Client) -> set[str]:
    result = supabase.table("ato_pages").select("url").execute()
    return {row["url"] for row in result.data}


def topic_group(url: str) -> str:
    """Derive a readable section label from a URL's top path segments."""
    path = urlparse(url).path.strip("/")
    segments = path.split("/")
    label = " > ".join(s.replace("-", " ").title() for s in segments[:3])
    return label


async def crawl(client: httpx.AsyncClient) -> set[str]:
    """BFS crawl from HUB_PAGES to depth MAX_DEPTH. Returns all discovered ATO URLs."""
    visited: set[str] = set(HUB_PAGES)
    discovered: set[str] = set()
    queue: deque[tuple[str, int]] = deque((url, 0) for url in HUB_PAGES)
    fetched = 0

    while queue and fetched < MAX_FETCHES:
        url, depth = queue.popleft()

        try:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            print(f"  SKIP  [{depth}] {url}: {exc}")
            await asyncio.sleep(1)
            continue

        fetched += 1
        links = extract_links(resp.text, str(resp.url))

        for link in links:
            if link not in visited:
                visited.add(link)
                discovered.add(link)
                if depth + 1 < MAX_DEPTH:
                    queue.append((link, depth + 1))

        print(f"  [{fetched:03d}/{MAX_FETCHES}] depth={depth} +{len(links)} links  {url}")
        await asyncio.sleep(1)

    if fetched >= MAX_FETCHES:
        print(f"\n  Reached MAX_FETCHES={MAX_FETCHES} limit — stopping early.")

    return discovered


def filter_leaves(urls: set[str]) -> set[str]:
    """Remove hub pages: any URL that has at least one child in the same set."""
    paths = {urlparse(u).path.rstrip("/") for u in urls}
    return {
        u for u in urls
        if not any(
            p != urlparse(u).path.rstrip("/") and p.startswith(urlparse(u).path.rstrip("/") + "/")
            for p in paths
        )
    }


def write_output(discovered: set[str], skip_set: set[str]) -> int:
    net_new = discovered - skip_set
    net_new = filter_leaves(net_new)

    # Group by topic prefix for readability
    groups: dict[str, list[str]] = {}
    for url in sorted(net_new):
        group = topic_group(url)
        groups.setdefault(group, []).append(url)

    lines: list[str] = [
        f"# Discovered by spider.py on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"# Net-new URLs only (not in ato_pages table or target_urls.txt)",
        f"# Total: {len(net_new)} URLs",
        f"# Review and prune, then run:",
        f"#   uv run --directory packages/scraper python scrape.py --urls-file discovered_urls.txt",
        "",
    ]

    for group, urls in sorted(groups.items()):
        lines.append(f"\n# === {group} ===")
        lines.extend(urls)

    OUTPUT_FILE.write_text("\n".join(lines) + "\n")
    return len(net_new)


async def main() -> None:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("Loading already-indexed URLs from Supabase...")
    indexed = load_indexed_urls(supabase)
    print(f"  {len(indexed)} pages in ato_pages")

    print("Loading target_urls.txt...")
    targeted = load_existing_urls()
    print(f"  {len(targeted)} URLs in target_urls.txt")

    skip_set = indexed | targeted
    print(f"  {len(skip_set)} total to skip\n")

    print(f"Starting BFS crawl (depth={MAX_DEPTH}, max_fetches={MAX_FETCHES}, 1 req/sec)...\n")
    async with httpx.AsyncClient(headers=BROWSER_HEADERS, timeout=30) as client:
        discovered = await crawl(client)

    total = write_output(discovered, skip_set)
    print(f"\nDone. {total} net-new URLs → {OUTPUT_FILE}")
    print("Review the file, prune junk, then run scrape.py --urls-file discovered_urls.txt")


if __name__ == "__main__":
    asyncio.run(main())
