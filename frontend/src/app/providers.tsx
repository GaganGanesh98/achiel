"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { AppHeader } from "@/components/app-header";
import { Toaster } from "@/components/ui/toaster";
import { CountryProvider } from "@/lib/country-context";
import { makeQueryClient } from "@/lib/queryClient";

export function Providers({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const [queryClient] = useState(() => makeQueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <CountryProvider>
        <div className={className}>
          <AppHeader />
          {children}
          <Toaster />
        </div>
      </CountryProvider>
    </QueryClientProvider>
  );
}
