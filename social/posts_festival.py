"""CollabHive — festival-anchored posts for 2027.

These are NOT dated. Each entry carries a festival key, and the scheduler places
it at (festival date - lead_days) from festivals.json. That timing is the whole
point: a post about planning a Diwali campaign is worth a great deal eight weeks
out, when brands are setting budgets, and nothing at all on Diwali itself.

Entry shape matches the evergreen banks, plus a leading festival key:

    (festival, pillar, headline, sub, caption, cta)
"""

# --------------------------------------------------------------- BRAND
FESTIVAL_BRAND = [
    ("diwali", "seasonal", "Diwali creators are booked by August",
     "By the time you brief in October, the good ones are full.",
     "Diwali is the single biggest commercial window in India, and every brand in your category remembers it in the same week.\n\nThe brands that win booked their creators while everyone else was still building a deck. They paid pre-season rates and chose from the whole roster instead of whoever was left.\n\nIf Diwali matters to your year, the work starts now.",
     "When did you start planning last Diwali?"),

    ("diwali", "money", "Diwali creator rates rise 40-60%",
     "Not greed. Simple scarcity — every brand wants the same three weeks.",
     "Creator pricing is a supply market, and in October the supply is gone.\n\nThe same creator who costs one rate in August costs meaningfully more in October, because they can fill that slot ten times over. Booking early is not just about availability, it is the cheapest the campaign will ever be.\n\nLock rates in writing now.",
     "Have you budgeted for peak-season rates?"),

    ("diwali", "format", "Diwali content needs to exist before the sale",
     "People decide what to buy days before they decide where.",
     "Brands concentrate spend on the sale week and miss the decision week.\n\nGift shortlists, hamper ideas and 'what to buy for whom' content get consumed early, while the buyer is still forming a list. By the time your discount lands, they have already chosen the brand.\n\nRun the consideration content first.",
     "When does your Diwali content start?"),

    ("dhanteras", "data", "Dhanteras is the highest-intent day of the year",
     "People are actively looking for a reason to buy something.",
     "Most marketing fights disinterest. Dhanteras is one of the rare days where buying is the point and the customer arrives already convinced.\n\nThat makes creator content unusually efficient: it does not need to create desire, only to be the thing someone finds while already shopping.\n\nPlan for presence, not persuasion.",
     "Do you run anything on Dhanteras?"),

    ("navratri", "seasonal", "Navratri is nine outfits, not one campaign",
     "The format is handed to you. Most brands still run a single post.",
     "Nine nights, nine looks, and an audience that genuinely wants outfit ideas every single day.\n\nIt is the most natural series structure in the Indian calendar, and it rewards brands that commit to the whole run rather than posting once and hoping.\n\nBook one creator for nine days, not nine creators for one.",
     "Would you commit to a nine-day series?"),

    ("karva_chauth", "money", "Karva Chauth is a beauty peak brands underuse",
     "High intent, concentrated in about ten days, and relatively uncontested.",
     "Diwali gets the budget and the attention. Karva Chauth gets the actual beauty purchase — makeup, mehendi, jewellery, salon appointments — from a buyer with a fixed date and no option to postpone.\n\nLess competition for creator slots, sharper intent. It is one of the better ratios in the year.",
     "Have you ever run a Karva Chauth campaign?"),

    ("wedding", "seasonal", "Wedding season is not one campaign either",
     "Sangeet, mehendi, the wedding, the reception. Four different buyers.",
     "Brands write one 'wedding season' brief and wonder why it feels generic.\n\nEach function is a distinct outfit, a distinct look and a distinct budget, and the guest is buying differently from the bride. Splitting the brief by occasion makes the content immediately more useful.\n\nOne brief per function beats one for the season.",
     "Which function does your product belong to?"),

    ("holi", "category", "Holi content is about protection, not colour",
     "The search is 'how do I not wreck my skin and hair'.",
     "Every brand posts colour. Almost nobody answers the actual worry.\n\nPre-Holi oiling, barrier creams, what actually removes the colour afterwards — that is the content people look for, and it positions your product as the sensible choice rather than the festive one.\n\nSolve the fear, not the aesthetic.",
     "What does your product do for Holi?"),

    ("rakhi", "format", "Rakhi is a gifting brief, not a product brief",
     "The buyer is not the user. Brief for the person choosing.",
     "Your customer at Rakhi is a sibling with a budget and no idea what to pick.\n\nContent that helps them decide — by price band, by personality, by delivery date — converts far better than content aimed at whoever ends up using the product.\n\nBrief the chooser.",
     "Who actually buys your product at Rakhi?"),

    ("valentines", "mistake", "Valentine's is not only couples",
     "The self-gifting market is larger and far less contested.",
     "Every brand in beauty runs the same couple campaign, competing for the same fortnight.\n\nMeanwhile a large share of February beauty spend is people buying for themselves, and almost nobody speaks to them. It is the same budget with a fraction of the noise.\n\nRun one campaign to the other half.",
     "Couples or self-gifting — which do you target?"),

    ("monsoon", "category", "Monsoon is a product-problem season",
     "Frizz, humidity, breakouts, things that will not dry.",
     "Monsoon has no gifting moment, so brands ignore it — and miss a season where the customer has a live, specific complaint.\n\nContent that names the problem gets saved, because the problem lasts three months. Fewer competitors, longer content shelf life.",
     "Does your product solve a monsoon problem?"),

    ("christmas", "seasonal", "December is two audiences, two weeks apart",
     "Gifting until the 24th. Party looks from the 26th.",
     "Brands run one December campaign across both and dilute each.\n\nThe gifting buyer wants to know what to purchase for someone else. The party buyer wants to know what to wear on the 31st. Same month, completely different intent.\n\nSplit the month in two.",
     "How do you split December?"),

    ("newyear", "process", "Book January in November",
     "Resolution season is the one time people want to be sold to.",
     "January is the strongest month in beauty and fitness because the customer arrives already looking for change.\n\nBut creators fill up over the festive run, so a January campaign booked in January gets leftovers. Booked in November, it gets the roster.\n\nPlan the new year before the old one ends.",
     "Do you plan a January push?"),

    ("akshaya", "category", "Akshaya Tritiya is a high-ticket day",
     "Buying is considered auspicious, so the objection is already answered.",
     "For jewellery and premium goods this is a rare day where price resistance drops on its own.\n\nCreator content works best here as reassurance rather than persuasion: craftsmanship, authenticity, what to look for. The decision to buy is made; the decision of where is not.",
     "Is this a day that moves your category?"),

    ("ganesh", "seasonal", "Ganesh Chaturthi is a regional goldmine",
     "Enormous in Maharashtra, and priced like a normal week elsewhere.",
     "National brands plan around national festivals and miss a ten-day window where one state is entirely focused on one thing.\n\nRegional creators for a regional festival cost a fraction of peak-season national rates, with far better resonance in the market that matters.\n\nGo regional for regional moments.",
     "Do you run region-specific campaigns?"),
]

