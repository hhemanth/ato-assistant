# Week 2 — Slice 2 Finish (RAG Hardening) + Slice 3 Start (Router + Calculator)

**Goal:** Slice 2 fully shipped by Wednesday with a clean RAG-with-citations product. Start slice 3 with routing and the tax calculator Thursday-Sunday.

**Budget:** ~24 hours.

**End-of-week deliverable:** Live URL with citation-grounded RAG over an expanded corpus, routing live for 4 query types, deterministic tax calculator working.

---

## ⛳ SLICE 2 FINISH: Production-grade RAG (Days 8-10)

### Mon (Day 8) — Expand the corpus + retrieval quality (4 hrs)

- [ ] Audit the 30-50 page corpus from Week 1: which questions failed? Which topics weren't covered?
- [ ] Expand to **~150 pages** (still not 300+) — add: super basics for individuals, BAS intro, capital gains intro, non-resident rates, working holiday rates, common deductions in detail
- [ ] Re-run scrape → chunk → embed
- [ ] **Add hybrid retrieval:** Postgres `tsvector` full-text search combined with vector similarity. Why: ATO pages have very specific terminology that BM25 catches better than embeddings.
- [ ] Re-test the 10 questions from last week — should see noticeable improvement

**Deliverable:** ~150 ATO pages indexed, hybrid retrieval working, measurably better answers on the test set.

### Tue (Day 9) — Error handling, streaming, rate limiting (4 hrs)

- [ ] Add streaming responses end-to-end (FastAPI → Vercel AI SDK → UI)
- [ ] Proper error states in UI: rate limit hit, retrieval failure, LLM error
- [ ] Rate limiting on the API: 10 requests/min per IP using Upstash Redis (free tier)
- [ ] Add a "Report incorrect answer" button — writes to a Supabase table `feedback` for review
- [ ] Langfuse dashboard: create custom views for slice 2 metrics
  - Latency p50/p95 per query
  - Citations per response (average)
  - Most common queries (for week 3 eval inspiration)

**Deliverable:** Live URL is robust to errors, streams smoothly, rate-limited.

### Wed (Day 10) — Polish slice 2 demo + content prep (4 hrs)

- [ ] Add 6-8 "example queries" on the landing page to lower friction
- [ ] Mobile responsive check
- [ ] Capture demo video showing citations expanding/contracting
- [ ] **🚀 Slice 2 officially "shipped"** — this is article #2's launch state

**Deliverable:** Slice 2 product feels polished. Demo-ready for content.

---

## ⛳ SLICE 3 START: Routing + Calculator Tool (Days 11-14)

### Thu (Day 11) — Router node (4 hrs)

- [ ] `packages/agent/nodes/router.py`: classify queries into 4 categories:
  - `factual` — info lookup (rates, deadlines, definitions)
  - `calculation` — wants a number computed
  - `personal_advice` — judgment-required ("should I claim X?")
  - `out_of_scope` — non-ATO or adversarial
- [ ] `prompts/router.md`: 2 few-shot examples per category
- [ ] Pydantic:
  ```python
  class RoutingDecision(BaseModel):
      category: Literal["factual", "calculation", "personal_advice", "out_of_scope"]
      confidence: float
      reasoning: str
  ```
- [ ] Update `graph.py` with conditional edges:
  - `factual` → retrieve → generate
  - `calculation` → calculator tool → format response
  - `personal_advice` → refusal generator
  - `out_of_scope` → polite redirect
- [ ] Write 20 test queries (5/category), verify routing ≥ 90% accurate

**Deliverable:** Router live, traced in Langfuse with category labels.

### Fri (Day 12) — Tax calculator tool (4 hrs)

- [ ] `packages/agent/tools/tax_calculator.py`: pure Python, no LLM. For 2024-25:
  - Resident income tax brackets
  - Medicare levy (2%) with low-income threshold
  - Medicare Levy Surcharge (income-tested)
  - Low Income Tax Offset (LITO)
  - HELP/HECS repayment thresholds (current 18 bands)
- [ ] Input/Output Pydantic models (see PLAN.md / original WEEK_2 for full schemas)
- [ ] **Unit tests at every bracket boundary** — calculator correctness is non-negotiable
- [ ] Wire as a LangGraph tool node, generator formats result with citations to source ATO pages

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
