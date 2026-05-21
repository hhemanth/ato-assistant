# Chat UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the ATO Assistant chat UI with a navy+gold official aesthetic, dark sidebar navigation, and Q&A document-style message rendering.

**Architecture:** Decompose the existing monolithic `chat-ui.tsx` into focused sub-components in `apps/web/components/chat/`. Each component has one responsibility. `ChatUI` (root) owns all state and composes the rest. No backend changes.

**Tech Stack:** Next.js 15, React 19, Tailwind CSS 3, TypeScript, `next/font/google` (Inter)

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `apps/web/tailwind.config.ts` | Add custom color tokens |
| Modify | `apps/web/app/layout.tsx` | Load Inter font, set page-bg on body |
| Create | `apps/web/components/chat/types.ts` | Shared `Message` type |
| Create | `apps/web/components/chat/DisclaimerBanner.tsx` | Static disclaimer strip |
| Create | `apps/web/components/chat/UserRow.tsx` | User message row |
| Create | `apps/web/components/chat/AssistantRow.tsx` | Assistant row + streaming cursor + citations slot |
| Create | `apps/web/components/chat/EmptyState.tsx` | Welcome heading + suggestion chips |
| Create | `apps/web/components/chat/InputBar.tsx` | Auto-resize textarea + send button |
| Create | `apps/web/components/chat/MessageList.tsx` | Scrollable list of message rows |
| Create | `apps/web/components/chat/Sidebar.tsx` | Dark nav sidebar with mobile overlay |
| Create | `apps/web/components/chat/index.ts` | Barrel re-exports |
| Rewrite | `apps/web/components/chat-ui.tsx` | Root: state + layout shell |

---

### Task 1: Tailwind custom colours + Inter font

**Files:**
- Modify: `apps/web/tailwind.config.ts`
- Modify: `apps/web/app/layout.tsx`

- [ ] **Step 1: Replace tailwind.config.ts with custom color tokens**

```ts
// apps/web/tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          deep: "#001f45",
          DEFAULT: "#003366",
          mid: "#004d99",
          light: "#e0eaf5",
        },
        gold: "#FFD700",
        "page-bg": "#f0f4f8",
        "user-row": "#f7f9fc",
        "chat-border": "#d0dae8",
        "disclaimer-bg": "#fef9e7",
        "disclaimer-border": "#f5d87a",
      },
    },
  },
  plugins: [],
};
export default config;
```

- [ ] **Step 2: Update layout.tsx to load Inter and apply page background**

```tsx
// apps/web/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ATO Assistant",
  description: "AI assistant for Australian Taxation Office information",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${inter.className} bg-page-bg text-gray-900 antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add apps/web/tailwind.config.ts apps/web/app/layout.tsx
git commit -m "style: add navy/gold tailwind tokens and Inter font"
```

---

### Task 2: Shared types

**Files:**
- Create: `apps/web/components/chat/types.ts`

- [ ] **Step 1: Create the shared Message type**

```ts
// apps/web/components/chat/types.ts
export interface Message {
  role: "user" | "assistant";
  content: string;
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/web/components/chat/types.ts
git commit -m "feat: add shared Message type for chat components"
```

---

### Task 3: DisclaimerBanner

**Files:**
- Create: `apps/web/components/chat/DisclaimerBanner.tsx`

- [ ] **Step 1: Create DisclaimerBanner**

```tsx
// apps/web/components/chat/DisclaimerBanner.tsx
export default function DisclaimerBanner() {
  return (
    <div className="bg-disclaimer-bg border-b border-disclaimer-border px-6 py-2 text-xs text-amber-800 flex-shrink-0">
      ⚠ This tool provides information from ATO public documents. It is not tax
      advice. Consult a registered tax agent.
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/web/components/chat/DisclaimerBanner.tsx
git commit -m "feat: add DisclaimerBanner component"
```

---

### Task 4: UserRow

**Files:**
- Create: `apps/web/components/chat/UserRow.tsx`

- [ ] **Step 1: Create UserRow**

