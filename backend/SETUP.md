# CollabHive — Backend setup (Google Sheets + Apps Script)

The site works in **demo mode** out of the box (sample brands/creators, writes to your
own browser). To make it **live** — so onboarded creators/brands appear for everyone and
the admin panel shows real numbers — connect a free Google Sheets backend. This takes ~10 minutes.

## What you need to do (the only manual steps)

### 1. Create a Google Sheet
- Go to sheets.google.com → create a blank sheet (name it `CollabHive`).
- Copy the **Sheet ID** from the URL: `https://docs.google.com/spreadsheets/d/<THIS_PART>/edit`

### 2. Create the Apps Script
- Go to script.google.com → **New project**.
- Delete the default `myFunction` code and paste the entire contents of `backend/Code.gs`.
- Save (rename the project to `CollabHive API`).

### 3. Set Script Properties
- In the editor: **Project Settings** (⚙) → **Script Properties** → **Add script property**:
  - `SHEET_ID` → the Sheet ID from step 1
  - `ADMIN_KEY` → a secret key of your choice (this locks the admin panel + brand/booking data)

### 4. Deploy as a Web App
- Click **Deploy** → **New deployment** → ⚙ gear → **Web app**.
  - Description: `CollabHive API`
  - Execute as: **Me**
  - Who has access: **Anyone**
- Click **Deploy**, authorize, then **copy the Web app URL** (looks like `https://script.google.com/macros/s/XXXX/exec`).

### 5. Point the site at it
- In the repo, open `assets/js/config.js`.
- Paste the Web app URL into `base` and set `adminKey` to your `ADMIN_KEY`.
- Commit + push (or tell me the URL and I'll wire + deploy it).

## How it works
| Sheet | Purpose | Public? |
|---|---|---|
| `creators` | Creator applications (onboard) | read public (powers directory + dashboard) |
| `brands` | Brand briefs (onboard) | admin only |
| `bookings` | Bookings from the dashboard "Book" button | admin only |

- **Onboard → visible:** a creator who submits the "Apply" form is appended to `creators`,
  and immediately appears in the directory on `brands.html#directory` and `dashboard.html`.
- **Booking → WhatsApp:** a brand taps "Book this creator" → a booking row is appended AND
  a pre-filled WhatsApp message opens to +91 81780 22572.
- **Admin panel:** `admin.html` → enter your `ADMIN_KEY` → stats (brands/creators/bookings) + full tables.

## Security notes
- The Web app is public (needed for the static site to call it). Creator data is public by
  design; brand + booking data and stats are gated by `ADMIN_KEY` (checked server-side).
- This is MVP-grade auth — fine for launch, but upgrade to a real backend (e.g. Firebase /
  Supabase) before storing anything sensitive like emails or payment info.
