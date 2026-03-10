"use client";

import { Badge } from "@/components/ui/badge";
import { formatScore } from "@/lib/utils";

function getTone(score: number): React.ComponentProps<typeof Badge>["variant"] {
  if (score >= 75) {
    return "success";
  }

  if (score >= 55) {
    return "warning";
  }

  return "danger";
}

function getLabel(score: number) {
  if (score >= 82) {
    return "Source";
  }

  if (score >= 75) {
    return "Digest";
  }

  if (score >= 55) {
    return "Review";
  }

  return "Hold";
}

export function ScoreBadge({ score }: { score: number }) {
  return (
    <Badge variant={getTone(score)} className="gap-1.5">
      <span>{formatScore(score)}</span>
      <span className="text-[11px] uppercase tracking-[0.16em] opacity-80">{getLabel(score)}</span>
    </Badge>
  );
}
