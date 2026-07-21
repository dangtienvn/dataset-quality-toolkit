import React from "react";

export const StreamingMessage: React.FC<{ text: string; isStreaming: boolean }> = ({ text, isStreaming }) => (
  <div className="p-4 rounded-lg bg-secondary text-secondary-foreground leading-relaxed">
    {text}
    {isStreaming && <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse" />}
  </div>
);
