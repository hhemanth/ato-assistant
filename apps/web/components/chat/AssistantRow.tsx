"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import JudgePanel from "./JudgePanel";

interface JudgeScores {
  helpfulness: number;
  correctness: number;
  coherence: number;
}

interface AssistantRowProps {
  content: string;
  query: string;
  isStreaming?: boolean;
}

const JUDGE_RE = /\n?__JUDGE__(\{.*?\})__/;

function parseContent(raw: string): { text: string; scores: JudgeScores | null } {
  const match = raw.match(JUDGE_RE);
  if (!match) return { text: raw, scores: null };
  try {
    return { text: raw.replace(JUDGE_RE, "").trimEnd(), scores: JSON.parse(match[1]) };
  } catch {
    return { text: raw.replace(JUDGE_RE, "").trimEnd(), scores: null };
  }
}

export default function AssistantRow({
  content,
  query,
  isStreaming = false,
}: AssistantRowProps) {
  const [reported, setReported] = useState(false);
  const { text, scores } = parseContent(content);

  async function handleReport() {
    if (reported) return;
    try {
      await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_query: query, response: text }),
      });
    } finally {
      setReported(true);
    }
  }

  return (
    <div className="bg-white border-b border-chat-border px-4 md:px-6 py-4 flex gap-3 items-start">
      <span className="bg-navy text-gold text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded flex-shrink-0 mt-0.5">
        ATO
      </span>
      <div className="flex-1 min-w-0">
        <div className="border-l-4 border-navy pl-3 overflow-x-auto">
          <div className="text-sm text-gray-900 leading-relaxed prose prose-sm max-w-none
            prose-headings:font-semibold prose-headings:text-navy prose-headings:mt-4 prose-headings:mb-1
            prose-h2:text-base prose-h3:text-sm
            prose-p:my-1.5
            prose-a:text-navy prose-a:underline hover:prose-a:text-navy-mid
            prose-strong:text-gray-900
            prose-blockquote:border-l-2 prose-blockquote:border-amber-400 prose-blockquote:pl-3 prose-blockquote:text-gray-600 prose-blockquote:not-italic
            prose-table:text-xs prose-table:w-full
            prose-th:bg-gray-50 prose-th:px-3 prose-th:py-2 prose-th:text-left prose-th:font-semibold prose-th:border prose-th:border-gray-200
            prose-td:px-3 prose-td:py-2 prose-td:border prose-td:border-gray-200
            prose-ul:my-1.5 prose-li:my-0.5
            prose-code:bg-gray-100 prose-code:px-1 prose-code:rounded prose-code:text-xs">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
            {isStreaming && (
              <span className="inline-block w-1.5 h-4 ml-0.5 bg-navy animate-pulse align-middle" />
            )}
          </div>
        </div>

        {!isStreaming && scores && <JudgePanel scores={scores} />}

        {!isStreaming && text && (
          <div className="mt-2 pl-3">
            <button
              onClick={handleReport}
              disabled={reported}
              className="text-xs text-gray-400 hover:text-red-500 disabled:text-gray-300 disabled:cursor-default transition-colors"
            >
              {reported ? "✓ Reported" : "Report incorrect answer"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
