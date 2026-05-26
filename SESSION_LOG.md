# Session Log

---

## 2026-05-22 — Slice 2, Days 8-9

**Slice:** 2 (RAG over ATO pages)

### What got done

**Scraper fixes (packages/scraper):**
- Fixed `pyproject.toml`: added `package = false` so uv skips editable install
- Fixed 403s: added full browser headers (Sec-Fetch-*, Accept-Language, etc.)
- Fixed brotli encoding: removed `br` from Accept-Encoding so server returns gzip
- Fixed embed.py: switched from `upsert` to `update` to avoid NOT NULL constraint errors
- Fixed Supabase RLS: switched to service_role key in .env

**Pipeline run:**
- Scraped 65/66 ATO pages (1 dead URL — key-dates-for-individuals)
- Chunked into 344 chunks
- Embedded all 344 chunks with voyage-3-large

**RAG pipeline (apps/api):**
- Migration 001: added `fts` tsvector column + GIN index + `search_chunks_hybrid` function (RRF hybrid retrieval)
- Migration 002: added `feedback` table with RLS enabled
- `chat.py`: embed query → hybrid retrieve → generate with citations
- `system.md`: prompt with citation rules + disclaimer
- `feedback.py`: POST /feedback endpoint
- Rate limiting: slowapi 10 req/min per IP
- Added voyageai + supabase + slowapi to API deps

**Frontend (apps/web):**
- Wired Next.js `/api/chat` proxy to Railway FastAPI backend
- Added `/api/feedback` proxy route
- Proper error states: 429 rate limit message, 503, generic fallback
- Markdown rendering: react-markdown + remark-gfm + @tailwindcss/typography
- "Report incorrect answer" button on each assistant message

**Deployment:**
- Pushed to main, Railway + Vercel auto-deployed
- Fixed production issue: NEXT_PUBLIC_API_URL in Vercel was missing `https://` prefix

### What's blocked / next

- Day 8 corpus expansion (target ~150 pages) was skipped — corpus is still 65 pages
- Day 9 Langfuse dashboard skipped (deferred per earlier decision)
- Day 10 (Wed): Polish — example queries on landing page, mobile check, demo video
- Then Slice 3: router node, tax calculator, refusal prompts

### Notes
- schema.sql intentionally kept without IVFFlat index (too small corpus; add when >10k chunks)
- Dead URL to remove from target_urls.txt: `https://www.ato.gov.au/individuals-and-families/key-dates-for-individuals`

---

## 2026-05-26 — Slice 3, Day 11

**Slice:** 3

### What got done
- packages/agent: new uv workspace member with LangGraph
- router_graph: Haiku 4.5 classifies queries into factual/calculation/personal_advice/out_of_scope (20/20 test accuracy)
- judge_graph: Nemotron 4 340B via NVIDIA NIM scores helpfulness/correctness/coherence (pending NVIDIA_API_KEY in .env)
- chat.py: routes before streaming, judges after, yields __JUDGE__ sentinel
- JudgePanel.tsx: collapsible quality scores UI rendered per response
- refusal.md + out_of_scope.md prompts added
- 20-query router test suite (100% accuracy)

### What's blocked
- ~~judge smoke test: NVIDIA_API_KEY not yet added~~ — replaced Nemotron with Haiku 4.5 judge (no NVIDIA key needed)

### What's next
- Day 12: Tax calculator ✓ (done same session, see below)

---

## 2026-05-26 — Slice 3, Day 12

**Slice:** 3

### What got done
- `packages/agent/tools/tax_calculator.py`: pure Python calculator, 2025-26 and 2026-27 only
  - Income tax brackets (2026-27 has 15% second band vs 16% in 2025-26)
  - Medicare levy with $26k shade-in threshold
  - Medicare Levy Surcharge (3 tiers, singles: $101k/118k/158k)
  - LITO (max $700, two-stage phase-out to $66,667)
  - HELP marginal repayment (new 2025-26 system, threshold $67k)
- 77/77 unit tests passing at every bracket boundary
- `calculator_node.py`: Haiku 4.5 extracts income/year from natural language, calls calculator
- `router_graph` updated: calculation → calculator_node → END (conditional edge)
- `chat.py`: calculation queries now stream a formatted markdown table with ATO source links
- Judge replaced: Nemotron deprecated, now using Haiku 4.5 LLM-as-judge (no NVIDIA key needed)
- JudgePanel: expanded by default; report button made more prominent (red border)

### What's next
- Day 13: Refusal prompts polish + edge case testing (adversarial prompts, jailbreaks)
- Day 14: Citation verifier scaffold
