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

const API_URL = "/api";

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
