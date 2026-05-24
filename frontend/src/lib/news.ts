import Parser from "rss-parser";

export type NewsItem = {
  title: string;
  link: string;
  source: string;
  isoDate?: string;
  contentSnippet?: string;
};

const parser = new Parser();

const USER_AGENT = "CampusVoice/1.0 (+https://campusvoice.local)";
const FETCH_TIMEOUT_MS = 8000;

const FEEDS: { url: string; source: string }[] = [
  {
    url: "https://techcrunch.com/category/artificial-intelligence/feed/",
    source: "TechCrunch AI",
  },
  {
    url: "https://www.insidehighered.com/rss.xml",
    source: "Inside Higher Ed",
  },
  {
    url: "https://hnrss.org/newest?q=AI+careers",
    source: "Hacker News",
  },
];

async function fetchFeed(url: string, source: string): Promise<NewsItem[]> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

  try {
    const res = await fetch(url, {
      headers: { "User-Agent": USER_AGENT, Accept: "application/rss+xml, application/xml, text/xml" },
      signal: controller.signal,
      next: { revalidate: 3600 },
    });
    if (!res.ok) return [];

    const xml = await res.text();
    const feed = await parser.parseString(xml);

    return (feed.items ?? []).map((item) => ({
      title: item.title?.trim() ?? "Untitled",
      link: item.link ?? item.guid ?? "",
      source,
      isoDate: item.isoDate ?? item.pubDate,
      contentSnippet: item.contentSnippet?.trim(),
    }));
  } catch {
    return [];
  } finally {
    clearTimeout(timeout);
  }
}

export async function fetchNews(): Promise<NewsItem[]> {
  const batches = await Promise.all(
    FEEDS.map(({ url, source }) => fetchFeed(url, source))
  );

  const seen = new Set<string>();
  const merged: NewsItem[] = [];

  for (const items of batches) {
    for (const item of items) {
      if (!item.link || seen.has(item.link)) continue;
      seen.add(item.link);
      merged.push(item);
    }
  }

  merged.sort((a, b) => {
    const ta = a.isoDate ? Date.parse(a.isoDate) : 0;
    const tb = b.isoDate ? Date.parse(b.isoDate) : 0;
    return tb - ta;
  });

  return merged.slice(0, 30);
}
