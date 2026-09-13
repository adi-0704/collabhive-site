# CollabHive — Instagram DM Templates

## Part 1 — Creator Outreach

Use this two-step sequence so Instagram doesn't flag you as spam. Send **Message 1**
first. Wait for a reply. Only after they reply (or reply to your follow-up), send
**Message 2** with the links. Sending links instantly = looks like spam → risk of
being marked/restricted.

---

## Message 1 — Opening (no links)

> Hey there! 👋 Your content caught our eye and we love your overall vibe here on Instagram. 🔥
>
> We're CollabHive, an influencer marketing agency. We're currently building a curated network of top-tier creators across all niches for upcoming brand collaborations and campaigns.
>
> We think you'd be a perfect fit for our network. Would you be open to connecting and hearing about upcoming opportunities? 😊

**Manual DM rules:**
- Send to ~10–15 creators per hour max.
- Do NOT paste links in this message.
- Personalize the first line if you can (e.g. their niche or a specific reel).
- New accounts send fewer per day; warm up slowly.
- Only message creators whose content you can genuinely match.

---

## Message 2 — Follow-up with links (ONLY after they reply)

> That's great to hear! 🎉
>
> Here's how it works: you fill out a quick 2-minute application form so we have your details, and our team reviews your profile for upcoming brand collabs. Once you're in, we match you with brands that fit your niclech and style — and you keep 90% of what you earn.
>
> 📝 Apply here: <APPLY_FORM_URL>
>
> 🌐 Learn more about us: <SITE_URL>
>
> Zero fees to join, no commitment. Once you're approved, we reach out whenever a fit comes up. 😊

---

## Replace placeholders before sending
- `<APPLY_FORM_URL>` → https://docs.google.com/forms/d/e/1FAIpQLScIV5PVkwbdcvMpzCyxTAzN71ORCqaTaIMY7Dr15xEMXSxIXQ/viewform
- `<SITE_URL>` → https://adi-0704.github.io/collabhive-site/

---

## Suggested follow-up words (if they haven't replied after 2–3 days)
> Just circling back on this — we're still building our creator network and would love to have you on board. 🚀 No pressure, just let me know if you're open to it!

---

## Tips to avoid an Instagram spam label
1. Never DM a link as the very first message.
2. Don't paste the same message word-for-word to hundreds at once — vary it slightly and only reach signed/matching accounts.
3. Don't open links often / at high volume from a brand-new account.
4. Respond to their reply naturally before dropping links.
5. Keep it conversational, not salesy.

---
---

## Part 2 — Brand Outreach (Fashion & Beauty focus)

This is the manual counterpart to the automated email pipeline in `outreach/`. The
email pipeline (`outreach/src/run.py`, scheduled via `.github/workflows/outreach-daily.yml`)
already discovers Fashion & Beauty brands, scrapes a public contact email off their
website, and sends them a personalized pitch daily — see the roadmap message for how
that's configured. Instagram DMs are the manual channel for brands that don't publish
an easy-to-scrape email, or as a faster/warmer first touch before the email lands.

**Do not re-target these on Instagram — they're already in the automated email queue**
(`outreach/data/brands_seed.json`, niches `Fashion & Apparel` / `Beauty & Cosmetics`):
Amara Shoes, Anouk Ethnic, Aqualogica, Asaya, Auli Lifestyle, Aurelia, Bella Vita Organic,
Berrylush, Biba, Biotique, Bunaai, Chemist at Play, Chumbak, Clovia, Deconstruct, Deyga
Organics, Doodlage, Dot & Key, Dr. Sheth's, Earth Rhythm, FabIndia, FableStreet, Forca By
Virat, Forest Essentials, Foxtale, Global Desi, Hair Originals, Juicy Chemistry, Just
Herbs, Mamaearth, Minimalist, Miraggio, Nappa Dori, Nykaa, Perfora, Plum, Rare Rabbit,
SUGAR Cosmetics, Snitch, SunScoop, Suta, The Ayurveda Company, The Derma Co, The House of
Rare, The Indian Garage Co., The Jodi Life, The Kaftan Company, The Label Life, The Souled
Store, Wow Skin, Zaliga, Zivame, Zudio. Use Instagram to find brands **outside** this list —
that's where the manual channel adds reach the automation doesn't already cover.

### Where & how to search

1. **Seed-and-expand**: follow 5–10 accounts from the list above on Instagram. Their
   "Suggested for you" carousel and the Explore tab will start surfacing similar-sized
   D2C fashion/beauty brands you haven't seen yet — that's the fastest source of
   genuinely comparable, still-small brands.
2. **Hashtag search** (Instagram search bar → Tags): `#indianfashionbrand`,
   `#d2cindia`, `#indianstartup`, `#ethnicwearindia`, `#streetwearindia`,
   `#beautybrandindia`, `#skincareindia`, `#indiandesigner`, `#sustainablefashionindia`,
   `#madeinindia`. Sort by "Recent" occasionally, not just "Top", to catch smaller
   accounts the algorithm doesn't push.
3. **Location tags**: search a city (Delhi, Mumbai, Bangalore, Jaipur, Hyderabad,
   Ahmedabad — the cities already in `outreach/config.json`) and browse tagged posts;
   small boutiques/labels tag their city often.
4. **"Tagged" tab of a bigger brand**: open a large fashion/beauty account's Tagged
   tab — smaller brands and creators they've cross-promoted or been compared to show
   up there.
5. **Bio-link check (qualify before DMing)**: open the brand's bio link. Good targets
   have a working checkout/DTC website and no existing "Partnerships: agency@..."
   email already advertised — if they list an agency contact, they're likely already
   working with someone; email them instead of DMing (their email will also get
   auto-discovered by the pipeline).

### Message 1 — Opening (no links)

> Hey [Brand] team! 👋 Been following your page — the [recent collection / specific post] really stood out.
>
> We're CollabHive, an influencer marketing agency running a curated network of Fashion & Beauty creators across India. We match D2C brands like yours with vetted creators for collabs — no retainer, no minimum spend, creators keep 90%.
>
> Would you be open to a quick campaign brief? Takes 2 minutes and we'll send back a shortlist + quote within a day.

### Message 2 — Follow-up with links (ONLY after they reply)

> Great! Here's how it works — you share your budget, city, and goal, and we match you with 3–6 creators from our network plus a transparent quote (fair 10% commission, no hidden fees).
>
> 📋 Share your brief: <BRIEF_FORM_URL>
> 🌐 See how we work: <SITE_URL>
>
> Happy to answer anything here first if you'd rather chat before filling it in.

Replace placeholders: `<BRIEF_FORM_URL>` → the brand-brief Google Form URL in
`outreach/config.json → profile.brand_brief_url`; `<SITE_URL>` → `profile.site_url`.

### Follow-up (no reply after 2–3 days)
> Just circling back — happy to share a quick shortlist + quote whenever it's useful, no pressure either way!

### Tracking (so IG and email don't collide)
If a brand replies positively on Instagram, add them straight to
`outreach/data/brand_briefs.json` (or point them at the brief form, which flows into
the same file automatically) so they enter the same shortlist/quote/pipeline
automation as email-sourced brands — you don't need a separate system for them.
