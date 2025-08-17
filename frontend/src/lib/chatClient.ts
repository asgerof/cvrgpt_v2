import { ChatRequest, ChatResponse } from "@/types/chat";

const API = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "dev-key";

export async function postChat(req: ChatRequest): Promise<ChatResponse> {
  const r = await fetch(`${API}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify(req),
  });
  if (!r.ok) throw new Error(`Chat failed: ${r.status}`);
  return r.json();
}

export async function exportCsv(thread_id: string): Promise<Blob> {
  const r = await fetch(`${API}/chat/export?thread_id=${encodeURIComponent(thread_id)}`, {
    headers: { "X-API-Key": API_KEY },
  });
  if (!r.ok) throw new Error("Export failed");
  return r.blob();
}
