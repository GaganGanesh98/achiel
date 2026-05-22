"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { api, getToken } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { User } from "@/types";

type ReportStatus = "pending" | "resolved_removed" | "resolved_kept" | "dismissed";

type ReportReason =
  | "names_individual"
  | "defamation"
  | "harassment"
  | "spam"
  | "hate_speech"
  | "sexual_content"
  | "other";

type Reporter = {
  id: string | null;
  display_name: string;
  email: string | null;
};

type ReportedPost = {
  type: "post";
  id: string;
  title: string;
  body: string;
  author: { display_name: string };
  created_at: string;
  is_hidden: boolean;
  hidden_reason: string | null;
};

type ReportedComment = {
  type: "comment";
  id: string;
  body: string;
  post_id: string;
  author: { display_name: string };
  created_at: string;
  is_hidden: boolean;
  hidden_reason: string | null;
};

type AdminReport = {
  id: string;
  target_type: "post" | "comment";
  target_id: string;
  reason: ReportReason;
  detail: string | null;
  status: ReportStatus;
  reporter: Reporter;
  target: ReportedPost | ReportedComment;
  created_at: string;
  resolved_at: string | null;
  resolver_note: string | null;
};

type AdminReportsPage = {
  items: AdminReport[];
  page: number;
  per_page: number;
  total: number;
  pages: number;
};

const TABS: { status: string; label: string }[] = [
  { status: "pending", label: "Pending" },
  { status: "resolved", label: "Resolved" },
  { status: "dismissed", label: "Dismissed" },
];

const REASON_LABELS: Record<ReportReason, string> = {
  names_individual: "Names individual",
  defamation: "Defamation",
  harassment: "Harassment",
  spam: "Spam",
  hate_speech: "Hate speech",
  sexual_content: "Sexual content",
  other: "Other",
};

function ReportCard({
  report,
  onResolved,
}: {
  report: AdminReport;
  onResolved: (id: string) => void;
}) {
  const [note, setNote] = useState("");
  const queryClient = useQueryClient();

  const resolveMutation = useMutation({
    mutationFn: (action: "remove" | "keep" | "dismiss") =>
      api<AdminReport>(`/admin/reports/${report.id}/resolve`, {
        method: "POST",
        body: { action, note: note.trim() || undefined },
      }),
    onSuccess: () => {
      onResolved(report.id);
      queryClient.invalidateQueries({ queryKey: ["admin-reports"] });
    },
  });

  const target = report.target;
  const isPost = target.type === "post";

  return (
    <article className="rounded-lg border border-border p-4 space-y-3">
      <div className="flex flex-wrap items-center gap-2 text-sm">
        <Badge variant="secondary">{REASON_LABELS[report.reason]}</Badge>
        <span className="text-muted-foreground">
          {new Date(report.created_at).toLocaleString()}
        </span>
      </div>

      <p className="text-sm">
        <span className="font-medium">Reporter:</span>{" "}
        {report.reporter.display_name}
        {report.reporter.email ? ` (${report.reporter.email})` : ""}
      </p>

      {report.detail && (
        <p className="text-sm text-muted-foreground">
          <span className="font-medium text-foreground">Detail:</span> {report.detail}
        </p>
      )}

      <div className="rounded-md bg-muted/40 p-3 text-sm space-y-1">
        <p className="text-xs text-muted-foreground uppercase tracking-wide">
          Reported {isPost ? "post" : "comment"}
        </p>
        {isPost ? (
          <>
            <p className="font-medium">{(target as ReportedPost).title}</p>
            <p className="whitespace-pre-wrap">{(target as ReportedPost).body}</p>
          </>
        ) : (
          <p className="whitespace-pre-wrap">{(target as ReportedComment).body}</p>
        )}
        <p className="text-xs text-muted-foreground mt-2">
          by {target.author.display_name} · {new Date(target.created_at).toLocaleString()}
        </p>
        {target.is_hidden && target.hidden_reason && (
          <p className="text-xs text-amber-700 dark:text-amber-400">
            Hidden: {target.hidden_reason}
          </p>
        )}
      </div>

      {report.status === "pending" && (
        <>
          <Textarea
            placeholder="Optional note for audit log…"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={2}
            className="text-sm"
          />
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant="destructive"
              disabled={resolveMutation.isPending}
              onClick={() => resolveMutation.mutate("remove")}
            >
              Remove content
            </Button>
            <Button
              size="sm"
              variant="secondary"
              disabled={resolveMutation.isPending}
              onClick={() => resolveMutation.mutate("keep")}
            >
              Keep content
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={resolveMutation.isPending}
              onClick={() => resolveMutation.mutate("dismiss")}
            >
              Dismiss report
            </Button>
          </div>
        </>
      )}
    </article>
  );
}

export function AdminReportsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const status = searchParams.get("status") || "pending";
  const page = Number(searchParams.get("page") || "1");

  const { data: user, isLoading: meLoading } = useQuery({
    queryKey: ["me"],
    queryFn: () => api<User>("/auth/me"),
    enabled: !!getToken(),
    retry: false,
  });

  useEffect(() => {
    if (!meLoading && user && !user.is_admin) {
      router.replace("/");
    }
    if (!meLoading && !getToken()) {
      router.replace("/login?next=/admin/reports");
    }
  }, [meLoading, user, router]);

  const { data, isLoading } = useQuery({
    queryKey: ["admin-reports", status, page],
    queryFn: () =>
      api<AdminReportsPage>("/admin/reports", {
        query: { status, page },
      }),
    enabled: !!user?.is_admin,
  });

  const [hiddenIds, setHiddenIds] = useState<Set<string>>(new Set());
  const visibleItems = data?.items.filter((r) => !hiddenIds.has(r.id)) ?? [];

  if (meLoading || !user?.is_admin) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-8">
        <p className="text-muted-foreground text-sm">Loading…</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Moderation queue</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Review reports and take action on flagged content.
        </p>
      </div>

      <nav className="flex gap-2 border-b border-border pb-2">
        {TABS.map((tab) => (
          <Link
            key={tab.status}
            href={`/admin/reports?status=${tab.status}`}
            className={cn(
              "text-sm px-3 py-1 rounded-md transition-colors",
              status === tab.status
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            {tab.label}
          </Link>
        ))}
      </nav>

      {isLoading && <p className="text-sm text-muted-foreground">Loading reports…</p>}

      {!isLoading && visibleItems.length === 0 && (
        <p className="text-sm text-muted-foreground">No reports in this tab.</p>
      )}

      <div className="space-y-4">
        {visibleItems.map((report) => (
          <ReportCard
            key={report.id}
            report={report}
            onResolved={(id) => setHiddenIds((s) => new Set(s).add(id))}
          />
        ))}
      </div>

      {data && data.pages > 1 && (
        <div className="flex gap-2 justify-center text-sm">
          {page > 1 && (
            <Link
              href={`/admin/reports?status=${status}&page=${page - 1}`}
              className="text-muted-foreground hover:text-foreground"
            >
              Previous
            </Link>
          )}
          <span className="text-muted-foreground">
            Page {page} of {data.pages}
          </span>
          {page < data.pages && (
            <Link
              href={`/admin/reports?status=${status}&page=${page + 1}`}
              className="text-muted-foreground hover:text-foreground"
            >
              Next
            </Link>
          )}
        </div>
      )}
    </main>
  );
}
