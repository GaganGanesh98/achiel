"use client";

import { Mail } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api } from "@/lib/api";

function VerifyPendingContent() {
  const params = useSearchParams();
  const router = useRouter();
  const [resending, setResending] = useState(false);
  const [resent, setResent] = useState(false);

  const email =
    params.get("email") ??
    (typeof window !== "undefined" ? sessionStorage.getItem("cv_pending_email") : null) ??
    "your email";

  async function resend() {
    if (!email || email === "your email") return;
    setResending(true);
    setResent(false);
    try {
      await api("/auth/resend-verification", {
        method: "POST",
        auth: false,
        body: { email },
      });
      setResent(true);
    } finally {
      setResending(false);
    }
  }

  return (
    <main className="mx-auto max-w-md py-16 px-4">
      {process.env.NODE_ENV === "development" && (
        <div className="rounded-md border border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200 text-xs px-3 py-2 mb-6">
          Dev mode: check your backend terminal for the verification link.
        </div>
      )}

      <Card>
        <CardContent className="pt-8 pb-6 text-center space-y-4">
          <Mail className="h-12 w-12 mx-auto text-muted-foreground" />
          <h1 className="text-2xl font-semibold">Check your email</h1>
          <p className="text-sm text-muted-foreground">
            We sent a verification link to <strong className="text-foreground">{email}</strong>.
            Click it to activate your account.
          </p>

          <Button
            variant="outline"
            className="w-full"
            disabled={resending}
            onClick={resend}
          >
            {resending ? "Sending…" : "Resend verification"}
          </Button>
          {resent && (
            <p className="text-xs text-green-700 dark:text-green-400">
              If an account exists, a new link was logged on the server.
            </p>
          )}

          <p className="text-sm text-muted-foreground">
            <Link href="/register" className="underline hover:text-foreground">
              Wrong email?
            </Link>
          </p>

          <Button variant="ghost" className="w-full" onClick={() => router.push("/login")}>
            Back to log in
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}

export default function VerifyPendingPage() {
  return (
    <Suspense fallback={<main className="p-8 text-sm text-muted-foreground">Loading…</main>}>
      <VerifyPendingContent />
    </Suspense>
  );
}
