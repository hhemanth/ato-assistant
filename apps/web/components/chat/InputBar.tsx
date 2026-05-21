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
