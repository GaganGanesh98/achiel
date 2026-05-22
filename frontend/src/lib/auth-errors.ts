import { ApiError } from "@/lib/api";

type ValidationIssue = { loc: (string | number)[]; msg: string };

export function parseApiFieldErrors(err: unknown): Record<string, string> {
  if (!(err instanceof ApiError) || err.status !== 422) return {};
  const detail = err.detail;
  if (!Array.isArray(detail)) return {};

  const out: Record<string, string> = {};
  for (const item of detail as ValidationIssue[]) {
    const field = item.loc[item.loc.length - 1];
    if (typeof field === "string") {
      out[field] = item.msg;
    }
  }
  return out;
}

export function apiErrorMessage(err: unknown, fallback: string): string {
  if (err instanceof ApiError) return err.message;
  return fallback;
}
