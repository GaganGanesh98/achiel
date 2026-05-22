"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { api, ApiError, getToken } from "@/lib/api";
import { SENTIMENT_BUTTON_CLASS } from "@/lib/sentiment-styles";
import { cn } from "@/lib/utils";
import type { Post, Sentiment, Topic, User } from "@/types";
import { SENTIMENT_LABELS, TOPIC_LABELS } from "@/types";

const TOPICS: Topic[] = [
  "travel",
  "culture",
  "cost_of_living",
  "academics",
  "housing",
  "jobs",
  "general",
];

const SENTIMENTS: Sentiment[] = ["positive", "neutral", "negative"];

export function Composer({ onPosted }: { onPosted: () => void }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [topic, setTopic] = useState<Topic>("general");
  const [sentiment, setSentiment] = useState<Sentiment | null>(null);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);

  const { data: user } = useQuery({
    queryKey: ["me"],
    queryFn: () => api<User>("/auth/me"),
    enabled: !!getToken(),
    retry: false,
  });

  const canPost =
    sentiment !== null && title.trim().length >= 4 && body.trim().length >= 10;

  const needsLogin = !getToken();
  const needsVerify = user && !user.is_verified;

  function resetForm() {
    setTitle("");
    setBody("");
    setSentiment(null);
    setTopic("general");
  }

  function openComposer() {
    if (needsLogin) {
      router.push("/login?next=/dashboard");
      return;
    }
    setOpen(true);
  }

  async function resendVerification() {
    if (!user?.email) return;
    setResending(true);
    try {
      await api("/auth/resend-verification", {
        method: "POST",
        auth: false,
        body: { email: user.email },
      });
    } finally {
      setResending(false);
    }
  }

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (needsLogin) {
      router.push("/login?next=/dashboard");
      return;
    }
    if (needsVerify || !sentiment || !canPost) return;
    setError(null);
    setLoading(true);
    try {
      await api<Post>("/posts", {
        method: "POST",
        body: {
          title: title.trim(),
          body: body.trim(),
          topic,
          sentiment,
        },
      });
      resetForm();
      setOpen(false);
      onPosted();
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/login?next=/dashboard");
      } else if (err instanceof ApiError && err.status === 403) {
        setError(err.message);
      } else if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to post");
      }
    } finally {
      setLoading(false);
    }
  }

  if (!open) {
    return (
      <button
        id="composer-trigger"
        type="button"
        onClick={openComposer}
        className="w-full text-left rounded-lg border border-input px-4 py-3 text-muted-foreground hover:border-foreground/40"
      >
        Share something with other students…
      </button>
    );
  }

  return (
    <div className="space-y-3">
      {needsVerify && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200 px-4 py-3 text-sm flex flex-wrap items-center justify-between gap-2">
          <span>Verify your email to start posting</span>
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={resending}
            onClick={resendVerification}
          >
            {resending ? "Sending…" : "Resend verification"}
          </Button>
        </div>
      )}

      <form
        onSubmit={onSubmit}
        className={cn(
          "space-y-3 rounded-lg border border-input p-4",
          needsVerify && "opacity-60 pointer-events-none"
        )}
      >
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">How does this post feel?</p>
          <div className="flex flex-wrap gap-2" role="group" aria-label="Post sentiment">
            {SENTIMENTS.map((s) => {
              const styles = SENTIMENT_BUTTON_CLASS[s];
              const selected = sentiment === s;
              return (
                <button
                  key={s}
                  type="button"
                  disabled={!!needsVerify}
                  onClick={() => setSentiment(s)}
                  className={cn(
                    "rounded-md border px-3 py-1.5 text-sm font-medium transition-colors",
                    selected ? styles.selected : styles.base
                  )}
                >
                  {SENTIMENT_LABELS[s]}
                </button>
              );
            })}
          </div>
        </div>

        <input
          id="composer-title"
          name="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          readOnly={!!needsVerify}
          required
          minLength={4}
          maxLength={200}
          placeholder="Title"
          className="w-full rounded-md border border-input px-3 py-2 text-sm"
        />
        <textarea
          name="body"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          readOnly={!!needsVerify}
          required
          minLength={10}
          maxLength={10000}
          rows={4}
          placeholder="What's on your mind? Keep it civil — slurs and threats get auto-flagged."
          className="w-full rounded-md border border-input px-3 py-2 text-sm resize-y"
        />
        <div className="flex items-center gap-2">
          <select
            value={topic}
            disabled={!!needsVerify}
            onChange={(e) => setTopic(e.target.value as Topic)}
            className="rounded-md border border-input px-2 py-1 text-sm"
          >
            {TOPICS.map((t) => (
              <option key={t} value={t}>
                {TOPIC_LABELS[t]}
              </option>
            ))}
          </select>
          <div className="ml-auto flex gap-2">
            <button
              type="button"
              onClick={() => {
                resetForm();
                setOpen(false);
              }}
              className="text-sm text-muted-foreground px-3 py-1"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !canPost || !!needsVerify}
              className="rounded-md bg-primary text-primary-foreground text-sm px-4 py-1 disabled:opacity-50"
            >
              {loading ? "Posting…" : "Post"}
            </button>
          </div>
        </div>
        {error && <p className="text-sm text-destructive">{error}</p>}
        {needsVerify && (
          <p className="text-xs text-muted-foreground pointer-events-auto">
            <Link href="/verify-pending" className="underline">
              Go to verification page
            </Link>
          </p>
        )}
      </form>
    </div>
  );
}
