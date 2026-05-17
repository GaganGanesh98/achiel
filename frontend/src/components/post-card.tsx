"use client";

import Link from "next/link";
import { api } from "@/lib/api";
import type { Post } from "@/types";
import { TOPIC_LABELS } from "@/types";

function timeAgo(iso: string): string {
  const sec = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (sec < 60) return `${sec}s`;
  if (sec < 3600) return `${Math.floor(sec / 60)}m`;
  if (sec < 86400) return `${Math.floor(sec / 3600)}h`;
  return `${Math.floor(sec / 86400)}d`;
}

export function PostCard({ post, onVoted }: { post: Post; onVoted: () => void }) {
  async function vote(value: 1 | -1) {
    // Toggle off if clicking the same direction
    const next = post.user_vote === value ? 0 : value;
    try {
      await api(`/posts/${post.id}/vote`, { method: "POST", body: { value: next } });
      onVoted();
    } catch {
      // swallow — feed will refetch on next interaction
    }
  }

  const uni = post.author.university;

  return (
    <article className="rounded-lg border border-neutral-200 p-4 hover:border-neutral-400 transition-colors">
      <div className="flex items-center gap-2 text-xs text-neutral-500 mb-2">
        <span className="rounded-full bg-neutral-100 px-2 py-0.5 text-neutral-700">
          {TOPIC_LABELS[post.topic]}
        </span>
        {uni && (
          <span>
            {uni.name} · {uni.country}
          </span>
        )}
        <span className="ml-auto">{timeAgo(post.created_at)}</span>
      </div>
      <Link href={`/post/${post.id}`} className="block group">
        <h2 className="font-medium group-hover:underline">{post.title}</h2>
        <p className="text-sm text-neutral-700 mt-1 line-clamp-3">{post.body}</p>
      </Link>
      <div className="flex items-center gap-3 mt-3 text-sm">
        <div className="flex items-center gap-1">
          <button
            onClick={() => vote(1)}
            className={`px-2 py-0.5 rounded ${
              post.user_vote === 1 ? "bg-black text-white" : "hover:bg-neutral-100"
            }`}
            aria-label="Upvote"
          >
            ▲
          </button>
          <span className="min-w-[2ch] text-center tabular-nums">{post.score}</span>
          <button
            onClick={() => vote(-1)}
            className={`px-2 py-0.5 rounded ${
              post.user_vote === -1 ? "bg-black text-white" : "hover:bg-neutral-100"
            }`}
            aria-label="Downvote"
          >
            ▼
          </button>
        </div>
        <Link
          href={`/post/${post.id}`}
          className="text-neutral-500 hover:text-black"
        >
          {post.comment_count} comments
        </Link>
        <span className="ml-auto text-neutral-500">by {post.author.display_name}</span>
      </div>
    </article>
  );
}
