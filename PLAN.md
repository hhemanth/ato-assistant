# ATO Assistant — 4-Week Build Plan (v2: Three-Slice Approach)

**Project:** A trustworthy AI assistant for Australian Taxation Office (ATO) information. Built in three vertical slices: ship a generic chat app first, evolve it into a grounded RAG agent, then expand into the full multi-surface assistant with eval harness.

**Positioning:** Building AI you can actually trust in regulated domains — and the eval systems that prove it works.

**Time budget:** ~22-24 hrs/week × 4 weeks = ~90 hrs total.

**Definition of "done" for PROD:** Public URL on Vercel, no auth required for demo, basic rate limiting, disclaimer banner present (from slice 2 onwards).

---

## Why three slices

The original plan built everything horizontally (scrape → chunk → embed → agent → UI → deploy) before anything was live. The slice approach ships vertically: a thin working product on day 3, then thicker products on day 10 and day 28.

**Slice 1 — Generic Chat (Days 1-3):** Plain Claude chat app, deployed. Zero AI complexity, all deployment plumbing.
**Slice 2 — ATO RAG v1 (Days 4-10):** Same app, brain swapped to RAG over ~30-50 ATO pages with citations.
**Slice 3 — Full ATO Assistant (Days 11-28):** Routing, calculator tool, voice, eval harness, citation verification, public dashboard, phone (stretch).

**Risk reduction:** Deployment pain is resolved on day 2 with a trivial app. RAG quality is resolved on day 8 with a tiny corpus. By the time you tackle the complex week 3-4 work, the foundation is rock-solid.

**Same repo throughout.** The git history *is* part of the portfolio — it shows iteration from prototype to production, which is the FDE muscle.

---

## Architecture (final state at end of week 4)

```
┌─────────────────────────────────────────────────────────────┐
│                     User Surfaces                            │
│   ┌──────────┐   ┌──────────────┐   ┌─────────────────┐    │
│   │  /chat   │   │   /voice     │   │  Twilio Phone   │    │
│   │  (text)  │   │  (web mic)   │   │   (stretch)     │    │
│   └────┬─────┘   └──────┬───────┘   └────────┬────────┘    │
│        │                │                     │              │
│        └────────────────┼─────────────────────┘              │
│                         ▼                                     │
│              ┌─────────────────────┐                          │
│              │   LangGraph Agent   │                          │
│              │  Router → Retrieve  │                          │
│              │  → Calculate → Gen  │                          │
│              │  → Verify Citations │                          │
│              └──────────┬──────────┘                          │
│                         ▼                                     │
│              ┌─────────────────────┐                          │
│              │   Langfuse Traces   │                          │
│              └─────────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │
              ┌───────────┴────────────┐
              │   Eval Harness         │
              │   (60 golden Qs +      │
              │    Ragas + custom)     │
              └───────────┬────────────┘
                          ▼
              /evals (public lite dashboard)
              /evals/admin (full, basic auth)
```

But you build it in this order:

```
Slice 1 (Days 1-3):   [/chat] → [Claude Sonnet] → [Langfuse]
Slice 2 (Days 4-10):  [/chat] → [Retrieve → Generate] → [Langfuse]    + 30-50 ATO pages
Slice 3 (Days 11-28): [/chat, /voice, /phone] → [Router → Retrieve → Calc → Gen → Verify] → [Langfuse + Evals]
```

---

## Tech Stack

| Layer | Choice | Introduced in |
|---|---|---|
| LLM (generation) | Claude Sonnet 4.6 via Anthropic API | Slice 1 |
| Frontend | Next.js 14 (App Router) + Vercel AI SDK | Slice 1 |
| Hosting | Vercel | Slice 1 |
| Observability | Langfuse Cloud | Slice 1 |
| Agent orchestration | LangGraph (Python) | Slice 2 |
| Embeddings | Voyage `voyage-3-large` (fallback: OpenAI `text-embedding-3-large`) | Slice 2 |
| Vector DB | Postgres + pgvector (Supabase) | Slice 2 |
| Scraping | `httpx` + `trafilatura` | Slice 2 |
| Backend host | Railway or Render | Slice 2 |
| LLM (eval judge) | Claude Opus 4.7 | Slice 3 |
| STT (voice) | Deepgram Nova-3 (fallback: Whisper) | Slice 3 |
| TTS (voice) | ElevenLabs Turbo v2.5 (fallback: OpenAI TTS) | Slice 3 |
| Phone (stretch) | Twilio Programmable Voice + Media Streams | Slice 3 |
| Eval metrics | Ragas + custom Python | Slice 3 |
| Rate limiting | Upstash Redis | Slice 3 |

