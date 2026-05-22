import { NewsTabs } from "@/components/news-tabs";
import { fetchNews } from "@/lib/news";

export const revalidate = 3600;

export default async function CurrentAffairsPage() {
  const items = await fetchNews();

  return (
    <main className="mx-auto max-w-4xl py-6 px-4 space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">Current Affairs</h1>
        <p className="text-sm text-muted-foreground mt-1">
          AI, education, and career news for verified students
        </p>
      </header>

      {items.length === 0 ? (
        <p className="text-sm text-muted-foreground rounded-lg border p-6 text-center">
          Couldn&apos;t load news right now. Please refresh in a few minutes.
        </p>
      ) : (
        <NewsTabs items={items} />
      )}
    </main>
  );
}
