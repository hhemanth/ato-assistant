"use client";

import { useState } from "react";

interface JudgeScores {
  helpfulness: number;
  correctness: number;
  coherence: number;
}

interface JudgePanelProps {
  scores: JudgeScores;
}

function barColor(score: number): string {
  if (score >= 0.75) return "bg-green-500";
  if (score >= 0.50) return "bg-amber-400";
  return "bg-red-400";
}

const LABELS: [keyof JudgeScores, string][] = [
  ["helpfulness", "Helpfulness"],
  ["correctness", "Correctness"],
  ["coherence", "Coherence"],
];

export default function JudgePanel({ scores }: JudgePanelProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className="mt-3 ml-3 border border-gray-100 rounded-lg text-xs overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-3 py-2 text-gray-400 hover:text-gray-500 hover:bg-gray-50 transition-colors"
      >
        <span className="font-medium">Answer quality</span>
        <span className="text-[10px]">{open ? "▴" : "▾"}</span>
      </button>

      {open && (
        <div className="px-3 pb-3 space-y-2 border-t border-gray-100 pt-2">
          {LABELS.map(([key, label]) => {
            const pct = Math.round(scores[key] * 100);
            return (
              <div key={key} className="flex items-center gap-2">
                <span className="w-20 text-gray-400 shrink-0">{label}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full transition-all ${barColor(scores[key])}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span className="w-7 text-right text-gray-400 tabular-nums">{pct}%</span>
              </div>
            );
          })}
          <p className="text-[10px] text-gray-300 pt-1">Powered by Nemotron 4 340B</p>
        </div>
      )}
    </div>
  );
}
