"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api, ApiError, setToken } from "@/lib/api";
import { apiErrorMessage, parseApiFieldErrors } from "@/lib/auth-errors";
import { COUNTRIES } from "@/lib/countries";
import { extractEmailDomain } from "@/lib/email-domain";
import { cn } from "@/lib/utils";
import type { RegisterResponse } from "@/types";

const YEAR_OPTIONS = ["1", "2", "3", "4", "5", "Masters", "PhD"] as const;

const schema = z
  .object({
    email: z.string().email("Enter a valid university email"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string(),
    display_name: z.string().min(2, "Display name is required").max(60),
    country: z.string().length(2, "Select your country"),
    program: z.string().max(255).optional().or(z.literal("")),
    year_of_study: z.string().optional().or(z.literal("")),
    privacy_consent: z.boolean().refine((v) => v, "You must accept the privacy policy"),
  })
  .refine((d) => d.password === d.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

type FormValues = z.infer<typeof schema>;

export default function RegisterPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [domainPreview, setDomainPreview] = useState<{
    university: string | null;
    status: "allowed" | "pending" | "rejected" | null;
    message: string | null;
  }>({ university: null, status: null, message: null });
  const [lookupLoading, setLookupLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    setError,
    formState: { errors, isSubmitting, isValid },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    mode: "onChange",
    defaultValues: {
      email: "",
      password: "",
      confirmPassword: "",
      display_name: "",
      country: "DE",
      program: "",
      year_of_study: "",
      privacy_consent: false,
    },
  });

  const emailValue = watch("email");

  const lookupDomain = useCallback(async (email: string) => {
    const domain = extractEmailDomain(email);
    if (!domain || domain.length < 2) {
      setDomainPreview({ university: null, status: null, message: null });
      return;
    }
    setLookupLoading(true);
    try {
      const res = await api<{
        university: string | null;
        status?: "allowed" | "pending" | "rejected" | null;
        message?: string | null;
      }>("/universities/lookup", {
        query: { domain },
        auth: false,
      });
      setDomainPreview({
        university: res.university,
        status: res.status ?? null,
        message: res.message ?? null,
      });
    } catch {
      setDomainPreview({ university: null, status: null, message: null });
    } finally {
      setLookupLoading(false);
    }
  }, []);

  useEffect(() => {
    const t = setTimeout(() => {
      if (emailValue?.includes("@")) lookupDomain(emailValue);
    }, 300);
    return () => clearTimeout(t);
  }, [emailValue, lookupDomain]);

  async function onSubmit(values: FormValues) {
    setFormError(null);
    try {
      const res = await api<RegisterResponse>("/auth/register", {
        method: "POST",
        auth: false,
        body: {
          email: values.email,
          password: values.password,
          display_name: values.display_name,
          country: values.country,
          program: values.program || undefined,
          year_of_study: values.year_of_study || undefined,
          privacy_consent: values.privacy_consent,
        },
      });
      sessionStorage.setItem("cv_pending_email", res.email);
      if (res.is_verified && res.access_token) {
        setToken(res.access_token);
        router.push(res.next || "/dashboard");
      } else if (res.is_verified) {
        router.push("/login");
      } else {
        router.push(`/verify-pending?email=${encodeURIComponent(res.email)}`);
      }
    } catch (err) {
      const fields = parseApiFieldErrors(err);
      for (const [key, msg] of Object.entries(fields)) {
        setError(key as keyof FormValues, { message: msg });
      }
      if (Object.keys(fields).length === 0) {
        setFormError(apiErrorMessage(err, "Registration failed"));
      }
    }
  }

  return (
    <main className="mx-auto max-w-5xl py-10 px-4">
      <div className="grid gap-10 md:grid-cols-2 md:gap-12 items-start">
        <div className="space-y-3">
          <h1 className="text-3xl font-semibold tracking-tight">Join CampusVoice</h1>
          <p className="text-muted-foreground">
            Verified students only. We check your university email.
          </p>
        </div>

        <Card>
          <CardContent className="pt-6 space-y-4">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium" htmlFor="email">
                  University email
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@srh.de"
                  suppressHydrationWarning
                  {...register("email")}
                  onBlur={() => emailValue && lookupDomain(emailValue)}
                />
                {errors.email && (
                  <p className="text-xs text-destructive">{errors.email.message}</p>
                )}
                {lookupLoading && (
                  <p className="text-xs text-muted-foreground">Checking domain…</p>
                )}
                {!lookupLoading && domainPreview.status === "allowed" && (
                  <p className="text-xs rounded-md border border-green-200 bg-green-50 text-green-800 dark:border-green-900 dark:bg-green-950 dark:text-green-300 px-2 py-1.5">
                    ✓ {domainPreview.university ?? "Recognised university domain"}
                  </p>
                )}
                {!lookupLoading && domainPreview.status === "pending" && emailValue?.includes("@") && (
                  <p className="text-xs rounded-md border border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200 px-2 py-1.5">
                    {domainPreview.message ??
                      "We don't recognise this domain yet — we'll review it within 24 hours and email you when your account is active."}
                  </p>
                )}
                {!lookupLoading && domainPreview.status === "rejected" && emailValue?.includes("@") && (
                  <p className="text-xs rounded-md border border-destructive/30 bg-destructive/10 text-destructive px-2 py-1.5">
                    {domainPreview.message ??
                      "Email domain not allowed. We only accept verified university emails."}
                  </p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium" htmlFor="password">
                  Password
                </label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    suppressHydrationWarning
                    {...register("password")}
                  />
                  <button
                    type="button"
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-muted-foreground"
                    onClick={() => setShowPassword((s) => !s)}
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </div>
                {errors.password && (
                  <p className="text-xs text-destructive">{errors.password.message}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium" htmlFor="confirmPassword">
                  Confirm password
                </label>
                <Input
                  id="confirmPassword"
                  type={showPassword ? "text" : "password"}
                  suppressHydrationWarning
                  {...register("confirmPassword")}
                />
                {errors.confirmPassword && (
                  <p className="text-xs text-destructive">{errors.confirmPassword.message}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium" htmlFor="display_name">
                  Display name
                </label>
                <Input
                  id="display_name"
                  suppressHydrationWarning
                  {...register("display_name")}
                />
                {errors.display_name && (
                  <p className="text-xs text-destructive">{errors.display_name.message}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium" htmlFor="country">
                  Country
                </label>
                <select
                  id="country"
                  suppressHydrationWarning
                  className={cn(
                    "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                  )}
                  {...register("country")}
                >
                  {COUNTRIES.map((c) => (
                    <option key={c.code} value={c.code}>
                      {c.flag} {c.name}
                    </option>
                  ))}
                </select>
                {errors.country && (
                  <p className="text-xs text-destructive">{errors.country.message}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium" htmlFor="program">
                  Program / major <span className="text-muted-foreground">(optional)</span>
                </label>
                <Input
                  id="program"
                  placeholder="e.g. MSc AI/ML"
                  suppressHydrationWarning
                  {...register("program")}
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium" htmlFor="year_of_study">
                  Year of study <span className="text-muted-foreground">(optional)</span>
                </label>
                <select
                  id="year_of_study"
                  suppressHydrationWarning
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                  {...register("year_of_study")}
                >
                  <option value="">—</option>
                  {YEAR_OPTIONS.map((y) => (
                    <option key={y} value={y}>
                      {y}
                    </option>
                  ))}
                </select>
              </div>

              <label className="flex items-start gap-2 text-sm">
                <input type="checkbox" className="mt-1" {...register("privacy_consent")} />
                <span>
                  I agree to the{" "}
                  <Link
                    href="/privacy"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:text-foreground"
                  >
                    Privacy Policy
                  </Link>{" "}
                  and confirm I&apos;m a current student at this institution.
                </span>
              </label>
              {errors.privacy_consent && (
                <p className="text-xs text-destructive">{errors.privacy_consent.message}</p>
              )}

              {formError && <p className="text-sm text-destructive">{formError}</p>}

              <Button type="submit" className="w-full" disabled={isSubmitting || !isValid}>
                {isSubmitting ? "Creating account…" : "Create account"}
              </Button>
            </form>

            <p className="text-sm text-center text-muted-foreground">
              Already have an account?{" "}
              <Link href="/login" className="underline hover:text-foreground">
                Log in →
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
