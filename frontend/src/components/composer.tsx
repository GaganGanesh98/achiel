"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { Post, Topic } from "@/types";
import { TOPIC_LABELS } from "@/types";

const TOPICS: Topic[] = ["travel", "culture", "cost_of_living", "academics", "housing", "general"];

export function Composer({ onPosted }: { onPosted: () => void }) {
  const [open, setOpen] = useState(false);
  const [topic, setTopic] = useState<Topic>("general");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const fd = new FormData(e.currentTarget);
    try {
      await api<Post>("/posts", {
        method: "POST",
        body: {
          title: fd.get("title"),
          body: fd.get("body"),
          topic,
        },
      });
      (e.currentTarget as HTMLFormElement).reset();
      setOpen(false);
      onPosted();
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setError("You need to verify your email before posting.");
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
        onClick={() => setOpen(true)}
        className="w-full text-left rounded-lg border border-neutral-300 px-4 py-3 text-neutral-500 hover:border-neutral-500"
      >
        Share something with other students…
      </button>
    );
  }

  return (
    <form
      onSubmit={onSubmit}
      className="space-y-3 rounded-lg border border-neutral-300 p-4"
    >
      <input
        name="title"
        required
        minLength={4}
        maxLength={200}
        placeholder="Title"
        className="w-full rounded border px-3 py-2 text-sm"
      />
      <textarea
        name="body"
        required
        minLength={10}
        maxLength={10000}
        rows={4}
        placeholder="What's on your mind? Keep it civil — slurs and threats get auto-flagged."
        className="w-full rounded border px-3 py-2 text-sm resize-y"
      />
      <div className="flex items-center gap-2">
        <select
          value={topic}
          onChange={(e) => setTopic(e.target.value as Topic)}
          className="rounded border px-2 py-1 text-sm"
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
            onClick={() => setOpen(false)}
            className="text-sm text-neutral-500 px-3 py-1"
          >
            Cancel
          </button>
          <button
            disabled={loading}
            className="rounded bg-black text-white text-sm px-4 py-1 disabled:opacity-50"
          >
            {loading ? "Posting…" : "Post"}
          </button>
        </div>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </form>
  );
}
