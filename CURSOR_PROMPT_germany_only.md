# Cursor Prompt — CampusVoice: Germany-only + full German university search

Paste into Cursor (Composer / Agent mode) at the repo root.

---

## Context

CampusVoice (`/Users/gagan/achiel`) currently supports multiple countries via a `CountrySwitcher` component and a `CountryProvider` context. We're pivoting to **Germany-only**: only DE public + private universities, only reviews from students at German institutions.

The current `/universities` page also has a UX confusion: there's a search input on the left and a "Select country" button on the right that looks like a search button but actually opens the country switcher. Once we're DE-only, the switcher disappears and the confusion goes with it.

Additionally, the universities search currently only returns universities that already exist in the DB (i.e. ones with at least one verified student). We want users to be able to **type any German university name** (e.g. "BSBI", "TUM", "RWTH") and have it appear in results, even if no student has signed up yet. Matching ones should show "Be the first to review" CTAs instead of "no results".

### Current state (what to read before changing anything)

- `frontend/src/lib/countries.ts` — list of supported countries, `DEFAULT_COUNTRY_CODE`.
- `frontend/src/lib/country-context.tsx` — `CountryProvider`, `useCountry`.
- `frontend/src/components/country-switcher.tsx` — the dropdown component.
- `frontend/src/components/app-header.tsx` — uses `CountrySwitcher` in compact mode.
- `frontend/src/app/providers.tsx` — wraps app in `CountryProvider`.
- `frontend/src/app/universities/page.tsx` — search + country switcher buttons.
- `frontend/src/app/dashboard/page.tsx` — main dashboard, currently has a `university_id` query param flow.
- `backend/app/api/universities.py` — `GET /universities` (filters DB, requires existing row) and `GET /universities/lookup`.
- `backend/app/models/university.py` — University SQLAlchemy model with `country` column.
- `backend/app/seed/german_private_unis.py` — already has private DE domains for auth gating.
- `backend/universities.json` — domain → name map. **Currently includes MIT, Stanford, Oxford, Cambridge, IIT Bombay, IIT Delhi.** These need to go.

---

## Work plan

Do these in order. Don't skip the verification step at the end.

---

### 1. Backend — comprehensive German universities catalogue

Create `backend/app/seed/german_universities.py` (separate from the existing `german_private_unis.py`, which is auth-related). This is the **searchable catalogue**, public + private, with metadata for display.

```python
from dataclasses import dataclass
from enum import StrEnum

class UniType(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    APPLIED_SCIENCES = "applied_sciences"  # Fachhochschule / HAW
    ART_MUSIC = "art_music"
    CHURCH = "church"

@dataclass(frozen=True)
class GermanUniversity:
    name: str               # canonical display name
    short_name: str | None  # e.g. "TUM", "RWTH", "LMU", "BSBI"
    aliases: tuple[str, ...]  # other ways students refer to it
    domain: str             # primary domain
    extra_domains: tuple[str, ...]  # student. prefixes, alternative TLDs
    city: str
    state: str              # German Land, e.g. "Berlin", "Bayern"
    type: UniType
    website: str

GERMAN_UNIVERSITIES: tuple[GermanUniversity, ...] = (
    # … see "Catalogue scope" below for coverage requirements
)
```

**Catalogue scope (minimum):**
- All **public universities** ("Universitäten") listed by the HRK (Hochschulrektorenkonferenz). There are ~110.
- All major **public universities of applied sciences** (HAW / Fachhochschulen). Cover at least the top 80 by enrolment.
- All recognised **private universities** with state accreditation. Cover at least: SRH (all campuses), IU, GISMA, BSBI (Berlin School of Business and Innovation), CODE, Hertie, ESMT, WHU, Frankfurt School, Zeppelin, Bard College Berlin, Constructor (formerly Jacobs), Hochschule Fresenius, FOM, Macromedia, HMKW, EBS, EBC, Touro, Steinbeis, Karlshochschule, Munich Business School, accadis, ISM, Cologne Business School.
- Major **art and music** universities: UdK Berlin, HFBK Hamburg, Folkwang, HfM Hanns Eisler, HMTM München, etc.

For each entry include realistic aliases. E.g. for TUM: `aliases=("TUM", "TU München", "TU Munich", "Technische Universität München")`. For BSBI: `aliases=("BSBI", "Berlin School of Business and Innovation")`. For RWTH: `aliases=("RWTH", "RWTH Aachen", "RWTH Aachen University")`.

If you don't have time to populate all ~200 entries by hand, use a reliable public source (HRK CSV, Wikipedia category list) and generate the file. **Cite the source in a comment at the top of the file.** Do not hallucinate domains — every domain must actually resolve. If unsure, leave `extra_domains=()` and document.

---

### 2. Backend — migrate the DB + search endpoint

