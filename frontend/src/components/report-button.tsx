"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Flag } from "lucide-react";
import { useRouter, usePathname } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { api, ApiError, getToken } from "@/lib/api";
import { cn } from "@/lib/utils";

export type ReportReason =
  | "names_individual"
  | "defamation"
  | "harassment"
  | "spam"
  | "hate_speech"
  | "sexual_content"
  | "other";

const REASONS: { value: ReportReason; label: string }[] = [
  { value: "names_individual", label: "Names an individual" },
  { value: "defamation", label: "Defamation" },
  { value: "harassment", label: "Harassment" },
  { value: "spam", label: "Spam" },
  { value: "hate_speech", label: "Hate speech" },
  { value: "sexual_content", label: "Sexual content" },
  { value: "other", label: "Other" },
];

type Props = {
  targetType: "post" | "comment";
  targetId: string;
  className?: string;
};

export function ReportButton({ targetType, targetId, className }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState<ReportReason>("harassment");
  const [detail, setDetail] = useState("");

  const authed = !!getToken();

  const { data: pendingCheck } = useQuery({
    queryKey: ["report-pending", targetType, targetId],
    queryFn: () =>
      api<{ pending: boolean }>("/reports/pending", {
        query: { target_type: targetType, target_id: targetId },
      }),
    enabled: authed,
    staleTime: 60_000,
  });

  const alreadyReported = pendingCheck?.pending === true;

  const submitMutation = useMutation({
    mutationFn: () =>
      api<{ id: string }>("/reports", {
        method: "POST",
        body: {
          target_type: targetType,
          target_id: targetId,
          reason,
          detail: detail.trim() || undefined,
        },
      }),
    onSuccess: () => {
      toast({
        title: "Thanks. Our team will review within 48 hours.",
      });
      setOpen(false);
      setDetail("");
      queryClient.setQueryData(["report-pending", targetType, targetId], {
        pending: true,
      });
    },
    onError: (err) => {
      if (err instanceof ApiError && err.status === 409) {
        queryClient.setQueryData(["report-pending", targetType, targetId], {
          pending: true,
        });
        return;
      }
      toast({
        variant: "destructive",
        title: err instanceof ApiError ? err.message : "Could not submit report",
      });
    },
  });

  function handleClick() {
    if (!getToken()) {
      const next = encodeURIComponent(pathname);
      router.push(`/login?next=${next}`);
      return;
    }
    if (!alreadyReported) setOpen(true);
  }

  const label = targetType === "post" ? "post" : "comment";

  return (
    <>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className={cn("h-8 w-8 text-muted-foreground", className)}
        onClick={handleClick}
        disabled={alreadyReported}
        title={
          alreadyReported
            ? "You've already reported this. Our team is reviewing."
            : "Report"
        }
        aria-label={alreadyReported ? "Already reported" : "Report"}
      >
        <Flag className="h-4 w-4" />
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Report this {label}</DialogTitle>
          </DialogHeader>
          <fieldset className="space-y-2">
            <legend className="text-sm font-medium mb-2">Reason</legend>
            {REASONS.map((r) => (
              <label
                key={r.value}
                className="flex items-center gap-2 text-sm cursor-pointer"
              >
                <input
                  type="radio"
                  name="report-reason"
                  value={r.value}
                  checked={reason === r.value}
                  onChange={() => setReason(r.value)}
                  className="accent-primary"
                />
                {r.label}
              </label>
            ))}
          </fieldset>
          <div className="space-y-1">
            <label htmlFor="report-detail" className="text-sm font-medium">
              Details (optional)
            </label>
            <Textarea
              id="report-detail"
              value={detail}
              onChange={(e) => setDetail(e.target.value.slice(0, 1000))}
              rows={3}
              maxLength={1000}
              placeholder="Add context for moderators…"
            />
            <p className="text-xs text-muted-foreground text-right">
              {detail.length}/1000
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => submitMutation.mutate()}
              disabled={submitMutation.isPending}
            >
              {submitMutation.isPending ? "Submitting…" : "Submit report"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
