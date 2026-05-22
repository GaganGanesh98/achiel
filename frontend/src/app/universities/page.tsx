"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";

import { api } from "@/lib/api";
import type { University } from "@/types";

export default function UniversitiesPage() {
  const [q, setQ] = useState("");
  const [country, setCountry] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["universities", q, country],
    queryFn: () =>
      api<University[]>("/universities", {
        auth: false,
        query: {
          q: q.length >= 2 ? q : undefined,
          country: country.length === 2 ? country : undefined,
        },
      }),
  });

  return (
    <main className="mx-auto max-w-2xl py-6 px-4 space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Universities</h1>
          <p className="text-sm text-neutral-500 mt-1">
            Schools with verified students on CampusVoice
          </p>
        </div>
        <Link href="/dashboard" className="text-sm text-neutral-600 hover:text-black">
          Dashboard
        </Link>
      </header>

      <div className="flex flex-col sm:flex-row gap-2">
        <input
          type="search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search by name…"
          className="flex-1 rounded border px-3 py-2 text-sm"
        />
        <input
          value={country}
          onChange={(e) => setCountry(e.target.value.toUpperCase())}
          maxLength={2}
          placeholder="Country (ISO-2)"
          className="w-full sm:w-28 rounded border px-3 py-2 text-sm"
        />
      </div>

      {isLoading && <p className="text-sm text-neutral-500">Loading…</p>}

      {!isLoading && data?.length === 0 && (
        <p className="text-sm text-neutral-500">No universities match your filters.</p>
      )}

      <ul className="divide-y border rounded-lg">
        {data?.map((uni) => (
          <li key={uni.id} className="px-4 py-3 hover:bg-neutral-50">
            <Link
              href={`/dashboard?university_id=${uni.id}`}
              className="block"
            >
              <p className="font-medium">{uni.name}</p>
              <p className="text-sm text-neutral-500">
                {uni.domain}
                {uni.city ? ` · ${uni.city}` : ""} · {uni.country}
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
