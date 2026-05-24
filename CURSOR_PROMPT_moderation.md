# Cursor Prompt — CampusVoice Content Safety Hardening

Paste this into Cursor (Composer / Agent mode) at the repo root. Work through it section by section; don't dump everything in one go.

---

## Context

CampusVoice (`/Users/gagan/achiel`) is a Next.js 15 + FastAPI + PostgreSQL 16 + Redis 7 university review platform. It serves users **aged ~12–30** in **Germany (DE) and English (EN)**. We are not affiliated with any university. We must avoid:

- Lawsuits from defamation, harassment, or hate speech directed at named individuals or protected groups.
- Liability under **JuSchG** (German youth protection), **DSA** (EU Digital Services Act — applies to us regardless of size), **NetzDG** (if we hit the 2M-user threshold, but moderation hygiene matters now), and **§ 130 StGB** (Volksverhetzung / incitement).
- Reputational damage from slurs, threats, sexual content, or doxxing slipping through.

### What already exists (do NOT rewrite — extend)

- `backend/app/services/moderation.py` — `check_and_clean(*texts)` using `better-profanity` + `severe_terms.txt` blocklist + `SEVERE_TERMS_JSON` env. Raises `Unsafe` for severe terms, returns censored text for mild profanity.
- `backend/severe_terms.txt` — substring blocklist (English only, threats + self-harm phrases).
- `backend/app/middleware/profanity.py` — placeholder, currently no-op.
- `backend/app/api/reports.py` — user report endpoints.
- `backend/app/api/posts.py` and `comments.py` — call `check_and_clean` on body text.
- `backend/name_watchlist.json` and `backend/app/services/name_screening.py` — individual name screening (currently empty list).

### What's missing (the work)

1. English-only coverage; **German is unmoderated**.
2. Wordlist-only; no contextual classifier — misses paraphrased hate, slurs in German, leetspeak we haven't seen.
3. Only post/comment **bodies** are checked — usernames, display names, bios, post titles, report reasons, university nicknames are NOT.
4. No Unicode normalisation — easily bypassed with confusables (`fυck`, `f​uck` with zero-width joiner, fullwidth `ｆｕｃｋ`).
5. No rate limiting on content endpoints — vulnerable to spam floods.
6. No moderation audit trail — when something is censored/blocked, we don't log who tried.
7. No admin moderation queue UI — reports go to DB and die there.
8. No frontend pre-submit check — user submits, server rejects, bad UX.
9. No Terms of Service, Community Guidelines, or Impressum page actually exists (footer links 404).
10. No tests for the moderation pipeline.

---

## Work plan

Implement in this order. Each section is one Cursor turn. Run the tests after each section and don't proceed if anything is red.

---

### 1. Backend — extend moderation service with multilingual API classifier

