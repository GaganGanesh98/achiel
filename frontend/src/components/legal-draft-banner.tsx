export function LegalDraftBanner({ children }: { children: React.ReactNode }) {
  return (
    <div className="not-prose rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-950 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-100 mb-8">
      {children}
    </div>
  );
}
