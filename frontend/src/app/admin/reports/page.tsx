import { Suspense } from "react";

import { AdminReportsContent } from "./admin-reports-content";

export default function AdminReportsPage() {
  return (
    <Suspense
      fallback={
        <main className="mx-auto max-w-3xl px-4 py-8">
          <p className="text-muted-foreground text-sm">Loading…</p>
        </main>
      }
    >
      <AdminReportsContent />
    </Suspense>
  );
}
