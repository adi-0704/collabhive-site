"""CollabHive — creator-page post bank (@collabvibe.in).

Audience: Indian beauty / fashion / lifestyle creators, roughly 5k-200k.
Every entry is distinct copy — no templating, no reworded duplicates.

    (pillar, headline, sub, caption, cta)
"""

CREATOR_POSTS = [
    ("rates", "You're undercharging. Here's the test",
     "If every brand says yes immediately, your rate is too low.",
     "A healthy rate gets pushback sometimes. If nobody has ever hesitated, you've priced below what the market would have paid.\n\nRaise it 20% on the next enquiry. The brands worth working with will still say yes — and you'll stop resenting the ones who don't.",
     "When did you last raise your rate?"),

    ("redflag", "'We'll pay you in exposure'",
     "Exposure doesn't pay rent, and brands with budgets never open with this.",
     "A brand that can afford product can afford people.\n\n'Great visibility', 'long-term potential', 'we'll feature you' — that's what companies say when they have a marketing budget but haven't allocated any of it to you.\n\nPolitely ask for their rate card. Watch what happens.",
     "What's the worst pitch you've received?"),

    ("pitch", "Your pitch email is about you",
     "Brands don't care about your follower count. They care what it does for them.",
     "Rewrite the opener. Instead of 'I have 40k followers and great engagement', try 'your new launch is aimed at students in Delhi — that's 60% of my audience'.\n\nOne is a statistic. The other is a reason to reply.",
     "Want a second pair of eyes on your pitch?"),

    ("mediakit", "A media kit doesn't need to be pretty",
     "It needs four numbers and one screenshot.",
     "Creators spend a weekend in Canva and miss the point.\n\nBrands want audience size, top city, gender split and average reel views — plus one screenshot of your insights so they know you're not making it up.\n\nOne page. Send it as a PDF. Done.",
     "Got a media kit yet, or still winging it?"),

    ("money", "Always ask for 50% upfront",
     "Not rude. Standard. Every other freelance industry does it.",
     "You wouldn't ask a photographer to shoot a whole campaign and invoice later, hopefully.\n\nHalf before you shoot, half on delivery. Brands that work with creators properly won't blink. The ones that argue are telling you something useful about the rest of the project.",
     "Do you take a deposit?"),

    ("growth", "Posting more won't fix it",
     "One post people send to a friend beats five nobody saves.",
     "The algorithm rewards sends and saves far above likes, because those are the only signals that can't be faked by habit.\n\nSo stop asking 'what can I post today' and start asking 'what would make someone send this to a friend'. Different question. Different account.",
     "What's your most-shared post ever?"),

    ("negotiation", "The rate isn't the only thing to negotiate",
     "Usage rights and exclusivity cost you more than the fee gains you.",
     "A brand asking for 6 months of paid usage and category exclusivity is asking for far more than one post.\n\nThat's your face in their ads and a ban on working with competitors. Price it, or cap it at 30 days and non-exclusive.\n\nThe fee is the easy part.",
     "Ever agreed to exclusivity without charging for it?"),

    ("mistake", "Your insights screenshot is hurting you",
     "Sending a good week instead of a normal month reads as a red flag.",
     "Brands book a lot of creators. They know what a cherry-picked screenshot looks like.\n\nSending your 30-day average, including the quiet weeks, builds more trust than your single viral reel — because it tells them what to actually expect.\n\nHonest numbers get repeat work.",
     "Do you send averages or highlights?"),

    ("confidence", "Small accounts get paid too",
     "Brands are actively looking for 5-15k creators. That's not a consolation prize.",
     "Micro creators convert better and cost less, so the smartest brands built their whole strategy around them.\n\nIf you've been waiting to hit some number before you pitch, you've been leaving paid work on the table the entire time.\n\nYou're already big enough.",
     "How many followers did you have at your first paid collab?"),

    ("community", "The collab you didn't get wasn't personal",
     "Most 'no's are budget timing, not you.",
     "Brands plan quarterly. You pitched in week 11.\n\nThe number of times a creator is turned down because the money is already committed dwarfs the number of times it's about their content. Keep the email. Follow up next quarter.",
     "Ever landed a brand on the second try?"),

    ("rates", "Charge for the shoot day, not the post",
     "The video is 30 seconds. The work is six hours.",
     "Creators price the output and forget the input: scripting, setup, filming, retakes, editing, captions, posting, replying to comments.\n\nWhen you price by the hour it actually took, your rate stops feeling greedy and starts feeling obvious.\n\nCount the hours once. You'll never underquote again.",
     "How long does one reel actually take you?"),

    ("redflag", "'Just send us the content first'",
     "No professional industry asks for the work before the contract.",
     "This is the oldest one in the book. They see the content, go quiet, and you have no recourse.\n\nA real brand sends a brief, a rate and terms before you touch a camera. If they won't put it in writing, there's a reason.\n\nContract first. Always.",
     "Has a brand ever ghosted you after delivery?"),

    ("pitch", "Follow up. Twice",
     "Most collabs happen on the second or third email, not the first.",
     "Brand inboxes are chaos. Your pitch arrived during a launch and got buried — that's usually the whole story.\n\nOne follow-up after a week, one more after two. Polite, short, no guilt. That alone puts you ahead of the creators who sent one email and gave up.",
     "How many times do you follow up?"),

    ("growth", "Your bio is doing nothing",
     "Someone landed on your profile. You have one line to tell them why to stay.",
     "'Delhi | foodie | dm for collabs' tells a visitor nothing and a brand less.\n\nSay what you make and who it's for: 'Delhi restaurant reviews for people who hate overpriced brunch'. Specific beats aesthetic every time.\n\nRewrite it today. It takes four minutes.",
     "What does your bio say right now?"),

    ("money", "Send an invoice, not a message",
     "'Can you pay me' gets forgotten. An invoice gets processed.",
     "Brands pay through finance systems, and those systems need a document with a number on it.\n\nAn invoice with your details, the deliverables and a due date moves into a queue automatically. A WhatsApp reminder moves nowhere.\n\nMake one template. Reuse it forever.",
     "Do you invoice properly?"),

    ("negotiation", "Ask what the budget is first",
     "Naming your number first means you can only lose from there.",
     "'What's the budget for this?' is a completely normal question and most brands will answer it.\n\nIf they insist you go first, give a range with your real number at the bottom. Never open below what you'd accept.\n\nWhoever names a number first is negotiating against themselves.",
     "Do you ask budget first or quote first?"),

    ("mistake", "Saying yes to everything",
     "Your feed becomes a catalogue and your audience stops trusting you.",
     "The reason brands pay you is that your recommendation means something.\n\nEvery product you promote that you wouldn't actually use spends a little of that trust. Spend enough and there's nothing left to sell.\n\nSaying no is how you stay worth paying.",
     "What was the last collab you turned down?"),

    ("confidence", "You don't need a niche to start",
     "You need a niche to scale. Those are different problems.",
     "Creators freeze for months trying to pick the perfect lane before posting anything.\n\nPost for three months, look at what performed, and the niche reveals itself from real data instead of a guess. That's a far better way to choose.\n\nStart broad. Narrow with evidence.",
     "Did you pick your niche or did it pick you?"),

    ("community", "Reply to every comment for the first hour",
     "It's the cheapest reach boost available to you.",
     "Early engagement tells the algorithm the post is worth pushing, and replies count.\n\nBlock the hour after you post. Answer everything, even the emojis. It compounds into distribution you'd otherwise pay for.\n\nThe first hour is the whole game.",
     "Do you stay online after posting?"),

    ("rates", "Different platforms, different prices",
     "A reel, a story and a YouTube Short are three products, not one.",
     "Brands often ask for 'the post' and quietly expect cross-posting everywhere.\n\nEach platform is separate work, separate audience and separate value. Price them individually and bundle at a discount if you want — but bundle deliberately.\n\nNever give a platform away for free.",
     "Do you price per platform?"),

    ("redflag", "The brief keeps growing after you agreed",
     "One extra story. Then a second version. Then usage rights.",
     "Scope creep is how a fairly-paid collab becomes an underpaid one, one small request at a time.\n\nEach addition is reasonable in isolation. Together they double the work at the original price.\n\n'Happy to add that — here's the revised quote' ends it politely.",
     "Has a brief ever crept on you?"),

    ("pitch", "Pitch the campaign, not yourself",
     "Send them an idea they can picture, not a request for consideration.",
     "'I'd love to collaborate' asks them to do the thinking.\n\n'Here's a 3-part series showing your serum across a week of night routines' gives them something to say yes to. You've done the creative work they'd otherwise have to brief.\n\nArrive with the idea.",
     "Do you pitch ideas or availability?"),

    ("growth", "Your best post is a template",
     "You found something that works. Do it again.",
     "Creators treat a hit as lightning and move on to something completely different.\n\nBut the format worked for a reason. Change the topic, keep the structure, and you can run the same winning shape a dozen times before it fatigues.\n\nRepeat what works. That's not lazy, it's strategy.",
     "What format performs best for you?"),

    ("money", "Late payment needs a late fee",
     "Put it in the invoice from day one and it usually never gets used.",
     "A line saying '2% per week after 30 days' changes how quickly finance teams process you.\n\nYou'll rarely have to enforce it. Its whole job is to exist on the document and move you up the queue.\n\nAdd it to your template today.",
     "Do you charge for late payment?"),

    ("negotiation", "Get the deliverables in writing",
     "'A reel and a couple of stories' means something different to each of you.",
     "Vague scope is the root of nearly every creator-brand dispute.\n\nOne reel, three story frames, 30-day organic usage, delivered by the 14th. Specific enough that neither side can drift. It protects you and it makes you look professional.\n\nWrite it down before you shoot.",
     "Do you confirm scope in writing?"),

    ("mistake", "Deleting posts that underperform",
     "You're removing the data and the reach.",
     "A reel that flopped in 48 hours can still find its audience in week three — Instagram surfaces old content constantly.\n\nDeleting it kills that chance and erases what it could have taught you about what doesn't work.\n\nLeave it up. Learn from it.",
     "Do you delete underperforming posts?"),

    ("confidence", "Your rate is not an apology",
     "Send the number. Don't explain it, don't soften it, don't discount preemptively.",
     "Creators send rates wrapped in justification — 'I know it's a lot, but...' — which invites a negotiation nobody asked for.\n\nState the number and stop typing. Silence after a rate is normal. Filling it costs you money.\n\nSend it plainly. Then wait.",
     "Do you over-explain your pricing?"),

    ("community", "Collaborate with other creators first",
     "Brand deals follow visibility, and creators give it away free.",
     "A collab with another creator in your niche puts you in front of a warm, relevant audience at zero cost.\n\nDo four of those and your reach, your follower quality and your pitch all improve. Most creators skip this and go straight to begging brands.\n\nBuild sideways first.",
     "Who could you collab with this month?"),

    ("rates", "Raise your rate when you're busy, not when you're broke",
     "Scarcity is the only leverage that actually works.",
     "The moment to increase pricing is when you're turning work away, because you can afford to lose a few brands.\n\nRaising it during a quiet month feels desperate and you'll cave on the first pushback. Timing is most of negotiation.\n\nRaise from strength.",
     "When did you last feel too busy?"),

    ("redflag", "They want to see your 'engagement rate' and nothing else",
     "It usually means they're buying by spreadsheet, not by fit.",
     "Brands that screen on a single number tend to brief badly, revise endlessly and treat you as interchangeable.\n\nThe good ones ask about your audience, your content style and what you'd suggest. That question tells you what the whole project will be like.\n\nNotice how they open.",
     "What's your favourite question a brand has asked?"),

    ("pitch", "Send it to a person, not info@",
     "Find the marketing manager on LinkedIn. It takes four minutes.",
     "Generic inboxes are where pitches go to die — nobody owns them, so nobody answers.\n\nOne named person with a reason to care will reply far more often than a shared address ever will. This single change doubles most creators' response rate.\n\nDo the four minutes.",
     "Where do you send your pitches?"),

    ("growth", "Post at the time your audience is online",
     "Not the time a blog told you was best.",
     "Your insights show exactly when your followers are active, and it's rarely the generic '7pm' advice.\n\nMatch your posting to your own data and the first hour of engagement improves immediately — which is the window that decides distribution.\n\nCheck your insights. Use your numbers.",
     "What time do you post?"),

    ("money", "Track your income properly",
     "You can't raise rates if you don't know what you earned last quarter.",
     "A spreadsheet with brand, deliverables, rate and payment date takes minutes a month.\n\nIt tells you which brands pay well, which pay late, and whether you're actually growing. Without it you're guessing about your own business.\n\nStart the sheet this week.",
     "Do you track your collab income?"),

    ("negotiation", "Counter once, not three times",
     "One firm counter reads as confident. Three reads as desperate.",
     "When a brand lowballs, come back once with your number and a short reason.\n\nIf they decline, accept it gracefully and stay in touch. Creators who keep dropping their price teach every brand to open lower next time.\n\nOne counter. Then decide.",
     "How do you handle a lowball offer?"),

    ("mistake", "Only posting when you have something to sell",
     "Your audience notices when you only show up for money.",
     "If every third post is a collab and nothing in between, the account becomes an ad channel and engagement collapses.\n\nThe free content is what makes the paid content work. Protect the ratio or the thing brands are buying disappears.\n\nEarn the right to sell.",
     "What's your paid-to-organic ratio?"),

    ("confidence", "Nobody is thinking about your flop",
     "You remember it for months. They scrolled past in a second.",
     "Creators stop posting after a bad reel because they're convinced everyone noticed.\n\nThey didn't. The audience has no memory of it by the next morning, and the algorithm has already moved on. The only lasting damage is you not posting.\n\nPost the next one.",
     "What's a flop you're still thinking about?"),

    ("community", "Answer DMs from your audience",
     "That's where your most loyal followers live.",
     "A reply to a DM turns a follower into someone who advocates for you.\n\nThose are also the people who comment first, share your posts and tell brands about you in your own comments. Ignoring them is expensive.\n\nBlock 10 minutes a day for DMs.",
     "How often do you reply to DMs?"),

    ("rates", "Add a rush fee",
     "If they need it in 48 hours, that costs more than a normal turnaround.",
     "Urgency is a service. Rearranging your week is real disruption and other freelancers charge for it.\n\n25-50% on top for anything under a week is completely standard. Brands with a real deadline will pay it without blinking.\n\nPut it on your rate card.",
     "Do you charge for rush jobs?"),

    ("redflag", "The 'contract' is a WhatsApp message",
     "Not because it's invalid, but because it's vague.",
     "The problem isn't the medium, it's that a chat thread never contains scope, usage, timeline and payment terms in one place.\n\nAsk for a simple written agreement. Any brand that's done this before already has one ready.\n\nIf they don't, that's your answer.",
     "Do you always get it in writing?"),

    ("pitch", "Keep your pitch under 120 words",
     "Nobody reads the long one.",
     "Who you are, who your audience is, one specific idea, one link. That's the whole email.\n\nEverything else belongs in the media kit they'll open if the first four lines landed. Length signals that you don't know what matters.\n\nCut it in half, then cut again.",
     "How long is your current pitch?"),

    ("growth", "Steal structures, not content",
     "The format is public. The words should be yours.",
     "When something outside your niche performs well, look at its shape: the hook, the pacing, where the payoff lands.\n\nThat structure works regardless of topic. Apply it to what you know and it's original work built on a proven frame.\n\nStudy structure obsessively.",
     "What's a format you've borrowed recently?"),

    ("money", "Separate your money from day one",
     "One account for creator income makes tax season survivable.",
     "Mixing collab payments with personal spending means you genuinely don't know what you earned.\n\nA separate account, and a fixed percentage moved aside for tax, turns a yearly panic into a non-event.\n\nOpen it before the next payment lands.",
     "Do you keep creator income separate?"),

    ("negotiation", "Say no slowly",
     "'Let me check my calendar' buys you the time to think clearly.",
     "Creators accept bad terms because they answer instantly while flattered.\n\nA day's gap lets you read the scope properly, work out the real hours, and reply with a number you won't resent. Almost no offer expires overnight.\n\nNever answer the same hour.",
     "Have you ever regretted a fast yes?"),

    ("mistake", "Copying bigger creators exactly",
     "What works at 500k doesn't work at 5k.",
     "Large accounts can post vague lifestyle content because people already follow them for who they are.\n\nYou don't have that yet, so your content has to be useful, specific or entertaining on its own merit. That's a different job.\n\nBuild the way they built, not the way they post now.",
     "Who do you look up to, and what do they do differently?"),

    ("confidence", "Being niche is not being small",
     "'Delhi vegetarian street food' beats 'lifestyle' every single time.",
     "A narrow, clear identity makes you the obvious choice for every brand in that space.\n\nBroad accounts compete with everyone and get chosen by no one. Specificity is what makes a brand's decision easy.\n\nGo narrower than feels comfortable.",
     "How specific is your niche?"),

    ("community", "Tag brands you actually love, unpaid",
     "It's the warmest possible introduction, and it costs nothing.",
     "Brands watch their tags. A genuine, well-made post about a product you use puts you on their radar as someone who already gets it.\n\nPlenty of paid collabs start exactly here. Not as a tactic — just as a by-product of posting honestly.\n\nTag three this week.",
     "Ever got a paid deal from an unpaid post?"),

    ("rates", "Package deals beat single posts",
     "Three posts over a month is easier to sell and better for the brand.",
     "A single post rarely moves anything, and brands quietly know it.\n\nOffering a month-long package makes their campaign work better and gives you predictable income. It's an easier yes than a one-off at the same total value.\n\nLead with the package.",
     "Do you offer packages?"),

    ("redflag", "'This will be great for your portfolio'",
     "Your portfolio is already full. That's why they contacted you.",
     "This line is only ever used on people who are visibly capable — which is the argument against it.\n\nIf your work is good enough to want, it's good enough to pay for. Portfolio-building is what you did before you had an audience.\n\nYou're past that stage.",
     "What's the most creative excuse you've heard for not paying?"),

    ("pitch", "Reference something specific they did",
     "One line proving you actually looked changes the whole email.",
     "'I saw your Diwali campaign with the three-part reel series' takes thirty seconds and immediately separates you from every mass-sent pitch in that inbox.\n\nBrands can tell instantly. That line is why they keep reading.\n\nAlways do the thirty seconds.",
     "Do you personalise your pitches?"),

    ("growth", "Hooks are a skill, not a talent",
     "Write ten before you shoot. Use the tenth.",
     "The first hook you think of is the obvious one, which means everyone else thought of it too.\n\nBy the eighth or ninth you're into something specific and surprising. That's the one that stops the scroll.\n\nTen every time. It gets faster.",
     "What's your process for writing hooks?"),

    ("money", "Know your minimum before the call",
     "Decide the number you'd walk away from while you're calm.",
     "In a live conversation with a brand you like, it's very easy to talk yourself downward.\n\nA floor decided in advance is a decision made by the version of you that isn't excited or nervous. Trust her.\n\nWrite it down before you dial.",
     "What's your walk-away number?"),

    ("negotiation", "Trade, don't discount",
     "If you drop the price, remove something too.",
     "Cutting your rate while delivering the same scope teaches the brand your original price was fiction.\n\nLower the fee and reduce the deliverables, shorten the usage, or drop a platform. The value ratio holds and your pricing stays credible.\n\nEvery discount needs a trade.",
     "Do you trade scope when you discount?"),

    ("mistake", "Ignoring your analytics entirely",
     "You're making decisions on vibes when the data is two taps away.",
     "Reach, saves, shares, follows-per-post, top city, peak hours — all sitting in your insights, all free.\n\nCreators who check weekly make better content and pitch better, because they can describe their audience in specifics rather than adjectives.\n\nTwo taps. Once a week.",
     "How often do you check insights?"),

    ("confidence", "Turn down the brand that treats you badly",
     "One bad collab costs more than the fee is worth.",
     "Endless revisions, late payment, rude feedback — these projects eat weeks and drain the enthusiasm that makes your content good.\n\nThe fee never covers that. And the good brands you'd have had space for went elsewhere.\n\nProtect your calendar.",
     "Ever walked away mid-project?"),

    ("community", "Share what you earn with other creators",
     "Rate secrecy only ever helps the people paying you.",
     "Brands know the market rate. Creators, working alone, mostly don't — which is exactly why lowballing works.\n\nTalking openly about numbers with creators you trust is how everyone stops being underpaid. Nothing else has worked.\n\nStart the conversation.",
     "Do you talk rates with other creators?"),

    ("rates", "Charge more for exclusivity windows",
     "You're being asked to turn down competitors. That's income you're losing.",
     "Three months of category exclusivity could mean refusing four other collabs.\n\nWork out what those would have paid, and that's your exclusivity fee. It's not a premium, it's compensation for lost work.\n\nDo the maths before you agree.",
     "Longest exclusivity you've agreed to?"),

    ("redflag", "They won't tell you the brand name upfront",
     "Legitimate campaigns don't need that much mystery.",
     "Agencies sometimes withhold the client early, which is normal. Refusing to name them before you commit is not.\n\nYou can't assess fit, check their reputation or price properly without knowing who it is. That's the whole basis of your decision.\n\nNo name, no yes.",
     "Ever been asked to commit blind?"),

    ("pitch", "Attach one example, not your whole portfolio",
     "The single most relevant piece beats a folder of everything.",
     "A brand has ninety seconds for your email. A link to twelve videos gets none of them opened.\n\nOne piece that matches what you're proposing does the entire job, because it shows exactly what they'd be buying.\n\nPick your closest match.",
     "What's your strongest example?"),

    ("growth", "Consistency beats frequency",
     "Three a week forever beats seven a week for a month.",
     "Burnout posting always ends in a silent fortnight, and the algorithm treats that gap as a reset.\n\nPick a rhythm you can hold through a busy week and hold it. Boring reliability compounds in a way sprints never do.\n\nChoose a pace you can survive.",
     "What's your posting rhythm?"),

    ("money", "Get paid in your own currency",
     "Conversion fees and delays eat international payments.",
     "Overseas brands often default to whatever's easy for them, and you absorb the cost.\n\nAgree the currency and who covers the transfer fee before you start. It's a five-word question that saves real money.\n\nAsk upfront, not on the invoice.",
     "Have you worked with overseas brands?"),

    ("negotiation", "Ask for the brief before you quote",
     "You cannot price work you haven't seen.",
     "Brands frequently ask for a rate before explaining what they want, and creators guess.\n\nGuess low and you're stuck. Guess high and you lose it. Ask for scope first every time — it's a completely normal request.\n\nScope, then number.",
     "Do you quote before or after the brief?"),

    ("mistake", "Not saving your own content",
     "Instagram is not a backup, and accounts get lost.",
     "Hacks, bans and accidental deletions happen constantly, and the raw files are what let you rebuild.\n\nKeep every final export and the originals in cloud storage. It's also how you deliver reuse rights to brands later.\n\nBack it up this week.",
     "Do you back up your content?"),

    ("confidence", "You are allowed to have a rate card",
     "Making brands ask every time costs you money and hours.",
     "A simple document with your packages and prices ends the awkward dance entirely.\n\nIt filters out brands below your range before they waste your week, and it makes you read as an established business rather than someone deciding on the spot.\n\nBuild it once.",
     "Do you have a rate card?"),

    ("community", "Credit the people who help you",
     "Your editor, your photographer, the friend who holds the light.",
     "Creator work looks solo and almost never is.\n\nTagging the people involved builds the small network that eventually sends work your way — and it's the difference between a scene and a set of competitors.\n\nGenerosity is strategy here.",
     "Who's on your team, officially or not?"),

    ("rates", "Your first rate is not your forever rate",
     "The number you invented nervously two years ago is not a law.",
     "Creators anchor on whatever they charged first and stay there long past the point it makes sense.\n\nYour audience, skill and turnaround have all improved. The price should have moved with them.\n\nReview your rate every six months, on a date in the calendar.",
     "When's your next rate review?"),

    ("redflag", "Unlimited revisions in the contract",
     "That's not a contract, it's an open-ended commitment.",
     "'Until the client is satisfied' has no end point and no extra payment attached.\n\nTwo rounds, then hourly. Every professional creative field works this way, and brands accept it immediately when you say it plainly.\n\nCap it before you sign.",
     "How many revisions do you allow?"),

    ("pitch", "Time your pitch to their calendar",
     "Pitch in the month before their season, not during it.",
     "Brands lock budgets weeks ahead. Pitching during a launch means everyone is busy and the money is already spent.\n\nWork out when they plan, and land in their inbox just before. Same email, completely different odds.\n\nTiming beats persuasion.",
     "When do you send your pitches?"),

    ("growth", "Make one thing people can't get elsewhere",
     "The whole account rests on that one thing.",
     "There's a version of your content only you can make — your city, your job, your sense of humour, your access.\n\nThat's the thing to double down on. Everything else you post is available from a hundred other accounts.\n\nFind it and repeat it.",
     "What's your unfair advantage?"),

    ("money", "Never work for revenue share alone",
     "Unless you control the product, the price and the marketing, you're not a partner.",
     "Revenue share sounds fair and isn't — every variable that decides your earnings sits with them.\n\nIf the brand's checkout is bad or the product's priced wrong, you did the work for nothing. Take a base fee. Add share on top.",
     "Ever been offered revenue share?"),

    ("negotiation", "Repeat the terms back in writing",
     "One email after the call prevents every future disagreement.",
     "Calls feel clear and memories diverge within a week.\n\n'Confirming: one reel, two stories, 30-day organic usage, ₹X, half upfront, live on the 14th.' Short, friendly, and now you both have the same version.\n\nSend it every time.",
     "Do you confirm calls in writing?"),

    ("mistake", "Chasing follower count over audience quality",
     "10k people who trust you is a business. 100k who scroll past isn't.",
     "Bought or baited followers inflate the number and destroy the engagement rate brands actually check.\n\nWorse, they dilute the real audience — the people who'd genuinely buy something you recommend.\n\nGrow slower with people who care.",
     "Would you take 10k engaged or 100k passive?"),

    ("confidence", "Your content doesn't need to be for everyone",
     "The people who don't get it were never going to buy anything.",
     "Softening your work to avoid criticism removes exactly the parts that made people care.\n\nA strong point of view loses some followers and converts the rest far harder. That trade is always worth it.\n\nBe more specific, not more agreeable.",
     "What opinion do you hold that splits your audience?"),

    ("community", "Support creators at your level",
     "The people growing alongside you become your network.",
     "Everyone tries to get noticed by creators far above them, who are overwhelmed with the same messages.\n\nThe creators at your stage will actually reply, collaborate and share opportunities. In three years that's your entire professional circle.\n\nLook sideways.",
     "Who's growing alongside you right now?"),

    ("rates", "Quote a range only when you must",
     "Brands will always hear the bottom of it.",
     "A range says you're unsure, and the lower number becomes the new ceiling.\n\nIf you genuinely need one because scope is unclear, make the bottom of the range a price you're happy with — because that's what you'll get.\n\nOne number, whenever possible.",
     "Do you quote ranges or fixed rates?"),

    ("redflag", "Payment 90 days after posting",
     "You're financing their campaign for three months.",
     "Long payment terms are normal in some industries and brutal for individuals with no cash cushion.\n\nNegotiate to 30 days, or take more upfront. A brand that can afford the campaign can afford to pay you this quarter.\n\nPush back. It usually moves.",
     "What's the longest you've waited to be paid?"),

    ("pitch", "Pitch the same brand more than once",
     "Different person, different quarter, different idea.",
     "A no in March from a marketing manager who's since left says nothing about September.\n\nBrands change budgets, teams and priorities constantly. Creators who pitch a brand three times over a year land far more of them.\n\nKeep a list. Work it.",
     "Which brand is on your list?"),

    ("growth", "Watch your retention graph",
     "It tells you the exact second people left.",
     "Instagram shows where viewers dropped off, which is the most useful feedback you'll ever get for free.\n\nA cliff at three seconds means the hook failed. A slow decline means the middle dragged. Fix the specific moment, not the whole video.\n\nCheck it on every reel.",
     "Do you look at retention?"),

    ("money", "Price for the audience, not the follower count",
     "A buying audience is worth more than a watching one.",
     "If your followers actually purchase what you recommend, you are worth considerably more than a larger account whose audience never converts.\n\nBring that to the negotiation: the code redemptions, the DMs asking where to buy. That evidence justifies the rate.\n\nSell the outcome.",
     "Can you prove your audience buys?"),

    ("negotiation", "Silence is a negotiating position",
     "After you send the number, stop talking.",
     "The instinct is to fill the pause with justification or a preemptive discount.\n\nLet it sit. Brands need time to check budgets, and the quiet is almost never rejection. Creators lose thousands filling that silence.\n\nSend it. Close the laptop.",
     "How long do you wait before following up on a quote?"),

    ("mistake", "Treating every brand deal as permanent",
     "Most collabs are one campaign, and that's completely normal.",
     "Creators read a single project as the start of a long relationship, then feel rejected when nothing follows.\n\nBrands work in campaigns. A great collab that doesn't repeat isn't a failure — it's a reference and a reason to follow up next quarter.\n\nAdjust the expectation.",
     "How many brands have rebooked you?"),

    ("confidence", "Post before you feel ready",
     "The account that exists beats the one you're still planning.",
     "Waiting for better equipment, a clearer niche or a nicer feed is the most common way creators lose a year.\n\nThe skills only develop through posting. Everyone's first fifty are bad, including the people you admire.\n\nPublish the imperfect one.",
     "What's stopping you posting today?"),

    ("community", "Ask your audience what they want",
     "They'll tell you, and then they'll watch it.",
     "A story poll or a question box is the fastest content research available, and it doubles as engagement.\n\nCreators guess for weeks about what to make while the answer sits one tap away in their own audience.\n\nAsk this week.",
     "When did you last ask your audience directly?"),

    ("rates", "Don't discount for 'long-term potential'",
     "Future work should be paid at future rates, not this one.",
     "'Do this cheap and there's more coming' is the most common way creators end up permanently underpriced.\n\nIf more work comes, price it then. If it doesn't, you've simply done a job for less than it was worth.\n\nThe first price sets every price after it.",
     "Ever discounted for promised future work?"),

    ("redflag", "They want your login details",
     "Never. There is no legitimate reason for this.",
     "No real campaign requires access to your account. Not for 'analytics', not for 'scheduling', not for 'verification'.\n\nAnything a brand genuinely needs, you can screenshot or export yourself. Handing over credentials is how accounts get stolen.\n\nHard no, every time.",
     "Has anyone ever asked you for account access?"),

    ("pitch", "Have one line that explains you",
     "You'll use it in every pitch, bio and introduction.",
     "'I make honest skincare reviews for people with sensitive skin in humid cities.'\n\nOne sentence that says what you make and who it's for. It makes you memorable and it makes brands' decisions easy — and most creators can't say theirs.\n\nWrite yours today.",
     "What's your one line?"),

    ("growth", "Batch your filming",
     "One shoot day beats seven scattered evenings.",
     "Setting up, lighting and getting into the right headspace is most of the effort, and doing it daily burns you out.\n\nShoot four pieces in one session and you've bought back your week — and consistency stops depending on daily motivation.\n\nPick a shoot day.",
     "Do you batch or shoot daily?"),

    ("money", "Charge for the usage, not just the post",
     "Their ads running your face for six months is a separate product.",
     "Organic posting and paid amplification are different rights with very different values.\n\nIf a brand wants to run your content as an ad, that's licensing — priced separately, for a defined term. Most creators give it away by accident.\n\nAlways ask how they'll use it.",
     "Do you charge for paid usage?"),

    ("negotiation", "It's fine to say the budget is too low",
     "Politely, once, without apology.",
     "'That's below my rate for this scope, but I'd love to work together if the budget changes' is professional and keeps the door open.\n\nIt also occasionally produces a better offer, because they had room they weren't using.\n\nSay it plainly and move on.",
     "How do you decline a low offer?"),

    ("mistake", "Letting brands set your posting schedule",
     "Your audience has a rhythm. Don't break it for a campaign.",
     "Brands sometimes demand a posting time that suits their launch and not your audience's habits.\n\nYou know when your people are online. Pushing back with your data is in the brand's interest too — better timing means better results for them.\n\nShare the insight. They'll agree.",
     "Have you pushed back on a posting time?"),

    ("confidence", "Comparison is a content killer",
     "Their highlight reel against your behind-the-scenes is not a fair fight.",
     "Every creator you compare yourself to has quiet months, flopped posts and rejected pitches you'll never see.\n\nMeasure against your own last quarter — the only comparison with any information in it.\n\nClose the app and open your own insights.",
     "Who do you compare yourself to?"),

    ("community", "Say thank you to brands that pay on time",
     "They're rarer than they should be, and they notice.",
     "A short message acknowledging a smooth, prompt payment costs nothing and makes you memorable for the right reason.\n\nThose are the brands you want to rebook, and being pleasant to work with is genuinely why creators get called back.\n\nSend the message.",
     "Which brand has been best to work with?"),

    ("faq", "Do I need to register as a business?",
     "Once creator income is regular, yes — and it makes you easier to pay.",
     "Many brands can only pay registered entities with a proper invoice, so it directly widens the work available to you.\n\nIt also separates your finances and makes tax straightforward. Talk to an accountant once; it's a short conversation.\n\nWorth doing earlier than feels necessary.",
     "Are you registered yet?"),

    ("faq", "Should I disclose paid partnerships?",
     "Yes. Legally and for your own credibility.",
     "Disclosure is required, and audiences are far better at spotting undisclosed ads than creators assume.\n\nBeing open about it costs you almost no engagement and protects the trust that your entire income depends on.\n\nUse the paid partnership label. Every time.",
     "Do you always disclose?"),

    ("growth", "Your caption is doing half the work",
     "People read it while the video loops. Give them something to read.",
     "Creators spend hours on the edit and write the caption in eight seconds.\n\nThe caption is where the context lives, where the question that drives comments goes, and where the searchable words sit. A blank one wastes the attention the video earned.\n\nWrite it before you shoot.",
     "How much time do you spend on captions?"),

    ("mistake", "Waiting for brands to find you",
     "The creators getting booked are the ones sending emails.",
     "Inbound happens eventually, and mostly to accounts that were already visible for other reasons.\n\nEveryone else pitches. The creators with full calendars are almost always the ones treating outreach as a weekly habit, not a last resort.\n\nSend three pitches this week.",
     "How many brands have you pitched this month?"),

    ("rates", "Price rises don't need an announcement",
     "Just quote the new number on the next enquiry.",
     "Creators agonise over how to tell existing brands about a rate change.\n\nYou don't have to. The next brief gets the new rate, with no explanation and no apology. Brands change their prices without telling you too.\n\nQuietly. From the next email.",
     "What's your next rate going to be?"),

    ("confidence", "One good collab is enough to build on",
     "You only need one brand willing to vouch for you.",
     "The hardest deal is the first, because there's nothing to point at.\n\nAfter one, every pitch has proof: here's what I made, here's how it performed, here's a brand that worked with me. That changes everything about how you're read.\n\nGet the first one. The rest follow.",
     "What was your first paid collab?"),

    ("community", "Go to creator meetups in your city",
     "Most opportunities travel by word of mouth, not by email.",
     "Brands ask creators they trust to recommend other creators, constantly.\n\nBeing a known, likeable person in your local scene puts you in those conversations in a way no pitch ever will. It's slow and it compounds.\n\nFind one this month.",
     "Been to a creator meetup?"),

    ("negotiation", "Ask who else is on the campaign",
     "It tells you your positioning and whether the rate is fair.",
     "Knowing the other creators reveals what tier the brand thinks you're in — and whether you're being paid accordingly.\n\nIt's a completely reasonable question, and the answer often justifies asking for more.\n\nAsk before you sign.",
     "Do you ask who else is involved?"),

    ("proof", "Keep receipts of your results",
     "Screenshots of results are your best sales material.",
     "A saved screenshot showing a brand's post drove 400 profile visits or sold out a code is worth more than any follower number.\n\nCollect them campaign by campaign. Within a year you have a portfolio of outcomes, not just content.\n\nStart the folder now.",
     "Do you save your campaign results?"),
]
