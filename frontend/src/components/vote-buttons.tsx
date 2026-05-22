"use client";

import { ChevronDown, ChevronUp } from "lucide-react";

import { cn } from "@/lib/utils";

type VoteButtonsProps = {
  score: number;
  myVote: number;
  onUp: () => void;
  onDown: () => void;
  disabled?: boolean;
  layout?: "column" | "row";
};

export function VoteButtons({
  score,
  myVote,
  onUp,
  onDown,
  disabled,
  layout = "column",
}: VoteButtonsProps) {
  const isColumn = layout === "column";

  return (
    <div
      className={cn(
        "flex shrink-0 items-center gap-0.5",
        isColumn ? "flex-col" : "flex-row"
      )}
    >
      <button
        type="button"
        disabled={disabled}
        onClick={onUp}
        aria-label="Upvote"
        className={cn(
          "rounded p-1 transition-colors disabled:opacity-50",
          myVote === 1
            ? "bg-primary text-primary-foreground"
            : "text-muted-foreground hover:bg-muted hover:text-foreground"
        )}
      >
        <ChevronUp className="h-4 w-4" />
      </button>
      <span
        className={cn(
          "tabular-nums font-medium text-sm",
          isColumn ? "py-0.5" : "min-w-[2ch] text-center"
        )}
      >
        {score}
      </span>
      <button
        type="button"
        disabled={disabled}
        onClick={onDown}
        aria-label="Downvote"
        className={cn(
          "rounded p-1 transition-colors disabled:opacity-50",
          myVote === -1
            ? "bg-primary text-primary-foreground"
            : "text-muted-foreground hover:bg-muted hover:text-foreground"
        )}
      >
        <ChevronDown className="h-4 w-4" />
      </button>
    </div>
  );
}
