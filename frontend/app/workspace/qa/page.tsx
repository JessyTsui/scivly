"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bot, Send } from "lucide-react";

import type { ChatMessageOut, PaperOut } from "@/lib/api/types";
import { listPapers } from "@/lib/api/papers";
import {
  createPaperChatSession,
  getChatHistory,
  listChatSessions,
  sendChatMessage,
} from "@/lib/api/chat";
import { useScivlySession } from "@/lib/auth/scivly-session";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { ScoreBadge } from "@/components/workspace/ScoreBadge";
import { formatDateTime } from "@/lib/utils";

function buildSeedMessages(defaultSelectedPaperId: string) {
  return [
    {
      id: `assistant-seed-${defaultSelectedPaperId || "empty"}`,
      role: "assistant" as const,
      content:
        "Ask about score reasons, limitations, or what deserves follow-up reading. Replies are stored through the backend chat API.",
      created_at: new Date().toISOString(),
      model: "gpt-4.1-mini",
    },
  ];
}

export default function WorkspaceQAPage() {
  const session = useScivlySession();
  const queryClient = useQueryClient();
  const [selectedPaperId, setSelectedPaperId] = useState("");
  const [draft, setDraft] = useState("");
  const [messagesByPaper, setMessagesByPaper] = useState<Record<string, ChatMessageOut[]>>({});
  const [sessionIdsByPaper, setSessionIdsByPaper] = useState<Record<string, string>>({});
  const queriesEnabled =
    session.isLoaded &&
    session.isSignedIn &&
    !session.isSyncing &&
    !session.error &&
    Boolean(session.workspace);

  const papersQuery = useQuery({
    queryKey: ["papers", "qa"],
    queryFn: () => listPapers({ per_page: 20, sort: "score_desc" }),
    enabled: queriesEnabled,
  });
  const sessionsQuery = useQuery({
    queryKey: ["chat-sessions"],
    queryFn: listChatSessions,
    enabled: queriesEnabled,
  });

  const papers = papersQuery.data?.items;
  const defaultSelectedPaperId = papers?.[0]?.id ?? "";
  const effectiveSelectedPaperId = selectedPaperId || defaultSelectedPaperId;
  const selectedPaper = papers?.find((paper) => paper.id === effectiveSelectedPaperId);
  const activeSession =
    sessionsQuery.data?.find((item) => item.paper_id === effectiveSelectedPaperId) ??
    (effectiveSelectedPaperId && sessionIdsByPaper[effectiveSelectedPaperId]
      ? {
          id: sessionIdsByPaper[effectiveSelectedPaperId],
          paper_id: effectiveSelectedPaperId,
        }
      : null);

  const historyQuery = useQuery({
    queryKey: ["chat-history", activeSession?.id],
    queryFn: () => getChatHistory(activeSession!.id),
    enabled: queriesEnabled && Boolean(activeSession?.id),
  });

  useEffect(() => {
    if (!sessionsQuery.data) {
      return;
    }

    setSessionIdsByPaper((current) => {
      const next = { ...current };
      sessionsQuery.data.forEach((chatSession) => {
        if (chatSession.paper_id) {
          next[chatSession.paper_id] = chatSession.id;
        }
      });
      return next;
    });
  }, [sessionsQuery.data]);

  useEffect(() => {
    if (!effectiveSelectedPaperId || !historyQuery.data) {
      return;
    }

    setMessagesByPaper((current) => ({
      ...current,
      [effectiveSelectedPaperId]: historyQuery.data,
    }));
  }, [effectiveSelectedPaperId, historyQuery.data]);

  const sendMessageMutation = useMutation({
    mutationFn: async ({ content, paper }: { content: string; paper: PaperOut }) => {
      const sessionId =
        sessionIdsByPaper[paper.id] ??
        (await createPaperChatSession({
          paperId: paper.id,
          title: `${paper.title.slice(0, 72)}`,
          workspaceId: session.workspace!.id,
        })).id;

      const reply = await sendChatMessage({ content, sessionId });
      return { paperId: paper.id, reply, sessionId };
    },
    onSuccess: ({ paperId, reply, sessionId }) => {
      setSessionIdsByPaper((current) => ({
        ...current,
        [paperId]: sessionId,
      }));
      setMessagesByPaper((current) => ({
        ...current,
        [paperId]: [
          ...(current[paperId] ?? buildSeedMessages(paperId)),
          reply.user_message,
          reply.assistant_message,
        ],
      }));
      queryClient.invalidateQueries({ queryKey: ["chat-sessions"] });
      queryClient.invalidateQueries({ queryKey: ["chat-history", sessionId] });
      setDraft("");
    },
  });

  const combinedError =
    papersQuery.error ?? sessionsQuery.error ?? historyQuery.error ?? sendMessageMutation.error ?? null;
  const messages =
    (effectiveSelectedPaperId && messagesByPaper[effectiveSelectedPaperId]) ||
    buildSeedMessages(effectiveSelectedPaperId);
  const suggestedPrompts = [
    "Why did this paper score so high?",
    "What is the main limitation?",
    "What should I read first in this paper?",
  ];

  async function handleSendMessage() {
    if (!draft.trim() || !selectedPaper || sendMessageMutation.isPending) {
      return;
    }

    await sendMessageMutation.mutateAsync({
      content: draft.trim(),
      paper: selectedPaper,
    });
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.25fr)_minmax(320px,0.85fr)]">
      <Card className="min-h-[680px]">
        <CardHeader className="gap-4">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <CardTitle className="text-2xl">Paper Q&A</CardTitle>
              <p className="mt-2 max-w-2xl text-sm leading-7 text-[var(--foreground-muted)]">
                Ask follow-up questions against paper context, score reasons, and stored backend chat history.
              </p>
            </div>
            <Select
              value={effectiveSelectedPaperId}
              onValueChange={setSelectedPaperId}
              disabled={!queriesEnabled || papersQuery.isLoading}
            >
              <SelectTrigger className="max-w-[360px]">
                <SelectValue placeholder="Choose a paper" />
              </SelectTrigger>
              <SelectContent>
                {(papers ?? []).map((paper) => (
                  <SelectItem key={paper.id} value={paper.id}>
                    {paper.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardHeader>

        <CardContent className="flex h-full flex-col gap-4">
          {!queriesEnabled ? (
            <div className="rounded-[28px] border border-[var(--border)] bg-[var(--surface-hover)]/55 p-4 text-sm text-[var(--foreground-muted)]">
              Syncing authenticated workspace context with the backend...
            </div>
          ) : combinedError ? (
            <div className="rounded-[28px] border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-500">
              {combinedError instanceof Error
                ? combinedError.message
                : "Failed to load Q&A data from the backend API."}
            </div>
          ) : null}

          <div className="flex-1 space-y-3 rounded-[28px] border border-[var(--border)] bg-[var(--surface-hover)]/55 p-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`max-w-[88%] rounded-[22px] px-4 py-3 text-sm leading-7 ${
                  message.role === "assistant"
                    ? "bg-[var(--surface)] text-[var(--foreground)] shadow-[var(--shadow-sm)]"
                    : "ml-auto bg-[linear-gradient(135deg,var(--primary)_0%,var(--primary-dark)_100%)] text-white"
                }`}
              >
                <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] opacity-70">
                  {message.role === "assistant" ? <Bot className="size-3.5" /> : null}
                  <span>{message.role}</span>
                  <span>{formatDateTime(message.created_at)}</span>
                </div>
                <p className="mt-2">{message.content}</p>
              </div>
            ))}
          </div>

          <div className="space-y-3">
            <div className="flex flex-wrap gap-2">
              {suggestedPrompts.map((prompt) => (
                <Button key={prompt} variant="outline" size="sm" onClick={() => setDraft(prompt)}>
                  {prompt}
                </Button>
              ))}
            </div>
            <div className="flex flex-col gap-3">
              <Textarea
                className="min-h-28"
                placeholder="Ask about methodology, score reasons, or whether this paper belongs in the digest."
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    void handleSendMessage();
                  }
                }}
              />
              <div className="flex justify-end">
                <Button
                  onClick={() => void handleSendMessage()}
                  disabled={!queriesEnabled || !draft.trim() || sendMessageMutation.isPending}
                >
                  <Send />
                  {sendMessageMutation.isPending ? "Responding..." : "Send"}
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-6">
        {selectedPaper ? (
          <Card>
            <CardHeader className="gap-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <CardTitle className="text-2xl">{selectedPaper.title}</CardTitle>
                  <p className="mt-2 text-sm leading-7 text-[var(--foreground-muted)]">
                    {selectedPaper.one_line_summary}
                  </p>
                </div>
                <ScoreBadge score={selectedPaper.score.total_score} />
              </div>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-[var(--foreground-muted)]">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                  Main evidence
                </p>
                <div className="mt-3 space-y-2">
                  {selectedPaper.key_points.map((point) => (
                    <div
                      key={point}
                      className="rounded-[20px] border border-[var(--border)] bg-[var(--surface-hover)]/70 px-4 py-3"
                    >
                      {point}
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                  Why it matched
                </p>
                <div className="mt-3 space-y-2">
                  {selectedPaper.score.matched_rules.positive.map((rule) => (
                    <div
                      key={rule}
                      className="rounded-[20px] border border-emerald-500/15 bg-emerald-500/10 px-4 py-3 text-emerald-700 dark:text-emerald-300"
                    >
                      {rule}
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-[24px] border border-[var(--border)] bg-[var(--surface-hover)]/75 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                  Limitation
                </p>
                <p className="mt-3 leading-7">
                  {selectedPaper.limitations ?? "No limitations section is available for this paper yet."}
                </p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="pt-6 text-sm text-[var(--foreground-muted)]">
              Select a paper to inspect its score and chat history.
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
