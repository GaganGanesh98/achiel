"use client";

import { ChevronDown } from "lucide-react";
import type { ReactNode } from "react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { COUNTRIES } from "@/lib/countries";
import { useCountry } from "@/lib/country-context";
import { cn } from "@/lib/utils";

type CountrySwitcherProps = {
  variant?: "compact" | "default";
  /** Custom trigger; dropdown anchors to this element when provided. */
  trigger?: ReactNode;
};

export function CountrySwitcher({
  variant = "default",
  trigger,
}: CountrySwitcherProps) {
  const { countryCode, setCountryCode, country } = useCountry();

  const defaultTrigger = (
    <Button variant="outline" size="sm" className="gap-1.5 h-8">
      <span aria-hidden>{country.flag}</span>
      {variant === "default" && <span>{country.name}</span>}
      <ChevronDown className="h-3.5 w-3.5 opacity-60" />
    </Button>
  );

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        {trigger ?? defaultTrigger}
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="max-h-72 overflow-y-auto">
        {COUNTRIES.map((c) => (
          <DropdownMenuItem
            key={c.code}
            onClick={() => setCountryCode(c.code)}
            className={cn(
              "gap-2 cursor-pointer",
              countryCode === c.code && "bg-accent"
            )}
          >
            <span aria-hidden>{c.flag}</span>
            <span>{c.name}</span>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
