export const COUNTRY = { code: "DE", name: "Germany", flag: "🇩🇪" } as const;

/** @deprecated Germany-only — use COUNTRY */
export const DEFAULT_COUNTRY_CODE = COUNTRY.code;

/** @deprecated Germany-only — use COUNTRY */
export function getCountryByCode(_code: string) {
  return COUNTRY;
}

/** @deprecated Germany-only */
export const COUNTRIES = [COUNTRY];

export type Country = typeof COUNTRY;
