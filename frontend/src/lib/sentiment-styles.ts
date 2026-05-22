import type { Sentiment } from "@/types";

export const SENTIMENT_PILL_CLASS: Record<Sentiment, string> = {
  positive:
    "bg-green-100 text-green-800 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-900",
  neutral:
    "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700",
  negative:
    "bg-red-100 text-red-800 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-900",
};

export const SENTIMENT_BUTTON_CLASS: Record<
  Sentiment,
  { base: string; selected: string }
> = {
  positive: {
    base: "border-green-200 bg-green-50/50 text-green-900 hover:bg-green-100 dark:border-green-900 dark:bg-green-950/40 dark:text-green-200 dark:hover:bg-green-950",
    selected:
      "border-green-500 bg-green-100 text-green-900 ring-1 ring-green-500 dark:border-green-600 dark:bg-green-900 dark:text-green-100",
  },
  neutral: {
    base: "border-slate-200 bg-slate-50/50 text-slate-800 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900/40 dark:text-slate-200 dark:hover:bg-slate-800",
    selected:
      "border-slate-500 bg-slate-100 text-slate-900 ring-1 ring-slate-500 dark:border-slate-500 dark:bg-slate-800 dark:text-slate-100",
  },
  negative: {
    base: "border-red-200 bg-red-50/50 text-red-900 hover:bg-red-100 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200 dark:hover:bg-red-950",
    selected:
      "border-red-500 bg-red-100 text-red-900 ring-1 ring-red-500 dark:border-red-600 dark:bg-red-900 dark:text-red-100",
  },
};
