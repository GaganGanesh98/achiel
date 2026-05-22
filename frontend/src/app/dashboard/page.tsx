"use client";

import { useQuery } from "@tanstack/react-query";
import { GraduationCap, MessageSquare, MessageSquarePlus, Users } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { Composer } from "@/components/composer";
import { PostCard } from "@/components/post-card";
import { Card, CardContent } from "@/components/ui/card";
import { api, ApiError } from "@/lib/api";
import type { Post, Topic } from "@/types";
import { TOPIC_LABELS } from "@/types";

const TOPICS: (Topic | "all")[] = [
  "all",
  "travel",
  "culture",
  "cost_of_living",
  "academics",
  "housing",
  "jobs",
  "general",
];

// TODO: fetch from GET /api/posts/trending?window=7d → { topic: string; post_count: number }[]
// Section is hidden until real data is available.
// const { data: trending } = useQuery({ queryKey: ["trending"], queryFn: () => api<...>(...) });
// {trending && trending.length > 0 && ( <TrendingSection ... /> )}

async function fetchStat(path: string): Promise<number | null> {
  try {
    const data = await api<{ count: number }>(path);
    return typeof data?.count === "number" ? data.count : null;
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    return null;
  }
}

export default function DashboardPage() {
  return (
    <Suspense
      fallback={
        <main className="mx-auto max-w-3xl py-6 px-4">
          <p className="text-sm text-muted-foreground">Loading…</p>
        </main>
      }
    >
      <DashboardContent />
    </Suspense>
  );
}

function DashboardContent() {
  const searchParams = useSearchParams();
  const universityId = searchParams.get("university_id") ?? undefined;
  const [topic, setTopic] = useState<Topic | "all">("all");
  const [sort, setSort] = useState<"new" | "top">("new");

  // TODO: GET /stats/users → { count: number }
  const { data: verifiedStudents } = useQuery({
    queryKey: ["stats", "users"],
    queryFn: () => fetchStat("/stats/users"),
    staleTime: 60_000,
  });

  // TODO: GET /stats/universities → { count: number }
  const { data: activeUniversities } = useQuery({
    queryKey: ["stats", "universities"],
    queryFn: () => fetchStat("/stats/universities"),
    staleTime: 60_000,
  });

  // TODO: GET /stats/posts/week → { count: number }
  const { data: postsThisWeek } = useQuery({
    queryKey: ["stats", "posts-week"],
    queryFn: () => fetchStat("/stats/posts/week"),
    staleTime: 60_000,
  });

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["feed", topic, sort, universityId],
    queryFn: () =>
      api<Post[]>("/posts", {
        query: {
          topic: topic === "all" ? undefined : topic,
          sort,
          university_id: universityId,
        },
      }),
  });

  function focusComposer() {
    const title = document.getElementById("composer-title");
    if (title instanceof HTMLInputElement) {
      title.scrollIntoView({ behavior: "smooth", block: "center" });
      title.focus();
      return;
    }
    document.getElementById("composer-trigger")?.click();
    setTimeout(() => {
      const input = document.getElementById("composer-title");
      input?.scrollIntoView({ behavior: "smooth", block: "center" });
      if (input instanceof HTMLInputElement) input.focus();
    }, 0);
  }

  return (
    <main className="mx-auto max-w-3xl py-6 px-4 space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">Global Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Verified students from universities worldwide
        </p>
      </header>

      <section className="grid grid-cols-3 gap-3">
        <StatCard
          icon={Users}
          label="Verified students"
          value={verifiedStudents}
        />
        <StatCard
          icon={GraduationCap}
          label="Universities active"
          value={activeUniversities}
        />
        <StatCard
          icon={MessageSquare}
          label="Posts this week"
          value={postsThisWeek}
        />
      </section>

      <Composer onPosted={() => refetch()} />

      <div className="flex flex-wrap items-center gap-2 border-b pb-3">
        <div className="flex flex-wrap gap-1">
          {TOPICS.map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTopic(t)}
              className={`text-xs px-3 py-1 rounded-full border transition-colors ${
                topic === t
                  ? "bg-primary text-primary-foreground border-primary"
                  : "bg-background text-muted-foreground border-input hover:border-foreground/40"
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
              type="button"
              onClick={() => setSort(s)}
              className={`text-xs px-3 py-1 rounded ${
                sort === s ? "underline font-medium" : "text-muted-foreground"
              }`}
            >
              {s === "new" ? "Newest" : "Top"}
            </button>
          ))}
        </div>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}

      {!isLoading && data?.length === 0 && (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center text-center py-10 px-6">
            <MessageSquarePlus className="h-10 w-10 text-muted-foreground mb-3" />
            <h2 className="text-lg font-semibold">
              {topic === "all"
                ? "No posts yet"
                : `No ${TOPIC_LABELS[topic]} posts yet. Be the first.`}
            </h2>
            {topic === "all" && (
              <p className="text-sm text-muted-foreground mt-2 max-w-sm">
                Share what&apos;s on your mind — your verified peers will see it.
              </p>
            )}
            <button
              type="button"
              onClick={focusComposer}
              className="mt-4 rounded-md bg-primary text-primary-foreground text-sm px-4 py-2 hover:bg-primary/90"
            >
              Start a post
            </button>
          </CardContent>
        </Card>
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

function StatCard({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Users;
  label: string;
  value: number | null | undefined;
}) {
  const hasRealValue = typeof value === "number";

  return (
    <Card>
      <CardContent className="p-4 flex flex-col gap-1">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">{label}</span>
          <Icon className="h-4 w-4 text-muted-foreground" />
        </div>
        <span className="text-2xl font-semibold tabular-nums">
          {hasRealValue ? value : "—"}
        </span>
        {!hasRealValue && (
          <span className="text-xs text-muted-foreground">(coming soon)</span>
        )}
      </CardContent>
    </Card>
  );
}
