# Week 1 — Slice 1 (Generic Chat → PROD) + Slice 2 Start (ATO RAG)

**Goal:** Ship a generic chat app to PROD by Wednesday. Start the ATO RAG slice Thursday.

**Budget:** ~22 hours.

**End-of-week deliverable:** Two live URLs of progress — Wednesday's generic chat is the first article topic, and Sunday has the ATO scrape + chunking complete with RAG wiring in progress.

---

## ⛳ SLICE 1: Generic Chat → PROD (Days 1-3)

The goal of slice 1 is **NOT** to build AI. It's to nail the deployment, observability, and UI plumbing with the simplest possible AI workload. Resist all temptation to add complexity.

### Mon (Day 1) — FastAPI backend + local test (4 hrs)

> **Revised scope:** LangGraph and Langfuse deferred to Slice 2. Slice 1 calls Anthropic directly.

- [ ] `uv init`, set up root `pyproject.toml`
- [ ] Create `apps/api/pyproject.toml` with deps: `anthropic`, `fastapi`, `uvicorn[standard]`, `pydantic`
- [ ] `apps/api/main.py`: FastAPI app + CORS middleware (allow all origins locally)
- [ ] `apps/api/routes/chat.py`: `POST /chat` — accepts `{messages: [{role, content}]}`, streams Anthropic tokens via `StreamingResponse`
- [ ] Set up `.env.example` with `ANTHROPIC_API_KEY`, `NEXT_PUBLIC_API_URL`
- [ ] Local test: `curl -N -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{"messages":[{"role":"user","content":"Hello"}]}'` — tokens stream to terminal

**Deliverable:** FastAPI running locally, streaming Claude Sonnet 4.6 responses.

### Tue (Day 2) — Next.js frontend + end-to-end local (4 hrs)

