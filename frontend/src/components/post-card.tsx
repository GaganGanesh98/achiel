"use client";

import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { CommentThread } from "@/components/comment-thread";
import { ReportButton } from "@/components/report-button";
import { VoteButtons } from "@/components/vote-buttons";
import { Badge } from "@/components/ui/badge";
import { api, ApiError, getToken } from "@/lib/api";
import { SENTIMENT_PILL_CLASS } from "@/lib/sentiment-styles";
import { cn } from "@/lib/utils";
import {
  applyVoteToPost,
  effectiveVote,
  mergeVoteCounts,
  nextVoteValue,
} from "@/lib/votes";
import type { Post, VoteCounts } from "@/types";
import { SENTIMENT_LABELS, TOPIC_LABELS } from "@/types";

function timeAgo(iso: string): string {
  const sec = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (sec < 60) return `${sec}s`;
  if (sec < 3600) return `${Math.floor(sec / 60)}m`;
  if (sec < 86400) return `${Math.floor(sec / 3600)}h`;
  return `${Math.floor(sec / 86400)}d`;
}

export function PostCard({
  post: initialPost,
  onVoted,
  defaultCommentsOpen = false,
}: {
  post: Post;
  onVoted: () => void;
  defaultCommentsOpen?: boolean;
}) {
  const router = useRouter();
  const [post, setPost] = useState(initialPost);
  const [commentsOpen, setCommentsOpen] = useState(defaultCommentsOpen);

  useEffect(() => {
    setPost(initialPost);
  }, [initialPost]);

  const voteMutation = useMutation({
    mutationFn: (value: number) =>
      api<VoteCounts>(`/posts/${post.id}/vote`, {
        method: "POST",
        body: { value },
      }),
    onMutate: async (value) => {
      const prev = post;
      setPost(applyVoteToPost(post, value));
      return { prev };
    },
    onError: (err, _value, ctx) => {
      if (ctx?.prev) setPost(ctx.prev);
      if (err instanceof ApiError && err.status === 401) {
        router.push("/login");
      }
    },
    onSuccess: (counts) => {
      setPost((p) => mergeVoteCounts(p, counts));
      onVoted();
    },
  });

  function handleVote(direction: 1 | -1) {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    const current = effectiveVote(post);
    const next = nextVoteValue(current, direction);
    voteMutation.mutate(next);
  }

  const uni = post.author.university;
  const myVote = effectiveVote(post);
  const isHidden = post.is_hidden === true;
  const autoFlagged =
    isHidden && (post.watchlist_matches?.length ?? 0) > 0;

  return (
    <article
      className={cn(
        "rounded-lg border border-border overflow-hidden hover:border-foreground/30 transition-colors relative",
        isHidden && "border-amber-500/40"
      )}
    >
      {isHidden && (
        <div className="absolute inset-0 bg-muted/50 pointer-events-none z-[1]" aria-hidden />
      )}
      <div className="flex gap-0">
        <div className="flex flex-col items-center justify-start gap-0.5 bg-muted/30 px-2 py-3 border-r border-border min-w-[2.75rem]">
          <VoteButtons
            layout="column"
            score={post.score}
            myVote={myVote}
            onUp={() => handleVote(1)}
            onDown={() => handleVote(-1)}
            disabled={voteMutation.isPending}
          />
        </div>

        <div className="flex-1 min-w-0 p-4 relative z-[2]">
          {isHidden && post.hidden_reason && (
            <p className="text-xs text-amber-800 dark:text-amber-300 bg-amber-500/10 border border-amber-500/30 rounded-md px-2 py-1 mb-2">
              Hidden pending moderation — {post.hidden_reason}
            </p>
          )}
          {autoFlagged && (
            <span
              className="inline-flex items-center rounded-full bg-amber-500/15 text-amber-800 dark:text-amber-300 text-xs px-2 py-0.5 mb-2 border border-amber-500/30 cursor-help"
              title={
                post.watchlist_matches?.length
                  ? `Matched watchlist: ${post.watchlist_matches.map((m) => m.name).join(", ")}. Your post is hidden from others until moderation completes. No action needed unless content is removed.`
                  : "Auto-flagged for review."
              }
            >
              Auto-flagged for review
            </span>
          )}
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground mb-2">
            <span className="rounded-full bg-muted px-2 py-0.5 text-foreground">
              {TOPIC_LABELS[post.topic]}
            </span>
            <Badge
              variant="outline"
              className={cn(
                "font-normal border",
                SENTIMENT_PILL_CLASS[post.sentiment]
              )}
            >
              {SENTIMENT_LABELS[post.sentiment]}
            </Badge>
            {uni && (
              <span>
                {uni.name}
                {uni.city ? ` · ${uni.city}` : ""}
              </span>
            )}
            <span className="ml-auto">{timeAgo(post.created_at)}</span>
          </div>

          <Link href={`/post/${post.id}`} className="block group">
            <h2 className="font-medium group-hover:underline">{post.title}</h2>
            <p className="text-sm text-muted-foreground mt-1 line-clamp-3">{post.body}</p>
          </Link>

          <div className="flex items-center gap-3 mt-3 text-sm">
            <button
              type="button"
              onClick={() => setCommentsOpen((o) => !o)}
              className="text-muted-foreground hover:text-foreground"
            >
              Comments ({post.comment_count})
            </button>
            <Link
              href={`/post/${post.id}`}
              className="text-xs text-muted-foreground hover:text-foreground"
            >
              Open thread
            </Link>
            <ReportButton targetType="post" targetId={post.id} />
            <span className="ml-auto text-muted-foreground">by {post.author.display_name}</span>
          </div>
        </div>
      </div>

      {commentsOpen && (
        <div className="px-4 pb-4 border-t border-border bg-muted/10">
          <CommentThread postId={post.id} />
        </div>
      )}
    </article>
  );
}
