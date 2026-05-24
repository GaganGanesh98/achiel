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

  const statusLabel =
    user.verification_status === "REJECTED"
      ? "Rejected"
      : user.verification_status === "awaiting_domain_review"
        ? "Domain under review"
        : user.verification_status === "VERIFIED"
          ? "Verified"
          : user.is_verified
            ? "Verified"
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

      <SecurityCard user={user} />

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

function SecurityCard({ user }: { user: User }) {
  const [pwError, setPwError] = useState<string | null>(null);
  const [pwSuccess, setPwSuccess] = useState(false);
  const [pwLoading, setPwLoading] = useState(false);
  const [verifyMsg, setVerifyMsg] = useState<string | null>(null);
  const [verifyLoading, setVerifyLoading] = useState(false);

  async function onChangePassword(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPwError(null);
    setPwSuccess(false);
    const fd = new FormData(e.currentTarget);
    const current = String(fd.get("current_password"));
    const next = String(fd.get("new_password"));
    const confirm = String(fd.get("confirm_password"));
    if (next !== confirm) {
      setPwError("New passwords do not match");
      return;
    }
    setPwLoading(true);
    try {
      await api("/auth/change-password", {
        method: "POST",
        body: { current_password: current, new_password: next },
      });
      setPwSuccess(true);
      e.currentTarget.reset();
    } catch (err) {
      setPwError(err instanceof ApiError ? err.message : "Could not update password");
    } finally {
      setPwLoading(false);
    }
  }

  async function sendVerificationLink() {
    setVerifyMsg(null);
    setVerifyLoading(true);
    try {
      await api("/auth/request-email-verification", { method: "POST" });
      setVerifyMsg("If your account is eligible, a verification email has been sent.");
    } catch (err) {
      setVerifyMsg(
        err instanceof ApiError ? err.message : "Could not send verification email"
      );
    } finally {
      setVerifyLoading(false);
    }
  }

  return (
    <section className="rounded-lg border p-4 space-y-4">
      <h2 className="text-lg font-medium">Security</h2>

      <form onSubmit={onChangePassword} className="space-y-3">
        <p className="text-sm font-medium">Change password</p>
        <input
          name="current_password"
          type="password"
          required
          placeholder="Current password"
          className="w-full rounded-md border border-input px-3 py-2 text-sm"
        />
        <input
          name="new_password"
          type="password"
          required
          minLength={8}
          maxLength={128}
          placeholder="New password"
          className="w-full rounded-md border border-input px-3 py-2 text-sm"
        />
        <input
          name="confirm_password"
          type="password"
          required
          minLength={8}
          maxLength={128}
          placeholder="Confirm new password"
          className="w-full rounded-md border border-input px-3 py-2 text-sm"
        />
        {pwError && <p className="text-sm text-destructive">{pwError}</p>}
        {pwSuccess && (
          <p className="text-sm text-green-700 dark:text-green-400">Password updated.</p>
        )}
        <button
          type="submit"
          disabled={pwLoading}
          className="rounded-md border border-input px-3 py-2 text-sm hover:bg-muted disabled:opacity-50"
        >
          {pwLoading ? "Updating…" : "Update password"}
        </button>
      </form>

      <div className="border-t pt-4 space-y-2">
        <p className="text-sm font-medium">Email confirmation</p>
        {user.email_confirmed_at ? (
          <p className="text-sm text-muted-foreground">
            Confirmed on {new Date(user.email_confirmed_at).toLocaleString()}
          </p>
        ) : (
          <>
            <p className="text-sm text-muted-foreground">Not confirmed yet.</p>
            <button
              type="button"
              onClick={sendVerificationLink}
              disabled={verifyLoading}
              className="rounded-md border border-input px-3 py-2 text-sm hover:bg-muted disabled:opacity-50"
            >
              {verifyLoading ? "Sending…" : "Send verification link"}
            </button>
          </>
        )}
        {verifyMsg && <p className="text-sm text-muted-foreground">{verifyMsg}</p>}
      </div>
    </section>
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
