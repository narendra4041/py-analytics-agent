export type ChatSession = {
  id: string;
  user_id: string;
  title: string;
  catalog: string;
  schema: string;
  created_at: string;
};

export type AgentResult =
  | {
      type: "text";
      summary: string;
    }
  | {
      type: "table";
      summary: string;
      columns: string[];
      rows: Record<string, string>[];
    }
  | {
      type: "chart";
      summary: string;
      chart_url: string;
    };

export type ChatMessage = {
  id: string;
  chat_id: string;
  user_id: string;
  role: "user" | "assistant";
  content: string | AgentResult;
  created_at: string;
};