# Day-0 Setup (do this before Week 1 Monday)

~2 hours of setup BEFORE the 4-week clock starts. Not part of the 90-hour budget.

The setup is grouped by slice — you only NEED slice 1 accounts before Monday. The slice 2 and 3 accounts can wait until you reach those slices, but it's cleaner to do them all up front.

---

## 🎯 Required for Slice 1 (do before Monday Day 1)

- [ ] **GitHub** — create repo `ato-assistant` (public from day 1 — show your work)
- [ ] **Anthropic API** — get API key with credits
- [ ] **Langfuse Cloud** — sign up, new project, get public + secret keys
- [ ] **Vercel** — connect to GitHub, ready to deploy
- [ ] **Railway** or **Render** — for FastAPI backend (free tier)

## 🎯 Required for Slice 2 (do before Thursday Day 4 — or all up front)

- [ ] **Supabase** — new project, note URL + anon + service_role keys, enable pgvector
- [ ] **Voyage AI** — sign up, get API key (or use OpenAI for embeddings as fallback)

## 🎯 Required for Slice 3 (do before Day 17)

- [ ] **Deepgram** — sign up for STT (free credits)
- [ ] **ElevenLabs** — sign up for TTS (free tier)
- [ ] **Upstash Redis** — free tier for rate limiting
- [ ] **Twilio** (stretch) — only if going for phone number in week 4

---

## Local environment

- [ ] Python 3.11+ installed
- [ ] `uv` installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Node.js 20+ installed
- [ ] `pnpm` (preferred for monorepo) or `npm`
- [ ] Claude Code installed and logged in
- [ ] `gh` CLI for GitHub
- [ ] Postgres client (`psql`) for Supabase debugging

---

## Repo bootstrap

- [ ] Clone the empty `ato-assistant` repo locally
- [ ] Copy these 8 markdown files into the repo root:
  - `PLAN.md`
  - `CLAUDE.md`
  - `WEEK_1.md` through `WEEK_4.md`
  - `CONTENT_PLAN.md`
  - `SETUP.md` (this file)
- [ ] Initial commit: *"chore: scaffold project plan and Claude Code instructions"*
- [ ] Push to GitHub
- [ ] Open the repo in Claude Code
- [ ] Test: ask Claude Code *"Read CLAUDE.md and PLAN.md. What are we building, and what slice are we starting with?"* — verify it picks up context and correctly identifies Slice 1

---

## Verify before starting Week 1

- [ ] `uv` commands work
- [ ] You can deploy hello-world to Vercel
- [ ] You can call Anthropic API from a local Python script
- [ ] Langfuse trace appears when you make an instrumented Anthropic call
- [ ] You have FastAPI deployed to Railway/Render (even just a `/health` endpoint)

If any of these fail, fix BEFORE Monday. Slice 1 is supposed to be **3 days** — setup friction will eat the whole window.

---

## First message to Claude Code on Monday morning

Copy-paste this:

> Read PLAN.md, CLAUDE.md, and WEEK_1.md. We're starting Slice 1 (Days 1-3) — generic chat app to PROD. NO RAG, NO routing, NO tools yet. Begin with Monday's tasks: scaffolding the repo (LangGraph minimal node, FastAPI service, Next.js frontend) and the first instrumented Anthropic call. Ask clarifying questions before writing code, especially on directory layout and any deviations from the structure in PLAN.md.

---

## Optional but recommended

- [ ] Set up a separate `ato-assistant-dev` Vercel project for previews (vs `ato-assistant-prod`)
- [ ] Enable Vercel password protection on previews so you don't accidentally ship something
- [ ] Create a `.cursorrules` or copy `CLAUDE.md` into Cursor settings if you also use Cursor
- [ ] Set up GitHub Actions secret store with all your API keys (you'll need them in Week 3 for nightly eval runs)
