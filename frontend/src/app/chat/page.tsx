"use client";

import { useState, useRef, useEffect } from "react";
import { ChatBlock, ChatMessage } from "@/types/chat";
import { postChat, exportCsv } from "@/lib/chatClient";
import { downloadCSV } from "../../lib/csv";

function BlockRenderer({
  block,
  onExport,
  threadId,
  onChoiceSelect
}: {
  block: ChatBlock;
  onExport: () => void;
  threadId: string;
  onChoiceSelect: (cvr: string) => void;
}) {
  if (block.type === "text") {
    let className = "my-2";
    if (block.emphasis === "warning") {
      className += " text-amber-600 bg-amber-50 border border-amber-200 rounded p-2";
    } else if (block.subtle) {
      className += " text-gray-500 text-sm";
    } else {
      className += " text-gray-800";
    }
    return <p className={className}>{block.text}</p>;
  }

  if (block.type === "chips") {
    return (
      <div className="my-3">
        <div className="flex flex-wrap gap-2">
          {block.items.map((chip, i) => (
            <span
              key={i}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 border border-blue-200"
            >
              {chip.label}
            </span>
          ))}
        </div>
      </div>
    );
  }

  if (block.type === "card") {
    const entries = Object.entries(block.kv).filter(([_, v]) => v && v.length);
    return (
      <div className="border border-gray-200 rounded-xl p-4 my-3 bg-white shadow-sm">
        <div className="font-semibold mb-2 text-gray-900">{block.title}</div>
        <dl className="grid grid-cols-2 gap-2">
          {entries.map(([k, v]) => (
            <div key={k}>
              <dt className="text-sm text-gray-500">{k}</dt>
              <dd className="font-medium text-gray-900">{v}</dd>
            </div>
          ))}
        </dl>
      </div>
    );
  }

  if (block.type === "table") {
    return (
      <div className="border border-gray-200 rounded-xl p-4 my-3 bg-white shadow-sm">
        {block.caption && <div className="font-semibold mb-2 text-gray-900">{block.caption}</div>}
        <div className="overflow-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                {block.columns.map(c => (
                  <th key={c} className="text-left p-2 font-medium text-gray-900">{c}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {block.rows.map((row, i) => (
                <tr key={i} className="border-t border-gray-100">
                  {row.map((cell, j) => (
                    <td key={j} className="p-2 text-gray-700">{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {block.footnote && <div className="text-xs text-gray-500 mt-2">{block.footnote}</div>}
        <div className="mt-3">
          <button
            onClick={() => downloadCSV(block.columns, block.rows, "events.csv")}
            className="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50 transition-colors"
          >
            Download CSV
          </button>
        </div>
      </div>
    );
  }

  if (block.type === "choice") {
    return (
      <div className="border border-gray-200 rounded-xl p-4 my-3 bg-white shadow-sm">
        <div className="font-semibold mb-3 text-gray-900">{block.prompt}</div>
        <ul className="space-y-2">
          {block.choices.map(ch => (
            <li key={ch.id} className="flex items-center justify-between p-2 border border-gray-100 rounded hover:bg-gray-50">
              <div>
                <div className="font-medium text-gray-900">{ch.label}</div>
                {ch.description && <div className="text-sm text-gray-500">{ch.description}</div>}
              </div>
              <button
                className="px-3 py-1 border border-blue-500 text-blue-500 rounded hover:bg-blue-50 transition-colors"
                onClick={() => onChoiceSelect(ch.id)}
              >
                Choose
              </button>
            </li>
          ))}
        </ul>
      </div>
    );
  }

  return null;
}

export default function ChatPage() {
  const [threadId, setThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [blocks, setBlocks] = useState<ChatBlock[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function send(text: string) {
    if (!text.trim() || loading) return;

    setLoading(true);
    setError(null);

    try {
      const newMessages = [...messages, { role: "user" as const, content: text }];
      const req = {
        thread_id: threadId,
        messages: newMessages
      };

      const res = await postChat(req);
      setThreadId(res.thread_id);
      setMessages([...newMessages, { role: "assistant" as const, content: "[blocks]" }]);
      setBlocks(res.blocks);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  }

  function onChoiceSelect(cvr: string) {
    send(cvr); // Forward CVR back to backend to lock context
  }

  async function onExport() {
    if (!threadId) return;

    try {
      const blob = await exportCsv(threadId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "export.csv";
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError("Export failed: " + (err instanceof Error ? err.message : "Unknown error"));
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const value = inputRef.current?.value?.trim();
    if (value) {
      send(value);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 min-h-[600px] flex flex-col">
          <div className="border-b border-gray-200 p-4">
            <h1 className="text-2xl font-bold text-gray-900">CVR Chat</h1>
            <p className="text-sm text-gray-600 mt-1">
              Ask about Danish companies using CVR numbers or names
            </p>
          </div>

          <div className="flex-1 p-4 space-y-4 overflow-y-auto">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <p className="text-red-800 text-sm">Error: {error}</p>
              </div>
            )}

            {blocks.length === 0 && !loading && (
              <div className="text-center py-8">
                <div className="text-gray-500 mb-4">
                  <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.955 8.955 0 01-2.126-.275c-.95-.297-2.057-.367-3.016.27-.681.45-1.54.919-2.378 1.092-1.302.269-2.22-.47-2.22-1.692 0-.52.211-1.06.474-1.526A8.001 8.001 0 013 12c0-4.418 3.582-8 8-8s8 3.582 8 8z" />
                  </svg>
                  Start a conversation
                </div>
                <p className="text-sm text-gray-400">
                  Try: "Revenue for Maersk 2023" or "12345678 profile"
                </p>
              </div>
            )}

            {blocks.map((block, i) => (
              <BlockRenderer
                key={i}
                block={block}
                onExport={onExport}
                threadId={threadId ?? ""}
                onChoiceSelect={onChoiceSelect}
              />
            ))}

            {loading && (
              <div className="flex items-center justify-center py-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                <span className="ml-2 text-gray-600">Processing...</span>
              </div>
            )}
          </div>

          <div className="border-t border-gray-200 p-4">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                ref={inputRef}
                data-testid="chat-input"
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder='Try: "recent bankruptcies in the IT sector (last 3 months)" or "What was the annual result of Demo IT ApS in 2022?"'
                disabled={loading}
              />
              <button
                type="submit"
                data-testid="chat-send"
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                disabled={loading}
              >
                Send
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
