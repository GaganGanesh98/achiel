"use client";

import { use } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { PostCard } from "@/components/post-card";
import { api, getToken } from "@/lib/api";
import type { Post } from "@/types";

export default function PostPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const qc = useQueryClient();

  const { data: post, isLoading } = useQuery({
    queryKey: ["post", id],
    queryFn: () => api<Post>(`/posts/${id}`, { auth: !!getToken() }),
  });

  if (isLoading) {
    return <main className="mx-auto max-w-3xl py-6 px-4">Loading…</main>;
  }

  if (!post) {
    return <main className="mx-auto max-w-3xl py-6 px-4">Post not found.</main>;
  }

  return (
    <main className="mx-auto max-w-3xl py-6 px-4 space-y-6">
      <PostCard
        post={post}
        defaultCommentsOpen
        onVoted={() => qc.invalidateQueries({ queryKey: ["post", id] })}
      />
    </main>
  );
}
