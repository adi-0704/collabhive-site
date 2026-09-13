# Instagram auto-posting — Meta setup

One-time setup, ~30 minutes. Do this once per page (brand page + creator page).
After it's done, `.github/workflows/social-daily.yml` posts every day at 11:00 IST
with no laptop involved.

You need 4 values at the end:

| GitHub Secret | What it is |
|---|---|
| `IG_BRAND_USER_ID` | Instagram Business account ID for the brand page |
| `IG_BRAND_TOKEN` | Long-lived access token for that page |
| `IG_CREATOR_USER_ID` | Instagram Business account ID for the creator page |
| `IG_CREATOR_TOKEN` | Long-lived access token for that page |

---

## 1. Convert both pages to Business accounts

Instagram app → Settings → Account type → **Switch to Professional → Business**.

> It must be **Business**, not Creator. The content-publishing API does not work
> with Creator accounts. This is the most common reason setup fails.

## 2. Connect each Instagram account to a Facebook Page

Instagram app → Settings → Business → **Connect a Facebook Page**. Create a new
Page if you don't have one (it can be empty — it just has to exist; the API
reaches Instagram *through* the Page).

## 3. Create a Meta app

1. Go to https://developers.facebook.com/apps → **Create App**
2. Use case: **Other** → App type: **Business**
3. Name it `CollabHive Publisher`
4. In the app dashboard → **Add products** → add **Instagram** (Graph API)

Leave the app in **Development mode**. You do *not* need App Review, because
you're publishing to accounts you own and administer. App Review is only
required to publish on behalf of other people's accounts.

## 4. Grant permissions and generate a token

1. Go to https://developers.facebook.com/tools/explorer (Graph API Explorer)
2. Top right: select your `CollabHive Publisher` app
3. Click **Generate Access Token**, and tick these permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
   - `business_management`
4. Log in and approve. You now have a **short-lived** token (expires in 1 hour).

## 5. Exchange it for a long-lived token

Short-lived tokens are useless for automation. Exchange it — paste this in your
browser, replacing the three values:

```
https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_LIVED_TOKEN
```

App ID and App Secret are in your app dashboard under **Settings → Basic**.
The response contains `access_token` — that's your long-lived token (~60 days).

## 6. Find each Instagram account ID

In the Graph API Explorer, run:

```
me/accounts?fields=name,instagram_business_account
```

You'll get one entry per Facebook Page. The `instagram_business_account.id`
value is what you need — match it to the right page by name.

## 7. Add the secrets to GitHub

Repo → **Settings → Secrets and variables → Actions → New repository secret**.
Add all four values from the table at the top.

## 8. Test before trusting it

Repo → **Actions → Social Daily → Run workflow**, with **dry_run = true**.
It prints exactly what it would post without publishing. If that looks right,
run it again with `dry_run` unticked.

---

## ⚠ Tokens expire every ~60 days

This is the part that will break your automation, so put a calendar reminder
now. When the token expires the workflow starts failing and posts stop.

Two options:
- **Manual:** repeat steps 4–5 every ~50 days and update the secret.
- **Better:** use a System User token from
  https://business.facebook.com → Business Settings → Users → System Users.
  System User tokens can be generated without expiry, which is the correct
  setup for unattended automation.

I'd do the System User route — it's slightly more setup once and then it
doesn't silently die two months later.

---

## Requirements the API enforces

- Images must be **public URLs** — that's why the PNGs are committed and served
  from GitHub Pages. A private repo breaks this.
- JPEG/PNG, aspect ratio between 4:5 and 1.91:1. The generated cards are
  1080×1350 (4:5), which is valid.
- Rate limit: **25 posts per account per 24h**. We post 1/day.
- Captions: max 2,200 characters and **30 hashtags**. We send ~15.