- [ ] `npx create-next-app@latest apps/web --typescript --tailwind --app`
- [ ] Add `ai` (Vercel AI SDK) + `@ai-sdk/react` to `apps/web`
- [ ] `apps/web/components/chat-ui.tsx`: `useChat` hook pointed at FastAPI, renders message list + input
- [ ] `apps/web/app/chat/page.tsx`: render `<ChatUI />`
- [ ] `apps/web/.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [ ] Streaming works end-to-end in browser (multi-turn conversation)

**Deliverable:** Local browser chat working, streaming visible, conversation history maintained.

### Wed (Day 3) — Deploy + Ship (4 hrs)

- [ ] Deploy `apps/api/` to Railway — set `ANTHROPIC_API_KEY` env var, set CORS to Vercel domain
- [ ] Deploy `apps/web/` to Vercel — set `NEXT_PUBLIC_API_URL` to Railway URL
- [ ] Smoke test live URL with 5 questions
- [ ] Take screenshot/gif for content

**Deliverable:** **🚀 First PROD URL live.** Generic chat working end-to-end.

### 📝 Slice 1 Content (Wednesday evening, 1 hr)

This isn't a long-form article — it's a **short post + teaser**. The long-form comes on Saturday after slice 2 has started.

- [ ] Update LinkedIn headline: *"Building agentic AI for high-stakes domains | Forward Deployed Engineer | Sydney"*
- [ ] **Short post #1 (Wed evening):** *"Day 3 update: shipped a generic Claude chat app to PROD. Now the real work starts — turning this into a grounded AI assistant for Australian tax info. Building in public over the next 4 weeks. [URL]"* — include a 10-sec gif.
- [ ] Update LinkedIn profile featured section: pin the live URL

---

## ⛳ SLICE 2: ATO RAG v1 — Start (Days 4-7)

Same repo. Same deployment. Swap the brain.

### Thu (Day 4) — Set up scraping infra (4 hrs)

- [ ] Set up Supabase project, enable pgvector extension
- [ ] Add `SUPABASE_URL`, `SUPABASE_KEY`, `VOYAGE_API_KEY` (or `OPENAI_API_KEY`) to `.env.example`
- [ ] Read `ato.gov.au/robots.txt`, document allowed paths in `SCRAPE_NOTES.md`
- [ ] **Define a tiny target list — just 30-50 pages.** Resist the urge to scrape more. Focus on:
  - Tax-free threshold + individual tax rates 2024-25
  - Key tax dates / deadlines
  - Medicare levy basics
  - HELP/HECS repayment threshold table
  - Top 5-10 individual deduction categories (work-related, donations, etc.)
- [ ] Save target URLs in `packages/scraper/target_urls.txt`

**Why tiny:** Slice 2 is about proving the RAG loop works end-to-end. A 30-page corpus you understand deeply beats a 300-page corpus you've never read. Expansion is week 2 work.

### Fri (Day 5) — Scrape + chunk + embed (4 hrs)

- [ ] `packages/scraper/scrape.py`: async scraper with `httpx`, 1 req/sec, descriptive User-Agent
- [ ] Use `trafilatura` for content extraction
- [ ] Schema:
  ```sql
  create table ato_pages (
    id uuid primary key default gen_random_uuid(),
    url text unique not null,
    raw_html text not null,
    markdown text not null,
    title text,
    last_modified timestamptz,
    scraped_at timestamptz default now()
  );

  create table ato_chunks (
    id uuid primary key default gen_random_uuid(),
    page_id uuid references ato_pages(id),
    parent_section text,
    chunk_text text not null,
    chunk_index int not null,
    heading_path text[],
    embedding vector(1024),
    created_at timestamptz default now()
  );

  create index on ato_chunks using ivfflat (embedding vector_cosine_ops);
  ```
- [ ] `packages/scraper/chunk.py`: semantic chunking ~500 tokens, 50-token overlap, parent-doc retrieval setup
- [ ] `packages/scraper/embed.py`: batch embed with Voyage `voyage-3-large`
- [ ] Run scrape → chunk → embed pipeline. Sanity check: 5 test queries on retrieval quality.

**Deliverable:** 30-50 ATO pages scraped and queryable via embedding similarity.

### Sat (Day 6) — Wire RAG into existing graph + Article #1 (5 hrs)

- [ ] Add `packages/agent/nodes/retriever.py`: top-k=5 with parent-document expansion
- [ ] Update `graph.py`: insert `retrieve` node before `generate`
- [ ] Update `prompts/generator.md`: citation contract
  > Every factual claim in your answer MUST have a citation marker in square brackets, e.g. [1]. The marker references a chunk from the retrieved context. Do not include claims that aren't directly supported by the retrieved context. If the context doesn't contain the answer, say so explicitly.
- [ ] Update Pydantic output:
  ```python
  class Citation(BaseModel):
      marker: int
      url: str
      snippet: str
      heading_path: list[str]

  class AgentResponse(BaseModel):
      answer: str  # contains [1], [2] markers
      citations: list[Citation]
  ```
- [ ] Update frontend: render citations as clickable footnotes with hover preview
- [ ] Add disclaimer banner: *"This tool provides information from ATO public documents. It is not tax advice. Consult a registered tax agent."*
- [ ] Test 10 ATO questions live, fix obvious issues

**Article #1 (Saturday 7am Sydney):** *"From a blank repo to live PROD in 3 days — and what I'm building next"*
- ~800 words
- Cover: the slice strategy, what was hard about deploying (not the AI), what's coming
- Live URL prominently linked
- See `CONTENT_PLAN.md` for full outline

### Sun (Day 7) — Polish + Week 1 retro (1 hr)

- [ ] Verify citations actually render correctly on mobile
- [ ] Fix any obvious bugs
- [ ] Write Week 1 retro in `SESSION_LOG.md`:
  1. Slice 1 ship: how long did deployment actually take? What surprised you?
  2. Slice 2 quality: are retrieval results good on 30 pages? What's missing?
  3. Biggest unknown going into Week 2?

---

## Week 1 success criteria

- [ ] Live PROD URL by Wed evening (generic chat)
- [ ] ATO RAG v1 wired and answering with citations by Sunday
- [ ] Article #1 published Saturday morning
- [ ] 2-3 short posts published during the week
- [ ] LinkedIn profile updated (headline, featured URL)
