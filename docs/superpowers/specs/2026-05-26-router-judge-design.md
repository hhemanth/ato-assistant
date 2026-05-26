# Router + LLM-as-Judge Design

**Date:** 2026-05-26
**Slice:** 3 (Day 11)
**Goal:** Classify every query into one of four categories before responding, and evaluate answer quality using a reward model after generation.

---

## Architecture Overview

Two separate LangGraph graphs with clear responsibilities:

```
POST /chat
  ↓
Phase 1 — router_graph.ainvoke({query, messages})
  ↓
router_node (Haiku 4.5, ~150ms)
  → {category, confidence, reasoning}
  ↓
chat.py matches category, streams response, buffers tokens:
  "factual"         → _rag_stream()      (existing, unchanged)
  "personal_advice" → _refusal_stream()  (new)
  "out_of_scope"    → _redirect_stream() (new)
  "calculation"     → placeholder text   (Day 12 calculator slots in here)
  ↓
Phase 2 — judge_graph.ainvoke({query, response}) [async, non-blocking]
  ↓
judge_node (Nemotron 4 340B via NVIDIA NIM)
  → {helpfulness, correctness, coherence} scores (0.0–1.0)
  → log all scores to LangSmith
  → yield __JUDGE__{...}__ sentinel as final stream chunk
  → if avg score < 0.6 → also yield low-confidence note before sentinel
```

### Two Graphs

| Graph | File | Nodes | Purpose |
|-------|------|-------|---------|
| `router_graph` | `graph.py` | `START → router → END` | Classify query |
| `judge_graph` | `judge_graph.py` | `START → judge → END` | Score response |

Both graphs share `AgentState` but only use the fields relevant to their phase.

---

## New Package: `packages/agent/`

```
packages/agent/
  pyproject.toml   — depends on: langgraph, anthropic, openai, pydantic, langsmith
  state.py         — AgentState TypedDict (shared by both graphs)
  graph.py         — router graph: START → router → END
  judge_graph.py   — judge graph:  START → judge  → END
  nodes/
    router.py      — Haiku 4.5 classification → RoutingDecision
    judge.py       — Nemotron 4 340B reward scores via NVIDIA NIM
  prompts/
    router.md      — system + 2 few-shot examples × 4 categories
```

Added to the existing `uv` workspace (`pyproject.toml` `[tool.uv.workspace]` members).

`apps/api/pyproject.toml` must also add `ato-agent` as a workspace dependency so `chat.py` can import from `packages/agent`.

### `state.py`

```python
class AgentState(TypedDict):
    messages: list[dict]          # [{role, content}, ...]
    query: str
    category: str | None          # factual | calculation | personal_advice | out_of_scope
    confidence: float | None
    reasoning: str | None
```

### `graph.py` — router graph

```
START → router_node → END
```

Conditional edges for calculator (Day 12) and verifier (Day 14) slot in without touching router_node.

```python
def build_router_graph() -> CompiledGraph:
    g = StateGraph(AgentState)
    g.add_node("router", router_node)
    g.add_edge(START, "router")
    g.add_edge("router", END)
    return g.compile()

router_graph = build_router_graph()
```

### `judge_graph.py` — judge graph

```
START → judge_node → END
```

```python
def build_judge_graph() -> CompiledGraph:
    g = StateGraph(AgentState)
    g.add_node("judge", judge_node)
    g.add_edge(START, "judge")
    g.add_edge("judge", END)
    return g.compile()

judge_graph = build_judge_graph()
```

### `nodes/router.py`

**Model:** `claude-haiku-4-5-20251001`
**Output format:** Structured JSON via Anthropic tool use or direct JSON response

```python
class RoutingDecision(BaseModel):
    category: Literal["factual", "calculation", "personal_advice", "out_of_scope"]
    confidence: float   # 0.0–1.0
    reasoning: str      # one sentence, used in LangSmith traces

async def router_node(state: AgentState) -> AgentState:
    ...
    return {"category": ..., "confidence": ..., "reasoning": ...}
```

**Prompt:** loaded from `packages/agent/prompts/router.md`
- System: role description + output format
- 2 few-shot examples per category (8 total)
- Categories and decision rules:
  - `factual` — asks for ATO information, rates, rules, deadlines, definitions
  - `calculation` — wants a number computed ("how much tax do I pay on $X")
  - `personal_advice` — asks what they personally should do ("should I claim X?")
  - `out_of_scope` — non-ATO topic, adversarial, or clearly off-topic

### `nodes/judge.py`

**Model:** `nvidia/nemotron-4-340b-reward` via NVIDIA NIM
**Client:** `openai.AsyncOpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY)`

```python
class JudgeScores(BaseModel):
    helpfulness: float    # 0.0–1.0
    correctness: float    # 0.0–1.0
    coherence: float      # 0.0–1.0

async def judge(query: str, response: str) -> JudgeScores:
    ...
```

Nemotron reward model input: `[{"role": "user", "content": query}, {"role": "assistant", "content": response}]`
Scores extracted from response logprobs.

**Threshold:** average score < 0.6 triggers low-confidence note.

---

## Updated `apps/api/routes/chat.py`

1. Import and invoke `packages/agent` graph
2. Stream based on category
3. Buffer tokens while streaming
4. After stream: fire `judge()` async, yield sentinel

### Sentinel format

```
__JUDGE__{"helpfulness":0.82,"correctness":0.91,"coherence":0.87}__
```

Appended as the final yielded chunk. Frontend strips it from display text.

### Low-confidence note (if avg < 0.6)

```
> ⚠️ Note: I may not have full ATO coverage on this — check [ato.gov.au](https://ato.gov.au) directly.
```

Yielded before the sentinel.

---

## New Prompt Files in `apps/api/prompts/`

### `refusal.md`

Structured refusal that:
1. Explains why personalised advice can't be given
2. States the relevant general ATO rule (from context if available)
3. Directs to a registered tax agent

### `out_of_scope.md`

Polite redirect that:
1. Notes the question is outside the assistant's scope
2. Names what it does cover (individual tax, deductions, super, CGT, GST)
3. Suggests ato.gov.au for other queries

---

## Frontend Changes

### `apps/web/components/chat/AssistantRow.tsx`

- As each chunk arrives, check for `__JUDGE__{...}__` sentinel
- If found: strip from display text, parse JSON scores, store in local state
- Pass scores to `JudgePanel`

### `apps/web/components/chat/JudgePanel.tsx` (new)

```
┌─────────────────────────────────────────────┐
│ Answer quality  ▾                           │
│                                             │
│  Helpfulness  ████████░░  82%               │
│  Correctness  █████████░  91%               │
│  Coherence    ████████░░  87%               │
│                                             │
│  Powered by Nemotron 4 340B                 │
└─────────────────────────────────────────────┘
```

- Collapsed by default
- Expands on click (toggle)
- Only renders after stream completes (scores !== null)
- Bar colours: green ≥ 0.75, amber 0.50–0.75, red < 0.50
- Tailwind only, no new dependencies

---

## New Environment Variable

`NVIDIA_API_KEY` — required by `judge.py`. Add to `.env`, Railway, and Vercel.

---

## Tests

`packages/agent/tests/test_router.py`

20 queries (5 per category), each calls `router_node` directly:
- Assert `decision.category == expected`
- Assert `decision.confidence >= 0.7`
- Target: ≥ 90% accuracy (18/20 correct)

---

## Future Graph Nodes (not today)

| Day | Addition |
|-----|----------|
| 12  | `calculator_node` + conditional edge `calculation → calculator → END` |
| 14  | `verifier_node` after generator, checks citation markers |
