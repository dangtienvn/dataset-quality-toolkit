"use client";

import { FormEvent, useRef, useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import AuthGuard from "@/components/AuthGuard";
import api from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

function ThinkingDots() {
  return (
    <div className="flex items-start gap-3 max-w-3xl">
      <div className="bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-3">
        <span className="text-sm text-gray-400 dot-animation">
          AI is thinking
          <span className="inline-block w-1">.</span>
          <span className="inline-block w-1">.</span>
          <span className="inline-block w-1">.</span>
        </span>
      </div>
    </div>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg: Message = { role: "user", content: input.trim() };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput("");
    setLoading(true);

    try {
      const res = await api.post("/api/v1/ai/chat", {
        messages: updated.map((m) => ({ role: m.role, content: m.content })),
      });
      setMessages([...updated, { role: "assistant", content: res.data.content }]);
    } catch {
      setMessages([
        ...updated,
        { role: "assistant", content: "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthGuard>
      <div className="flex flex-col h-screen bg-gray-950">
        <Navbar />
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <aside className="hidden lg:flex flex-col w-72 border-r border-gray-800 p-4">
            <h2 className="text-sm font-semibold text-gray-400 mb-4">Chat Sessions</h2>
            <div className="flex-1 space-y-2">
              <div className="px-3 py-2 rounded-xl bg-gray-800/50 border border-gray-700 text-sm">
                Current Chat
              </div>
              <p className="text-xs text-gray-600 px-3 pt-2">More sessions coming soon</p>
            </div>
          </aside>

          {/* Chat area */}
          <div className="flex-1 flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
              {messages.length === 0 && !loading && (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <p className="text-4xl mb-4">🤖</p>
                    <p className="text-gray-400">Start a conversation with AI</p>
                    <p className="text-sm text-gray-600 mt-1">
                      Type a message below to begin
                    </p>
                  </div>
                </div>
              )}
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-2xl px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                      msg.role === "user"
                        ? "bg-gradient-to-r from-violet-600 to-indigo-600 rounded-tr-sm"
                        : "bg-gray-800 text-gray-200 rounded-tl-sm"
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              {loading && <ThinkingDots />}
              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <form
              onSubmit={handleSend}
              className="border-t border-gray-800 px-6 py-4 flex gap-3"
            >
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend(e);
                  }
                }}
                placeholder="Type your message..."
                rows={1}
                className="flex-1 resize-none px-4 py-2.5 rounded-xl border border-gray-700 bg-gray-800 text-white placeholder-gray-500 focus:outline-none focus:border-violet-500 transition-colors"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-6 py-2.5 rounded-xl font-semibold bg-gradient-to-r from-violet-600 to-indigo-600 hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                Send
              </button>
            </form>
          </div>
        </div>
      </div>
    </AuthGuard>
  );
}
