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
      {messages.map((msg, i) => {
        if (msg.role === "user") {
          return <UserRow key={i} content={msg.content} />;
        }
        const precedingQuery =
          messages.slice(0, i).findLast((m) => m.role === "user")?.content ?? "";
        return (
          <AssistantRow
            key={i}
            content={msg.content}
            query={precedingQuery}
            isStreaming={streaming && i === messages.length - 1}
          />
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
}
