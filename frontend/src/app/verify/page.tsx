"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { User } from "@/types";

function VerifyForm() {
  const router = useRouter();
  const params = useSearchParams();
  const email = params.get("email") ?? "";
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const token = String(new FormData(e.currentTarget).get("token"));
    try {
      await api<User>(`/auth/verify?email=${encodeURIComponent(email)}`, {
        method: "POST",
        body: { token },
        auth: false,
      });
      router.push("/login");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Verification failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-md py-12 px-4">
      <h1 className="text-2xl font-semibold mb-2">Verify your email</h1>
      <p className="text-sm text-neutral-500 mb-6">
        We sent a 6-digit code to <strong>{email}</strong>. Check your inbox (and dev console in development).
      </p>
      <form onSubmit={onSubmit} className="space-y-4">
        <input
          name="token"
          required
          inputMode="numeric"
          pattern="[0-9]{6}"
          maxLength={6}
          placeholder="6-digit code"
          className="w-full rounded border px-3 py-2 tracking-widest text-center text-lg"
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          disabled={loading}
          className="w-full rounded bg-black text-white py-2 disabled:opacity-50"
        >
          {loading ? "Verifying…" : "Verify"}
        </button>
      </form>
    </main>
  );
}

export default function VerifyPage() {
  return (
    <Suspense>
      <VerifyForm />
    </Suspense>
  );
}
