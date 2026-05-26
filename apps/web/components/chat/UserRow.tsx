interface UserRowProps {
  content: string;
}

export default function UserRow({ content }: UserRowProps) {
  return (
    <div className="bg-user-row border-b border-chat-border px-4 md:px-6 py-4 flex gap-3 items-start">
      <span className="bg-navy-light text-navy text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded flex-shrink-0 mt-0.5">
        You
      </span>
      <p className="text-sm text-gray-900 leading-relaxed whitespace-pre-wrap break-words min-w-0">
        {content}
      </p>
    </div>
  );
}
