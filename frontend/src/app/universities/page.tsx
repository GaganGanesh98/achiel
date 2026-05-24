"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useEffect, useState } from "react";

import { TypeBadge } from "@/components/type-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";
import type { University } from "@/types";

function useDebounced(value: string, ms: number) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), ms);
    return () => clearTimeout(id);
  }, [value, ms]);
  return debounced;
}

function UniversityListRow({ uni }: { uni: University }) {
  return (
    <>
      <div className="flex items-center gap-2 flex-wrap">
        <p className="font-medium">{uni.name}</p>
        {uni.short_name && (
          <span className="text-xs text-muted-foreground">({uni.short_name})</span>
        )}
        <TypeBadge type={uni.type} />
      </div>
      <p className="text-sm text-muted-foreground">
        {[uni.city, uni.state].filter(Boolean).join(" · ")}
        {(uni.verified_student_count ?? 0) > 0
          ? ` · ${uni.verified_student_count} ${t("universities.verifiedStudents")}`
          : ` · ${t("universities.beFirst")}`}
      </p>
    </>
  );
}

export default function UniversitiesPage() {
  const [q, setQ] = useState("");
  const debounced = useDebounced(q, 250);

  const { data, isLoading } = useQuery({
    queryKey: ["universities", debounced],
    queryFn: () =>
      api<University[]>("/universities", {
        auth: false,
        query: debounced.length >= 1 ? { q: debounced } : undefined,
      }),
  });

  const suggestMailto = `mailto:hello@campusvoice.app?subject=${encodeURIComponent(
    `Add ${debounced || "a university"} to CampusVoice`
  )}`;

  return (
    <main className="mx-auto max-w-2xl py-6 px-4 space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">{t("universities.title")}</h1>
        <p className="text-sm text-muted-foreground mt-1">{t("universities.subtitle")}</p>
      </header>

      <Input
        type="search"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder={t("universities.searchPlaceholder")}
      />

      {isLoading && (
        <p className="text-sm text-muted-foreground">{t("universities.loading")}</p>
      )}

      {!isLoading && (data?.length ?? 0) === 0 && debounced.length >= 1 && (
        <EmptyState suggestMailto={suggestMailto} />
      )}

      <ul className="divide-y border rounded-lg">
        {data?.map((uni) => (
          <li key={uni.id} className="px-4 py-3 hover:bg-muted/50">
            <Link href={`/dashboard?university_id=${uni.id}`} className="block">
              <UniversityListRow uni={uni} />
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}

function EmptyState({ suggestMailto }: { suggestMailto: string }) {
  return (
    <div className="rounded-lg border border-dashed p-8 text-center space-y-3">
      <p className="text-sm text-muted-foreground">{t("universities.noResults")}</p>
      <Button variant="outline" asChild>
        <a href={suggestMailto}>{t("universities.suggest")}</a>
      </Button>
    </div>
  );
}
