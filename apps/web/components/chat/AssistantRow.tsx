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
