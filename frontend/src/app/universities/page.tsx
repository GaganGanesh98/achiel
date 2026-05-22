"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useMemo, useState } from "react";

import { CountrySwitcher } from "@/components/country-switcher";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { useCountry } from "@/lib/country-context";
import type { University } from "@/types";

export default function UniversitiesPage() {
  const [q, setQ] = useState("");
  const { country } = useCountry();

  const { data, isLoading } = useQuery({
    queryKey: ["universities", q, country.code],
    queryFn: () =>
      api<University[]>("/universities", {
        auth: false,
        query: {
          q: q.length >= 2 ? q : undefined,
          country: country.code,
        },
      }),
  });

  const filtered = useMemo(() => {
    if (!data) return [];
    return data.filter(
      (uni) =>
        !uni.country ||
        uni.country.toUpperCase() === country.code.toUpperCase()
    );
  }, [data, country.code]);

  return (
    <main className="mx-auto max-w-2xl py-6 px-4 space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">Universities</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Schools with verified students on CampusVoice
        </p>
      </header>

      <div className="flex flex-col sm:flex-row gap-2 sm:items-center">
        <Input
          type="search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search by name…"
          className="flex-1"
        />
        <CountrySwitcher
          trigger={
            <Button variant="secondary" className="w-full sm:w-auto shrink-0">
              Select country
            </Button>
          }
        />
      </div>

      <CountrySwitcher
        trigger={
          <button
            type="button"
            className="inline-flex items-center gap-1 rounded-md bg-muted/60 px-2 py-0.5 text-xs text-muted-foreground hover:bg-muted transition-colors"
          >
            <span aria-hidden>{country.flag}</span>
            <span>{country.name}</span>
          </button>
        }
      />

      {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}

      {!isLoading && filtered.length === 0 && (
        <div className="rounded-lg border border-dashed p-8 text-center space-y-3">
          <p className="text-sm text-muted-foreground">
            No universities match your search in {country.name} yet.
          </p>
          <Button variant="outline" asChild>
            <a href="mailto:hello@campusvoice.local">
              Invite your university
            </a>
          </Button>
        </div>
      )}

      <ul className="divide-y border rounded-lg">
        {filtered.map((uni) => (
          <li key={uni.id} className="px-4 py-3 hover:bg-muted/50">
            <Link
              href={`/dashboard?university_id=${uni.id}`}
              className="block"
            >
              <p className="font-medium">{uni.name}</p>
              <p className="text-sm text-muted-foreground">
                {uni.domain}
                {uni.city ? ` · ${uni.city}` : ""}
                {uni.country ? ` · ${uni.country}` : ""}
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
