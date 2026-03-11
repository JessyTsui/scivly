import { apiRequest } from "@/lib/api/client";
import type { ChatMessageOut, PaginatedResponse } from "@/lib/api/types";

export interface ChatSessionOut {
  id: string;
  workspace_id: string;
  paper_id: string | null;
  session_type: "paper_qa" | "digest_qa" | "general";
  title: string;
  created_at: string;
}

interface ChatReplyOut {
  assistant_message: ChatMessageOut;
  cited_paper_ids: string[];
  session: ChatSessionOut;
  user_message: ChatMessageOut;
}

export async function listChatSessions() {
  const response = await apiRequest<PaginatedResponse<ChatSessionOut>>("/chat/sessions", {
    query: { per_page: 100 },
  });
  return response.items;
}

export async function createPaperChatSession(input: {
  paperId: string;
  title: string;
  workspaceId: string;
}) {
  return apiRequest<ChatSessionOut>("/chat/sessions", {
    method: "POST",
    body: {
      workspace_id: input.workspaceId,
      paper_id: input.paperId,
      session_type: "paper_qa",
      title: input.title,
    },
  });
}

export async function getChatHistory(sessionId: string) {
  const response = await apiRequest<PaginatedResponse<ChatMessageOut>>(
    `/chat/sessions/${sessionId}/messages`,
    {
      query: { per_page: 100 },
    }
  );
  return response.items;
}

export async function sendChatMessage(input: { content: string; sessionId: string }) {
  return apiRequest<ChatReplyOut>(`/chat/sessions/${input.sessionId}/messages`, {
    method: "POST",
    body: { content: input.content },
  });
}
