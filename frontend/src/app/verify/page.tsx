"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api, ApiError } from "@/lib/api";

function VerifyContent() {
  const params = useSearchParams();
  const router = useRouter();
  const token = params.get("token") ?? "";
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    token ? "loading" : "error"
  );
  const [message, setMessage] = useState(
    token ? "" : "Missing verification token. Use the link from your email."
  );

  useEffect(() => {
    if (!token) return;

    let cancelled = false;

    (async () => {
      try {
        await api("/auth/verify", {
          method: "POST",
          auth: false,
          body: { token },
        });
        if (cancelled) return;
        setStatus("success");
        setMessage("Your account is verified. Redirecting…");
        setTimeout(() => router.push("/login"), 2000);
      } catch (err) {
        if (cancelled) return;
        setStatus("error");
        setMessage(
          err instanceof ApiError ? err.message : "Verification failed. Try again."
        );
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [token, router]);

  return (
    <main className="mx-auto max-w-md py-16 px-4">
      <Card>
        <CardContent className="pt-8 pb-6 text-center space-y-4">
          {status === "loading" && (
            <>
              <p className="text-sm text-muted-foreground">Verifying your account…</p>
              <div className="h-8 w-8 mx-auto border-2 border-primary border-t-transparent rounded-full animate-spin" />
            </>
          )}
          {status === "success" && (
            <p className="text-sm text-green-700 dark:text-green-400">{message}</p>
          )}
          {status === "error" && (
            <>
              <p className="text-sm text-destructive">{message}</p>
              <Button asChild variant="outline">
                <Link href="/verify-pending">Request a new link</Link>
              </Button>
            </>
          )}
        </CardContent>
      </Card>
    </main>
  );
}

export default function VerifyPage() {
  return (
    <Suspense fallback={<main className="p-8 text-sm text-muted-foreground">Loading…</main>}>
      <VerifyContent />
    </Suspense>
  );
}