```tsx
// apps/web/components/chat/UserRow.tsx
interface UserRowProps {
  content: string;
}

export default function UserRow({ content }: UserRowProps) {
  return (
    <div className="bg-user-row border-b border-chat-border px-6 py-4 flex gap-3 items-start">
      <span className="bg-navy-light text-navy text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded flex-shrink-0 mt-0.5">
        You
      </span>
      <p className="text-sm text-gray-900 leading-relaxed whitespace-pre-wrap">
        {content}
      </p>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/web/components/chat/UserRow.tsx
git commit -m "feat: add UserRow component"
```

---

### Task 5: AssistantRow

**Files:**
- Create: `apps/web/components/chat/AssistantRow.tsx`

- [ ] **Step 1: Create AssistantRow**

`citations` is `string[] | undefined` — renders nothing in Slice 1, populated in Slice 2.

```tsx
// apps/web/components/chat/AssistantRow.tsx
interface AssistantRowProps {
  content: string;
  citations?: string[];
  isStreaming?: boolean;
}

export default function AssistantRow({
  content,
  citations,
  isStreaming = false,
}: AssistantRowProps) {
  return (
    <div className="bg-white border-b border-chat-border px-6 py-4 flex gap-3 items-start">
      <span className="bg-navy text-gold text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded flex-shrink-0 mt-0.5">
        ATO
      </span>
      <div className="flex-1 min-w-0">
        <div className="border-l-4 border-navy pl-3">
          <p className="text-sm text-gray-900 leading-relaxed whitespace-pre-wrap">
            {content}
            {isStreaming && (
              <span className="inline-block w-1.5 h-4 ml-0.5 bg-navy animate-pulse align-middle" />
            )}
          </p>
          {citations && citations.length > 0 && (
            <footer className="mt-3 pt-3 border-t border-chat-border">
              {citations.map((url, i) => (
                <p key={i} className="text-xs text-[#6b7fa3]">
                  [{i + 1}]{" "}
                  <a
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:underline"
                  >
                    {url}
                  </a>
                </p>
              ))}
            </footer>
          )}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/web/components/chat/AssistantRow.tsx
git commit -m "feat: add AssistantRow with streaming cursor and citations slot"
```

---

### Task 6: EmptyState

**Files:**
- Create: `apps/web/components/chat/EmptyState.tsx`

- [ ] **Step 1: Create EmptyState**

```tsx
// apps/web/components/chat/EmptyState.tsx
const SUGGESTIONS = [
  "What is the tax-free threshold for 2024–25?",
  "How do I claim work-from-home deductions?",
  "What is the Medicare levy?",
  "When is the tax return deadline?",
];

interface EmptyStateProps {
  onSuggestionClick: (text: string) => void;
}

export default function EmptyState({ onSuggestionClick }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center flex-1 px-6 py-16 text-center">
      <h2 className="text-xl font-semibold text-navy mb-2">
        What would you like to know about Australian tax?
      </h2>
      <p className="text-sm text-gray-500 mb-8">
        Ask anything about individual tax — rates, deductions, Medicare,
        HELP/HECS.
      </p>
      <div className="flex flex-wrap gap-2 justify-center max-w-lg">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => onSuggestionClick(s)}
            className="border border-chat-border rounded-full px-4 py-2 text-sm text-navy hover:bg-page-bg cursor-pointer transition-colors"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/web/components/chat/EmptyState.tsx
git commit -m "feat: add EmptyState with suggestion chips"
```

---

### Task 7: InputBar

**Files:**
- Create: `apps/web/components/chat/InputBar.tsx`

- [ ] **Step 1: Create InputBar**

Textarea auto-resizes on input (max 96px ≈ 3 lines). Enter submits; Shift+Enter inserts a newline.

