# CollabHive Outreach Automation

A **fully free, daily, automated** brand-outreach system. It finds small/startup
businesses across Indian niches, extracts their public emails, emails them an
intro to CollabHive + your website/apply links, and logs everything to a
monitoring dashboard you reach from the **admin panel**.

Zero cost: Python stdlib only (+ optional Playwright), GitHub Actions free
tier, GitHub Pages free hosting, Gmail SMTP with your app password.

---

## What it does every day (scheduled)
1. **Discovers** target brands (Google Maps scrape, throttled, 1 niche/day, plus
   the curated seed pool).
2. **Extracts emails** from each brand's website (free).
3. **Sends** up to `daily_limit` (default 18) personalized emails, niche-
   rotated across the week, with randomized delays + circuit breaker.
4. **Sales & reach** (automatic): scans Gmail replies → builds a Closing Queue of
   hot leads; auto-matches brand briefs to best-fit creators → daily shortlist;
   generates programmatic niche×city SEO pages.
5. **Logs** every send and writes `data/report.json`.
6. **Pushes** the report + SEO pages back to the repo so the site + dashboard
   update.

You never have to touch it. You just monitor.

---

## How it's hosted (all free)
| Piece | Where |
|---|---|
| Daily scheduled run | `.github/workflows/outreach-daily.yml` (cron `30 3 * * *` = 09:00 IST) |
| Brand discovery (Maps) | `.github/workflows/outreach-maps.yml` (manual only) |
| Dashboard | `outreach/dashboard/index.html` on GitHub Pages |
| Data | `outreach/data/*.json` (committed after each run) |
| Login for email | Gmail SMTP via GitHub Secrets |

---

## ✅ One-time setup (manual, human-only)

### 1. Add GitHub Secrets (Repo → Settings → Secrets → Actions)
You **must** add these for email to send:
- `OUTREACH_EMAIL_USER` → `collabhive.in@gmail.com`
- `OUTREACH_EMAIL_PASS` → your Gmail **app password** (the 16-char one)

> Your app password is **never** committed. It lives only in GitHub Secrets.
> Update Gmail → Security → 2-Step Verification → App passwords if you need a new one.

### 2. Enable Pages (if not already)
Repo → **Settings → Pages** → Source: `Deploy from a branch` → `main` / root.
The dashboard is at:
```
https://adi-0704.github.io/collabhive-site/outreach/dashboard/
```

### 3. Add brands to the seed pool
`outreach/data/brands_seed.json`. Each entry:
```json
{ "name": "Zesty Foods", "niche": "Food & Beverage", "city": "Delhi",
  "website": "https://zesty.in", "email": "", "emails": [], "source": "seed" }
```
The daily run extracts emails from each `website` automatically.
You can also add them from the admin panel flow, or manually.

### 4. (Optional) Test the daily run manually
Repo → **Actions** → "Outreach Daily Run" → **Run workflow** (mode `all`). Check the log.

---

## Monitoring
- **Admin panel → "Open Outreach Monitor"** (links to the dashboard).
- Dashboard shows: emails sent, unique brands, pool size, remaining candidates,
  distribution by niche + city, and the recent-sends table.
- `data/report.json` is the raw source the dashboard reads.

---

## Configuration
`outreach/config.json`:
- `smtp.daily_limit` / `daily_hard_cap` → emails per day (mandatory 15–20 range).
- `smtp.min/max_delay_seconds` → randomized send spacing (anti-spam).
- `niches.categories` → niches, keywords, cities. Rotates daily.
- `profile.site_url` / `apply_url` → links inside every email.
- `sales.*` → reply-triage keywords, closing queue, creator pool, briefs, commission.
- `seo.*` → programmatic page generation.

## Sales & reach automations
- **Reply triage**: `python src/run.py sales` reads Gmail IMAP inbox, classifies
  replies (interested / negotiating / declined) and fills the Closing Queue in
  `data/closing_queue.json`. Uses your Gmail app password via IMAP.
- **Auto-match**: reads `data/brand_briefs.json` ↔ `data/creators_pool.json`,
  scores each creator, writes `data/shortlist.json` (best-fit per brief).
- **Quote builder**: auto-generates campaign quotes with your commission.
- **SEO pages**: `python src/run.py seo` writes niche×city landing pages to
  `seo-pages/` (published with the site, committed by the daily run).

---

## Google Maps scraper (automated now — read the warning)
`outreach/src/maps_scraper.py` auto-discovers brands from Google Maps using
Playwright. It runs **inside the daily scheduled workflow** (1 niche/day,
low volume via `outreach/config.json → discovery`), with throttling, a session
cap, exponential backoff, and a cooldown after repeated failures.

> ⚠️ **Risk accepted by the owner.** Google Maps scraping violates Google's
> Terms of Service and can trigger IP throttling or bans. It is tuned to be
> low-volume and self-protecting, but it is not guaranteed safe. If you later
> want reliability without this risk, switch `discovery.enabled` to `false`
> and use the curated seed pool, or move to the paid Places API.

See `outreach/config.json → discovery` to tune volume / turn it off.

---

## IP-ban protection
- Daily runs from GitHub's rotating IPs to send email (not your home IP).
- `outreach/src/protect.py`: token bucket, per-hour cap, session cap, randomized
  jitter, exponential backoff, and a circuit breaker that stops after repeated
  SMTP failures.
- Volume kept to 15–20/day, spread across niches and days.

---

## Local testing (optional)
```
cd outreach
cp .env.example .env      # fill in credentials for SMTP test
python src/run.py report  # writes data/report.json
python src/run.py daily   # dry-sends if password set, else safe-skip
```
