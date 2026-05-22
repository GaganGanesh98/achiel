"use client";

import { useMemo, useState } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { NewsItem } from "@/lib/news";
import { cn } from "@/lib/utils";

type NewsTab = "all" | "ai" | "education" | "careers";

const TAB_LABELS: Record<NewsTab, string> = {
  all: "All",
  ai: "AI",
  education: "Education",
  careers: "Careers",
};

function classifyItem(title: string): Exclude<NewsTab, "all"> | null {
  const t = title.toLowerCase();
  if (
    t.includes("ai") ||
    t.includes("artificial intelligence") ||
    t.includes("machine learning") ||
    t.includes("llm") ||
    t.includes("openai")
  ) {
    return "ai";
  }
  if (
    t.includes("university") ||
    t.includes("college") ||
    t.includes("education") ||
    t.includes("student") ||
    t.includes("campus") ||
    t.includes("higher ed")
  ) {
    return "education";
  }
  if (
    t.includes("career") ||
    t.includes("job") ||
    t.includes("hiring") ||
    t.includes("workforce") ||
    t.includes("internship")
  ) {
    return "careers";
  }
  return null;
}

function relativeTime(isoDate?: string): string {
  if (!isoDate) return "";
  const then = Date.parse(isoDate);
  if (Number.isNaN(then)) return "";
  const diffSec = Math.round((then - Date.now()) / 1000);
  const rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
  const units: [Intl.RelativeTimeFormatUnit, number][] = [
    ["year", 60 * 60 * 24 * 365],
    ["month", 60 * 60 * 24 * 30],
    ["week", 60 * 60 * 24 * 7],
    ["day", 60 * 60 * 24],
    ["hour", 60 * 60],
    ["minute", 60],
    ["second", 1],
  ];
  for (const [unit, secs] of units) {
    const n = Math.round(diffSec / secs);
    if (Math.abs(n) >= 1 || unit === "second") {
      return rtf.format(n, unit);
    }
  }
  return "";
}

const SOURCE_STYLES: Record<string, string> = {
  "TechCrunch AI": "bg-violet-100 text-violet-800",
  "Inside Higher Ed": "bg-sky-100 text-sky-800",
  "Hacker News": "bg-orange-100 text-orange-800",
};

export function NewsTabs({ items }: { items: NewsItem[] }) {
  const [tab, setTab] = useState<NewsTab>("all");

  const filtered = useMemo(() => {
    if (tab === "all") return items;
    return items.filter((item) => classifyItem(item.title) === tab);
  }, [items, tab]);

  return (
    <div className="space-y-6">
      <Tabs value={tab} onValueChange={(v) => setTab(v as NewsTab)}>
        <TabsList>
          {(Object.keys(TAB_LABELS) as NewsTab[]).map((key) => (
            <TabsTrigger key={key} value={key}>
              {TAB_LABELS[key]}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {filtered.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          No articles in this category right now.
        </p>
      ) : (
        <ul className="grid gap-4 md:grid-cols-2">
          {filtered.map((item) => (
            <li key={item.link}>
              <Card className="h-full hover:shadow-md transition-shadow">
                <CardHeader className="pb-2">
                  <span
                    className={cn(
                      "inline-flex w-fit rounded-full px-2 py-0.5 text-xs font-medium",
                      SOURCE_STYLES[item.source] ?? "bg-muted text-muted-foreground"
                    )}
                  >
                    {item.source}
                  </span>
                  <CardTitle className="text-base leading-snug pt-2">
                    <a
                      href={item.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:underline"
                    >
                      {item.title}
                    </a>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {item.contentSnippet && (
                    <p className="text-sm text-muted-foreground line-clamp-3">
                      {item.contentSnippet}
                    </p>
                  )}
                  {item.isoDate && (
                    <p className="text-xs text-muted-foreground">
                      {relativeTime(item.isoDate)}
                    </p>
                  )}
                </CardContent>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