```tsx
// apps/web/components/chat/InputBar.tsx
import { useRef, type FormEvent, type KeyboardEvent } from "react";

interface InputBarProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled: boolean;
}

export default function InputBar({
  value,
  onChange,
  onSubmit,
  disabled,
}: InputBarProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function handleInput() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 96)}px`;
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!disabled && value.trim()) onSubmit();
    }
  }

  return (
    <div className="bg-white border-t border-chat-border px-6 py-3 flex-shrink-0">
      <form
        onSubmit={(e: FormEvent) => {
          e.preventDefault();
          if (!disabled && value.trim()) onSubmit();
        }}
        className="flex gap-3 items-end"
      >
        <textarea
          ref={textareaRef}
          rows={1}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onInput={handleInput}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Ask about Australian tax…"
          className="flex-1 resize-none overflow-hidden rounded-lg border border-chat-border px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-navy disabled:bg-gray-50 leading-relaxed"
          style={{ minHeight: "40px", maxHeight: "96px" }}
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="bg-navy text-white rounded-lg px-5 py-2 text-sm font-medium hover:bg-navy-mid disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex-shrink-0"
        >
          Send
        </button>
      </form>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/web/components/chat/InputBar.tsx
git commit -m "feat: add InputBar with auto-resize textarea and Enter-to-submit"
```

---

### Task 8: MessageList

**Files:**
- Create: `apps/web/components/chat/MessageList.tsx`

- [ ] **Step 1: Create MessageList**

```tsx
// apps/web/components/chat/MessageList.tsx
import { useEffect, useRef } from "react";
import type { Message } from "./types";
import UserRow from "./UserRow";
import AssistantRow from "./AssistantRow";

interface MessageListProps {
  messages: Message[];
  streaming: boolean;
}

export default function MessageList({ messages, streaming }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto">
      {messages.map((msg, i) =>
        msg.role === "user" ? (
          <UserRow key={i} content={msg.content} />
        ) : (
          <AssistantRow
            key={i}
            content={msg.content}
            isStreaming={streaming && i === messages.length - 1}
          />
        )
      )}
      <div ref={bottomRef} />
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/web/components/chat/MessageList.tsx
git commit -m "feat: add MessageList component"
```

---

### Task 9: Sidebar

**Files:**
- Create: `apps/web/components/chat/Sidebar.tsx`

- [ ] **Step 1: Create Sidebar**

On mobile, the sidebar slides in from the left over a dark backdrop; clicking the backdrop closes it. On `md+` screens the sidebar is always visible and `position: relative`.

```tsx
// apps/web/components/chat/Sidebar.tsx
const TOPICS = [
  { label: "Tax Rates" },
  { label: "Deductions" },
  { label: "Medicare" },
  { label: "HELP / HECS" },
];

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  onNewChat: () => void;
}

export default function Sidebar({ open, onClose, onNewChat }: SidebarProps) {
  return (
    <>
      {/* Mobile backdrop */}
      {open && (
        <div
          className="fixed inset-0 bg-black/40 z-40 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-50 w-[220px] bg-navy-deep flex flex-col
          transition-transform duration-200
          ${open ? "translate-x-0" : "-translate-x-full"}
          md:relative md:translate-x-0 md:flex
        `}
      >
        {/* Logo */}
        <div className="px-5 py-5 flex items-center gap-3 border-b border-white/10">
          <div className="w-5 h-5 bg-gold rounded flex-shrink-0" />
          <span className="text-white text-xs font-semibold tracking-widest uppercase">
            ATO Assistant
          </span>
        </div>

        {/* Topics */}
        <nav className="flex-1 px-3 py-4">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-gold/60 px-2 mb-2">
            Topics
          </p>
          {TOPICS.map((t) => (
            <button
              key={t.label}
              className="w-full text-left px-3 py-2 rounded text-sm text-[#7fa8cc] hover:bg-navy-mid/40 transition-colors"
            >
              {t.label}
            </button>
          ))}
        </nav>

        {/* New chat */}
        <div className="px-3 py-4 border-t border-white/10">
          <button
            onClick={onNewChat}
            className="w-full text-left px-3 py-2 rounded text-sm text-[#7fa8cc] hover:bg-navy-mid/40 transition-colors"
          >
            + New chat
          </button>
        </div>
      </aside>
    </>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/web/components/chat/Sidebar.tsx
git commit -m "feat: add Sidebar with topic links and mobile overlay"
```

---

### Task 10: Barrel export + ChatUI root

**Files:**
- Create: `apps/web/components/chat/index.ts`
- Rewrite: `apps/web/components/chat-ui.tsx`

- [ ] **Step 1: Create barrel export**

```ts
// apps/web/components/chat/index.ts
export { default as Sidebar } from "./Sidebar";
export { default as DisclaimerBanner } from "./DisclaimerBanner";
export { default as MessageList } from "./MessageList";
export { default as UserRow } from "./UserRow";
export { default as AssistantRow } from "./AssistantRow";
export { default as EmptyState } from "./EmptyState";
export { default as InputBar } from "./InputBar";
export type { Message } from "./types";
```

- [ ] **Step 2: Rewrite chat-ui.tsx**

```tsx
// apps/web/components/chat-ui.tsx
"use client";

import { useState } from "react";
import {
  Sidebar,
  DisclaimerBanner,
  MessageList,
  EmptyState,
  InputBar,
} from "./chat";
import type { Message } from "./chat";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function ChatUI() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  function clearChat() {
    setMessages([]);
    setInput("");
  }

  async function sendMessage() {
    const text = input.trim();
    if (!text || streaming) return;

    const userMessage: Message = { role: "user", content: text };
    const nextMessages = [...messages, userMessage];
    setMessages([...nextMessages, { role: "assistant", content: "" }]);
    setInput("");
    setStreaming(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: nextMessages }),
      });

      if (!res.ok || !res.body) throw new Error(`API error: ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content: updated[updated.length - 1].content + chunk,
          };
          return updated;
        });
      }
    } catch {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
        };
        return updated;
      });
    } finally {
      setStreaming(false);
    }
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onNewChat={clearChat}
      />

      {/* Chat panel */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Mobile header bar */}
        <div className="md:hidden flex items-center gap-3 px-4 py-3 bg-navy border-b border-navy-mid flex-shrink-0">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-white text-xl leading-none"
            aria-label="Open menu"
          >
            ☰
          </button>
          <span className="text-white text-sm font-semibold tracking-widest uppercase">
            ATO Assistant
          </span>
        </div>

        <DisclaimerBanner />

        {messages.length === 0 ? (
          <EmptyState onSuggestionClick={(text) => setInput(text)} />
        ) : (
          <MessageList messages={messages} streaming={streaming} />
        )}

        <InputBar
          value={input}
          onChange={setInput}
          onSubmit={sendMessage}
          disabled={streaming}
        />
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add apps/web/components/chat/ apps/web/components/chat-ui.tsx
git commit -m "feat: wire up ChatUI root with sidebar, messages, and input"
```

---

### Task 11: Visual QA

**Files:** None changed in this task.

- [ ] **Step 1: Start the backend**

```bash
cd apps/api && uv run uvicorn main:app --reload
```

Expected: `Uvicorn running on http://127.0.0.1:8000`