**Alembic migration:**
- Drop the `country` column from `universities` (or set a CHECK constraint `country = 'DE'` and default it — your call, but if you're going DE-only forever, drop it cleanly).
- Add columns: `short_name VARCHAR(40) NULL`, `aliases JSONB NOT NULL DEFAULT '[]'`, `state VARCHAR(64) NULL`, `type VARCHAR(32) NULL`, `website VARCHAR(255) NULL`.
- Add a GIN trigram index on `name` and a GIN index on `aliases` for fast fuzzy search:
  ```sql
  CREATE EXTENSION IF NOT EXISTS pg_trgm;
  CREATE INDEX idx_universities_name_trgm ON universities USING gin (name gin_trgm_ops);
  CREATE INDEX idx_universities_short_name_trgm ON universities USING gin (short_name gin_trgm_ops);
  CREATE INDEX idx_universities_aliases ON universities USING gin (aliases);
  ```

**Data migration:** in the same migration, upsert every entry from `GERMAN_UNIVERSITIES` into the table. Delete (or soft-delete via a `deleted_at` column) any existing row whose domain isn't in the German catalogue. The pre-existing US/UK/India entries in `backend/universities.json` and the DB go away.

**Replace `GET /universities`** in `backend/app/api/universities.py`:

```python
@router.get("", response_model=list[UniversityOut])
async def list_universities(
    q: str | None = Query(default=None, min_length=1, max_length=100),
    db: AsyncSession = Depends(get_db),
) -> list[University]:
    if not q:
        stmt = select(University).order_by(University.name).limit(50)
    else:
        # Search name, short_name, aliases (case-insensitive, trigram-friendly)
        like = f"%{q.lower()}%"
        stmt = (
            select(University)
            .where(
                or_(
                    func.lower(University.name).like(like),
                    func.lower(University.short_name).like(like),
                    University.aliases.op("?|")(cast([q.lower()], ARRAY(String))),
                    # plus a trigram similarity fallback for typos:
                    func.similarity(func.lower(University.name), q.lower()) > 0.3,
                )
            )
            .order_by(
                func.similarity(func.lower(University.name), q.lower()).desc(),
                University.name,
            )
            .limit(50)
        )
    result = await db.execute(stmt)
    return list(result.scalars().all())
```

Adjust the JSONB containment query to match your SQLAlchemy version. The point: **any q ≥ 1 char** searches name + short_name + aliases + fuzzy. The response includes universities even with **zero verified students** — the catalogue is the source of truth, not the user table.

**Remove the country query param entirely.** Country no longer exists in the API surface.

**Also remove**: `backend/universities.json` non-German entries (or delete the file if no longer referenced after the catalogue migration). Update `backend/app/services/universities.lookup_university` to read from the new catalogue / DB instead.

---

### 3. Backend — restrict signup to German university domains

In `backend/app/services/university_email.py` (and wherever signup validation lives):

- Allow only domains present in the German catalogue (`GERMAN_UNIVERSITIES` + their `extra_domains`).
- Reject everything else with a clear i18n key `auth.signup.non_german_domain`.
- Keep the pending-review flow for unknown domains but **scope it to `.de` TLDs** + a small allowlist of known German universities with non-`.de` domains (`iu.org`, `code.berlin`, `esmt.berlin`, `whu.edu`, `constructor.university`, `bard-college-berlin.de`).

Update the message constants in `backend/app/api/universities.py`:
- `REJECTED_DOMAIN_MESSAGE` should say "CampusVoice is currently for students at German universities only."
- Translate to German for the DE locale.

---

### 4. Frontend — kill the country switcher

Delete (or leave with a deprecation notice and unwire all callers):

- `frontend/src/components/country-switcher.tsx` — delete.
- `frontend/src/lib/country-context.tsx` — delete the provider, keep a tiny `useCountry()` that hardcodes Germany if any leftover caller needs it. Better: rip out all callers.
- `frontend/src/lib/countries.ts` — replace with a single export: `export const COUNTRY = { code: "DE", name: "Germany", flag: "🇩🇪" } as const;` so anything still importing it doesn't break.
- `frontend/src/app/providers.tsx` — remove `<CountryProvider>` wrapper.
- `frontend/src/components/app-header.tsx` — remove the `<CountrySwitcher variant="compact" />` from the header. Leave the German flag as a static icon next to the logo if you want a visual identity cue.

---

### 5. Frontend — fix the universities search page

Rewrite `frontend/src/app/universities/page.tsx`:

- Single search input, no second button.
- Hit `GET /universities?q=...` (no country param).
- Use a 250ms debounce on the query — don't fire on every keystroke.
- For each result, show: name, short_name in muted text, city · state, type badge (Public / Private / HAW), and either "X verified students" or "Be the first to review" CTA.
- If no results: show a "Suggest a university" link that opens a contact form / mailto pre-filled with `Subject: Add [query] to CampusVoice`.

Result item structure:

```tsx
<li className="px-4 py-3 hover:bg-muted/50">
  <Link href={`/dashboard?university_id=${uni.id}`} className="block">
    <div className="flex items-center gap-2">
      <p className="font-medium">{uni.name}</p>
      {uni.short_name && (
        <span className="text-xs text-muted-foreground">({uni.short_name})</span>
      )}
      <TypeBadge type={uni.type} />
    </div>
    <p className="text-sm text-muted-foreground">
      {uni.city} · {uni.state}
      {uni.verified_student_count > 0
        ? ` · ${uni.verified_student_count} verified students`
        : " · Be the first to review"}
    </p>
  </Link>
</li>
```

(Add `verified_student_count` to `UniversityOut` schema — quick subquery on signup-confirmed users joined by university_id.)

---

### 6. Frontend — universal university search on dashboard + header

Add a global university search to the header (replacing the deleted country switcher's slot):

- `frontend/src/components/university-search.tsx` — combobox using shadcn/ui's `Command` component (`cmdk`).
- Trigger keyboard shortcut `Cmd/Ctrl + K` or a button in the header with the search icon.
- Hits `GET /universities?q=...`, shows top 8 results inline as the user types.
- Selecting a result navigates to `/dashboard?university_id=<uuid>`.
- Works for any visitor (no auth required) — let prospects browse before signing up.

On the dashboard (`frontend/src/app/dashboard/page.tsx`): if `?university_id=<uuid>` is set, scope the feed to that university and show a header card with the uni's name + "I study here" CTA (which routes to signup with that university pre-selected for verified domains, or to the "request access" form for unknown domains).

---

### 7. i18n + copy update

Since the site now serves only Germany, the default UI locale should default to `de` for visitors with `Accept-Language: de*`. Add German translations for:

- All new error messages (`auth.signup.non_german_domain`, "Be the first to review", "Suggest a university", etc.).
- Update existing English copy that implied multi-country: e.g. "Schools with verified students on CampusVoice" → "Verifizierte Studierende an deutschen Hochschulen" / "Verified students at German universities".
- Hero / landing copy should mention "deutsche Universitäten und Hochschulen" explicitly.

Update the footer too — the "We are not affiliated with any university" line stays but the Impressum needs to reflect a German-only operation (mention TMG § 5 compliance, German jurisdiction).

---

### 8. Tests

Backend (`backend/tests/`):

- `test_universities_search.py`:
  - `test_search_by_short_name` — `q=TUM` returns Technical University of Munich.
  - `test_search_by_alias` — `q=BSBI` returns Berlin School of Business and Innovation.
  - `test_search_fuzzy_typo` — `q=Münchn` still returns Munich universities (trigram similarity).
  - `test_search_empty_returns_first_50` — no `q` param returns alphabetical list, limit 50.
  - `test_no_country_param` — passing `?country=US` is silently ignored (or 422 — your call, document it).
- `test_signup_rejects_non_german_domain` — signup with `@harvard.edu` → 422 with `auth.signup.non_german_domain`.
- `test_signup_accepts_de_domain` — `@tu-berlin.de` → success.
- `test_signup_accepts_allowlisted_non_de` — `@iu.org` → success.

Frontend (`frontend/tests/` Playwright):

- `test('header search jumps to university dashboard')` — type "TUM" in header search, click result, lands on `/dashboard?university_id=...`.
- `test('universities page no-results shows suggest cta')` — search "Hogwarts" → empty state with "Suggest a university" link.

---

### 9. Cleanup

- Delete `backend/universities.json` if nothing imports it after the migration (grep first).
- Delete `frontend/src/components/country-switcher.tsx`.
- Delete `frontend/src/lib/country-context.tsx` once all callers are migrated.
- Grep for `country` references across both apps — remove dead code.
- Update `README.md`: clarify CampusVoice is a German-only platform, document the catalogue source.

---

## Constraints

- **No breaking auth changes**: existing verified users at non-German domains (if any seeded test data exists) need a migration path. Soft-delete or migrate to a "legacy" flag — don't wipe accounts silently.
- **Pydantic v2** patterns only.
- **Don't hardcode the German catalogue in two places** — DB is the source of truth, `german_universities.py` is the seed. Search hits the DB only.
- **Catalogue must be auditable**: cite the source list in a comment, version-pin the data file.
- **No country leak**: after this lands, there should be zero UI affordance to pick a country, and zero API param for country. Grep should return clean.

---

## Acceptance criteria

- [ ] `GET /universities?q=BSBI` returns Berlin School of Business and Innovation, even if no user has signed up there.
- [ ] `GET /universities?q=tum` returns TUM as the top result (case-insensitive, short-name match).
- [ ] `GET /universities?q=münchn` returns Munich universities (fuzzy).
- [ ] Country switcher no longer appears anywhere in the UI.
- [ ] Signing up with `@stanford.edu` is rejected with a German-language error (when locale is `de`).
- [ ] Header has a `Cmd+K` search that lets unauthenticated visitors browse universities.
- [ ] Dashboard `/dashboard?university_id=<uuid>` shows that uni's feed and a "I study here" CTA.
- [ ] `make test` passes; new search and signup tests included.
- [ ] `grep -ri "country" frontend/src backend/app` returns only intentional references (e.g. ISO country in addresses, if any).

---

## What this prompt does NOT do (future)

- A user-facing university suggestion workflow with admin approval — that's a separate piece.
- Per-state filtering (Berlin only, Bayern only) — easy add later via the `state` column.
- Auto-import from a HRK API on a schedule — manual seeding for now.
