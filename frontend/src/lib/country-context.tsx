"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  COUNTRIES,
  DEFAULT_COUNTRY_CODE,
  getCountryByCode,
  type Country,
} from "@/lib/countries";

const STORAGE_KEY = "cv.country";

type CountryContextValue = {
  countryCode: string;
  setCountryCode: (code: string) => void;
  country: Country;
};

const CountryContext = createContext<CountryContextValue | null>(null);

function isValidCode(code: string): boolean {
  return COUNTRIES.some((c) => c.code === code);
}

export function CountryProvider({ children }: { children: ReactNode }) {
  const [countryCode, setCountryCodeState] = useState(DEFAULT_COUNTRY_CODE);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored && isValidCode(stored)) {
        setCountryCodeState(stored);
      }
    } catch {
      /* ignore private browsing / blocked storage */
    }
  }, []);

  const setCountryCode = useCallback((code: string) => {
    const next = code.toUpperCase();
    if (!isValidCode(next)) return;
    setCountryCodeState(next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      /* ignore */
    }
  }, []);

  const value = useMemo<CountryContextValue>(
    () => ({
      countryCode,
      setCountryCode,
      country: getCountryByCode(countryCode),
    }),
    [countryCode, setCountryCode]
  );

  return (
    <CountryContext.Provider value={value}>{children}</CountryContext.Provider>
  );
}

export function useCountry(): CountryContextValue {
  const ctx = useContext(CountryContext);
  if (!ctx) {
    throw new Error("useCountry must be used within CountryProvider");
  }
  return ctx;
}
