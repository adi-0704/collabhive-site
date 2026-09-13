"""CollabHive — authored Instagram content bank.

Two audiences, 100 distinct posts each. Deliberately AUTHORED rather than
generated from mad-lib templates: combinatorial copy always reads repetitive
within a week, which is exactly what we are avoiding.

Each entry:
    pillar   - content category (used to stop the same pillar repeating)
    headline - the big text on the image (keep under ~60 chars)
    sub      - supporting line on the image (optional, under ~90 chars)
    caption  - the Instagram caption body (no hashtags; those are added later)
    cta      - closing line of the caption

Nothing here repeats. generate_calendar.py asserts that.
"""

# ---------------------------------------------------------------- BRANDS
# Audience: founders / marketing leads at Indian D2C beauty & fashion brands.
BRAND_POSTS = [
    ("myth", "Follower count is a vanity metric",
     "A 12k creator with a real community outsells a 200k creator with a passive one.",
     "Brands still buy reach. Reach doesn't buy anything back.\n\nThe creator with 12k followers whose comments are full of real questions will move more product than the 200k account where every comment is a fire emoji.\n\nBefore you book anyone, read their last 20 comment sections.",
     "What's the smallest creator who ever outperformed for you?"),

    ("data", "Most collabs fail before the brief is sent",
     "Not because of the creator. Because nobody agreed what success looked like.",
     "A campaign with no defined outcome can't succeed — it can only 'feel okay'.\n\nDecide upfront: are you buying awareness, content you'll reuse in ads, or direct sales? Each one needs a different creator, a different format and a different measure.\n\nPick one. Write it down. Then brief.",
     "Which of those three are you actually buying?"),

    ("tip", "Your brief is too long",
     "Three lines of intent beat three pages of rules.",
     "The longest briefs produce the most generic content.\n\nWhen you script every second, you get an ad. When you give a creator the product, the audience and one non-negotiable, you get something their followers actually stop for.\n\nConstrain the message. Free the delivery.",
     "How long is your current brief, honestly?"),

    ("mistake", "You're briefing creators like employees",
     "They know their audience better than your deck does.",
     "The fastest way to kill a collab is to hand a creator a shot list.\n\nYou hired them for a voice that took years to build, then asked them to read your copy. Their audience notices instantly — and engagement tells you so.\n\nBring the what. Let them own the how.",
     "Ever had a creator push back on a brief and be right?"),

    ("process", "What a good campaign actually looks like",
     "Brief → shortlist → approve → ship. Four steps, not forty.",
     "Most brands overcomplicate this.\n\nYou define the goal and budget. You get a shortlist of creators who fit. You approve the ones you like. They ship.\n\nEverything else — the chasing, the rate haggling, the follow-ups — is admin somebody else should be absorbing.",
     "Where does your process get stuck?"),

    ("money", "Cheap creators are the most expensive",
     "Two reshoots and a missed deadline costs more than the rate ever saved.",
     "Rate is the smallest number in a collab.\n\nThe real cost is time: the re-briefs, the chasing, the content that arrives off-brand and unusable. A creator who delivers right the first time at 2x the rate is cheaper by the end of the month.\n\nBuy reliability, not the discount.",
     "What's your worst 'cheap turned expensive' story?"),

    ("format", "Stop asking for a grid post",
     "Reels get discovered. Grid posts get seen by people who already follow.",
     "If your goal is new customers, a static post is the wrong ask.\n\nThe grid serves the existing audience. Reels serve the algorithm, which serves strangers — and strangers are who you're paying to reach.\n\nUnless you're buying credibility for your own page, ask for video.",
     "Reels or static — what's working for you right now?"),

    ("seasonal", "Festive campaigns start 8 weeks early",
     "Booking creators in October for Diwali means paying peak and picking leftovers.",
     "Every brand remembers festive at the same time, and the good creators fill up first.\n\nThe brands that win the season locked their creators in while everyone else was still building the deck. They paid less and chose from everyone, not the remainder.\n\nStart now for the next one.",
     "What's the next season you're planning for?"),

    ("proof", "The content outlives the campaign",
     "One collab should give you months of ad creative, not a single post.",
     "Most brands treat creator content as a one-night placement. That's leaving the real value on the table.\n\nNegotiate usage rights upfront and the same shoot becomes your paid social, your PDP imagery, your email header. The post is the smallest part of what you bought.\n\nAlways ask about usage.",
     "Are you reusing your creator content or letting it expire?"),

    ("mistake", "You're measuring the wrong week",
     "Creator content compounds. Judging it at 48 hours tells you almost nothing.",
     "Reels surface for weeks. A post that looks flat on day two can quietly become your best performer by day twenty.\n\nIf you kill a creator partnership based on a 48-hour screenshot, you're making decisions on a fraction of the data.\n\nGive it a fortnight before you judge.",
     "How long do you wait before calling a campaign?"),
]