**File:** `backend/app/services/moderation.py` (extend, don't replace).

Add a second layer on top of the existing word-list filter:

- New function `classify_content(text: str, *, lang: str | None = None) -> ModerationResult`.
- Use **OpenAI's `omni-moderation-latest`** (free, multilingual, returns category scores). Add `OPENAI_API_KEY` to `backend/app/core/config.py` `Settings`. Fall back to word-list-only if the key is missing (degraded mode, log a warning).
- Categories that **block**: `hate`, `hate/threatening`, `harassment/threatening`, `self-harm/instructions`, `sexual/minors`, `violence/graphic`. Any score ≥ 0.5 → reject.
- Categories that **flag for review** (don't block, but queue): `harassment`, `sexual`, `violence` at score ≥ 0.3.
- Cache results in Redis with a SHA-256 key of the normalised text, TTL 7 days, so duplicate submissions don't re-hit the API.
- Add a **Unicode normalisation** pre-step: NFKC normalise, strip zero-width chars (`​-‍⁠﻿`), map confusables (use the `confusables` package or the homoglyph map in `unicodedata`). Apply this BEFORE both the word list AND the API call.

Define:

```python
from dataclasses import dataclass
from enum import StrEnum

class Decision(StrEnum):
    ALLOW = "allow"
    CENSOR = "censor"      # publish with masked profanity
    REVIEW = "review"      # publish but flag for admin review
    BLOCK = "block"        # do not publish

@dataclass
class ModerationResult:
    decision: Decision
    cleaned_text: str
    reasons: list[str]            # human-readable: "openai.hate=0.82", "wordlist.severe"
    categories: dict[str, float]  # raw category scores
```

Wrap the existing `check_and_clean` so old callers still work, but new callers should use `moderate(text, lang=None) -> ModerationResult` which combines both layers.

**Also:** Add a small German + multilingual severe-term list (`backend/severe_terms_de.txt`). Include `§ 130 StGB`-relevant terms (Holocaust denial phrases, common neo-Nazi slogans, ethnic slurs in German). Load both files. Do NOT commit slurs to the public repo — load via env in production.

---

### 2. Backend — apply moderation to ALL user-generated fields

Audit every endpoint that accepts user text and route it through `moderate()`. At minimum:

- `backend/app/api/auth.py` — username, display name, on signup.
- `backend/app/api/posts.py` — title AND body (currently only body).
- `backend/app/api/comments.py` — body.
- `backend/app/api/reports.py` — report reason text.
- `backend/app/api/universities.py` — any user-submitted university nickname / alias.
- Any "bio" / "about" / "profile" field in user settings.

For each: if `BLOCK`, return 422 with a generic message ("Content violates community guidelines — see /community-guidelines"). Do NOT echo the offending substring back (avoids "what's blocked?" probing).

For `REVIEW` cases: persist the content but flag it in a new `moderation_flags` table (see section 4).

---

### 3. Backend — rate limiting on content endpoints

Use `slowapi` (or Redis-backed `fastapi-limiter`).

- POST `/posts`: 10 per hour per user, 30 per day.
- POST `/comments`: 30 per hour per user.
- POST `/reports`: 20 per day per user (prevent report-bombing).
- Signup: 5 per hour per IP.

Return 429 with a `Retry-After` header. Add a `RATE_LIMIT_ENABLED` config flag so tests can disable it.

---

### 4. Backend — moderation audit log + flag queue

Two new SQLAlchemy models, one Alembic migration:

```python
class ModerationEvent(Base):  # immutable audit log
    id: UUID
    created_at: datetime
    user_id: UUID | None
    resource_type: Literal["post", "comment", "username", "report", "bio"]
    resource_id: UUID | None
    decision: str            # allow/censor/review/block
    reasons: list[str]       # JSONB
    categories: dict         # JSONB raw scores
    text_hash: str           # SHA-256, NEVER store the raw blocked text
    text_excerpt: str        # first 80 chars, only for REVIEW/CENSOR (not BLOCK)

class ModerationFlag(Base):  # mutable review queue
    id: UUID
    created_at: datetime
    resource_type: str
    resource_id: UUID
    status: Literal["pending", "approved", "removed"]
    reviewed_by: UUID | None
    reviewed_at: datetime | None
    notes: str | None
```

Every call to `moderate()` writes a `ModerationEvent`. `REVIEW` decisions also write a `ModerationFlag` with `status="pending"`.

Add endpoints (admin-only, gated by `is_admin` on User):

- `GET /admin/moderation/queue` — paginated pending flags.
- `POST /admin/moderation/flags/{id}/approve` — clears the flag.
- `POST /admin/moderation/flags/{id}/remove` — soft-deletes the underlying resource and clears the flag.

---

### 5. Frontend — pre-submit check + clear UX

In `frontend/src/`:

- Add a lightweight client-side profanity filter (`obscenity` npm package — better than `bad-words` for circumvention resistance). Use it for **instant warning only**, never as the source of truth.
- On the post/comment composer: as the user types, debounce 400ms, if profanity detected show an inline warning ("This may be flagged by our community guidelines"). Don't block submit — let the server decide.
- On a 422 from the server: show a friendly modal explaining the post wasn't published, link to `/community-guidelines`, and provide a "Report a mistake" button that opens the contact flow.
- On a 429: show "You're posting too quickly — try again in N minutes" with the actual `Retry-After` value.

---

### 6. Frontend — legal & guidelines pages

The footer currently links to `/privacy`, `/terms`, `/community-guidelines`, `/impressum`, `/contact` — most 404. Create them as Next.js app-router pages under `frontend/src/app/(legal)/`:

- `/community-guidelines` — plain language, age-appropriate (we have minors). Sections: respectful communication, no hate speech (with German `§ 130 StGB` reference), no harassment of named individuals, no doxxing, no sexual content involving minors, no self-harm content, consequences (warn → temp ban → permanent ban). Include the report flow.
- `/terms` — standard ToS. Disclaim affiliation with universities. Clarify user-generated content licence (limited licence to display, not transfer of copyright). Limitation of liability. Governing law: Germany.
- `/privacy` — GDPR. Data controller (you), what's collected, why, retention, rights (Art. 15–22), DPO contact (if applicable), cookies.
- `/impressum` — **legally required in Germany** under § 5 TMG. Full name, address, email, responsible person under § 18 Abs. 2 MStV.
- `/contact` — a simple form that emails you, plus a clear "Report a safety issue" CTA.

Use plain prose, not bullet hell. Render content from MDX or markdown files in `frontend/src/content/legal/` so non-devs can edit later.

---

### 7. Backend — minor-protection touches

We have users from age 12. We are not Reddit; we don't ask DOB. But:

- Add a `MINOR_PROTECTION_MODE=true` config flag (default on).
- When on: image uploads (if/when added) get an automatic NSFW classifier check before storing. For now, this is a stub — but wire the interface so it's ready.
- Default new accounts to `searchable_by_email=false`. Force users to opt in before their profile becomes discoverable by email lookup.
- Strip EXIF GPS data from any uploaded image (already a good practice; do it now to avoid retro-fixing).

---

### 8. Tests

Add `backend/tests/test_moderation.py`:

- `test_clean_text_passes` — benign text → `ALLOW`.
- `test_mild_profanity_censored` — "this is shit" → `CENSOR`, cleaned text contains `****`.
- `test_severe_term_blocked` — phrase from `severe_terms.txt` → `BLOCK`.
- `test_unicode_bypass_blocked` — `f​uck` and `ｆｕｃｋ` and `fυck` → not allowed through (mild or severe depending on word).
- `test_german_slur_blocked` — at least one entry from `severe_terms_de.txt` → `BLOCK`.
- `test_openai_classifier_called_when_key_set` — mock the OpenAI client, assert it's invoked, assert hate score ≥ 0.5 → `BLOCK`.
- `test_openai_classifier_skipped_when_key_missing` — `OPENAI_API_KEY=""` → no call, falls back to word list only, logs a warning.
- `test_redis_cache_hit` — same text twice → only one OpenAI call.
- `test_rate_limit_posts` — 11th post in an hour → 429.
- `test_moderation_event_written` — `BLOCK` decision writes a `ModerationEvent` row with the text **hash**, not the text.
- `test_review_writes_flag` — `REVIEW` decision writes a `ModerationFlag` with `status="pending"`.
- `test_admin_queue_requires_admin` — non-admin → 403.

Add a Playwright test in `frontend/`:

- `test('flagged post shows guidelines modal')` — submit a post with a blocked word, expect the friendly error modal with the guidelines link.

---

### 9. Operational

- Add a `Makefile` target `make moderation-test` that runs only the moderation tests + lints.
- Add a `scripts/check_severe_terms.py` that lints the term files: no duplicates, no empty lines, no obvious typos in the German file (use `pyenchant` if you want, or just length checks).
- Document the moderation pipeline in `backend/README.md`: what runs in what order, how to add a term, how to rotate `OPENAI_API_KEY`, how to read the audit log.

---

## Constraints

- **Pydantic v2** patterns only (we're on `pydantic>=2.7`).
- **No breaking changes** to the existing `check_and_clean` signature — wrap it.
- **Never store the full text** of `BLOCK`ed content. Hash only. (Storing it could itself be a problem — e.g. CSAM hash matches, hate speech archives.) For `CENSOR`/`REVIEW`, an 80-char excerpt is fine.
- **Never log API keys**. The OpenAI client should read `settings.OPENAI_API_KEY` and nothing else.
- **All admin endpoints** must verify `current_user.is_admin` and write to an audit log.
- **i18n**: error messages returned to the frontend must be i18n keys (e.g. `moderation.blocked.hate`), not hardcoded English strings. The frontend translates.
- **Tests must pass on CI** without an `OPENAI_API_KEY` — mock the client.
- **Don't add a new ML model** to the backend. We're not self-hosting BERT/Qwen. OpenAI moderation API is the contextual layer; word lists are the deterministic layer. That's the architecture.

---

## Acceptance criteria

- [ ] A post containing a German slur is blocked with a friendly error.
- [ ] A post containing `f​uck` is treated the same as `fuck`.
- [ ] A post containing borderline harassment is published but appears in the admin moderation queue.
- [ ] A user posting 11 times in an hour gets a 429.
- [ ] An admin can approve or remove flagged content from `/admin/moderation`.
- [ ] All footer links (`/privacy`, `/terms`, `/community-guidelines`, `/impressum`, `/contact`) render real content, not 404.
- [ ] `make moderation-test` passes locally and in CI.
- [ ] `OPENAI_API_KEY` removed from env → app still boots, moderation degrades to word-list-only with a warning logged.

---

## What this prompt deliberately does NOT cover (do later)

- Image moderation beyond the stub interface.
- Federated learning / on-device classifiers.
- Appeals workflow with user-facing escalation (v2).
- BERT/Qwen self-hosted classifier — explicitly rejected as over-engineered for our scale.
- Account age verification (no reliable way without ID checks; document the limitation in `/community-guidelines`).
