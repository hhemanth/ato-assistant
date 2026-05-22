# Instructions for Claude Code

You are helping build the **ATO Assistant** — a trustworthy AI assistant for Australian Taxation Office information. Built in **three vertical slices** (generic chat → ATO RAG → full assistant) over 4 weeks.

Read `PLAN.md` for architecture and `WEEK_N.md` for the current week's tasks. The plan files are the source of truth.

## How to work with me

1. **Check the current week file first** (`WEEK_1.md`, `WEEK_2.md`, etc.) before starting work. Tasks are ordered intentionally.
2. **Understand which slice we're in.** Don't introduce slice-3 complexity (routing, eval harness) into slice-1 code. Each slice is intentionally minimal until it isn't.
3. **Update the week file's task checkboxes** as you complete items. Commit after each completed task with a clear, conventional commit message.
4. **Surface trade-offs proactively.** If you see a better approach than what the plan specifies, raise it before implementing. Don't silently deviate.
5. **Ship working > perfect.** Especially in slice 1 — the goal is a live URL, not elegant code. We refactor in slice 2 when we know what's stable.
6. **Write tests for anything touching citations or eval logic** (slice 2 onwards). These are the trust layer.

## The slice principle

**Slice 1 (Days 1-3):** Generic chat. NO RAG, NO routing, NO tools. Just Claude → UI. The goal is to nail deployment and observability.

**Slice 2 (Days 4-10):** Add RAG over ~30-50 ATO pages. NO router, NO calculator, NO voice. Just retrieve + generate with citations.

**Slice 3 (Days 11-28):** Add router, calculator, voice, citation verifier, eval harness, public dashboard, phone (stretch).

If I ask you to add a slice-3 thing during slice 1 or 2, **push back** and remind me of the slice principle. The point of slicing is to ship early; complexity creep kills that.

## Hard constraints (from slice they're introduced)

**Slice 1+:**
- Python 3.11+ with `uv` for package management
- Type hints required on all function signatures
- Every LLM call traced to Langfuse
- Pydantic for all structured I/O
- Prompts in `.md` files, loaded at import

**Slice 2+:**
- No claim without a citation
- Disclaimer banner present on every page
- Scrape ato.gov.au respectfully: robots.txt, 1 req/sec, User-Agent with contact email

**Slice 3+:**
- Refuse personalized tax advice
- Citation verifier active
- Eval judge model ≠ generator model (Opus 4.7 judges Sonnet 4.6)

## Code style

- **Single-responsibility nodes.** Each LangGraph node does one thing. If a node grows past ~50 lines, split it.
- **Structured outputs** via Pydantic, not freeform JSON parsing.
- **Errors are values.** Wrap LLM/tool calls in result types. Don't swallow exceptions.
- **Log to Langfuse on every node.** Use `@observe`.
- **Never commit `.env`, API keys, or scraped raw HTML.**

## When you finish a session

End each session by:
1. Committing all changes with a descriptive conventional commit message
2. Updating the current `WEEK_N.md` checkbox status
3. Writing a brief entry in `SESSION_LOG.md`: what got done, what's blocked, what's next, what slice we're in

## Questions to ask me, not assume

- Whether to add a new dependency (especially LLM/eval-related)
- Whether to change the eval golden dataset structure
- Whether to deploy a breaking change to the live URL
- Whether prompts touching refusal logic should change
- Whether we're ready to graduate from one slice to the next (don't assume — ask)

## Things I want you to push back on

- If I ask for a feature that compromises citation integrity → push back
- If I ask to skip eval coverage for new logic → push back
- If I ask to remove the disclaimer banner → push back
- If I ask to scrape faster than 1 req/sec → push back
- If I try to add slice-3 complexity during slice 1 or 2 → push back, remind me of the slice principle
