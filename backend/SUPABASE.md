# CollabHive — Supabase backend setup (recommended)

Supabase gives a real, multi-user backend (Postgres + REST API) with a generous free tier.
The site talks to it directly via PostgREST — no server to run. Once wired, onboarding →
visible-to-brands, bookings, and the admin panel all work live for everyone.

## Steps

### 1. Create a project
- Go to https://supabase.com → sign in → **New project** (free tier is fine).
- Pick a region close to India (e.g. ap-south-1) for low latency.

### 2. Copy your keys
- In the dashboard: **Project Settings → API** (or the green **Connect** button).
- Copy:
  - **Project URL** (looks like `https://xxxx.supabase.co`)
  - **anon / public** key (a long JWT starting `eyJ...`)

### 3. Create the tables
- Open **SQL Editor** → **New query**.
- Paste the entire contents of `backend/supabase.sql` → **Run**.

### 4. Set your admin key (optional but recommended)
- The SQL seeds the admin key as `collabhive`. Change it by running:
  ```sql
  update public.settings set value = 'YOUR_SECRET_KEY' where key = 'admin_key';
  ```

### 5. Point the site at Supabase
- Open `assets/js/config.js` and set:
  - `supabaseUrl` → your Project URL
  - `supabaseAnonKey` → your anon key
  - `adminKey` → the key you set in step 4
- Commit + push (or tell me the values and I'll wire + deploy).

## How it works
| Data | Read | Write |
|---|---|---|
| `creators` (onboarding) | public (powers directory + dashboard) | public (Apply form) |
| `brands` (briefs) | admin only | public (brief form) |
| `bookings` | admin only | public (dashboard "Book") |

- **Onboard → visible:** a creator who submits the Apply form is inserted into `creators`
  and appears immediately in `brands.html#directory` and `dashboard.html`.
- **Booking → WhatsApp:** "Book this creator" inserts a `bookings` row AND opens a pre-filled
  WhatsApp message to +91 81780 22572.
- **Admin panel:** `admin.html` → enter your admin key → it calls the `admin_data` RPC, which
  checks the key **server-side** and returns brands, bookings and counts.

## Security
- Row Level Security is enabled: `creators` is public; `brands` and `bookings` have no anon
  SELECT policy, so they can only be read through the `admin_data` function (SECURITY DEFINER)
  after the admin key is verified server-side.
- The anon key is safe to ship in the frontend — it only grants what RLS allows.
