"use client";

import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Bot, Send, Sparkles } from "lucide-react";

import type { ChatMessageOut, PaperOut } from "@/lib/api/types";
import { listPapers } from "@/lib/api/papers";
import { hoursAgo } from "@/lib/mock/time";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { ScoreBadge } from "@/components/workspace/ScoreBadge";
import { formatDateTime } from "@/lib/utils";

function buildAssistantReply(paper: PaperOut, prompt: string) {
  const promptLower = prompt.toLowerCase();

  if (promptLower.includes("why")) {
    return `The score is mainly carried by ${paper.score.topical_relevance} topical-relevance points and ${paper.score.actionability} actionability points. The strongest matched rules were ${paper.score.matched_rules.positive.slice(0, 2).join(" and ")}.`;
  }

  if (promptLower.includes("risk") || promptLower.includes("limitation")) {
    return `The main limitation called out in the mock summary is: ${paper.limitations ?? "the paper did not provide a detailed limitations section."}`;
  }

  const followUpTarget = paper.key_points.find((point) => point.trim().length > 0);

  if (!followUpTarget) {
    return `The paper's core takeaway is: ${paper.one_line_summary} A good follow-up would be to inspect the evaluation details and supporting evidence.`;
  }

  return `The paper's core takeaway is: ${paper.one_line_summary} A good follow-up would be to inspect ${followUpTarget.toLowerCase()}.`;
}

export default function WorkspaceQAPage() {
  const papersQuery = useQuery({
    queryKey: ["papers", "qa"],
    queryFn: () => listPapers({ per_page: 10, sort: "score_desc" }),
  });
  const papers = papersQuery.data?.items;
  const [selectedPaperId, setSelectedPaperId] = useState("");
  const [draft, setDraft] = useState("");
  const [messagesByPaper, setMessagesByPaper] = useState<Record<string, ChatMessageOut[]>>({});
  const [pendingPaperIds, setPendingPaperIds] = useState<Record<string, boolean>>({});
  const replyTimeoutIdsRef = useRef<number[]>([]);

  useEffect(() => {
    if (!papers?.length) {
      return;
    }

    setSelectedPaperId((current) => current || papers[0].id);
    setMessagesByPaper((current) =>
      Object.keys(current).length
        ? current
        : {
            [papers[0].id]: [
              {
                id: "assistant-welcome",
                role: "assistant",
                content:
                  "I can explain score breakdowns, summarize the paper, or suggest what to read next.",
                created_at: hoursAgo(2),
                model: "gpt-4o-mini (mock)",
              },
            ],
          }
    );
  }, [papers]);

  useEffect(() => {
    return () => {
      replyTimeoutIdsRef.current.forEach((timeoutId) => window.clearTimeout(timeoutId));
      replyTimeoutIdsRef.current = [];
    };
  }, []);

  useEffect(() => {
    if (!selectedPaperId || messagesByPaper[selectedPaperId]) {
      return;
    }

    setMessagesByPaper((current) => ({
      ...current,
      [selectedPaperId]: [
        {
          id: `assistant-seed-${selectedPaperId}`,
          role: "assistant",
          content:
            "Ask about score reasons, limitations, or what deserves follow-up reading. I will stay grounded to the mock paper context.",
          created_at: new Date().toISOString(),
          model: "gpt-4o-mini (mock)",
        },
      ],
    }));
  }, [messagesByPaper, selectedPaperId]);

  const selectedPaper = papers?.find((paper) => paper.id === selectedPaperId);
  const messages = messagesByPaper[selectedPaperId] ?? [];
  const isCurrentPaperPending = Boolean(selectedPaperId && pendingPaperIds[selectedPaperId]);
  const suggestedPrompts = [
    "Why did this paper score so high?",
    "What is the main limitation?",
    "What should I read first in this paper?",
  ];

  function sendMessage() {
    if (!draft.trim() || !selectedPaper || pendingPaperIds[selectedPaper.id]) {
      return;
    }

    const submitted = draft.trim();
    const timestamp = new Date().toISOString();

    setMessagesByPaper((current) => ({
      ...current,
      [selectedPaper.id]: [
        ...(current[selectedPaper.id] ?? []),
        {
          id: `user-${crypto.randomUUID()}`,
          role: "user",
          content: submitted,
          created_at: timestamp,
        },
      ],
    }));
    setDraft("");
    setPendingPaperIds((current) => ({
      ...current,
      [selectedPaper.id]: true,
    }));

    const timeoutId = window.setTimeout(() => {
      setMessagesByPaper((current) => ({
        ...current,
        [selectedPaper.id]: [
          ...(current[selectedPaper.id] ?? []),
          {
            id: `assistant-${crypto.randomUUID()}`,
            role: "assistant",
            content: buildAssistantReply(selectedPaper, submitted),
            created_at: new Date().toISOString(),
            model: "gpt-4o-mini (mock)",
          },
        ],
      }));
      setPendingPaperIds((current) => ({
        ...current,
        [selectedPaper.id]: false,
      }));
      replyTimeoutIdsRef.current = replyTimeoutIdsRef.current.filter((id) => id !== timeoutId);
    }, 450);

    replyTimeoutIdsRef.current.push(timeoutId);
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.25fr)_minmax(320px,0.85fr)]">
      <Card className="min-h-[680px]">
        <CardHeader className="gap-4">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <CardTitle className="text-2xl">Paper Q&A</CardTitle>
              <p className="mt-2 max-w-2xl text-sm leading-7 text-[var(--foreground-muted)]">
                Ask follow-up questions against mock paper context, score reasons, and digest-ready summaries.
              </p>
            </div>
            <Select value={selectedPaperId} onValueChange={setSelectedPaperId}>
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
                    sendMessage();
                  }
                }}
              />
              <div className="flex justify-end">
                <Button onClick={sendMessage} disabled={!draft.trim() || isCurrentPaperPending}>
                  <Send />
                  {isCurrentPaperPending ? "Responding..." : "Send"}
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
            </CardContent>
          </Card>
        ) : null}

        <Card className="bg-[linear-gradient(160deg,rgba(15,23,42,0.98),rgba(23,37,84,0.92))] text-white shadow-[var(--shadow-lg)]">
          <CardHeader>
            <CardTitle className="text-2xl text-white">Powered by</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-slate-200">
            <div className="rounded-[20px] bg-white/6 px-4 py-3">
              <div className="flex items-center gap-2 font-medium">
                <Sparkles className="size-4 text-[var(--accent)]" />
                gpt-4o-mini (mock)
              </div>
              <p className="mt-2 text-slate-300">
                Context bundle: abstract, one-line summary, score reasons, and key points.
              </p>
            </div>
            <div className="rounded-[20px] bg-white/6 px-4 py-3">
              Keep answers grounded to paper evidence. The final backend integration can swap the
              model without changing this UI surface.
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
