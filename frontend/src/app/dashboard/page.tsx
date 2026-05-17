"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Post, Topic } from "@/types";
import { TOPIC_LABELS } from "@/types";
import { PostCard } from "@/components/post-card";
import { Composer } from "@/components/composer";

const TOPICS: (Topic | "all")[] = [
  "all",
  "travel",
  "culture",
  "cost_of_living",
  "academics",
  "housing",
  "general",
];

export default function DashboardPage() {
  const [topic, setTopic] = useState<Topic | "all">("all");
  const [sort, setSort] = useState<"new" | "top">("new");

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["feed", topic, sort],
    queryFn: () =>
      api<Post[]>("/posts", {
        query: { topic: topic === "all" ? undefined : topic, sort },
      }),
  });

  return (
    <main className="mx-auto max-w-3xl py-6 px-4 space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Global Dashboard</h1>
        <Link
          href="/me"
          className="text-sm text-neutral-600 hover:text-black"
        >
          Account
        </Link>
      </header>

      <Composer onPosted={() => refetch()} />

      <div className="flex flex-wrap items-center gap-2 border-b pb-3">
        <div className="flex flex-wrap gap-1">
          {TOPICS.map((t) => (
            <button
              key={t}
              onClick={() => setTopic(t)}
              className={`text-xs px-3 py-1 rounded-full border transition-colors ${
                topic === t
                  ? "bg-black text-white border-black"
                  : "bg-white text-neutral-700 border-neutral-300 hover:border-neutral-500"
              }`}
            >
              {t === "all" ? "All" : TOPIC_LABELS[t]}
            </button>
          ))}
        </div>
        <div className="ml-auto flex gap-1">
          {(["new", "top"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setSort(s)}
              className={`text-xs px-3 py-1 rounded ${
                sort === s ? "underline font-medium" : "text-neutral-500"
              }`}
            >
              {s === "new" ? "Newest" : "Top"}
            </button>
          ))}
        </div>
      </div>

      {isLoading && <p className="text-sm text-neutral-500">Loading…</p>}
      {data?.length === 0 && (
        <p className="text-sm text-neutral-500">
          No posts yet. Be the first to share something.
        </p>
      )}
      <ul className="space-y-3">
        {data?.map((post) => (
          <li key={post.id}>
            <PostCard post={post} onVoted={() => refetch()} />
          </li>
        ))}
      </ul>
    </main>
  );
}
