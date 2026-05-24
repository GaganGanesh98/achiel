"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api, ApiError } from "@/lib/api";

function ResetPasswordForm() {
  const router = useRouter();
  const params = useSearchParams();
  const token = params.get("token") ?? "";
  const [error, setError] = useState<string | null>(
    token ? null : "Missing reset token. Use the link from your email."
  );
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!token) return;
    setError(null);
    setLoading(true);
    const fd = new FormData(e.currentTarget);
    const newPassword = String(fd.get("new_password"));
    const confirm = String(fd.get("confirm_password"));
    if (newPassword !== confirm) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }
    try {
      await api("/auth/reset-password", {
        method: "POST",
        auth: false,
        body: { token, new_password: newPassword },
      });
      router.push("/login?reset=1");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not reset password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-md py-16 px-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Set a new password</CardTitle>
        </CardHeader>
        <CardContent>
          {token ? (
            <form onSubmit={onSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium" htmlFor="new_password">
                  New password
                </label>
                <Input
                  id="new_password"
                  name="new_password"
                  type="password"
                  required
                  minLength={8}
                  maxLength={128}
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium" htmlFor="confirm_password">
                  Confirm password
                </label>
                <Input
                  id="confirm_password"
                  name="confirm_password"
                  type="password"
                  required
                  minLength={8}
                  maxLength={128}
                />
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Updating…" : "Update password"}
              </Button>
            </form>
          ) : (
            <p className="text-sm text-destructive">{error}</p>
          )}
          <p className="text-sm text-center text-muted-foreground mt-6">
            <Link href="/login" className="underline hover:text-foreground">
              Back to log in
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<main className="p-8 text-sm text-muted-foreground">Loading…</main>}>
      <ResetPasswordForm />
    </Suspense>
  );
}
