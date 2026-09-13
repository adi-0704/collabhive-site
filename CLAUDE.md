# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

CollabHive is a static influencer-marketing marketplace site (plain HTML/CSS/JS, hosted on GitHub Pages, no build step) paired with a self-contained, zero-cost Python outreach-automation subsystem in `outreach/`. The automation runs daily via GitHub Actions, emails prospective brands, triages replies, auto-publishes creator applicants to the live site, generates SEO pages, and commits its own state/report back to the repo.

## Commands

All outreach commands are run from the `outreach/` directory.

```bash
cd outreach && python src/tests.py
```
Full sandboxed test suite (stdlib `unittest`, ~24 tests). Runs against a temp dir (`OUTREACH_ROOT`), stubs SMTP/IMAP/network — never sends real email or touches live `data/`. Safe to run anytime.

```bash
cd outreach && python src/tests.py <module>
```
Run tests for a single module (e.g. `brands`, `mailer`, `sales`).

```bash
cd outreach && python src/run.py <mode>
```
Pipeline entry point. Modes: `daily`, `enrich`, `pool`, `report`, `sales`, `seo`, `verify`, `automation`, `growth`, `onboarding`, `publish`, `buffer`, `record`, `all`. `all` runs the full daily pipeline (pool → enrich → daily → sales → automation → growth → onboarding → publish → seo → verify → report) and is what the scheduled workflow effectively does.

No install step is needed for the daily path — `outreach/requirements.txt` is stdlib-only. Playwright (`pip install playwright && playwright install chromium`) is only needed to run the Google Maps brand-discovery scraper manually.

To disable Google Maps discovery locally (bash):
```bash
OUTREACH_DISCOVERY=0 python src/run.py daily
```

## Architecture

**Frontend** (`index.html`, `brands.html`, `creators.html`, `dashboard.html`, `admin.html`, `assets/`): plain static pages with one config seam, `assets/js/config.js`, which points the site at either a Supabase backend (`supabaseUrl`/`supabaseAnonKey` — the currently live path) or a Google Sheets + Apps Script backend (`base`/`adminKey`, alternative). Setup docs live in `backend/SUPABASE.md` and `backend/SETUP.md`; `backend/Code.gs` is the Apps Script API, `backend/supabase.sql` the Postgres schema. `data/*.json` at the root is demo-mode sample data.

**Outreach automation** (`outreach/`): `config.json` is the single source of truth (SMTP, niches/cities, sales, SEO, social/Buffer, onboarding settings). `src/run.py` dispatches to modules under `src/`:
- `brands.py` / `pool.py` — seed pool management, email enrichment
- `maps_scraper.py` — optional Playwright-based Google Maps discovery (against Google ToS by its own admission; throttled, opt-in via `config.json → discovery`)
- `mailer.py` / `protect.py` — sends the daily batch, rate-limited with a token bucket + circuit breaker
- `sales.py` — IMAP reply triage, brief↔creator auto-matching, SEO page generation
- `automation.py` / `growth.py` — lead scoring, auto-quotes, follow-ups, weekly digest, DNC/pool pruning, sitemap
- `onboarding.py` — funnel analytics, instant-value emails, remarketing, referral tracking, A/B CTA
- `publication.py` — auto-publishes creator form submissions to the live site (Supabase) and drafts social posts
- `buffer.py` — queues social drafts to Buffer's API
- `verify.py` — confirms sent mail landed / detects bounces via IMAP
- `common.py` — config/path/logging helpers (`ROOT`, `load_config`, etc.)

State and generated data live in `outreach/data/*.json`; `outreach/dashboard/index.html` (GitHub Pages) reads `outreach/data/report.json`. `outreach/track/worker.js` is an optional Cloudflare Worker for open/click tracking and a funnel `/events` endpoint.

**Scheduling & deploy** (`.github/workflows/`):
- `outreach-daily.yml` — cron 09:00 IST daily (`30 3 * * *`) or manual dispatch with a mode choice (default `all`); always follows up with `seo`, `growth`, `onboarding`, `publish`, then commits `outreach/data/` and `seo-pages/` back to `main` (`[skip ci]`). This workflow is both the scheduler and the deploy mechanism — generated files are pushed directly to the repo.
- `outreach-maps.yml` — manual-only Maps discovery run.
- `outreach-tests.yml` — runs `python src/tests.py` on pushes/PRs touching `outreach/src/**` or `outreach/config.json`.

`seo-pages/` (niche×city landing pages, `sitemap.xml`, `robots.txt`) is generated output from `run.py seo`/`growth` — treat as build artifacts, not hand-edited source.
