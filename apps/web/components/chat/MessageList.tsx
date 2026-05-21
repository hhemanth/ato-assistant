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
