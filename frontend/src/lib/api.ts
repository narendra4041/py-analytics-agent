import type {
  AgentResult,
  ChatMessage,
  ChatSession,
} from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

const USER_ID =
  process.env.NEXT_PUBLIC_DEV_USER_ID ?? "narendra";

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "x-user-id": USER_ID,
      ...(options?.headers || {}),
    },
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json();
}

export async function getHealth() {
  return request<{ status: string }>("/health");
}

export async function getChats() {
  return request<ChatSession[]>("/chats");
}

export async function getMessages(chatId: string) {
  return request<ChatMessage[]>(
    `/chats/${chatId}/messages`
  );
}

export async function sendAgentMessage(
  chatId: string,
  message: string
) {
  return request<{
    chat_id: string;
    intent: string;
    result: AgentResult;
    execution_error: string | null;
  }>("/agent/chat", {
    method: "POST",
    body: JSON.stringify({
      chat_id: chatId,
      message,
    }),
  });
}

export async function getCatalogs() {
  return request<{
    catalogs: string[];
  }>("/databricks/catalogs");
}


export async function getSchemas(
  catalog: string
) {
  return request<{
    catalog: string;
    schemas: string[];
  }>(
    `/databricks/schemas?catalog=${catalog}`
  );
}


export async function createChat(
  title: string,
  catalog: string,
  schema: string
) {
  return request<ChatSession>(
    "/chats",
    {
      method: "POST",
      body: JSON.stringify({
        title,
        catalog,
        schema,
      }),
    }
  );
}