# --------------------------------------------------------------- CREATOR
FESTIVAL_CREATOR = [
    ("diwali", "rates", "Charge festive rates. Every other industry does",
     "Photographers, caterers and venues all price the season. So should you.",
     "Your October slots are genuinely scarce, and scarcity has a price.\n\nRaising rates for the festive window is not opportunism — it is the same logic every seasonal business runs on. Brands have peak budgets precisely because they expect peak pricing.\n\nDecide your festive rate in August and hold it.",
     "Do you charge more during festive season?"),

    ("diwali", "money", "Your Diwali calendar fills in August",
     "Say yes to the right brands before you are out of slots.",
     "The first offers to arrive are rarely the best ones, but if you accept them all you have nothing left when the good brands come asking in September.\n\nDecide how many festive collabs you will take, and hold two slots back. The late offers are usually the highest paid.",
     "How many festive slots do you take?"),

    ("diwali", "growth", "Festive content gets found for years",
     "A Diwali look from this year resurfaces every year after.",
     "Most content has a two-week life. Seasonal content is different: it gets searched again next October, and the one after.\n\nThat makes festive posts worth more production effort than a normal week, because you are building an asset rather than filling a slot.\n\nMake the festive ones properly.",
     "Does your old festive content still get views?"),

    ("navratri", "growth", "Nine days is nine pieces of content",
     "The most reliable series format in the Indian calendar.",
     "Audiences actively want an outfit idea each day, which means the hardest part of content — the reason to watch — is already solved.\n\nIt is also the easiest series to pitch to a brand, because nine posts is a package rather than a favour.\n\nPlan the nine before the first.",
     "Are you doing a Navratri series?"),

    ("karva_chauth", "pitch", "Pitch beauty brands for Karva Chauth in September",
     "Huge intent, a fixed date, and far less competition than Diwali.",
     "Every creator pitches Diwali and the inboxes are full. Karva Chauth sits two weeks either side with real budget and a fraction of the noise.\n\nMakeup that lasts a full day of fasting, mehendi, jewellery styling — brief, specific, and genuinely useful content.\n\nPitch it while others are still chasing Diwali.",
     "Have you pitched a Karva Chauth collab?"),

    ("wedding", "money", "Wedding season is where creator rates peak",
     "Bridal-adjacent content commands more than anything else you make.",
     "The buyer has a fixed date, a large budget and no option to delay — which is exactly the combination that supports premium pricing.\n\nIf your content touches bridal beauty, outfits or guest styling, your November rate should not look like your June rate.\n\nPrice the season, not the post.",
     "Do you have a wedding-season rate?"),

    ("holi", "production", "Shoot Holi content before Holi",
     "On the day you will be covered in colour and your phone will not survive.",
     "Every year creators plan to capture it live and come back with nothing usable.\n\nShoot the prep, the outfit and the product the week before, when you control the light and your hands are clean. Keep the day itself for stories.\n\nPlan the shoot, not the day.",
     "Have you ever lost a shoot to the actual festival?"),

    ("rakhi", "pitch", "Rakhi brands brief in July",
     "Pitch in June or you are pitching after the budget is spent.",
     "Gifting campaigns are planned a clear month ahead because the product has to ship before the date.\n\nA creator who pitches in July is competing for whatever is left. One who pitches in June is in the plan from the start.\n\nWork a month ahead of every festival.",
     "How far ahead do you pitch?"),

    ("valentines", "confidence", "You do not need a partner for Valentine's content",
     "The self-care angle outperforms couple content for most creators.",
     "Single creators skip February assuming the season is not theirs, and lose a strong brand month.\n\nSelf-gifting, getting-ready content and the anti-Valentine's angle all attract the same brands, often with less competition than the couple bracket.\n\nThe season is yours too.",
     "Do you make Valentine's content?"),

    ("monsoon", "growth", "Monsoon is the best time to build your archive",
     "Nobody is outside, everyone is scrolling, and the problems are specific.",
     "Brands spend less in monsoon, so competition for attention drops while audience time goes up.\n\nIt is the ideal window to make the evergreen content you never have time for during festive season — the routines, the explainers, the pieces that keep earning.\n\nBuild in the quiet months.",
     "What do you make during monsoon?"),

    ("newyear", "rates", "Raise your rate on 1 January",
     "A clean date makes the conversation easy for everyone.",
     "A rate rise mid-year invites a discussion. A rate rise at the start of the year is simply how business works, and brands accept it without friction.\n\nDecide the new number in December, put it in your rate card, and quote it from the first enquiry.",
     "What is your 2027 rate going to be?"),

    ("christmas", "community", "December brands decide in October",
     "By the time the lights go up, the campaign is already cast.",
     "Creators pitch December content in December and cannot understand the silence.\n\nEnd-of-year campaigns are signed off in the previous quarter, alongside the annual budget. Pitching in October puts you in the planning conversation rather than the leftovers.",
     "When do you pitch December work?"),

    ("ganesh", "community", "Regional festivals are your advantage",
     "National creators cannot speak to a local moment credibly.",
     "If you live in the region a festival belongs to, you have something no larger creator can buy: genuine familiarity with how it is actually celebrated.\n\nBrands running regional campaigns pay well for exactly that, and the competition is a fraction of the national pool.\n\nOwn your city's moments.",
     "Which local festival could you own?"),

    ("onam", "pitch", "Regional festivals need regional pitches",
     "A Kerala brand does not want a generic festive deck.",
     "The pitch that works names the festival, the specific tradition and what your audience in that market responds to.\n\nIt takes ten extra minutes and immediately separates you from every creator sending the same seasonal template to everyone.\n\nSpecific beats polished.",
     "Do you tailor pitches by region?"),

    ("akshaya", "negotiation", "High-ticket collabs deserve different terms",
     "Jewellery campaigns often want exclusivity. Price it.",
     "Premium categories frequently ask for category exclusivity around an auspicious date, which means turning down every competitor in the window.\n\nThat is real lost income and should be a separate line in your quote, not a favour folded into the fee.\n\nCharge for what you are giving up.",
     "Have you been asked for exclusivity?"),
]