- [ ] **Step 2: Start the frontend**

```bash
cd apps/web && npm run dev
```

Expected: `▲ Next.js 15.x.x  Local: http://localhost:3000`

- [ ] **Step 3: Open http://localhost:3000/chat and run through the checklist**

| Check | Expected |
|---|---|
| Page background | Light blue-gray (`#f0f4f8`) |
| Sidebar | Visible on desktop, dark navy, gold square logo, 4 topic links |
| Disclaimer strip | Amber background, correct text |
| Empty state | Navy heading + 4 chip buttons |
| Chip click | Pre-fills textarea, empty state still shows |
| Type + Enter | Message sent, transitions to Q&A rows |
| User row | Light blue-gray background, `You` navy pill |
| Assistant row | White background, navy left border, `ATO` gold-on-navy pill |
| Streaming | Navy blinking cursor on last assistant row |
| Auto-scroll | Chat scrolls to bottom as tokens arrive |
| Textarea grows | Grows up to ~3 lines then stops |
| Shift+Enter | Inserts newline instead of submitting |
| New chat | Clears all messages, returns to empty state |
| Hamburger (narrow window) | `< 768px`: sidebar hidden, ☰ visible in navy top bar |
| Sidebar open/close | Tap ☰ → slides in with dark backdrop; tap backdrop → closes |
| Inter font | Verify in DevTools → Elements → Computed → font-family |

- [ ] **Step 4: Fix any visual issues and commit**

```bash
git add -p
git commit -m "fix: visual QA corrections from local review"
```
