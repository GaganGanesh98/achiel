"use client";

import { use, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ApiError } from "@/lib/api";
import type { Comment, Post } from "@/types";
import { PostCard } from "@/components/post-card";

export default function PostPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const qc = useQueryClient();
  const [reportOpen, setReportOpen] = useState(false);

  const { data: post } = useQuery({
    queryKey: ["post", id],
    queryFn: () => api<Post>(`/posts/${id}`),
  });

  const { data: comments, refetch: refetchComments } = useQuery({
    queryKey: ["comments", id],
    queryFn: () => api<Comment[]>(`/posts/${id}/comments`),
  });

  if (!post) return <main className="mx-auto max-w-3xl py-6 px-4">Loading…</main>;

  return (
    <main className="mx-auto max-w-3xl py-6 px-4 space-y-6">
      <PostCard post={post} onVoted={() => qc.invalidateQueries({ queryKey: ["post", id] })} />

      <section className="space-y-3">
        <h2 className="text-sm font-medium text-neutral-700">Comments</h2>
        <CommentForm postId={id} onPosted={refetchComments} />
        <ul className="space-y-3">
          {comments?.map((c) => (
            <li key={c.id} className="border-l-2 border-neutral-200 pl-3">
              <p className="text-xs text-neutral-500">
                {c.author.display_name}
                {c.author.university && ` · ${c.author.university.name}`}
              </p>
              <p className="text-sm mt-1 whitespace-pre-wrap">{c.body}</p>
            </li>
          ))}
        </ul>
      </section>

      <button
        onClick={() => setReportOpen(!reportOpen)}
        className="text-xs text-neutral-500 hover:text-red-600"
      >
        Report this post
      </button>
      {reportOpen && <ReportForm postId={id} onDone={() => setReportOpen(false)} />}
    </main>
  );
}

function CommentForm({ postId, onPosted }: { postId: string; onPosted: () => void }) {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const fd = new FormData(e.currentTarget);
    try {
      await api(`/posts/${postId}/comments`, {
        method: "POST",
        body: { body: fd.get("body") },
      });
      (e.currentTarget as HTMLFormElement).reset();
      onPosted();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-2">
      <textarea
        name="body"
        required
        minLength={1}
        maxLength={2000}
        rows={2}
        placeholder="Add a comment…"
        className="w-full rounded border px-3 py-2 text-sm"
      />
      {error && <p className="text-xs text-red-600">{error}</p>}
      <button
        disabled={loading}
        className="rounded bg-black text-white text-xs px-3 py-1 disabled:opacity-50"
      >
        {loading ? "Posting…" : "Comment"}
      </button>
    </form>
  );
}

function ReportForm({ postId, onDone }: { postId: string; onDone: () => void }) {
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    const fd = new FormData(e.currentTarget);
    try {
      await api(`/posts/${postId}/report`, { method: "POST", body: { reason: fd.get("reason") } });
      onDone();
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-2 border rounded p-3 mt-2">
      <textarea
        name="reason"
        required
        minLength={4}
        maxLength={500}
        rows={2}
        placeholder="Why are you reporting this?"
        className="w-full rounded border px-3 py-2 text-sm"
      />
      <div className="flex gap-2">
        <button
          disabled={loading}
          className="rounded bg-red-600 text-white text-xs px-3 py-1"
        >
          Submit report
        </button>
        <button type="button" onClick={onDone} className="text-xs text-neutral-500">
          Cancel
        </button>
      </div>
    </form>
  );
}
