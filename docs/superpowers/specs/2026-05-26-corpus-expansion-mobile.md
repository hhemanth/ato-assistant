# Corpus Expansion + Mobile Responsive Check

**Date:** 2026-05-26  
**Slice:** 2  
**Goal:** Expand the ATO RAG corpus from 65 to 150-300 indexed pages using a BFS spider, then fix any mobile layout issues in the chat UI.

---

## Part 1 — Spider + Corpus Expansion

### New file: `packages/scraper/spider.py`

BFS crawler that discovers net-new ATO leaf-page URLs.

**Inputs:**
- Hardcoded list of 24 hub pages (see below)
- Supabase `ato_pages` table — queried at startup for already-indexed URLs
- `packages/scraper/target_urls.txt` — read to exclude already-targeted URLs

**Crawl behaviour:**
- Depth: 2 hops from each hub page
- Rate: 1 request/sec (same constraint as scraper)
- Uses same `BROWSER_HEADERS` as `scrape.py`
- Follows only `https://www.ato.gov.au/` internal links

**URL filters (exclude if any match):**
- Contains: `/legal/`, `/about-ato/`, `/media-centre/`, `/news/`, `/calculators-and-tools/`, `/sitemap/`, `/search/`, `/contact-us/`, `/online-services/`
- Ends with: `.pdf`, `.doc`, `.xlsx`, `.zip`
- Contains `?` (query strings)
- Contains `#` (anchors)
- Path depth < 3 segments (these are hub/nav pages, not leaf content)

**Deduplication:**
- Union of Supabase `ato_pages.url` + lines from `target_urls.txt` = skip set
- Only URLs not in the skip set are written to output

**Output:** `packages/scraper/discovered_urls.txt`
- Grouped by inferred topic (derived from URL path prefix)
- Header comment with timestamp and counts (total discovered, already known, net-new)
- One URL per line within each group

**Hub pages (24 total):**

```
# Individuals & Families — Income & Deductions
https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/income-you-must-declare
https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/deductions-you-can-claim
https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/tax-offsets

# Individuals & Families — Employment & Life Events
https://www.ato.gov.au/individuals-and-families/jobs-and-employment-types
https://www.ato.gov.au/individuals-and-families/coming-to-australia-or-going-overseas
https://www.ato.gov.au/individuals-and-families/your-tax-return

# Investments & Assets
https://www.ato.gov.au/individuals-and-families/investments-and-assets/capital-gains-tax
https://www.ato.gov.au/individuals-and-families/investments-and-assets/property-and-land/residential-rental-properties
https://www.ato.gov.au/individuals-and-families/investments-and-assets/shares-funds-and-trusts
https://www.ato.gov.au/individuals-and-families/investments-and-assets/crypto-asset-investments

# Super, Medicare, HELP
https://www.ato.gov.au/individuals-and-families/super-for-individuals-and-families/super
https://www.ato.gov.au/individuals-and-families/medicare-and-private-health-insurance
https://www.ato.gov.au/individuals-and-families/study-and-training-support-loans

# Business / Sole Trader
https://www.ato.gov.au/businesses-and-organisations/gst
https://www.ato.gov.au/businesses-and-organisations/business-activity-statements-bas
https://www.ato.gov.au/businesses-and-organisations/income-deductions-and-concessions
https://www.ato.gov.au/businesses-and-organisations/starting-registering-or-closing-a-business
https://www.ato.gov.au/businesses-and-organisations/employer-obligations
https://www.ato.gov.au/businesses-and-organisations/super-for-employers
https://www.ato.gov.au/businesses-and-organisations/income-deductions-and-concessions/sharing-economy-and-tax

# Rates, Forms & Other
https://www.ato.gov.au/tax-rates-and-codes
https://www.ato.gov.au/tax-rates-and-codes/key-superannuation-rates-and-thresholds
https://www.ato.gov.au/forms-and-instructions
https://www.ato.gov.au/not-for-profit
```

---

### Modified: `packages/scraper/scrape.py`

Add `--urls-file` CLI argument (default: `target_urls.txt`).

```
uv run python scrape.py --urls-file discovered_urls.txt
```

No other logic changes — the existing upsert-on-conflict is safe for re-runs.

---

### Workflow

1. Run `spider.py` → outputs `discovered_urls.txt`
2. User reviews and prunes `discovered_urls.txt`
3. Run `scrape.py --urls-file discovered_urls.txt` → indexes net-new pages
4. Run existing `chunk.py` and `embed.py` to chunk and embed new pages

---

## Part 2 — Mobile Responsive Check

**Scope:** The chat UI at `/chat`. No new features, fix layout only.

**Components to audit:**
- `components/chat-ui.tsx` — outer shell, sidebar toggle, mobile header bar
- `components/chat/Sidebar.tsx` — overlay behaviour on mobile
- `components/chat/MessageList.tsx` — message bubbles, citation panels
- `components/chat/InputBar.tsx` — textarea, send button tap targets
- `components/chat/DisclaimerBanner.tsx` — wrapping/overflow
- `components/chat/EmptyState.tsx` — suggestion chips layout

**Checks to run:**
- Viewport: 375px (iPhone SE), 390px (iPhone 14), 768px (iPad)
- Sidebar: opens/closes correctly, overlays content (does not push)
- Messages: no horizontal overflow, long URLs wrap
- Input bar: keyboard doesn't cover it (check `env(safe-area-inset-bottom)`)
- Citation links: tap targets ≥ 44px
- Disclaimer banner: text wraps, not truncated

**Fix approach:** Tailwind responsive classes only (`sm:`, `md:`). No layout restructuring.

---

## Success criteria

- `discovered_urls.txt` contains ≥ 100 net-new URLs after spider run
- After scrape: `ato_pages` row count ≥ 150
- After chunk+embed: queries for sole trader GST, BAS, non-resident tax return correctly
- Chat UI has no horizontal overflow on 375px viewport
- All interactive elements have ≥ 44px tap targets on mobile
