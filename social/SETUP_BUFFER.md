# Instagram auto-posting via Buffer

Simpler than the Meta Graph API: Buffer handles the Instagram connection, so
there's no Meta app, no permission review and no 60-day token expiry to babysit.

Once set up, `.github/workflows/social-daily.yml` queues the day's post for both
pages every morning and Buffer publishes them. Your laptop is not involved.

---

## 1. Create the Buffer account and connect both pages

1. Sign up at https://buffer.com
2. **Connect Channels** → Instagram → connect the **brand page**
3. Connect Channels again → Instagram → connect the **creator page**

> Both Instagram accounts must be **Business or Creator** accounts connected to
> a Facebook Page. Buffer will walk you through it during connection — this is
> an Instagram requirement, not a Buffer one.

**Free plan covers 3 channels**, so two Instagram pages fit. Note the free plan
holds 10 queued posts per channel, which is plenty for one post a day.

## 2. Get your API token

1. Go to https://publish.buffer.com/developers/api
2. Create an access token (or use the existing one if you already made a Buffer
   developer app)
3. Copy it

## 3. Add it to GitHub

Repo → **Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|---|---|
| `BUFFER_ACCESS_TOKEN` | the token from step 2 |

That secret is already wired into both workflows — nothing else to configure
there.

## 4. Find your two channel IDs

Locally, with the token exported:

```bash
export BUFFER_ACCESS_TOKEN=your_token_here
python social/publish_buffer.py --list-channels
```

You'll get something like:

```
organization: CollabHive  id=6a99504c4cc393783e8d69fe
   channel  instagram    collabhive.brands      id=6a9951...
   channel  instagram    collabhive.creators    id=6a9952...
```

## 5. Put the IDs in config

Open `outreach/config.json` and fill in the two ids:

```json
"buffer": {
  "channels": {
    "brand":   "6a9951...",
    "creator": "6a9952..."
  }
}
```

Commit and push that change.

## 6. Test before trusting it

Repo → **Actions → Social Daily → Run workflow** with **dry_run = true**.
It prints exactly what it would queue, without touching Buffer.

If that looks right, run it again with `dry_run` unticked, then check your
Buffer queue — the post should be sitting there.

---

## How the images work

Buffer fetches the image from a public URL rather than taking an upload. The
rendered PNGs are committed to the repo and served by GitHub Pages at
`https://adi-0704.github.io/collabhive-site/social/calendar/images/...`, so
committing the image *is* the upload.

Two consequences worth knowing:
- The repo has to stay **public** for this to work.
- Generated images must be **committed before** the posting workflow runs.
  Run `python social/generate_calendar.py` and push whenever you extend the
  calendar.

## Instagram publishing caveat

Buffer auto-publishes single images to Instagram Business accounts without any
manual step. For **carousels and some Reels formats** Buffer sends a phone
reminder instead of publishing directly. Everything the generator produces is a
single 1080×1350 image, so it publishes automatically.

## Scheduling

The workflow runs at **11:00 IST daily**. Buffer then posts according to your
channel's posting schedule — so either set your Buffer schedule to roughly that
time, or let Buffer's own queue timing decide. Don't set both to fight each
other; pick one and leave it.
