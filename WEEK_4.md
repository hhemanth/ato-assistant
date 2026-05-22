# Week 4 — Iterate, Polish, Phone (stretch), Push for Inbound

**Goal:** Drive eval scores up, polish the demo, convert audience into recruiter conversations.

**Budget:** ~22 hours.

**End-of-week deliverable:** Eval score climbed measurably, Loom walkthrough live, "I'm available" article published, optional Twilio phone number live.

---

## Mon-Tue (Days 22-23) — Close the eval gaps (8 hrs)

### Goal: 80%+ overall, 90%+ on refusal correctness

- [ ] Review Week 3 failures by category. Pick **2-3 highest-impact improvements**:

  **If retrieval is the issue:**
  - Add reranking: Cohere `rerank-v3` or Voyage `rerank-2` on top of hybrid retrieval
  - Query rewriting: small Haiku call to rephrase ambiguous queries before retrieval
  - Better chunking for multi-hop questions (larger parent sections)

  **If generation is the issue:**
  - Stricter system prompt with concrete examples of good/bad citations
  - Self-check reasoning step before final answer
  - Higher top-k with reranking pruning

  **If refusal is the issue:**
  - Tune router prompt with more `personal_advice` examples
  - Add explicit refusal templates per common pattern

- [ ] **Re-run evals after EVERY change.** Document every change.
- [ ] Maintain `packages/evals/CHANGELOG.md`:
  ```markdown
  ## 2026-06-15 — Added Cohere reranking
  Before: 72% overall, 60% multi-hop
  After: 81% overall, 78% multi-hop
  Trade-off: +400ms p50 latency
  ```
- [ ] Publish the changelog to `/evals` public dashboard — this transparency is rare and signals seriousness

**Deliverable:** Eval score improved by ≥ 10 percentage points from week 3 baseline. Public changelog documents every change.

---

## Wed-Thu (Days 24-25) — Pick ONE: Phone OR Polish (8 hrs)

### Decision rule
- **On track + evals healthy → Phone (Option A, strongly recommended)**
- **Behind or evals messy → Polish (Option B)**

### Option A: Twilio phone number (recommended)

- [ ] Sign up for Twilio, buy an Australian local number (~$5/month + per-minute)
- [ ] `infra/twilio/voice_webhook.py`: FastAPI endpoint Twilio calls
- [ ] Use Twilio Media Streams (WebSocket) for real-time audio
- [ ] Pipe audio through same Deepgram → LangGraph → ElevenLabs pipeline as `/voice`
- [ ] Greeting: *"You've reached the ATO Assistant. This is an AI providing general tax information, not advice. How can I help you?"*
- [ ] Disclaimer audio plays at call start and whenever `personal_advice` is detected
- [ ] **Test thoroughly** — call yourself 20 times, hit edge cases
- [ ] Update LinkedIn headline: *"Call the demo: +61 X XXXX XXXX"*

### Option B: Polish

- [ ] Graceful degradation everywhere (retry logic, friendly error states)
- [ ] Share-able conversation links (UUIDs, public read-only view)
- [ ] 6-8 "example queries" on landing page to lower first-visit friction
- [ ] Proper landing page at `/`: problem → demo → architecture → eval results → CTA
- [ ] Mobile responsive check on all surfaces

**Deliverable:** Either a working phone number visible on LinkedIn, OR a substantially polished product.

---

## Fri (Day 26) — Final polish (3 hrs)

### Loom walkthrough video (the recruiter funnel)

- [ ] **Loom video, 3-5 mins, do 2-3 takes:**
  - 0:00 The problem (regulated domain, hallucinations dangerous)
  - 0:30 Demo text: factual question with citations
  - 1:00 Demo: calculation with breakdown
  - 1:30 Demo: refusal of personal advice
  - 2:00 Voice demo + phone demo (if Option A)
  - 3:00 Architecture diagram walkthrough
  - 3:30 Eval results — pass rate, what improved, public dashboard
  - 4:30 What you'd build next

- [ ] **Pin Loom to LinkedIn profile** as a featured post

### Public repo polish

- [ ] Clean README with:
  - Hero gif at top
  - Architecture diagram
  - Tech stack table
  - "Why I built this" — link to article #3
  - Live demo link, eval dashboard link, Loom link
  - Eval methodology summary
  - Local dev setup
- [ ] Run `gitleaks` (or similar) — verify no secrets leaked in history
- [ ] Verify `.env.example` is complete
- [ ] Add `LICENSE` (MIT)

**Deliverable:** Loom pinned, repo public and polished.

---

## Sat-Sun (Days 27-28) — Push for inbound (3 hrs)

### Article #4 — Recruiter-magnet (Saturday 7am Sydney)

*"What I learned shipping a 3-surface AI agent in 4 weeks: text, voice, phone, and the evals that keep it honest."*
- ~1500 words
- Retrospective + architecture deep-dive + explicit ask
- Ends with: *"I'm exploring Forward Deployed Engineer roles where I'd be shipping AI for regulated, high-stakes, or complex domains. If your team is building in that space, I'd love to talk. DMs open. Loom walkthrough pinned to my profile."*
- See `CONTENT_PLAN.md` for full outline

### Promote in 3 places

- [ ] LinkedIn organic — ask 5 friends to engage in first hour
- [ ] r/LocalLLaMA or r/MachineLearning if relevant (be careful of self-promo rules)
- [ ] Hacker News (Show HN) — only if you have something genuinely novel; the eval harness might qualify

### Direct outreach (10 messages)

Don't apply through portals. Find the engineering lead or hiring manager on LinkedIn, send a short DM linking to demo + Loom. Companies to consider:

- **Vertical AI startups:** Harvey, Hebbia, Sierra, Decagon, Crew AI
- **AI infra:** Anthropic FDE team, LangChain, Anthropic itself
- **Australian consultancies:** Mantel Group, Eliiza, Max Kelsen
- **Australian fintech (regulated AI):** Athena, Up, Airwallex, Tyro

### Final week content cadence

- **Mon:** Short post — Eval improvement, before/after chart
- **Tue:** Short post — **PHONE NUMBER announcement** (if Option A) — biggest-engagement post of the 4 weeks
- **Wed:** Short post — Final architecture diagram
- **Thu:** Short post — Loom video drop
- **Fri:** Short post — README walkthrough
- **Sat:** Article #4 (recruiter ask)
- **Sun:** Thank-you post naming 3-5 specific people who engaged most

---

## Week 4 retrospective

1. Final eval score per category — which moved most?
2. What inbound have you received? (DMs, comments, recruiter messages)
3. What's the natural week 5-8 extension if you wanted to keep building?
4. Three things you'd tell yourself if starting over?

---

## Done. Now what?

**If you're getting inbound but not enough:**
- Keep posting short updates 2x/week
- Add an evaluation case study every 2 weeks (eval a public AI product, write it up)
- Apply directly to FDE roles using this as the portfolio anchor

**If you're not getting inbound:**
- Re-evaluate LinkedIn distribution — are posts getting reach? Is your network too narrow?
- Cross-post: X/Twitter, YouTube (turn Loom into proper video)
- Cold outreach is highest-ROI — you have the artifact, use it