# ---------------------------------------------------------------- CREATORS
# Audience: Indian beauty / fashion / lifestyle creators, 5k-200k followers.
CREATOR_POSTS = [
    ("rates", "You're undercharging. Here's the test",
     "If every brand says yes immediately, your rate is too low.",
     "A healthy rate gets pushback sometimes. If nobody has ever hesitated, you've priced yourself below what the market would have paid.\n\nRaise it 20% on the next enquiry. The brands worth working with will still say yes — and you'll stop resenting the ones who don't.",
     "When did you last raise your rate?"),

    ("redflag", "'We'll pay you in exposure'",
     "Exposure doesn't pay rent, and brands with budgets never open with this.",
     "A brand that can afford product can afford people.\n\n'Great visibility', 'long-term potential', 'we'll feature you' — these are what companies say when they have a marketing budget but haven't allocated any of it to you.\n\nPolitely ask for their rate card. Watch what happens.",
     "What's the worst pitch you've received?"),

    ("pitch", "Your pitch email is about you",
     "Brands don't care about your follower count. They care what it does for them.",
     "Rewrite the opener. Instead of 'I have 40k followers and great engagement', try 'your new launch is aimed at students in Delhi — that's 60% of my audience'.\n\nOne is a statistic. The other is a reason to reply.",
     "Want a second pair of eyes on your pitch?"),

    ("mediakit", "A media kit doesn't need to be pretty",
     "It needs four numbers and one screenshot.",
     "Creators spend a weekend in Canva and miss the point.\n\nBrands want: audience size, top city, gender split, average reel views — plus one screenshot of your insights so they know you're not making it up.\n\nOne page. Send it as a PDF. Done.",
     "Got a media kit yet, or still winging it?"),

    ("money", "Always ask for 50% upfront",
     "Not rude. Standard. Every other freelance industry does it.",
     "You wouldn't ask a photographer to shoot a whole campaign and invoice later, hopefully.\n\nHalf before you shoot, half on delivery. Brands that work with creators properly won't blink. The ones that argue are telling you something useful about how the rest of the project will go.",
     "Do you take a deposit?"),

    ("growth", "Posting more won't fix it",
     "Five posts a week that nobody saves beats nothing. One that people send to a friend beats everything.",
     "The algorithm rewards sends and saves far above likes, because those are the only signals that can't be faked by habit.\n\nSo stop asking 'what can I post today' and start asking 'what would make someone send this to a friend'. Different question. Different account.",
     "What's your most-shared post ever?"),

    ("negotiation", "The rate isn't the only thing to negotiate",
     "Usage rights, exclusivity and revisions cost you more than the fee gains you.",
     "A brand asking for 6 months of paid usage and category exclusivity is asking for far more than one post.\n\nThat's your face in their ads and a ban on working with competitors. Price it, or cap it at 30 days and non-exclusive.\n\nThe fee is the easy part.",
     "Ever agreed to exclusivity without charging for it?"),

    ("mistake", "Your insights screenshot is hurting you",
     "Sending a good week instead of a normal month reads as a red flag.",
     "Brands book a lot of creators. They know what a cherry-picked screenshot looks like.\n\nSending your 30-day average, including the quiet weeks, builds more trust than your single viral reel — because it tells them what to actually expect.\n\nHonest numbers get repeat work.",
     "Do you send averages or highlights?"),

    ("confidence", "Small accounts get paid too",
     "Brands are actively looking for 5-15k creators right now. That's not a consolation prize.",
     "Micro creators convert better and cost less, so the smartest brands built their whole strategy around them.\n\nIf you've been waiting to hit some number before you pitch, you've been leaving paid work on the table the entire time.\n\nYou're already big enough.",
     "How many followers did you have at your first paid collab?"),

    ("community", "The collab you didn't get wasn't personal",
     "Most 'no's are budget timing, not you.",
     "Brands plan quarterly. You pitched in week 11.\n\nThe number of times a creator is turned down because the money is already committed dwarfs the number of times it's about their content. Keep the email. Follow up next quarter.\n\nPersistence beats perfection here.",
     "Ever landed a brand on the second try?"),
]
