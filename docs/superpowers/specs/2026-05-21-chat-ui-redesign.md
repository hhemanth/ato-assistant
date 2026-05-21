# ATO Assistant — Chat UI Redesign Spec

**Date:** 2026-05-21  
**Scope:** Visual redesign of `apps/web` before first deployment. No backend changes.  
**Files affected:** `apps/web/components/chat-ui.tsx`, `apps/web/app/layout.tsx`, `apps/web/app/globals.css`, `apps/web/app/chat/page.tsx`

---

## Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Visual direction | Official & Trustworthy | Navy + gold signals authority; appropriate for tax information |
| Layout | Sidebar + Chat | Dark nav sidebar, main chat panel; suits repeat users and topic navigation |
| Message style | Q&A Document | Full-width alternating rows; formal, easy to scan, reinforces credibility |

---

## Colour Palette

| Token | Hex | Usage |
|---|---|---|
| `navy-deep` | `#001f45` | Sidebar background |
| `navy` | `#003366` | Header, YOU label, accents, citation markers |
| `navy-mid` | `#004d99` | Sidebar hover states |
| `gold` | `#FFD700` | ATO pill label background, logo accent |
| `page-bg` | `#f0f4f8` | Outer page background |
| `chat-bg` | `#ffffff` | Chat panel background |
| `user-row` | `#f7f9fc` | User message row background |
| `border` | `#d0dae8` | Row dividers, input borders |
| `disclaimer-bg` | `#fef9e7` | Disclaimer strip background |
| `disclaimer-border` | `#f5d87a` | Disclaimer strip border |

---

## Typography

- **Font:** Inter (loaded via `next/font/google`) — clean, professional, widely readable
- **Body:** 14–15px, `text-gray-900` on white backgrounds
- **Labels (YOU / ATO):** 10px, `font-semibold`, uppercase, letter-spacing
- **Citations:** 12px, `text-navy`, displayed below assistant turn

---

## Layout Structure

```
┌─────────────────────────────────────────────────┐
│  Sidebar (220px, navy-deep)  │  Chat Panel       │
│  ─────────────────────────   │  ───────────────  │
│  [Logo] ATO ASSISTANT        │  [Disclaimer]     │
│                              │  ─────────────    │
│  TOPICS                      │  [Message rows]   │
│  › Tax Rates                 │                   │
│  › Deductions                │                   │
│  › Medicare                  │                   │
│  › HELP/HECS                 │                   │
│                              │                   │
│  [+ New chat]                │  [Input bar]      │
└─────────────────────────────────────────────────┘
```

### Sidebar
- Width: 220px, fixed, `bg-[#001f45]`
- Top: logo mark (gold square) + "ATO ASSISTANT" wordmark in white, `text-xs font-semibold tracking-widest`
- Topic links: `text-[#7fa8cc]`, active state `bg-[#002a5c]`, hover `bg-[#002a5c]/60`
- "New chat" button pinned to bottom, `text-[#7fa8cc]` with `+` prefix
- Mobile: hidden by default, toggled via hamburger button in chat header

### Chat Panel
- Takes remaining width, `bg-white`
- Top: slim disclaimer strip (`bg-[#fef9e7] border-b border-[#f5d87a]`), full width, text: *"This tool provides information from ATO public documents. It is not tax advice. Consult a registered tax agent."*
- Below disclaimer: scrollable message list, fills remaining height
- Bottom: sticky input bar

---

## Message Rendering — Q&A Document Style

Each exchange is a pair of full-width rows separated by a `border-b border-[#d0dae8]`.

### User row
- Background: `bg-[#f7f9fc]`
- Layout: `YOU` pill (`bg-[#e0eaf5] text-[#003366] text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded`) + message text
- Padding: `px-6 py-4`

### Assistant row
- Background: `bg-white`
- Left accent: `border-l-4 border-[#003366]` (applied to inner content wrapper, not the full row)
- Layout: `ATO` pill (`bg-[#003366] text-[#FFD700] text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded`) + answer text + citations
- Citations: rendered below the answer as a `<footer>` block, `text-xs text-[#6b7fa3]`, each line `[N] url`
- Inline citation markers: `[1]` in `text-[#003366] font-semibold`
- Streaming: animated blinking cursor (`animate-pulse`) appended to last text node while `streaming === true`
- Padding: `px-6 py-4`

---

## Empty State

Shown when `messages.length === 0`:

- Centered vertically in chat area
- Heading: "What would you like to know about Australian tax?" in `text-xl font-semibold text-[#003366]`
- Subtext: "Ask anything about individual tax — rates, deductions, Medicare, HELP/HECS." in `text-sm text-gray-500`
- 4 suggested question chips, clicking pre-fills the input:
  1. "What is the tax-free threshold for 2024–25?"
  2. "How do I claim work-from-home deductions?"
  3. "What is the Medicare levy?"
  4. "When is the tax return deadline?"
- Chips: `border border-[#d0dae8] rounded-full px-4 py-2 text-sm text-[#003366] hover:bg-[#f0f4f8] cursor-pointer`

---

## Input Bar

- Sticky to bottom of chat panel, `bg-white border-t border-[#d0dae8] px-6 py-3`
- `<textarea>` (single-line, grows to 3 lines max), `rounded-lg border border-[#d0dae8] focus:ring-2 focus:ring-[#003366]`, placeholder "Ask about Australian tax…"
- Send button: `bg-[#003366] text-white rounded-lg px-5 py-2 text-sm font-medium hover:bg-[#004d99] disabled:opacity-40`
- Submit on Enter (Shift+Enter for newline), disabled while streaming

---

## Mobile Behaviour

- Sidebar hidden (`hidden md:flex`) on `< md` breakpoint
- Hamburger icon (`☰`) shown in a slim top bar on mobile, toggles sidebar via `useState`
- Sidebar overlays chat on mobile (`fixed inset-y-0 left-0 z-50`)
- Tap outside sidebar to close

---

## Component Structure

Refactor `chat-ui.tsx` into focused sub-components:

| Component | Responsibility |
|---|---|
| `<Sidebar>` | Nav links, new chat button, mobile toggle |
| `<DisclaimerBanner>` | Static disclaimer strip |
| `<MessageList>` | Scrollable list of message rows |
| `<UserRow>` | Single user message |
| `<AssistantRow>` | Single assistant message + citations (citations is `string[] \| undefined`; renders nothing in Slice 1) |
| `<EmptyState>` | Welcome heading + suggestion chips |
| `<InputBar>` | Textarea + send button |
| `<ChatUI>` (root) | State, layout shell, composes all above |

Each component lives in `apps/web/components/chat/` and is re-exported from `apps/web/components/chat/index.ts`.

---

## Out of Scope

- No changes to `apps/api/`
- No Vercel AI SDK — existing fetch + streaming approach is kept
- No conversation persistence (Slice 2+)
- No dark mode toggle (Slice 3+)
- No citation rendering (citations exist in Slice 2; the `AssistantRow` component leaves a `citations` prop slot that renders nothing in Slice 1)
