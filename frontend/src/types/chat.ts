export type Role = "user" | "assistant" | "tool";

export type TextBlock = { type: "text"; text: string };
export type CardBlock = { type: "card"; title: string; kv: Record<string,string> };
export type TableBlock = { type: "table"; caption?: string; columns: string[]; rows: string[][]; footnote?: string };
export type ChoiceItem = { id: string; label: string; description?: string };
export type ChoiceBlock = { type: "choice"; prompt: string; choices: ChoiceItem[] };

export type ChatBlock = TextBlock | CardBlock | TableBlock | ChoiceBlock;

export type ChatMessage = { role: Role; content: string };

export type ChatRequest = {
  thread_id?: string | null;
  messages: ChatMessage[];
  cvr?: string | null;
  years?: number[] | null;
};

export type ChatResponse = {
  thread_id: string;
  blocks: ChatBlock[];
};
