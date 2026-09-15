# Comment-to-DM automation

Turns the 149 days of scheduled content into a lead-capture channel. Someone
comments a keyword on a post, and they automatically receive a DM.

This is the **only** kind of Instagram DM automation worth doing.

---

## Why not automate cold DMs

There is no official API for messaging someone who has not messaged you first.
Every tool that offers it drives your account through an unofficial login, and
that is the most common cause of Instagram restrictions and bans.

The accounts at risk are @collabhive.in and @collabvibe.in — the ones your 43
creators came through. Losing them costs more than the manual DM effort saves.

Inbound automation is fully supported by Meta and carries none of that risk.

---

## Two routes

| | Meta Graph API | ManyChat |
|---|---|---|
| Cost | Free | ~$15/mo |
| Setup | Meta app + App Review for `instagram_manage_messages` | Connect account, done |
| Time | Days (review queue) | An afternoon |

**Use ManyChat.** It is an official Meta partner, the review is already done on
their side, and the Meta app route was abandoned once already on this project.

---

## Setup (ManyChat)

1. Sign up at https://manychat.com and connect **both** Instagram accounts.
   Each is a separate "page" in ManyChat.
2. **Automation → New Automation → Instagram Comments**
3. Set the trigger keyword, pick "Any post" (so it applies to all 149 days),
   and write the DM that goes out.
4. Turn on **"Reply to comment"** as well — a public reply makes the automation
   visible to everyone else reading, which is where most of the extra reach
   comes from.

### Keywords to configure

**@collabhive.in (brands)** — keyword `QUOTE`

> Hey! Thanks for commenting 👋
>
> Here's how a free shortlist works: tell me your budget, city and campaign goal, and we'll send back matched creators plus a transparent quote within a day.
>
> Creators keep 90%. No retainer, no minimum spend.
>
> Share the details here, or use this 2-min form: {BRAND_BRIEF_URL}

**@collabvibe.in (creators)** — keyword `JOIN`

> Hey! Thanks for commenting 👋
>
> We match creators with beauty & fashion brands in India — you keep 90% of what you earn, and there's no fee to join.
>
> Takes 2 minutes to apply: {APPLY_FORM_URL}
>
> Any questions, just reply here.

Replace the placeholders with the URLs in `outreach/config.json` →
`profile.brand_brief_url` and `profile.apply_url`.

---

## Making the posts ask for it

A comment-to-DM automation does nothing if the content never invites a comment.

`social/generate_calendar.py` supports a `comment_cta` config block. When set,
every generated caption ends with the prompt, so all 149 days ask for the
comment automatically:

```json
"social_cta": {
  "enabled": true,
  "brand":   "Comment QUOTE and we'll DM you a free creator shortlist 👇",
  "creator": "Comment JOIN and we'll DM you the application link 👇"
}
```

After changing it, push — the Social Generate workflow rebuilds every caption.

---

## What to expect

Comment-to-DM typically converts far better than a link in bio, because the
person never leaves the app. It also boosts the post: comments are a strong
engagement signal, so asking for one lifts reach on the content itself.

Watch it in the daily brief — `social/insights.py` tracks comments per post, so
you will see whether the CTA is actually producing them.
