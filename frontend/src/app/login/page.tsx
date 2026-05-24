"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api, ApiError, setToken } from "@/lib/api";
import type { AuthToken } from "@/types";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = searchParams.get("next") ?? "/dashboard";
  const [error, setError] = useState<string | null>(null);
  const [unverified, setUnverified] = useState(false);
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setUnverified(false);
    setLoading(true);
    const fd = new FormData(e.currentTarget);
    const loginEmail = String(fd.get("email"));
    setEmail(loginEmail);
    try {
      const tok = await api<AuthToken>("/auth/login", {
        method: "POST",
        body: { email: loginEmail, password: fd.get("password") },
        auth: false,
      });
      setToken(tok.access_token);
      router.push(next.startsWith("/") ? next : "/dashboard");
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          setError("Wrong email or password.");
        } else if (
          err.status === 403 &&
          err.message.toLowerCase().includes("verified")
        ) {
          setUnverified(true);
          setError(null);
        } else {
          setError(err.message);
        }
      } else {
        setError("Login failed");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-md py-16 px-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Log in</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium" htmlFor="email">
                Email
              </label>
              <Input
                id="email"
                name="email"
                type="email"
                required
                placeholder="you@university.edu"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium" htmlFor="password">
                Password
              </label>
              <Input id="password" name="password" type="password" required />
            </div>

            {error && <p className="text-sm text-destructive">{error}</p>}

            {unverified && (
              <p className="text-sm text-amber-800 dark:text-amber-200 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-900 rounded-md px-3 py-2">
                Your email isn&apos;t verified yet.{" "}
                <Link
                  href={`/verify-pending?email=${encodeURIComponent(email)}`}
                  className="underline font-medium"
                >
                  Resend verification email
                </Link>
              </p>
            )}

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Signing in…" : "Log in"}
            </Button>
            <p className="text-sm text-center">
              <Link
                href="/forgot-password"
                className="text-muted-foreground underline hover:text-foreground"
              >
                Forgot password?
              </Link>
            </p>
          </form>

          <p className="text-sm text-center text-muted-foreground mt-6">
            New here?{" "}
            <Link href="/register" className="underline hover:text-foreground">
              Create an account →
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<main className="p-8 text-sm text-muted-foreground">Loading…</main>}>
      <LoginForm />
    </Suspense>
  );
}
