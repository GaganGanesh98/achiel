"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { UniversitySearch } from "@/components/university-search";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { COUNTRY } from "@/lib/countries";
import { api, clearToken, getToken } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { User } from "@/types";

const NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/universities", label: "Universities" },
  { href: "/current-affairs", label: "Current Affairs" },
] as const;

function navClass(active: boolean) {
  return cn(
    "text-sm transition-colors",
    active ? "text-foreground font-medium" : "text-muted-foreground hover:text-foreground"
  );
}

export function AppHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [hasToken, setHasToken] = useState(false);
  useEffect(() => setHasToken(!!getToken()), []);

  const { data: user } = useQuery({
    queryKey: ["me"],
    queryFn: () => api<User>("/auth/me"),
    enabled: hasToken,
    retry: false,
    staleTime: 30_000,
  });

  function logout() {
    clearToken();
    queryClient.removeQueries({ queryKey: ["me"] });
    api("/auth/logout", { method: "POST" }).catch(() => {});
    router.push("/");
  }

  const isAuthPage = ["/login", "/register", "/verify", "/verify-pending"].some((p) =>
    pathname.startsWith(p)
  );

  return (
    <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between gap-4 px-4">
        <Link
          href={user ? "/dashboard" : "/"}
          className="text-lg font-semibold tracking-tight shrink-0 flex items-center gap-1.5"
        >
          <span aria-hidden>{COUNTRY.flag}</span>
          CampusVoice
        </Link>

        <div className="flex items-center gap-3 sm:gap-4">
          <UniversitySearch compact />

          {user && (
            <nav className="hidden sm:flex items-center gap-4">
              {NAV.map(({ href, label }) => (
                <Link
                  key={href}
                  href={href}
                  className={navClass(
                    pathname === href || pathname.startsWith(`${href}/`)
                  )}
                >
                  {label}
                </Link>
              ))}
            </nav>
          )}

          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="max-w-[10rem] truncate">
                  {user.display_name}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem asChild>
                  <Link href="/me">My account</Link>
                </DropdownMenuItem>
                {user.is_admin && (
                  <>
                    <DropdownMenuItem asChild>
                      <Link href="/admin/reports">Reports</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link href="/admin/domains">Domains</Link>
                    </DropdownMenuItem>
                  </>
                )}
                <DropdownMenuItem onClick={logout}>Log out</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            !isAuthPage && (
              <div className="flex items-center gap-2">
                <Link
                  href="/login"
                  className="text-sm text-muted-foreground hover:text-foreground"
                >
                  Log in
                </Link>
                <Button size="sm" asChild>
                  <Link href="/register">Sign up</Link>
                </Button>
              </div>
            )
          )}
        </div>
      </div>
    </header>
  );
}
