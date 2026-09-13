"""CollabHive — brand-page post bank (@collabhive.in).

Audience: founders and marketing leads at Indian D2C beauty & fashion brands.
Every entry is distinct copy — no templating, no reworded duplicates.

    (pillar, headline, sub, caption, cta)
"""

BRAND_POSTS = [
    ("myth", "Follower count is a vanity metric",
     "A 12k creator with a real community outsells a 200k creator with a passive one.",
     "Brands still buy reach. Reach doesn't buy anything back.\n\nThe creator with 12k followers whose comments are full of real questions will move more product than the 200k account where every comment is a fire emoji.\n\nBefore you book anyone, read their last 20 comment sections.",
     "What's the smallest creator who ever outperformed for you?"),

    ("data", "Most collabs fail before the brief is sent",
     "Not because of the creator. Because nobody agreed what success looked like.",
     "A campaign with no defined outcome can't succeed — it can only 'feel okay'.\n\nDecide upfront: are you buying awareness, content you'll reuse in ads, or direct sales? Each needs a different creator, format and measure.\n\nPick one. Write it down. Then brief.",
     "Which of those three are you actually buying?"),

    ("tip", "Your brief is too long",
     "Three lines of intent beat three pages of rules.",
     "The longest briefs produce the most generic content.\n\nWhen you script every second you get an ad. Give a creator the product, the audience and one non-negotiable, and you get something their followers actually stop for.\n\nConstrain the message. Free the delivery.",
     "How long is your current brief, honestly?"),

    ("mistake", "You're briefing creators like employees",
     "They know their audience better than your deck does.",
     "The fastest way to kill a collab is to hand a creator a shot list.\n\nYou hired them for a voice that took years to build, then asked them to read your copy. Their audience notices instantly — and engagement tells you so.\n\nBring the what. Let them own the how.",
     "Ever had a creator push back on a brief and be right?"),

    ("process", "What a good campaign actually looks like",
     "Brief. Shortlist. Approve. Ship.",
     "Most brands overcomplicate this.\n\nYou define the goal and budget. You get a shortlist of creators who fit. You approve the ones you like. They ship.\n\nEverything else — the chasing, the rate haggling, the follow-ups — is admin somebody else should absorb.",
     "Where does your process get stuck?"),

    ("money", "Cheap creators are the most expensive",
     "Two reshoots and a missed deadline cost more than the rate ever saved.",
     "Rate is the smallest number in a collab.\n\nThe real cost is time: the re-briefs, the chasing, the content that arrives off-brand and unusable. A creator who delivers right the first time at twice the rate is cheaper by month end.\n\nBuy reliability, not the discount.",
     "What's your worst 'cheap turned expensive' story?"),

    ("format", "Stop asking for a grid post",
     "Reels get discovered. Grid posts get seen by people who already follow you.",
     "If your goal is new customers, a static post is the wrong ask.\n\nThe grid serves your existing audience. Reels serve the algorithm, which serves strangers — and strangers are who you're paying to reach.\n\nUnless you're buying credibility for your own page, ask for video.",
     "Reels or static — what's working for you right now?"),

    ("seasonal", "Festive campaigns start 8 weeks early",
     "Booking in October for Diwali means paying peak and picking leftovers.",
     "Every brand remembers festive at the same time, and the good creators fill up first.\n\nThe brands that win the season locked creators in while everyone else was still building the deck. They paid less and chose from everyone, not the remainder.\n\nStart now for the next one.",
     "What's the next season you're planning for?"),

    ("proof", "The content outlives the campaign",
     "One collab should give you months of ad creative, not a single post.",
     "Most brands treat creator content as a one-night placement. That leaves the real value on the table.\n\nNegotiate usage rights upfront and the same shoot becomes your paid social, your PDP imagery, your email header. The post is the smallest part of what you bought.\n\nAlways ask about usage.",
     "Are you reusing creator content or letting it expire?"),

    ("mistake", "You're measuring the wrong week",
     "Creator content compounds. Judging it at 48 hours tells you almost nothing.",
     "Reels surface for weeks. A post that looks flat on day two can quietly become your best performer by day twenty.\n\nIf you kill a partnership based on a 48-hour screenshot, you're deciding on a fraction of the data.\n\nGive it a fortnight before you judge.",
     "How long do you wait before calling a campaign?"),

    ("faq", "How many creators should one campaign use?",
     "Fewer creators, more posts each. Almost always.",
     "Brands instinctively spread budget across as many creators as possible. It feels like more reach.\n\nBut one creator posting three times builds familiarity — the audience sees the product repeatedly from someone they trust. Nine creators posting once each is nine ads nobody remembers.\n\nDepth beats spread.",
     "Do you go wide or deep with your budget?"),

    ("tip", "Send the product before the contract",
     "A creator who has actually used it makes content you couldn't script.",
     "The difference between a genuine recommendation and a read-out is whether they've lived with the product.\n\nShip it two weeks early. Let them try it, form an opinion, find the detail your marketing team never thought to mention.\n\nThat detail is usually the thing that sells.",
     "How far ahead do you ship product?"),

    ("money", "What a fair creator rate actually looks like",
     "If you're paying less than the content costs to make, it isn't a partnership.",
     "A reel is a shoot, an edit, a script and a posting slot on an audience they spent years building.\n\nWhen a rate doesn't cover the production, creators either cut corners or stop replying. Neither is a saving.\n\nPrice for the work, not for the follower count.",
     "What's your average rate per post right now?"),

    ("myth", "Bigger brands get better creator deals",
     "Smaller brands get better creator content. That matters more.",
     "Big budgets buy access. They don't buy enthusiasm.\n\nCreators make their best work for products they'd actually use, and small brands are far more likely to be that. The output gap usually favours the underdog.\n\nYour size isn't the disadvantage you think it is.",
     "Has a small budget ever produced your best content?"),

    ("mistake", "Approving content to death",
     "Four rounds of revisions and it no longer sounds like anyone.",
     "Every revision pulls the content closer to your brand deck and further from the creator's voice.\n\nBy round four you have something safe, polished and completely ignorable. The audience scrolls past it because it reads like an ad, because it now is one.\n\nOne round. Two at most.",
     "How many revision rounds do you allow?"),

    ("format", "The first three seconds decide everything",
     "If the hook fails, nothing after it matters.",
     "You can have a perfect product, a perfect creator and a perfect offer, and lose all of it in three seconds.\n\nWhen you review creator content, watch only the opening. If you'd keep scrolling, so will everyone else.\n\nBrief the hook. Let them handle the rest.",
     "What's the best hook you've seen this month?"),

    ("process", "Who actually owns the campaign internally?",
     "If the answer is 'marketing', nothing will move quickly.",
     "Creator campaigns die in approval chains. A creator asks one question and waits four days for an answer that needed one person.\n\nName a single decision-maker who can approve content and spend without a meeting. Speed is a real competitive advantage here.\n\nOne name. Not a team.",
     "Who signs off on creator content at your company?"),

    ("data", "Comments tell you more than likes",
     "Likes are a reflex. Comments are effort.",
     "Anyone can double-tap without reading. A comment means someone stopped, processed and chose to respond.\n\nWhen you're evaluating a creator, ignore the like count and read the comments. Are they real questions, or a wall of emojis from engagement pods?\n\nThat's your whole due diligence in five minutes.",
     "What's your quickest way to spot a fake audience?"),

    ("tip", "Give creators the objection, not the feature",
     "They already know how to sell. They just need to know what's blocking the sale.",
     "Most briefs list features. The useful brief lists what stops people buying.\n\nToo expensive? Unsure about the shade range? Worried it won't suit oily skin? Hand the creator the real objection and they'll answer it in their own words.\n\nThat's what converts.",
     "What's the #1 objection your product faces?"),

    ("seasonal", "Your slow month is the best time to test",
     "Everyone crowds the peak. Nobody competes in the trough.",
     "Creator rates soften off-season, audiences are less advertised-to, and you get to make your mistakes when the stakes are low.\n\nBrands that test in the quiet months walk into peak season knowing exactly which creator and format works.\n\nLearn cheap. Scale expensive.",
     "When's your quietest month?"),

    ("mistake", "You're only looking at Instagram",
     "Your customer is on YouTube Shorts too, and creators there are cheaper right now.",
     "Attention has spread across platforms faster than most brand budgets have.\n\nThe same creator often posts to Instagram, YouTube Shorts and sometimes a newsletter — and will bundle all three for barely more than the reel alone. Most brands never ask.\n\nAsk what else they've got.",
     "Which platform is underrated for your category?"),

    ("proof", "Ask for the analytics screenshot after, not before",
     "Pre-campaign numbers are marketing. Post-campaign numbers are truth.",
     "Any creator can send you a deck with their best month on it.\n\nWhat matters is the screenshot 7 days after your post went live: reach, saves, shares, profile visits. Build that into the agreement from the start and every campaign teaches you something.\n\nMake reporting part of the deal.",
     "Do you ask creators for post-campaign data?"),

    ("money", "Paying late costs you the good creators",
     "Word travels in creator communities faster than it does in yours.",
     "Creators talk to each other constantly. A brand that pays 60 days late becomes known as one within a week.\n\nThe creators you most want are the ones who can afford to say no to you. Slow payment is how you lose them permanently.\n\nPay on delivery. It's the cheapest reputation you'll ever buy.",
     "What are your current payment terms?"),

    ("myth", "You need a big campaign to start",
     "Two creators and one clear goal is a campaign.",
     "Brands postpone creator marketing waiting for a budget that justifies a 'proper' launch.\n\nMeanwhile a competitor is running two creators a month, learning what works, and compounding. In six months they have data and you still have a deck.\n\nStart small. Start now.",
     "What's stopping you from starting this month?"),

    ("tip", "Let creators keep the content on their page",
     "Deleting it after 30 days destroys most of what you paid for.",
     "Takedown clauses feel like control. They're actually value destruction.\n\nThat post keeps accumulating reach, keeps showing up in search, keeps being the thing a customer finds when they Google your brand at midnight. Removing it deletes an asset you already bought.\n\nLeave it up.",
     "Do your contracts have a takedown clause?"),

    ("format", "Carousels convert better than you'd think",
     "Reels get reach. Carousels get saves, and saves get remembered.",
     "Everyone chased Reels and quietly abandoned the format that people actually revisit.\n\nA good carousel gets saved, sent to a friend, and reopened a week later when someone's ready to buy. That's a longer sales window than any video.\n\nUse both. They do different jobs.",
     "Reels for reach, carousels for saves — agree?"),

    ("mistake", "Hiring creators who've never used your category",
     "Their audience can tell, and so can yours.",
     "A fashion creator doing skincare for one post is obvious to everyone watching.\n\nThe audience followed them for a specific reason. When a brand shows up outside that lane, it reads as paid — because it is, and only because it is.\n\nStay in their lane. It's why it works.",
     "Ever booked outside a creator's niche? How'd it go?"),

    ("process", "Write the caption brief too",
     "Most brands art-direct the video and forget the words underneath it.",
     "The caption is where the offer lives. It's where the discount code goes, where the objection gets answered, where the link gets mentioned.\n\nBrands obsess over the visual and leave the caption entirely to chance. Then wonder why nobody clicked.\n\nBrief both.",
     "Do you brief captions or just the visual?"),

    ("data", "Saves are the metric nobody reports",
     "A save means 'I intend to act on this later'.",
     "Likes are a reflex, comments are conversation, but a save is intent — the closest thing Instagram gives you to a purchase signal.\n\nIf your creator content is getting saved, it's working, regardless of what the like count says.\n\nAsk for saves in every report.",
     "What's your best-saved piece of content?"),

    ("money", "Commission-only deals rarely work",
     "The creators who'd accept them are the ones who can't fill their calendar.",
     "Affiliate-only sounds efficient: pay for results, risk nothing.\n\nBut established creators have paid work queued and no reason to gamble. You end up with whoever had a gap — which is exactly the selection problem you didn't want.\n\nPay a base. Add commission on top.",
     "Have you tried affiliate-only? Did it work?"),

    ("faq", "How long before creator marketing shows results?",
     "First signal in 2 weeks. Real pattern at 3 months.",
     "One campaign tells you almost nothing — it could be the creator, the format, the timing or luck.\n\nThree months of consistent collabs tells you which combination works for your product. Brands that quit at week three quit right before the data becomes useful.\n\nCommit to a quarter or don't start.",
     "How long have you been running creator campaigns?"),

    ("tip", "Repost creator content to your own grid",
     "It's the cheapest social proof you will ever produce.",
     "You paid for content made by someone your customers already trust. Then you let it live only on their page.\n\nWith permission, that content on your grid does something your own photography can't: it shows a real person choosing you.\n\nAsk for reposting rights in the brief.",
     "Is your grid mostly product shots or real people?"),

    ("myth", "Engagement rate is the only filter you need",
     "A 9% engagement rate on the wrong audience is still the wrong audience.",
     "Engagement rate became the single number brands screen on, which made it the single number creators optimise.\n\nA high rate means people react. It doesn't mean they're in your city, your age bracket, or able to afford your product.\n\nAsk for the audience breakdown instead.",
     "What do you screen creators on first?"),

    ("mistake", "Launching the product and the campaign together",
     "Creator content needs a head start to find its audience.",
     "Brands schedule creator posts for launch day, expecting a spike.\n\nBut reels take days to distribute. By the time the content finds people, the launch moment has passed and the urgency is gone.\n\nStart creator content a week early. Let the algorithm warm it up.",
     "When do you schedule creator posts relative to launch?"),

    ("process", "Keep a creator roster, not a contact list",
     "The second collab with someone is always better than the first.",
     "First campaigns are expensive in time: explaining the brand, the tone, the product, the do-nots.\n\nAll of that is already paid for the second time. Brands that rebook their best creators get better content for less effort every single round.\n\nBuild a bench, not a database.",
     "How many creators have you worked with twice?"),

    ("format", "Tutorials outperform testimonials",
     "Showing someone use it beats hearing someone praise it.",
     "'I love this product' is a claim. 'Here's how I use it every morning' is a demonstration.\n\nOne asks for belief. The other removes doubt by showing the thing working in a real routine with real hands.\n\nBrief the routine, not the review.",
     "Tutorial or testimonial — which converts for you?"),

    ("money", "Budget for the second campaign before the first",
     "One-off collabs almost never pay back.",
     "Creator marketing compounds. The first post introduces you, the second makes you familiar, the third makes you a brand they've 'heard of'.\n\nBrands that fund exactly one campaign are paying entirely for the introduction and none of the payoff.\n\nBudget in threes.",
     "Is your creator budget one-off or recurring?"),

    ("data", "Your best creator is probably already a customer",
     "Check your tagged photos before you check a database.",
     "Someone is already posting about your product for free, with genuine enthusiasm, to an audience that trusts them.\n\nThey're in your notifications right now. A brand that turns existing fans into paid creators skips the entire trust-building problem.\n\nGo look at your tags.",
     "Ever hired a creator who was already a customer?"),

    ("tip", "Give a discount code, not just a link",
     "A code is trackable, memorable and repeatable in the caption.",
     "Links die in bios and get lost in stories. A code survives the scroll.\n\nIt also tells you exactly which creator drove which sale — no attribution guesswork, no dashboard arguments. And people screenshot codes.\n\nOne unique code per creator, always.",
     "Do you give codes, links, or both?"),

    ("myth", "Creator marketing is only for awareness",
     "It's the only channel that does awareness and conversion in the same post.",
     "The framing that creators are 'top of funnel' comes from brands who never gave them a conversion job.\n\nA creator who demonstrates the product, answers the main objection and drops a code is running the entire funnel in 30 seconds.\n\nAsk for the sale. They're allowed to.",
     "Do you brief creators to actually ask for the sale?"),

    ("mistake", "Ignoring the creator's own analytics advice",
     "They post daily. You post quarterly. Who knows the platform better?",
     "Brands routinely override creators on posting time, format and hook — the three things creators have tested hundreds of times.\n\nIt's the most expensive kind of ego: paying an expert and then ignoring the expertise.\n\nAsk what they'd do. Usually, do that.",
     "When did a creator last change your mind?"),

    ("process", "Decide the KPI before the kickoff call",
     "Otherwise the campaign gets judged on whatever number looks best afterwards.",
     "Without a pre-agreed metric, every campaign is a success and none of them teach you anything.\n\nReach was great but sales were flat? Then it was an awareness play. Sales were good but reach was low? Then it was conversion. You can't lose, and you also can't learn.\n\nPick the number first.",
     "What's your primary creator KPI?"),

    ("seasonal", "Wedding season is not just for jewellery",
     "Skincare, fashion, fitness and travel all peak alongside it.",
     "Indian wedding season reshapes spending across categories far beyond the obvious ones.\n\nPeople buy skincare for the photos, outfits for the functions, gym memberships for the timeline. If your product touches how someone looks or feels, the season is yours too.\n\nPlan for it like jewellery brands do.",
     "Does wedding season move your numbers?"),

    ("format", "Ask for raw footage, not just the final cut",
     "The offcuts become your next month of ads.",
     "You paid for a shoot. You received one 30-second edit.\n\nThe raw files contain angles, takes and product shots you can cut into paid social for months. Most creators will share them if you ask in the brief — and almost nobody asks.\n\nPut it in the agreement.",
     "Do you ask for raw footage?"),

    ("money", "Gifting works, but only above a certain product value",
     "Nobody makes a reel for a ₹300 sample.",
     "Gifting is real currency when the product is genuinely desirable and expensive enough to matter.\n\nBelow that threshold you're asking for professional work in exchange for a free sample, and the creators who accept are the ones with nothing booked.\n\nBe honest about which side of the line you're on.",
     "Has gifting ever worked for your brand?"),

    ("data", "Watch time beats view count",
     "A thousand people who watched it all beats ten thousand who bounced.",
     "View counts are inflated by an algorithm that counts a fraction of a second.\n\nAverage watch time tells you whether the content actually held anyone. It's the number that predicts whether the platform will keep pushing it, and whether the message landed.\n\nAsk for it every time.",
     "Do you get watch time in your reports?"),

    ("tip", "Name the thing you don't want",
     "One clear 'never' is worth ten pages of guidelines.",
     "Creators can work with almost any constraint if they know it exists.\n\nDon't say the competitor's name, don't shoot in the bathroom, don't claim it cures anything. Three sentences. Then get out of the way.\n\nBoundaries free people. Instructions don't.",
     "What's your one non-negotiable?"),

    ("myth", "You have to be on every platform",
     "One platform done properly beats four done thinly.",
     "Spreading a small budget across Instagram, YouTube, LinkedIn and X gives you four channels with no momentum.\n\nPick the one where your customer already spends time and own it. You can expand once something is working — not before.\n\nDepth first. Always.",
     "Which single platform matters most for you?"),

    ("mistake", "Treating the creator as a media buy",
     "The relationship is the asset, not the post.",
     "Brands that transact get one campaign. Brands that build get an advocate who mentions them unprompted for years.\n\nThe difference costs almost nothing: reply to their messages, pay on time, send the product again, congratulate them when something goes well.\n\nIt's not a placement. It's a person.",
     "Who's your longest creator relationship?"),

    ("process", "Book the follow-up before the first post goes live",
     "Momentum is much cheaper than restarting.",
     "The gap between campaigns is where creator marketing loses its compounding.\n\nIf you wait for results before booking the next one, you introduce a month of silence — and pay full price to rebuild the attention you already had.\n\nSchedule the next one on day one.",
     "How big is the gap between your campaigns?"),

    ("proof", "Show the results to the creator",
     "They'll make better content next time, and they'll tell other creators about you.",
     "Creators almost never find out whether their work sold anything.\n\nSend them the numbers — the code redemptions, the traffic, the sales. They learn what works for your product, and you become the brand that treats them like a partner.\n\nBoth of those pay you back.",
     "Do you share results with your creators?"),

    ("faq", "Should we work with creators who post competitors?",
     "Usually yes — it means they're trusted enough to be booked.",
     "Brands panic when a creator has posted a competitor. But an audience that responds to your category is exactly the audience you want.\n\nThe only real question is timing. Ask for a reasonable gap, not lifetime exclusivity you don't want to pay for.\n\nOverlap is a signal, not a risk.",
     "Do you enforce category exclusivity?"),

    ("format", "Stories are underrated for conversion",
     "Less polish, more urgency, a swipe-up that actually gets used.",
     "Feed content builds the case. Stories close it.\n\nThe format is casual enough that a direct 'here's the link, it's 20% off today' doesn't feel like an ad. And it's the only place a creator can point straight at your site.\n\nAlways buy stories alongside the post.",
     "Do you include stories in your creator deals?"),

    ("money", "The cheapest campaign is the one you repeat",
     "Onboarding a new creator costs more than rebooking a good one.",
     "Every new creator means re-explaining the brand, re-negotiating terms, re-checking quality and re-doing paperwork.\n\nA creator who already knows your product ships better content in half the time. That saving never shows up in the rate card but it's real.\n\nRebook before you recruit.",
     "What's your rebooking rate?"),

    ("data", "Track the profile visits, not just the clicks",
     "People research before they buy, and that starts with your profile.",
     "Most customers don't click straight through from a creator post. They visit your profile, scroll, decide, and come back days later.\n\nIf you only count same-day link clicks, creator marketing will always look like it underperforms — because you're measuring the wrong step.\n\nWatch profile visits after every post.",
     "How do you attribute creator-driven sales?"),

    ("tip", "One creator, three posts, one month",
     "Repetition from a trusted voice is what actually changes behaviour.",
     "Nobody buys on first exposure. They buy when something has been in their feed enough times to feel normal.\n\nThree posts from one creator over a month does that. One post from three creators doesn't — it's three strangers, once each.\n\nBuy frequency, not variety.",
     "Do you buy single posts or packages?"),

    ("myth", "Creators are expensive",
     "Compared to what? Run the maths against your last ad spend.",
     "Brands quote creator rates like they're extravagant, then spend the same amount on paid ads in three days with nothing reusable at the end.\n\nA creator gives you content, distribution and credibility. Ads give you distribution and stop the moment you stop paying.\n\nCompare properly.",
     "What's your cost per acquisition on each channel?"),

    ("mistake", "No clear call to action",
     "The audience liked it, then didn't know what to do next.",
     "Beautiful content with no instruction converts nobody.\n\nTell them exactly what happens next: the code, the link, the offer, the deadline. Creators will say it naturally if you tell them what it is.\n\nAssume nothing is obvious. It isn't.",
     "What's your standard CTA?"),

    ("process", "Contract the deliverables, not the ideas",
     "Specify what you receive. Don't specify what they think.",
     "A good agreement covers count, format, timeline, usage and payment. That's it.\n\nThe moment it starts dictating creative direction it stops being a contract and starts being a leash — and leashed content performs like leashed content.\n\nBe precise about logistics, loose about creative.",
     "What's in your standard creator agreement?"),

    ("format", "Before-and-after still works",
     "It's the oldest format in beauty because it's the most honest one.",
     "Nothing outperforms visible change. Not testimonials, not unboxings, not aesthetic flat-lays.\n\nIf your product does something you can see, the whole brief is: show it before, show it after, be honest about how long it took.\n\nHonesty about the timeline is what makes it credible.",
     "Does your product have a visible before/after?"),

    ("money", "Negotiate the package, not the rate",
     "Asking a creator to drop their price damages the relationship. Asking for more deliverables doesn't.",
     "'Can you do it cheaper' says you think they're overpriced.\n\n'At that budget, could we include stories and raw footage' says you're trying to make it work. Same outcome on value, completely different starting point for a long relationship.\n\nAdd scope instead of cutting price.",
     "How do you approach rate conversations?"),

    ("seasonal", "January is the best month in beauty and fitness",
     "Resolutions are the one time people actively want to be sold to.",
     "For most of the year you're interrupting. In January you're assisting.\n\nPeople are searching for the exact transformation your product promises. Creator content in that window doesn't have to create desire — it only has to be the thing they find.\n\nBook December. Post January.",
     "Do you plan a January push?"),

    ("data", "Your worst performing post teaches you most",
     "Success has too many possible causes. Failure usually has one.",
     "When something works, you can't tell whether it was the creator, the hook, the timing or luck.\n\nWhen something flops, the reason is usually obvious in hindsight — wrong audience, weak hook, unclear offer. That's a lesson you can act on.\n\nReview the failures properly.",
     "What did your worst campaign teach you?"),

    ("tip", "Let them post it their way first",
     "Approve the concept, not the edit.",
     "Approval loops are where creator content goes to die.\n\nAgree the idea before they shoot, then trust the execution. You save a week of revisions and get something that still sounds like a human made it.\n\nFront-load the alignment. Back off the polish.",
     "Do you approve concepts or final cuts?"),

    ("myth", "Bigger campaigns are safer",
     "Big campaigns just mean you find out you were wrong more expensively.",
     "Every large launch is a bet placed before any evidence exists.\n\nThree small tests cost less than one big campaign and tell you which creator, format and hook actually works. Then you scale the winner.\n\nSmall isn't cautious. It's informed.",
     "Do you test before you scale?"),

    ("mistake", "Waiting for the perfect creator",
     "The good-enough creator you book this week beats the perfect one you book in March.",
     "Brands spend months searching for an ideal fit that may not exist.\n\nMeanwhile they learn nothing, build no content library, and enter the busy season with no experience. The perfect creator is usually found by working with several decent ones.\n\nStart. Refine later.",
     "How long is your creator search taking?"),

    ("process", "Have a one-page brand sheet ready",
     "Creators ask the same six questions. Answer them once.",
     "Tone, audience, key benefit, what to avoid, links, deadline.\n\nOne page, sent with every brief, saves a week of back-and-forth per campaign and makes you dramatically easier to work with than the brands competing for the same creator.\n\nBeing easy to work with is a real advantage.",
     "Do you have a brand sheet?"),

    ("format", "Ask for a hook variant",
     "Same video, two openings. Run both. Keep the winner.",
     "The hook is the highest-leverage three seconds in the whole campaign, and it costs a creator almost nothing to record twice.\n\nYou get a built-in A/B test, and a second version to use in paid ads when the first fatigues.\n\nRequest it in every brief.",
     "Do you test hooks?"),

    ("money", "Pay for exclusivity or don't ask for it",
     "Blocking a creator from your whole category removes most of their income.",
     "Exclusivity is a real cost to a creator — you're asking them to turn down work for months.\n\nBrands request it casually and then are surprised by the quote. The quote is correct. If it isn't worth paying for, it wasn't worth asking for.\n\nPrice it or drop it.",
     "Do you ask for exclusivity?"),

    ("data", "Compare creators to each other, not to a benchmark",
     "Industry averages are built from businesses that aren't yours.",
     "Chasing a benchmark engagement rate you read in a report tells you nothing about your product, your price point or your market.\n\nWhat matters is which of your creators outperformed the others on the same brief. That's a controlled comparison. Everything else is noise.\n\nBuild your own baseline.",
     "What's your internal benchmark?"),

    ("tip", "Ask the creator what they'd buy",
     "They've seen a thousand brand briefs. They know which ones worked.",
     "Creators sit downstream of every marketing decision in your category and watch what their audience responds to.\n\nMost brands never ask. The ones that do get free strategic advice from someone with more relevant data than their agency.\n\nAsk before you brief.",
     "Have you ever asked a creator for strategy input?"),

    ("myth", "You need a big following to be worth partnering with",
     "Nano creators convert at rates that embarrass celebrity accounts.",
     "Under 10k followers usually means the audience is friends, family and genuine interest — the highest-trust audience that exists.\n\nThey cost a fraction, reply quickly, and their recommendation carries the weight of a personal one.\n\nDon't skip the small accounts.",
     "What's the smallest creator you've worked with?"),

    ("mistake", "Only measuring the campaign window",
     "Creator content keeps selling long after the invoice is paid.",
     "A reel from March is still being found in August. Someone searches your category, lands on that video, buys.\n\nIf your reporting closes two weeks after the campaign, all of that is invisible — and creator marketing looks worse than it is.\n\nCheck back at 90 days.",
     "Do you re-measure old campaigns?"),

    ("process", "Keep every creator's content in one place",
     "Most brands lose the files within six months.",
     "You paid for it. Then it lived in a WeTransfer link that expired, a WhatsApp thread, and someone's laptop who left the company.\n\nOne shared drive, one folder per creator, downloaded on delivery. That library becomes the most valuable marketing asset you own.\n\nSet it up before the next campaign.",
     "Where does your creator content live?"),

    ("format", "Try a 'day in the life' placement",
     "Your product shows up inside a real routine instead of being the subject.",
     "Dedicated product videos announce themselves as ads within a second.\n\nWhen your product appears naturally inside content someone would have watched anyway, it bypasses the ad filter entirely. Lower production, higher trust.\n\nAsk for integration, not a feature.",
     "Dedicated post or integration — which works better for you?"),

    ("money", "Set the budget per quarter, not per campaign",
     "Campaign-by-campaign budgeting guarantees you'll stop right before it works.",
     "When each campaign has to justify itself individually, the first flat result kills the channel.\n\nA quarterly budget lets you run enough volume to find the pattern. That's the only way creator marketing ever makes sense financially.\n\nFund the quarter.",
     "How do you budget for creators?"),

    ("data", "Ask which of their posts flopped",
     "How a creator talks about failure tells you how they'll handle yours.",
     "Every creator has content that underperformed. The good ones know exactly why and have adjusted.\n\nThe ones who claim everything works are either new or not paying attention — and neither is who you want running your campaign.\n\nIt's the best interview question there is.",
     "What's your best creator-vetting question?"),

    ("tip", "Send a deadline, not a date range",
     "'Sometime next month' produces content sometime after next month.",
     "Creators juggle many brands and prioritise the ones with clear dates.\n\nA specific deadline isn't pressure, it's clarity — and it moves you up the queue ahead of every brand that was vague.\n\nOne date. In writing.",
     "How specific are your deadlines?"),

    ("myth", "Good content needs a big production budget",
     "The best-performing creator content usually looks like it cost nothing.",
     "Polished, lit, colour-graded content reads as advertising, and audiences skip advertising.\n\nA phone, a window and someone genuinely enthusiastic outperforms a studio shoot in almost every category. That's not a compromise — it's the point.\n\nStop over-producing.",
     "Has a low-budget post ever beaten a polished one?"),

    ("mistake", "Changing the brief after they've shot it",
     "You're not asking for an edit. You're asking for a reshoot.",
     "Brands add a requirement after filming and treat it as a minor tweak.\n\nIt isn't. It's a new shoot day, unpaid. Do it twice and that creator quietly stops replying to your emails.\n\nLock the brief before the camera comes out.",
     "Ever had to ask for a reshoot?"),

    ("process", "Give creators a single point of contact",
     "Three people emailing them is how deadlines get missed.",
     "When a creator gets conflicting feedback from marketing, brand and the founder, everything stops until it's resolved.\n\nOne person owns the relationship and filters everything internally. Faster for them, and far more professional from the outside.\n\nOne inbox. One voice.",
     "Who's the point of contact at your company?"),

    ("format", "Ask for a comment-section plan",
     "The comments are a second ad slot, and they're free.",
     "When a creator posts, dozens of people ask the same questions: where to buy, does it work on X, what's the price.\n\nIf the creator knows the answers in advance, every reply becomes a conversion. If they don't, the questions go unanswered.\n\nBrief the FAQs, not just the video.",
     "Do you prep creators for comments?"),

    ("money", "Don't pay everything upfront either",
     "Half on booking, half on delivery protects both sides.",
     "Full payment upfront removes the creator's urgency. Full payment after gives them no security.\n\nSplitting it is the standard across every freelance industry for a reason — both parties have something at stake until the work lands.\n\nHalf and half. Every time.",
     "What are your payment splits?"),

    ("data", "Look at follower growth, not follower count",
     "A growing 20k account is worth more than a stagnant 80k one.",
     "Growth means the algorithm is currently favouring them and new people are discovering their content every week.\n\nA large but flat account is often a historical audience that has stopped paying attention. The follower number hides that completely.\n\nAsk for the 90-day growth chart.",
     "Do you check growth trends before booking?"),

    ("tip", "Reply to every comment on the reposted version",
     "You bought the attention. Don't ignore it when it arrives.",
     "Brands repost creator content then leave the comments unanswered for a week.\n\nEvery unanswered question is a customer who was interested enough to type. Answering within the hour while the post is live is the highest-converting work anyone on your team does that day.\n\nStaff the comments.",
     "Who handles your comments?"),

    ("myth", "One viral post will fix everything",
     "Virality is a lottery. Consistency is a strategy.",
     "Brands chase the breakout moment and treat steady performance as failure.\n\nBut a viral post brings a flood of people who've never heard of you and mostly never return. Twelve consistent posts build an audience that actually knows who you are.\n\nBuild the floor, not the spike.",
     "Have you had a viral post? Did it convert?"),

    ("mistake", "Ghosting creators you didn't select",
     "They talk to each other, and they remember.",
     "Brands reach out, receive rates, then disappear.\n\nIt costs one line to say 'not this time, let's revisit next quarter' — and it keeps the door open with someone you may want later. Silence closes it permanently.\n\nAlways reply. Even to a no.",
     "Do you reply to creators you pass on?"),

    ("process", "Debrief every campaign in 15 minutes",
     "What worked, what didn't, what we'd change. Written down.",
     "Most brands finish a campaign and move straight to the next without recording anything.\n\nSix months later they repeat the same mistake because the person who learned it has left or forgotten. Fifteen minutes and a shared doc prevents that entirely.\n\nWrite it down every time.",
     "Do you debrief your campaigns?"),

    ("format", "Test one creator across two formats",
     "Same voice, same audience — now you know it's the format.",
     "Comparing a reel from one creator to a carousel from another tells you nothing; too many variables.\n\nHold the creator constant and change only the format. Suddenly the result is interpretable, and you know what to buy next time.\n\nControl your variables.",
     "Have you ever tested format properly?"),

    ("money", "Build a rate card for yourself",
     "Know what you'll pay at each follower tier before you start negotiating.",
     "Brands negotiate from scratch every time, which is slow and inconsistent — and creators compare notes.\n\nDecide your ranges in advance. It speeds up every conversation and stops you overpaying for one creator and underpaying another with the same reach.\n\nDecide before you're asked.",
     "Do you have internal rate bands?"),

    ("data", "The right metric depends on the price point",
     "High-ticket products should not be judged on same-week sales.",
     "Something costing ₹5,000 involves research, comparison and often a conversation with a partner.\n\nExpecting that to convert in the 48 hours after a reel is a measurement error, not a campaign failure. Match the window to the decision length.\n\nLong consideration needs long measurement.",
     "How long is your average purchase decision?"),

    ("tip", "Ask for the link in their bio for 48 hours",
     "It's usually free and it's where the serious buyers go.",
     "People who want to buy don't click a story — they open the profile and look for the link.\n\nMost creators will keep it up for a day or two at no extra cost if you simply ask in the brief. Almost no brand asks.\n\nPut it in the deliverables list.",
     "Do you request bio-link placement?"),

    ("myth", "Creator marketing can't be measured",
     "It can. It just can't be measured the way you measure ads.",
     "Last-click attribution was built for search, where intent already exists. Creator content creates intent, which last-click will never capture.\n\nUse codes, post-purchase surveys and profile-visit lifts instead. The data is there — the default dashboard just isn't looking for it.\n\nChange the instrument.",
     "How do you currently measure creator impact?"),

    ("mistake", "Booking only creators who look like your customer",
     "Aspirational and relatable both sell. They just sell differently.",
     "Brands over-index on demographic matching and miss the creators their customers actually aspire to be.\n\nBoth work. One says 'this is for someone like you', the other says 'this is who you could be'. Most categories need a mix.\n\nDon't cast only one type.",
     "Aspirational or relatable — which works for you?"),

    ("process", "Start the next brief the day content lands",
     "Everything you learned is fresh and nobody has moved on yet.",
     "A week later the details blur, the team is on something else, and the next brief gets written from memory.\n\nWriting it while the campaign is live means the next one inherits every insight instead of starting from zero.\n\nSame day. Always.",
     "When do you write your next brief?"),

    ("faq", "Can we use creator content in paid ads?",
     "Only if you agreed it in writing beforehand. Otherwise, no.",
     "Organic posting rights and paid usage rights are different things, and creators price them differently for good reason — their face in your ad reaches people who never chose to follow them.\n\nAsk upfront, agree a term, pay for it. Retrofitting it later costs far more.\n\nGet it in the brief.",
     "Do you buy paid usage rights?"),

    ("tip", "Make the offer time-bound",
     "Without a deadline, 'I'll buy it later' means never.",
     "The content did its job — someone is interested. Then nothing forces a decision, so the moment passes and they forget.\n\nA code that expires on Sunday converts dramatically better than one with no end date. Same offer, different urgency.\n\nAlways add an expiry.",
     "Do your creator codes expire?"),

    ("seasonal", "Plan your quiet-season content in advance",
     "The best time to build a library is when you aren't launching anything.",
     "Content made under launch pressure is rushed content.\n\nUse the slow weeks to bank evergreen creator videos — the explainer, the routine, the objection-handler. Then launch season becomes distribution instead of production.\n\nShoot when calm. Post when busy.",
     "Do you bank content ahead of launches?"),

    ("faq", "What if a creator's post underperforms?",
     "Nothing, if you agreed deliverables rather than results.",
     "Creators sell the work, not the algorithm — nobody can guarantee reach, and any creator who does is guessing.\n\nWhat you can expect is the content, on time, to brief. If reach is what you need guaranteed, that's what paid amplification is for.\n\nBuy the asset, then boost it.",
     "Do you boost creator posts with paid spend?"),

    ("proof", "Your first campaign is research, not revenue",
     "Judge it on what you learned, not what it earned.",
     "Brands write off creator marketing after one flat campaign — the one that was always going to be a learning exercise.\n\nThe first run tells you which creator type, format and hook to bet on. That knowledge is what the money bought.\n\nBudget it as research and you'll actually continue.",
     "What did your first creator campaign teach you?"),
]
