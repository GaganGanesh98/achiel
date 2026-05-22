"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { ReportButton } from "@/components/report-button";
import { VoteButtons } from "@/components/vote-buttons";
import { api, ApiError, getToken } from "@/lib/api";
import { buildCommentTree, type CommentNode } from "@/lib/comments-tree";
import { cn } from "@/lib/utils";
import {
  applyVoteToComment,
  effectiveVote,
  mergeVoteCounts,
  nextVoteValue,
} from "@/lib/votes";
import type { Comment, VoteCounts } from "@/types";

function timeAgo(iso: string): string {
  const sec = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (sec < 60) return `${sec}s ago`;
  if (sec < 3600) return `${Math.floor(sec / 60)}m ago`;
  if (sec < 86400) return `${Math.floor(sec / 3600)}h ago`;
  return `${Math.floor(sec / 86400)}d ago`;
}

function CommentSkeleton() {
  return (
    <div className="space-y-3 animate-pulse">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-16 rounded-md bg-muted/60" />
      ))}
    </div>
  );
}

type ReplyFormProps = {
  postId: string;
  parentId: string | null;
  onSuccess: () => void;
  onCancel?: () => void;
  placeholder?: string;
};

function ReplyForm({
  postId,
  parentId,
  onSuccess,
  onCancel,
  placeholder = "Write a reply…",
}: ReplyFormProps) {
  const router = useRouter();
  const [body, setBody] = useState("");
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (text: string) =>
      api<Comment>(`/posts/${postId}/comments`, {
        method: "POST",
        body: {
          body: text,
          parent_comment_id: parentId,
        },
      }),
    onSuccess: () => {
      setBody("");
      setError(null);
      onSuccess();
    },
    onError: (err) => {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/login");
        return;
      }
      setError(err instanceof ApiError ? err.message : "Failed to post comment");
    },
  });

  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!getToken()) {
      router.push("/login");
      return;
    }
    const text = body.trim();
    if (!text) return;
    mutation.mutate(text);
  }

  return (
    <form onSubmit={submit} className="space-y-2 mt-2">
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        rows={2}
        maxLength={2000}
        placeholder={placeholder}
        className="w-full rounded-md border border-input px-3 py-2 text-sm resize-y"
      />
      {error && <p className="text-xs text-destructive">{error}</p>}
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={mutation.isPending || !body.trim()}
          className="rounded-md bg-primary text-primary-foreground text-xs px-3 py-1 disabled:opacity-50"
        >
          {mutation.isPending ? "Posting…" : "Post"}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="text-xs text-muted-foreground"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

function CommentRow({
  node,
  postId,
  depth,
  onInvalidate,
}: {
  node: CommentNode;
  postId: string;
  depth: number;
  onInvalidate: () => void;
}) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [replyOpen, setReplyOpen] = useState(false);
  const [local, setLocal] = useState(node);

  useEffect(() => {
    setLocal(node);
  }, [node]);

  const voteMutation = useMutation({
    mutationFn: (value: number) =>
      api<VoteCounts>(`/comments/${node.id}/vote`, {
        method: "POST",
        body: { value },
      }),
    onMutate: async (value) => {
      const prev = local;
      setLocal(applyVoteToComment(local, value));
      return { prev };
    },
    onError: (err, _value, ctx) => {
      if (ctx?.prev) setLocal(ctx.prev);
      if (err instanceof ApiError && err.status === 401) router.push("/login");
    },
    onSuccess: (counts) => {
      setLocal((c) => mergeVoteCounts(c, counts));
      queryClient.invalidateQueries({ queryKey: ["comments", postId] });
    },
  });

  function handleVote(direction: 1 | -1) {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    const current = effectiveVote(local);
    const next = nextVoteValue(current, direction);
    voteMutation.mutate(next);
  }

  const displayBody =
    local.is_deleted || local.body === "[removed]"
      ? "[removed]"
      : local.is_hidden
        ? local.body
        : local.body;

  return (
    <div
      className={cn(
        "relative",
        depth > 0 && "ml-4 border-l border-border pl-3"
      )}
    >
      <div className="flex gap-2 py-2">
        <VoteButtons
          layout="column"
          score={local.score}
          myVote={effectiveVote(local)}
          onUp={() => handleVote(1)}
          onDown={() => handleVote(-1)}
          disabled={voteMutation.isPending}
        />
        <div className="min-w-0 flex-1">
          {local.is_hidden && local.hidden_reason && (
            <p className="text-xs text-amber-800 dark:text-amber-300 bg-amber-500/10 border border-amber-500/30 rounded px-2 py-0.5 mb-1">
              Hidden pending moderation — {local.hidden_reason}
            </p>
          )}
          <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 text-xs text-muted-foreground">
            <span className="font-medium text-foreground">{local.author.display_name}</span>
            <span>{timeAgo(local.created_at)}</span>
          </div>
          <p
            className={cn(
              "text-sm mt-1 whitespace-pre-wrap",
              (local.is_deleted || local.body === "[removed]") && "text-muted-foreground italic"
            )}
          >
            {displayBody}
          </p>
          <div className="flex items-center gap-2 mt-1">
            {!local.is_deleted && local.body !== "[removed]" && (
              <button
                type="button"
                onClick={() => setReplyOpen((o) => !o)}
                className="text-xs text-muted-foreground hover:text-foreground"
              >
                Reply
              </button>
            )}
            <ReportButton targetType="comment" targetId={local.id} />
          </div>
          {replyOpen && (
            <ReplyForm
              postId={postId}
              parentId={local.id}
              onSuccess={() => {
                setReplyOpen(false);
                onInvalidate();
              }}
              onCancel={() => setReplyOpen(false)}
            />
          )}
        </div>
      </div>
      {node.children.map((child) => (
        <CommentRow
          key={child.id}
          node={child}
          postId={postId}
          depth={depth + 1}
          onInvalidate={onInvalidate}
        />
      ))}
    </div>
  );
}

export function CommentThread({ postId }: { postId: string }) {
  const queryClient = useQueryClient();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["comments", postId],
    queryFn: () => api<Comment[]>(`/posts/${postId}/comments`),
  });

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["comments", postId] });

  const tree = data ? buildCommentTree(data) : [];

  return (
    <section className="space-y-3 border-t pt-4">
      <h3 className="text-sm font-medium text-muted-foreground">Comments</h3>

      {isLoading && <CommentSkeleton />}
      {isError && (
        <p className="text-sm text-destructive">Could not load comments.</p>
      )}

      {!isLoading && !isError && tree.length === 0 && (
        <p className="text-sm text-muted-foreground">No comments yet.</p>
      )}

      <div className="space-y-1">
        {tree.map((node) => (
          <CommentRow
            key={node.id}
            node={node}
            postId={postId}
            depth={0}
            onInvalidate={invalidate}
          />
        ))}
      </div>

      <div className="pt-2">
        <p className="text-xs text-muted-foreground mb-2">Add a comment</p>
        <ReplyForm
          postId={postId}
          parentId={null}
          onSuccess={invalidate}
          placeholder="Share your thoughts…"
        />
      </div>
    </section>
  );
}