---

## Repo Structure (final — grown incrementally)

```
ato-assistant/
├── PLAN.md                          # This file
├── CLAUDE.md                        # Claude Code instructions
├── README.md                        # Public-facing
├── SESSION_LOG.md                   # Running session notes
├── .env.example
├── pyproject.toml
├── package.json
│
├── apps/
│   └── web/                         # Next.js — created in Slice 1
│       ├── app/
│       │   ├── chat/page.tsx        # Slice 1
│       │   ├── voice/page.tsx       # Slice 3
│       │   ├── evals/page.tsx       # Slice 3 (public lite)
│       │   └── evals/admin/page.tsx # Slice 3 (basic auth)
│       └── components/
│
├── packages/
│   ├── agent/                       # Created in Slice 1 (minimal), evolves through Slice 3
│   │   ├── graph.py                 # Slice 1: just generate. Slice 2: + retrieve. Slice 3: + router + verify
│   │   ├── nodes/
│   │   │   ├── generator.py         # Slice 1
│   │   │   ├── retriever.py         # Slice 2
│   │   │   ├── router.py            # Slice 3
│   │   │   └── verifier.py          # Slice 3
│   │   ├── tools/
│   │   │   └── tax_calculator.py    # Slice 3
│   │   └── prompts/
│   │
│   ├── scraper/                     # Created in Slice 2
│   │   ├── scrape.py
│   │   ├── chunk.py
│   │   └── embed.py
│   │
│   ├── voice/                       # Created in Slice 3
│   │   ├── stt.py
│   │   └── tts.py
│   │
│   └── evals/                       # Created in Slice 3
│       ├── golden_dataset.jsonl
│       ├── runner.py
│       └── metrics/
│
└── infra/
    ├── supabase/migrations/         # Slice 2
    └── twilio/                      # Slice 3 stretch
```

---

## Hard Rules (DO NOT VIOLATE)

These apply from the slice they're introduced onwards:

**From Slice 1:**
1. **Every LLM call traced to Langfuse.** Even the trivial slice 1 chat. Build the discipline early.
2. **Pydantic models for all structured I/O.** No freeform JSON parsing.
3. **Prompts live in `.md` files**, not Python strings.

**From Slice 2:**
4. **No claim without a citation.** Every factual statement must reference a real chunk.
5. **Disclaimer banner is non-negotiable.** *"This tool provides information from ATO public documents. It is not tax advice. Consult a registered tax agent."*
6. **Respect ato.gov.au:** robots.txt-compliant, 1 req/sec max, User-Agent identifies you with contact email.

**From Slice 3:**
7. **Refuse personalized tax advice.** Factual rule + redirect to a registered tax agent.
8. **Citation verifier strips unverified claims.** Not optional.
9. **Eval judge model ≠ generator model.** Opus 4.7 judges Sonnet 4.6.
10. **Never log full user queries to public dashboards.** Anonymize.

---

## Success Criteria (end of week 4)

- [ ] Slice 1 live by Day 3 (Wed of Week 1)
- [ ] Slice 2 live by Day 10 (Wed of Week 2)
- [ ] Slice 3 mostly complete by Day 28 (Sunday of Week 4)
- [ ] Public URL with working chat, voice, and (stretch) phone
- [ ] 60-question golden eval dataset, hand-curated
- [ ] Public eval dashboard at /evals showing pass rates ≥ 80% overall, ≥ 90% on refusals
- [ ] 4 LinkedIn long-form articles published
- [ ] ~18 short LinkedIn posts published
- [ ] GitHub repo public with README, architecture diagram, deploy instructions
- [ ] Loom walkthrough video pinned to LinkedIn profile
- [ ] LinkedIn headline updated to FDE positioning

See `WEEK_1.md` through `WEEK_4.md` for day-by-day tasks.
See `CLAUDE.md` for Claude Code working instructions.
See `CONTENT_PLAN.md` for the LinkedIn schedule.
See `SETUP.md` for Day-0 environment setup.
