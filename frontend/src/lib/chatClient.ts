import { ChatRequest, ChatResponse } from "@/types/chat";

export async function postChat(req: ChatRequest): Promise<ChatResponse> {
  const r = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req),
  });
  if (!r.ok) throw new Error(`Chat failed: ${r.status}`);
  return r.json();
}

export async function exportCsv(thread_id: string): Promise<Blob> {
  const r = await fetch(`/api/chat/export?thread_id=${encodeURIComponent(thread_id)}`);
  if (!r.ok) throw new Error("Export failed");
  return r.blob();
}
