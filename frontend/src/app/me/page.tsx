"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { api, ApiError, clearToken } from "@/lib/api";
import type { User } from "@/types";

export default function MePage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const { data: user, isLoading, error: loadError } = useQuery({
    queryKey: ["me"],
    queryFn: () => api<User>("/auth/me"),
    retry: false,
  });

  useEffect(() => {
    if (loadError instanceof ApiError && loadError.status === 401) {
      router.replace("/login");
    }
  }, [loadError, router]);

  const update = useMutation({
    mutationFn: (body: {
      display_name: string;
      country: string | null;
      program?: string | null;
      year_of_study?: string | null;
    }) => api<User>("/auth/me", { method: "PATCH", body }),
    onSuccess: (updated) => {
      queryClient.setQueryData(["me"], updated);
      setSaved(true);
      setError(null);
      setTimeout(() => setSaved(false), 2000);
    },
    onError: (err) => {
      setSaved(false);
      setError(err instanceof ApiError ? err.message : "Could not save changes");
    },
  });

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const countryRaw = String(fd.get("country") ?? "").trim();
    update.mutate({
      display_name: String(fd.get("display_name")),
      country: countryRaw ? countryRaw.toUpperCase() : null,
      program: String(fd.get("program") ?? "") || null,
      year_of_study: String(fd.get("year_of_study") ?? "") || null,
    });
  }

  function signOut() {
    clearToken();
    queryClient.clear();
    router.push("/login");
  }

  if (isLoading) {
    return (
      <main className="mx-auto max-w-md py-12 px-4">
        <p className="text-sm text-muted-foreground">Loading account…</p>
      </main>
    );
  }

  if (!user) return null;

  const statusLabel = user.is_verified
    ? "Verified"
    : user.verification_status === "rejected"
      ? "Rejected"
      : "Pending email verification";

  return (
    <main className="mx-auto max-w-md py-12 px-4 space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">Account</h1>
      </header>

      <dl className="text-sm space-y-2 rounded-lg border p-4 bg-muted/30">
        <DetailRow label="Email" value={user.email} />
        <DetailRow label="Status" value={statusLabel} />
        {user.university && <DetailRow label="University" value={user.university} />}
        {user.program && <DetailRow label="Program" value={user.program} />}
        {user.year_of_study && <DetailRow label="Year of study" value={user.year_of_study} />}
        <DetailRow label="Country" value={user.country} />
        <DetailRow
          label="Member since"
          value={new Date(user.created_at).toLocaleDateString()}
        />
      </dl>

      {!user.is_verified && (
        <p className="text-sm text-amber-800 dark:text-amber-200 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-900 rounded-md px-3 py-2">
          Verify your email to post and vote.{" "}
          <Link
            href={`/verify-pending?email=${encodeURIComponent(user.email)}`}
            className="underline"
          >
            Resend verification
          </Link>
        </p>
      )}

      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="text-sm font-medium block mb-1">Display name</label>
          <input
            name="display_name"
            required
            minLength={2}
            maxLength={60}
            defaultValue={user.display_name}
            className="w-full rounded-md border border-input px-3 py-2"
          />
        </div>
        <div>
          <label className="text-sm font-medium block mb-1">Country (ISO-2)</label>
          <input
            name="country"
            maxLength={2}
            defaultValue={user.country}
            placeholder="e.g. DE"
            className="w-full rounded-md border border-input px-3 py-2"
          />
        </div>
        <div>
          <label className="text-sm font-medium block mb-1">Program</label>
          <input
            name="program"
            defaultValue={user.program ?? ""}
            className="w-full rounded-md border border-input px-3 py-2"
          />
        </div>
        <div>
          <label className="text-sm font-medium block mb-1">Year of study</label>
          <input
            name="year_of_study"
            defaultValue={user.year_of_study ?? ""}
            className="w-full rounded-md border border-input px-3 py-2"
          />
        </div>
        {error && <p className="text-sm text-destructive">{error}</p>}
        {saved && <p className="text-sm text-green-700 dark:text-green-400">Saved.</p>}
        <button
          type="submit"
          disabled={update.isPending}
          className="w-full rounded-md bg-primary text-primary-foreground py-2 disabled:opacity-50"
        >
          {update.isPending ? "Saving…" : "Save changes"}
        </button>
      </form>

      <button
        type="button"
        onClick={signOut}
        className="w-full rounded-md border border-input py-2 text-sm hover:bg-muted"
      >
        Sign out
      </button>
    </main>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-right">{value}</dd>
    </div>
  );
}
