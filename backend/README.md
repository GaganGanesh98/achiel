# CampusVoice API

**Germany-only:** university search and signup use the HRK/Hochschulkompass catalogue in `app/seed/german_universities.py` (208 institutions). After pulling, run `uv run alembic upgrade head` to seed the `universities` table and enable `pg_trgm` search.

## Local development

See the repo root `README.md` for Postgres, Redis, migrations, and `uvicorn`.

## Email (SMTP)

Transactional email uses `aiosmtplib` via `app/services/email.py`.

| Variable | Purpose |
|----------|---------|
| `SMTP_HOST` | SMTP server hostname (empty = dev mode) |
| `SMTP_PORT` | Port (`2525` Mailtrap, `587` Gmail) |
| `SMTP_USER` / `SMTP_PASSWORD` | Credentials |
| `SMTP_FROM` | From address |
| `SMTP_TLS` | `true` for STARTTLS (Gmail on 587) |
| `APP_BASE_URL` | Frontend base for links in emails |
| `ENV` | `development` prints emails to stdout when `SMTP_HOST` is empty |

### Dev

Leave `SMTP_HOST` empty — password-reset and email-confirmation messages are printed to the terminal (no Mailtrap required).

To use [Mailtrap](https://mailtrap.io) (free inbox), paste their SMTP credentials:

```env
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=your_mailtrap_user
SMTP_PASSWORD=your_mailtrap_password
SMTP_TLS=false
```

### Production (Railway)

Use Gmail with an [app password](https://support.google.com/accounts/answer/185833):

```env
ENV=production
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_TLS=true
SMTP_FROM=no-reply@campusvoice.app
APP_BASE_URL=https://your-frontend.up.railway.app
```

Gmail caps at ~500 emails/day. For higher volume, switch to Resend or Postmark and update `EmailService` accordingly.
