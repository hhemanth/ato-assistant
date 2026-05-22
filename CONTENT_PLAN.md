# Content Plan — LinkedIn (v2: slice-aware)

## Rules

- **Cadence:** Tue / Thu / Sat at 7-8am Sydney time
- **Every post has a visual** — screenshot, gif, video, or diagram. No pure text.
- **Long-form articles** publish on Saturdays
- **Every long-form ends with one clear question** to drive comments
- **Reply to every comment within 4 hours** for the first 24 hours after posting
- **Tag thoughtfully** — only people you legitimately reference, max 2-3 per post

---

## How articles map to slices

| Article | When | Slice State | Theme |
|---|---|---|---|
| #1 | Week 1 Sat | Slice 1 shipped, Slice 2 in progress | Shipping discipline + slice strategy |
| #2 | Week 2 Sat | Slice 2 shipped, Slice 3 starting | Adding grounding without breaking what works |
| #3 | Week 3 Sat | Eval harness running | **Signature piece** — evals + the embarrassing failure |
| #4 | Week 4 Sat | All slices done | Retrospective + recruiter ask |

The slice approach gives each article a natural shipping moment to anchor on. Article #1 isn't "I'm starting a project" — it's "I shipped in 3 days, here's what's next."

---

## Article Outlines

### Article 1 (Week 1 Sat, Day 6) — "From a blank repo to live PROD in 3 days — and what I'm building next"

**Length:** ~800 words

**Outline:**
1. **Hook:** "Most AI side projects die in week 2 because they front-load complexity. Mine is shipping to PROD on day 3 — deliberately boring, so I can spend the next 25 days making it *actually useful*."
2. **The slice strategy:** Why generic chat first → ATO RAG → full assistant. De-risking deployment before AI complexity.
3. **What's actually live today:** Plain Claude chat, deployed. Show the URL.
4. **What's coming this week:** Same app, but now grounded in ATO docs with verifiable citations. Tease the citation contract.
5. **The 4-week roadmap:** Three slices, the bigger vision (regulated-domain AI you can trust).
6. **CTA:** *"What's a question you'd want an AI tax assistant to handle? I'm building the eval set this week — your hard cases welcome."*

**Visuals:** Demo gif of generic chat, slice diagram (3 boxes), live URL screenshot.

---

### Article 2 (Week 2 Sat, Day 13) — "Day 10 update: I added grounding and citations to my chat app. Here's what changed."

**Length:** ~1000 words

**Outline:**
1. **Hook:** "Last week I shipped a generic Claude chat app in 3 days. This week I made it cite its sources. The product looks 95% the same. The trust profile is night and day."
2. **What changed under the hood:** Added retrieval + citation contract + disclaimer banner. Show the diff.
3. **Why parent-document retrieval beat naive chunking** — quick technical detail with example
4. **Why hybrid retrieval (BM25 + vectors) for regulated content** — embeddings alone miss the precise ATO terminology
5. **What I deliberately didn't add yet:** routing, calculator, voice — those come in slice 3. Discipline beats feature-creep.
6. **The 4 query types I'm about to support:** factual, calculation, personal_advice, out_of_scope. Why one LLM prompt can't cleanly handle all four.
7. **CTA:** *"What's a query type you've seen LLM products fail to route well? Curious what others have shipped."*

**Visuals:** Side-by-side answer screenshots (with/without citations), retrieval diagram, before/after of the same query.

---

### Article 3 (Week 3 Sat, Day 20) — SIGNATURE PIECE — "I built an AI assistant for Australian tax info. Then I built the eval system that grades it. Here's what 60% on my own benchmark taught me."

**Length:** ~1200 words. This is the one most likely to convert recruiter inbound. Spend 4+ hours.

**Outline:**
1. **Hook:** "I built what I thought was a careful AI assistant. Then I tested it against 60 hand-curated questions. It got 60%. Here's what I learned."
2. **Why most AI demos lie:** Cherry-picked examples, no systematic test, no failure analysis. FDE work is the opposite.
3. **The golden dataset:** 60 questions, 6 categories. Show 2-3 sample questions per category.
4. **The metrics that matter:** citation precision, refusal correctness, faithfulness, answer correctness. Why each, what they catch.
5. **First run results** — show scores by category, screenshots from the public dashboard.
6. **The worst failure** — most embarrassing one. Show the question, wrong answer, why it failed. *Honesty is the post's superpower.*
7. **What I'm fixing in week 4** — reranking, query rewriting, stricter refusal prompts.
8. **Why this matters for FDE work** — in regulated domains, shipping without evals is malpractice.
9. **CTA:** *"Eval dashboard is public: [URL]. What's the eval question I'm not asking?"*

**Visuals:** Dashboard screenshot, golden dataset sample, failure case screenshot, score-by-category chart.

**Tagging:** Ragas, Langfuse, Anthropic eval work, Hamel Husain's writing on evals — tag where legitimate.

---

### Article 4 (Week 4 Sat, Day 27) — RECRUITER ASK — "What I learned shipping a 3-surface AI agent in 4 weeks: text, voice, phone, and the evals that keep it honest"

**Length:** ~1500 words. Retrospective + architecture + ask.

