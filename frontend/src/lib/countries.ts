export type Country = {
  code: string;
  name: string;
  flag: string;
};

/** ISO-3166 alpha-2 → regional indicator flag emoji */
function flagEmoji(code: string): string {
  return code
    .toUpperCase()
    .split("")
    .map((c) => String.fromCodePoint(0x1f1e6 - 65 + c.charCodeAt(0)))
    .join("");
}

export const COUNTRIES: Country[] = [
  { code: "DE", name: "Germany", flag: flagEmoji("DE") },
  { code: "IN", name: "India", flag: flagEmoji("IN") },
  { code: "US", name: "United States", flag: flagEmoji("US") },
  { code: "GB", name: "United Kingdom", flag: flagEmoji("GB") },
  { code: "FR", name: "France", flag: flagEmoji("FR") },
  { code: "NL", name: "Netherlands", flag: flagEmoji("NL") },
  { code: "ES", name: "Spain", flag: flagEmoji("ES") },
  { code: "IT", name: "Italy", flag: flagEmoji("IT") },
  { code: "CA", name: "Canada", flag: flagEmoji("CA") },
  { code: "AU", name: "Australia", flag: flagEmoji("AU") },
  { code: "SG", name: "Singapore", flag: flagEmoji("SG") },
  { code: "JP", name: "Japan", flag: flagEmoji("JP") },
];

export const DEFAULT_COUNTRY_CODE = "DE";

export function getCountryByCode(code: string): Country {
  return (
    COUNTRIES.find((c) => c.code === code) ??
    COUNTRIES.find((c) => c.code === DEFAULT_COUNTRY_CODE)!
  );
}
