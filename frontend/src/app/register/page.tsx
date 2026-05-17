"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { User } from "@/types";

export default function RegisterPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const fd = new FormData(e.currentTarget);
    const payload = {
      email: String(fd.get("email")),
      password: String(fd.get("password")),
      display_name: String(fd.get("display_name")),
      country: (fd.get("country") as string) || undefined,
    };

    try {
      await api<User>("/auth/register", { method: "POST", body: payload, auth: false });
      // OTP is sent — go to verify page with email preserved
      router.push(`/verify?email=${encodeURIComponent(payload.email)}`);
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
      else setError("Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-md py-12 px-4">
      <h1 className="text-2xl font-semibold mb-2">Create your account</h1>
      <p className="text-sm text-neutral-500 mb-6">
        Must be a student. We verify via your university email domain.
      </p>
      <form onSubmit={onSubmit} className="space-y-4">
        <input
          name="email"
          type="email"
          required
          placeholder="you@university.edu"
          className="w-full rounded border px-3 py-2"
        />
        <input
          name="display_name"
          required
          minLength={2}
          maxLength={60}
          placeholder="Display name"
          className="w-full rounded border px-3 py-2"
        />
        <input
          name="country"
          maxLength={2}
          placeholder="Country (ISO-2, e.g. DE)"
          className="w-full rounded border px-3 py-2"
        />
        <input
          name="password"
          type="password"
          required
          minLength={8}
          placeholder="Password (8+ chars)"
          className="w-full rounded border px-3 py-2"
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          disabled={loading}
          className="w-full rounded bg-black text-white py-2 disabled:opacity-50"
        >
          {loading ? "Creating…" : "Create account"}
        </button>
      </form>
    </main>
  );
}
