import { ApiError } from "@/lib/api";

type ValidationIssue = { loc: (string | number)[]; msg: string };

export function parseApiFieldErrors(err: unknown): Record<string, string> {
  if (!(err instanceof ApiError) || err.status !== 422) return {};
  const detail = err.detail;
  // FastAPI 422 detail can be: array of issues, or {detail: [...]} wrapper.
  let issues: ValidationIssue[] | null = null;
  if (Array.isArray(detail)) {
    issues = detail as ValidationIssue[];
  } else if (
    detail &&
    typeof detail === "object" &&
    "detail" in detail &&
    Array.isArray((detail as { detail: unknown }).detail)
  ) {
    issues = (detail as { detail: ValidationIssue[] }).detail;
  }
  if (!issues) return {};

  const out: Record<string, string> = {};
  for (const item of issues) {
    const field = item.loc[item.loc.length - 1];
    if (typeof field === "string") {
      out[field] = item.msg;
    }
  }
  return out;
}

export function apiErrorMessage(err: unknown, fallback: string): string {
  if (err instanceof ApiError) return err.message || fallback;
  if (err instanceof Error && err.message) return err.message;
  return fallback;
}
