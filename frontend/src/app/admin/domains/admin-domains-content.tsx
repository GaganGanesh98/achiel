"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { api, getToken } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { User } from "@/types";

type PendingDomain = {
  domain: string;
  first_seen_email: string;
  request_count: number;
  confidence: "high" | "low";
  country_hint: string | null;
  first_seen_at: string;
  last_seen_at: string;
  status: string;
};

export function AdminDomainsContent() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [rejectDomain, setRejectDomain] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState("");

  const { data: me } = useQuery({
    queryKey: ["me"],
    queryFn: () => api<User>("/auth/me"),
    enabled: !!getToken(),
    retry: false,
  });

  useEffect(() => {
    if (me && !me.is_admin) router.replace("/dashboard");
  }, [me, router]);

  const { data: domains = [], isLoading } = useQuery({
    queryKey: ["admin-pending-domains"],
    queryFn: () => api<PendingDomain[]>("/admin/pending-domains"),
    enabled: !!me?.is_admin,
  });

  const approveMutation = useMutation({
    mutationFn: (domain: string) =>
      api<PendingDomain>(`/admin/pending-domains/${encodeURIComponent(domain)}/approve`, {
        method: "POST",
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-pending-domains"] }),
  });

  const rejectMutation = useMutation({
    mutationFn: ({ domain, reason }: { domain: string; reason: string }) =>
      api<PendingDomain>(`/admin/pending-domains/${encodeURIComponent(domain)}/reject`, {
        method: "POST",
        body: { reason },
      }),
    onSuccess: () => {
      setRejectDomain(null);
      setRejectReason("");
      queryClient.invalidateQueries({ queryKey: ["admin-pending-domains"] });
    },
  });

  if (!me?.is_admin) {
    return (
      <main className="mx-auto max-w-5xl px-4 py-10 text-sm text-muted-foreground">
        Loading…
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-5xl px-4 py-10 space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Pending domains</h1>
          <p className="text-sm text-muted-foreground">
            Review signup domains awaiting approval.
          </p>
        </div>
        <Link
          href="/admin/reports"
          className="text-sm text-muted-foreground underline hover:text-foreground"
        >
          Reports →
        </Link>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}

      {!isLoading && domains.length === 0 && (
        <p className="text-sm text-muted-foreground">No pending domains.</p>
      )}

      <div className="overflow-x-auto rounded-md border">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50 text-left">
              <th className="p-3 font-medium">Domain</th>
              <th className="p-3 font-medium">Confidence</th>
              <th className="p-3 font-medium">Requests</th>
              <th className="p-3 font-medium">First email</th>
              <th className="p-3 font-medium">Last seen</th>
              <th className="p-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {domains.map((row) => (
              <tr key={row.domain} className="border-b last:border-0">
                <td className="p-3 font-mono text-xs">{row.domain}</td>
                <td className="p-3">
                  <Badge
                    variant="outline"
                    className={cn(
                      row.confidence === "high"
                        ? "border-green-600 text-green-700"
                        : "border-amber-600 text-amber-700"
                    )}
                  >
                    {row.confidence}
                  </Badge>
                </td>
                <td className="p-3">{row.request_count}</td>
                <td className="p-3 text-xs text-muted-foreground">{row.first_seen_email}</td>
                <td className="p-3 text-xs text-muted-foreground">
                  {new Date(row.last_seen_at).toLocaleString()}
                </td>
                <td className="p-3 space-x-2">
                  <Button
                    size="sm"
                    disabled={approveMutation.isPending}
                    onClick={() => approveMutation.mutate(row.domain)}
                  >
                    Approve
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setRejectDomain(row.domain);
                      setRejectReason("");
                    }}
                  >
                    Reject
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {rejectDomain && (
        <div className="rounded-md border p-4 space-y-3 max-w-lg">
          <p className="text-sm font-medium">Reject {rejectDomain}</p>
          <Textarea
            placeholder="Reason shown to affected users"
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            rows={3}
          />
          <div className="flex gap-2">
            <Button
              variant="destructive"
              size="sm"
              disabled={rejectReason.length < 3 || rejectMutation.isPending}
              onClick={() =>
                rejectMutation.mutate({ domain: rejectDomain, reason: rejectReason })
              }
            >
              Confirm reject
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setRejectDomain(null)}>
              Cancel
            </Button>
          </div>
        </div>
      )}
    </main>
  );
}
