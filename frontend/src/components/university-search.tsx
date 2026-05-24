"use client";

import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { TypeBadge } from "@/components/type-badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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

function SearchResultInner({ uni }: { uni: University }) {
  return (
    <>
      <div className="flex items-center gap-2">
        <span className="font-medium text-sm">{uni.name}</span>
        {uni.short_name && (
          <span className="text-xs text-muted-foreground">({uni.short_name})</span>
        )}
        <TypeBadge type={uni.type} />
      </div>
      <p className="text-xs text-muted-foreground mt-0.5">
        {[uni.city, uni.state].filter(Boolean).join(" · ")}
      </p>
    </>
  );
}

export function UniversitySearch({ compact = false }: { compact?: boolean }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const debounced = useDebounced(q, 250);

  const { data, isLoading } = useQuery({
    queryKey: ["university-search", debounced],
    queryFn: () =>
      api<University[]>("/universities", {
        auth: false,
        query: debounced.length >= 1 ? { q: debounced } : undefined,
      }),
    enabled: open && debounced.length >= 1,
  });

  const onKeyDown = useCallback((e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      setOpen(true);
    }
  }, []);

  useEffect(() => {
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onKeyDown]);

  function selectUniversity(uni: University) {
    setOpen(false);
    setQ("");
    router.push(`/dashboard?university_id=${uni.id}`);
  }

  return (
    <>
      <Button
        variant={compact ? "ghost" : "outline"}
        size="sm"
        className="gap-2 text-muted-foreground"
        onClick={() => setOpen(true)}
      >
        <Search className="h-4 w-4" />
        {!compact && <span>{t("search.shortcut")}</span>}
        {!compact && (
          <kbd className="hidden sm:inline text-[10px] bg-muted px-1 rounded">⌘K</kbd>
        )}
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-md p-0 gap-0">
          <DialogHeader className="p-4 pb-2">
            <DialogTitle className="sr-only">{t("search.placeholder")}</DialogTitle>
            <Input
              autoFocus
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder={t("search.placeholder")}
              className="border-0 shadow-none focus-visible:ring-0"
            />
          </DialogHeader>
          <ul className="max-h-72 overflow-y-auto border-t">
            {isLoading && (
              <li className="px-4 py-3 text-sm text-muted-foreground">
                {t("universities.loading")}
              </li>
            )}
            {!isLoading && debounced.length >= 1 && data?.length === 0 && (
              <li className="px-4 py-3 text-sm text-muted-foreground">
                {t("universities.noResults")}
              </li>
            )}
            {data?.slice(0, 8).map((uni) => (
              <li key={uni.id}>
                <button
                  type="button"
                  className="w-full text-left px-4 py-3 hover:bg-muted/50"
                  onClick={() => selectUniversity(uni)}
                >
                  <SearchResultInner uni={uni} />
                </button>
              </li>
            ))}
          </ul>
        </DialogContent>
      </Dialog>
    </>
  );
}
