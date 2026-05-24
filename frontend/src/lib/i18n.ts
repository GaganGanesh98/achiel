export type Locale = "de" | "en";

const messages = {
  de: {
    "universities.title": "Hochschulen",
    "universities.subtitle": "Verifizierte Studierende an deutschen Hochschulen",
    "universities.searchPlaceholder": "Name, Kürzel oder Alias…",
    "universities.beFirst": "Sei der Erste mit einer Bewertung",
    "universities.verifiedStudents": "verifizierte Studierende",
    "universities.noResults": "Keine Hochschule gefunden.",
    "universities.suggest": "Hochschule vorschlagen",
    "universities.loading": "Laden…",
    "university.type.public": "Staatlich",
    "university.type.private": "Privat",
    "university.type.applied_sciences": "HAW",
    "university.type.art_music": "Kunst/Musik",
    "university.type.church": "Kirchlich",
    "dashboard.title": "Dashboard",
    "dashboard.subtitle": "Verifizierte Studierende an deutschen Hochschulen",
    "dashboard.globalTitle": "CampusVoice Deutschland",
    "dashboard.studyHere": "Ich studiere hier",
    "dashboard.signUpToReview": "Registrieren & bewerten",
    "search.placeholder": "Hochschule suchen…",
    "search.shortcut": "Suche",
    "auth.signup.non_german_domain":
      "CampusVoice ist derzeit nur für Studierende an deutschen Hochschulen.",
  },
  en: {
    "universities.title": "Universities",
    "universities.subtitle": "Verified students at German universities",
    "universities.searchPlaceholder": "Name, short name, or alias…",
    "universities.beFirst": "Be the first to review",
    "universities.verifiedStudents": "verified students",
    "universities.noResults": "No universities match your search.",
    "universities.suggest": "Suggest a university",
    "universities.loading": "Loading…",
    "university.type.public": "Public",
    "university.type.private": "Private",
    "university.type.applied_sciences": "HAW",
    "university.type.art_music": "Art/Music",
    "university.type.church": "Church",
    "dashboard.title": "Dashboard",
    "dashboard.subtitle": "Verified students at German universities",
    "dashboard.globalTitle": "CampusVoice Germany",
    "dashboard.studyHere": "I study here",
    "dashboard.signUpToReview": "Sign up to review",
    "search.placeholder": "Search universities…",
    "search.shortcut": "Search",
    "auth.signup.non_german_domain":
      "CampusVoice is currently for students at German universities only.",
  },
} as const;

export type MessageKey = keyof (typeof messages)["en"];

/**
 * Default locale used during SSR and the first client render.
 * MUST be deterministic — never branch on `typeof window`, `navigator`,
 * `Date.now()`, etc. inside the render path. Doing so causes hydration
 * mismatches because the server picks one value and the client picks another.
 *
 * To honour the user's browser preference, read it inside `useEffect` and
 * store the choice in a cookie or localStorage; then re-render with the new
 * locale on the SECOND pass. See `useLocale()` in `hooks/use-locale.ts`.
 */
export const DEFAULT_LOCALE: Locale = "de";

/**
 * Client-only locale detection. NEVER call during render — only inside
 * `useEffect`, event handlers, or other post-hydration code.
 */
export function detectBrowserLocale(): Locale {
  if (typeof window === "undefined") return DEFAULT_LOCALE;
  const langs = navigator.languages?.length
    ? navigator.languages
    : [navigator.language];
  if (langs.some((l) => l.toLowerCase().startsWith("de"))) return "de";
  return "en";
}

export function t(key: MessageKey, locale: Locale = DEFAULT_LOCALE): string {
  return messages[locale][key] ?? messages.en[key];
}

export function translateError(message: string, locale: Locale = DEFAULT_LOCALE): string {
  if (message === "auth.signup.non_german_domain") {
    return t("auth.signup.non_german_domain", locale);
  }
  return message;
}