**Outline:**
1. **Hook:** "4 weeks ago I had an idea and a blank repo. Today there's a live URL, a phone number you can call, and a public dashboard that grades the whole thing every night."
2. **The slice journey:** Day 3 ship, Day 10 ship, Day 28 ship. Why this de-risking pattern is exactly how FDE teams work with customers.
3. **What I shipped:** screenshots — chat, voice, phone (if Option A), eval harness, public dashboard.
4. **Architecture deep-dive:** LangGraph nodes, routing logic, verification flow, eval harness. Full Excalidraw diagram.
5. **The hardest part** — almost certainly the golden dataset curation. Talk honestly about how tedious it was and why it was worth it.
6. **What I'd do differently** — concrete, not platitudes.
7. **Numbers:** final eval scores, total LoC, latency, cost per query.
8. **What this taught me about FDE work:** meeting users where they are (voice + phone), evaluating rigorously, refusing scope when scope is dangerous.
9. **The ask:** *"I'm exploring Forward Deployed Engineer roles where I'd be shipping AI for regulated, high-stakes, or complex domains. If your team is building in that space, I'd love to talk. DMs open. Loom walkthrough pinned to my profile."*

**Visuals:** Hero image of all three surfaces, full architecture diagram, eval-over-time chart, embedded Loom.

---

## Short Post Bank (~18 posts over 4 weeks)

### Week 1 (3 posts)

- **Wed (Day 3, evening):** *"Day 3 update: shipped a generic Claude chat app to PROD. Now the real work starts — turning this into a grounded AI assistant for Australian tax info. Building in public over the next 4 weeks. [URL]"* — 10-sec gif of deployment + chat working
- **Thu (Day 4):** *"Scraping ATO public docs. 30 pages, not 30,000. Quality over quantity, especially in regulated domains. Here's the target list."* — screenshot of target_urls.txt
- **Sat (Day 6):** Article #1

### Week 2 (3-4 posts)

- **Tue (Day 9):** *"Hybrid retrieval = BM25 + embeddings. Here's why both, with an example."* — before/after retrieval result
- **Thu (Day 11):** *"Routing in LangGraph: how my agent decides what to do with each query."* — Excalidraw diagram
- **Sat (Day 13):** Article #2
- **Sun (Day 14):** *"Calculator demo: why LLMs shouldn't do tax math."* — 15-sec video of `$95k → tax breakdown`

### Week 3 (5 posts — highest-volume week)

- **Mon (Day 15):** *"Caught a hallucination today. My post-generation verifier stripped it. Here's the trace."* — screenshot
- **Wed (Day 17):** **Voice demo video** — biggest expected reach of the 4 weeks. Make it good.
- **Thu (Day 18):** *"60 questions, 6 categories. Why I hand-curated my own benchmark instead of using a public one."* — dataset sample
- **Fri (Day 19):** *"First eval run: 60%. Here's the public dashboard."* — screenshot + link
- **Sat (Day 20):** Article #3 (signature)

### Week 4 (5-6 posts)

- **Mon (Day 22):** *"Added Cohere reranking. Score jumped 9 points. Here's the trace and the trade-off."* — before/after chart
- **Tue (Day 23):** PHONE NUMBER announcement (if Option A) — short video calling it. **Highest-engagement single post of the 4 weeks if Option A goes well.**
- **Wed (Day 24):** Final architecture diagram (clean Excalidraw)
- **Thu (Day 25):** *"Loom walkthrough — 4 mins covers everything. Pinned to my profile."* — embedded video preview
- **Fri (Day 26):** *"Cleaning up the repo for public release. Here's how I structured the eval harness."* — repo screenshot
- **Sat (Day 27):** Article #4 (recruiter ask)
- **Sun (Day 28):** Thank-you post — mention 3-5 specific people who engaged most

---

## Engagement playbook

**For each post:**
1. Draft → wait 4 hours → re-read with fresh eyes → edit → post
2. Send link to 3-5 friends/colleagues in DMs in the first hour asking for thoughts (seeds engagement, doesn't manipulate)
3. Reply to every comment for first 24 hrs — substantive replies, not just thanks
4. If a comment is substantive, write a 4-6 sentence response — treat as mini-article

**For each long-form:**
- Post a teaser short post on Friday evening before publishing
- Cross-post body (with minor edits) to personal blog or Substack if you have one — owned audience matters long-term

---

## Anti-patterns to avoid

- ❌ "Just shipped X 🚀" with no substance
- ❌ Listicles ("10 things I learned about AI")
- ❌ Reposting other people's takes with one-line agreement
- ❌ Vague achievement humble-brags
- ❌ Engagement-bait questions ("agree?")
- ❌ AI-generated text that sounds like AI (use AI to outline, write final pass in your voice)

---

## Profile setup checklist (do this on Day 1)

- [ ] Headline: *"Building agentic AI for high-stakes domains | Forward Deployed Engineer | Sydney"*
- [ ] About section: 3 short paragraphs — what you build, what you believe about AI in production, what roles you want
- [ ] Featured section: pin live URL on Day 3, pin Loom on Day 26
- [ ] Open to Work badge: ON, set to *"Forward Deployed Engineer, AI Solutions Engineer, AI Engineer"* — visible to recruiters only
- [ ] Banner image: simple architecture diagram or demo screenshot (not generic stock photo)
