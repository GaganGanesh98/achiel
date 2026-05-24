"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api, ApiError } from "@/lib/api";

function VerifyEmailContent() {
  const params = useSearchParams();
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
        await api("/auth/verify-email", {
          method: "POST",
          auth: false,
          body: { token },
        });
        if (cancelled) return;
        setStatus("success");
        setMessage("Your email is confirmed.");
      } catch (err) {
        if (cancelled) return;
        setStatus("error");
        setMessage(
          err instanceof ApiError ? err.message : "Link expired or invalid."
        );
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <main className="mx-auto max-w-md py-16 px-4">
      <Card>
        <CardContent className="pt-8 pb-6 text-center space-y-4">
          {status === "loading" && (
            <>
              <p className="text-sm text-muted-foreground">Confirming your email…</p>
              <div className="h-8 w-8 mx-auto border-2 border-primary border-t-transparent rounded-full animate-spin" />
            </>
          )}
          {status === "success" && (
            <>
              <p className="text-sm text-green-700 dark:text-green-400">{message}</p>
              <Button asChild variant="outline">
                <Link href="/me">Go to account</Link>
              </Button>
            </>
          )}
          {status === "error" && (
            <>
              <p className="text-sm text-destructive">{message}</p>
              <Button asChild variant="outline">
                <Link href="/me">Account settings</Link>
              </Button>
            </>
          )}
        </CardContent>
      </Card>
    </main>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<main className="p-8 text-sm text-muted-foreground">Loading…</main>}>
      <VerifyEmailContent />
    </Suspense>
  );
}
