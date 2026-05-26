# Week 2 — Slice 2 Finish (RAG Hardening) + Slice 3 Start (Router + Calculator)

**Goal:** Slice 2 fully shipped by Wednesday with a clean RAG-with-citations product. Start slice 3 with routing and the tax calculator Thursday-Sunday.

**Budget:** ~24 hours.

**End-of-week deliverable:** Live URL with citation-grounded RAG over an expanded corpus, routing live for 4 query types, deterministic tax calculator working.

---

## ⛳ SLICE 2 FINISH: Production-grade RAG (Days 8-10)

### Mon (Day 8) — Expand the corpus + retrieval quality (4 hrs)

- [x] Audit the 30-50 page corpus from Week 1: which questions failed? Which topics weren't covered?
- [x] Expand to **~275 pages** — spider from 24 hub pages, leaf-only filter, scraped 209 net-new pages (total ~275 indexed)
- [x] Re-run scrape → chunk → embed
- [x] **Add hybrid retrieval:** Postgres `tsvector` full-text search combined with vector similarity.

**Deliverable:** ~275 ATO pages indexed, hybrid retrieval working.

### Tue (Day 9) — Error handling, streaming, rate limiting (4 hrs)

- [x] Add streaming responses end-to-end (FastAPI → Vercel AI SDK → UI)
- [x] Proper error states in UI: rate limit hit, retrieval failure, LLM error
- [x] Rate limiting on the API: 10 requests/min per IP using slowapi
- [x] Add a "Report incorrect answer" button — writes to a Supabase table `feedback` for review
- [ ] Langfuse dashboard: create custom views for slice 2 metrics (deferred)

**Deliverable:** Live URL is robust to errors, streams smoothly, rate-limited.

### Wed (Day 10) — Polish slice 2 demo + content prep (4 hrs)

- [x] Add 8 example queries on the landing page (WFH, Medicare, CGT, GST, crypto, rideshare, super, HELP)
- [x] Mobile responsive check (safe-area, tap targets, responsive padding, table overflow)
- [ ] Capture demo video showing citations expanding/contracting
- [x] **🚀 Slice 2 officially "shipped"**

**Deliverable:** Slice 2 product feels polished. Demo-ready for content.

---

## ⛳ SLICE 3 START: Routing + Calculator Tool (Days 11-14)

### Thu (Day 11) — Router node (4 hrs)

- [x] `packages/agent/nodes/router.py`: classify queries into 4 categories:
  - `factual` — info lookup (rates, deadlines, definitions)
  - `calculation` — wants a number computed
  - `personal_advice` — judgment-required ("should I claim X?")
  - `out_of_scope` — non-ATO or adversarial
- [x] `prompts/router.md`: 2 few-shot examples per category
- [x] Pydantic:
  ```python
  class RoutingDecision(BaseModel):
      category: Literal["factual", "calculation", "personal_advice", "out_of_scope"]
      confidence: float
      reasoning: str
  ```
- [x] Update `graph.py` with conditional edges (implemented as two separate graphs: router_graph + judge_graph):
  - `factual` → retrieve → generate
  - `calculation` → calculator tool → format response
  - `personal_advice` → refusal generator
  - `out_of_scope` → polite redirect
- [x] Write 20 test queries (5/category), verify routing ≥ 90% accurate (100% achieved)

**Deliverable:** Router live, traced in Langfuse with category labels.

### Fri (Day 12) — Tax calculator tool (4 hrs)

- [x] `packages/agent/tools/tax_calculator.py`: pure Python, no LLM. 2025-26 and 2026-27:
  - Resident income tax brackets (16%→15% cut in 2026-27)
  - Medicare levy (2%) with low-income shade-in ($26k threshold)
  - Medicare Levy Surcharge (3 tiers: $101k/1%, $118k/1.25%, $158k/1.5%)
  - Low Income Tax Offset (LITO, max $700, two-stage phase-out)
  - HELP/HECS marginal repayment system (new from 2025-26, threshold $67k)
- [x] TaxInput + TaxResult Pydantic models
- [x] **Unit tests at every bracket boundary — 77/77 passing**
- [x] Wired as calculator_node in router_graph (conditional edge: calculation → calculator → END)

**Deliverable:** Calculator passes all bracket boundary tests. *"I earned $95,000 — what's my tax?"* returns clean breakdown with sources.

### Sat (Day 13) — Refusal prompts + Article #2 (4 hrs)

- [ ] `prompts/refusal.md`: structured refusal that always (a) explains *why* it can't answer personally, (b) gives the relevant factual rule from ATO docs, (c) directs to a registered tax agent
- [ ] `prompts/out_of_scope.md`: polite redirect that mentions what the assistant DOES cover
- [ ] Test edge cases: adversarial prompts, leading questions, jailbreaks (note failures for week 3 eval dataset)

**Article #2 (Saturday 7am Sydney):** *"Day 10 update: I added grounding and citations to my chat app. Here's what changed."*
- ~1000 words
- The slice-2 evolution: same product, much higher trust
- Show retrieval examples, citation rendering, why parent-doc retrieval matters
- Tease the next slice (routing + voice + evals coming)
- See `CONTENT_PLAN.md` for full outline

### Sun (Day 14) — Citation verifier scaffold (3 hrs)

This kicks off the bigger citation verification work that completes Mon/Tue of Week 3.

- [ ] `packages/agent/nodes/verifier.py`: scaffold the verifier node
- [ ] For each `[N]` marker in the answer:
  1. URL check — does it exist in `ato_pages`?
  2. Snippet check — does the cited chunk text support the claim? (Haiku 4.5 call, structured output)
- [ ] Add `verification_summary` field to response
- [ ] First version is OK to be rough — week 3 polishes it and ties it to eval metrics

**Deliverable:** Verifier scaffold in place, runs on every response. Failure logging to Langfuse working.

---

## Week 2 content cadence

- **Tue (Day 9):** Short post — *"Hybrid retrieval: BM25 + embeddings. Here's why both."* + before/after example
- **Thu (Day 11):** Short post — *"Routing in LangGraph: how my agent decides what to do."* + diagram
- **Sat (Day 13):** Article #2 published
- **Sun:** Short post — *"Calculator demo: why LLMs shouldn't do tax math."* + 15-sec video

---

## Week 2 retrospective

1. Router accuracy on 20 test queries — what's failing?
2. Calculator coverage — what edge cases did you skip? Document them.
3. First impressions of citation verifier output — what's the most common failure pattern you see?
