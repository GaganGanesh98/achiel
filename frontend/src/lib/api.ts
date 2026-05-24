import Cookies from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const TOKEN_COOKIE = "cv_token";

export class ApiError extends Error {
  constructor(public status: number, message: string, public detail?: unknown) {
    super(message);
  }
}

export function setToken(token: string) {
  Cookies.set(TOKEN_COOKIE, token, {
    expires: 7,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
  });
}

export function clearToken() {
  Cookies.remove(TOKEN_COOKIE);
}

export function getToken(): string | undefined {
  return Cookies.get(TOKEN_COOKIE);
}

type Method = "GET" | "POST" | "PATCH" | "PUT" | "DELETE";

interface ApiOptions {
  method?: Method;
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined | null>;
  auth?: boolean; // default true
}

export async function api<T>(path: string, opts: ApiOptions = {}): Promise<T> {
  const { method = "GET", body, query, auth = true } = opts;

  const url = new URL(`${API_URL}${path}`);
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, String(v));
    }
  }

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  let res: Response;
  try {
    res = await fetch(url.toString(), {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      cache: "no-store",
    });
  } catch (e) {
    // Network failure / CORS / backend down. Surface a useful message
    // instead of letting the caller fall back to a generic string.
    const reason = e instanceof Error ? e.message : "Network error";
    throw new ApiError(
      0,
      `Couldn't reach the API at ${API_URL}. Is the backend running? (${reason})`,
      { cause: e },
    );
  }

  if (!res.ok) {
    let detail: unknown;
    try {
      detail = await res.json();
    } catch {
      detail = await res.text();
    }
    let msg = res.statusText || `HTTP ${res.status}`;
    if (typeof detail === "object" && detail && "detail" in detail) {
      const d = (detail as { detail: unknown }).detail;
      // FastAPI 422 returns an array of {loc, msg, ...} — flatten for display.
      if (Array.isArray(d)) {
        msg =
          d
            .map((item) => {
              const v = item as { msg?: string; loc?: unknown[] };
              const field = Array.isArray(v.loc) ? v.loc[v.loc.length - 1] : "";
              return field ? `${field}: ${v.msg}` : v.msg;
            })
            .filter(Boolean)
            .join("; ") || msg;
      } else if (typeof d === "string") {
        msg = d;
      }
    } else if (typeof detail === "string" && detail) {
      msg = detail;
    }
    throw new ApiError(res.status, msg, detail);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}
