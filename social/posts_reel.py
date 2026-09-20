"""CollabHive - reel-only content. Separate stream from the static feed.

Deliberately different from the static banks in two ways:

  * TOPICS do not overlap. The static calendar consumes posts_brand*.py and
    posts_creator*.py; nothing here appears there. A follower seeing both on
    the same day sees two different things.
  * REGISTER is shorter and louder. Static posts are read; reels are watched at
    speed with the sound off, so the headline carries almost everything and the
    sub is one line of payoff.

    (pillar, headline, sub, caption, cta)
"""

# --------------------------------------------------------------- BRAND reels
REEL_BRAND = [
    ("hook", "Stop booking creators by follower count",
     "Read their comments instead. Takes five minutes.",
     "Follower count is the easiest number to see and the least useful one.\n\nOpen their last twenty posts and read the comments. Real questions mean a real audience. A wall of emojis means a wall of emojis.",
     "What do you check first?"),

    ("hook", "Your discount code is doing nothing",
     "If your homepage runs the same offer, the code is decoration.",
     "A creator code only works if it gets the audience something they cannot get by going straight to your site.\n\nEarly access, a bundle, an extra unit. Otherwise you are paying for a link.",
     "Is your code actually exclusive?"),

    ("truth", "Most brands brief the product",
     "The good ones brief the objection.",
     "Features tell a creator what it does. Objections tell them what to overcome.\n\nHand them the reason people do not buy and watch what they build around it.",
     "What stops people buying from you?"),

    ("truth", "You are paying for content, not a post",
     "The placement expires. The footage does not.",
     "Once usage rights are in the deal, one shoot becomes ads, PDP video, email headers and stories for months.\n\nPriced as a placement it looks expensive. Priced as production it is cheap.",
     "Do you negotiate usage?"),

    ("mistake", "Approving creator content to death",
     "Round four is where the personality dies.",
     "Every revision drags the work closer to your brand deck and further from the voice you paid for.\n\nOne round. Two at most. Then let it go.",
     "How many rounds do you run?"),

    ("mistake", "Launching with low stock",
     "The fastest way to waste a good campaign.",
     "Creator content drives a spike, and a spike landing on a sold-out page converts nobody and annoys everyone.\n\nCheck inventory before you confirm the date.",
     "Has this caught you out?"),

    ("number", "48 hours is not a result",
     "Reels surface for weeks. Judge it at day fourteen.",
     "A post that looks flat on Tuesday can be your best performer by the end of the month.\n\nKilling a partnership on a two-day screenshot means deciding on a fraction of the data.",
     "When do you call a campaign?"),

    ("number", "3 posts beats 9 creators",
     "Repetition from one trusted voice changes behaviour.",
     "Nobody buys on first exposure. They buy when something has been in their feed enough times to feel normal.\n\nNine strangers once each is nine adverts. One person three times is familiarity.",
     "Depth or spread?"),

    ("quick", "Ask for the raw footage",
     "You paid for the shoot, not one export.",
     "The offcuts become next month's ads, and most creators will share them if it is in the brief.\n\nAlmost nobody asks.",
     "Do you ask for raws?"),

    ("quick", "Put a deadline on your own reply",
     "Creators hold slots for brands who answer fast.",
     "A thread you leave for five days is a shoot date someone else booked.\n\nAnswer inside 24 hours or tell them when you will.",
     "How fast do you reply?"),

    ("contrarian", "Big budgets buy access, not enthusiasm",
     "Small brands get better content and do not know it.",
     "Creators make their best work for products they would actually use, and that is far more often a small brand than a large one.\n\nYour size is an advantage. Use it.",
     "Has a small budget ever beaten a big one?"),

    ("contrarian", "Do not chase the trend",
     "By the time a brand joins, it has peaked.",
     "Trend content needs speed most brands structurally cannot manage, and arriving late is worse than not arriving.\n\nBe useful instead of current. Useful keeps working.",
     "Do you chase trends?"),

    ("money", "Pay on delivery, not in 60 days",
     "Creators talk to each other. Constantly.",
     "A brand that pays late becomes known as one within a week, and the creators you most want are the ones who can afford to decline you.\n\nFast payment is the cheapest reputation you will ever buy.",
     "What are your terms?"),

    ("money", "Cheap gets expensive by month end",
     "Two reshoots and a missed deadline cost more than the rate saved.",
     "Rate is the smallest number in a collab. The real cost is chasing, re-briefing and unusable content.\n\nBuy reliability.",
     "Worst cheap-turned-expensive story?"),

    ("tactic", "Read your competitor's comments",
     "Free research, brutally honest.",
     "People say things under a creator's post they would never put in your feedback form - about price, sizing, delivery, whether it worked.\n\nAn hour there tells you what to brief next.",
     "When did you last look?"),

    ("tactic", "Ask customers which creators they follow",
     "One line in your post-purchase email.",
     "Your buyers will hand you a ranked shortlist of exactly who influences them, for free, if you ask.\n\nBetter than any database.",
     "Have you asked?"),

    ("tactic", "Book festive creators in August",
     "October rates are 40-60% higher. Same people.",
     "Creator pricing is supply and demand, and in festive season the supply is gone.\n\nBooking early is not just availability. It is the cheapest the campaign will ever be.",
     "When do you book festive?"),

    ("belief", "The comment section is a second ad slot",
     "And it is free.",
     "Dozens of people ask the same questions under every collab. If the creator knows the answers, each reply converts.\n\nIf they do not, the questions sit there unanswered.",
     "Do you prep creators for comments?"),

    ("belief", "Your packaging is a content brief",
     "If the box is worth filming, people film it.",
     "It is the one piece of marketing every customer touches, and the only one that generates content without you asking.\n\nSpend on the box.",
     "Is yours worth filming?"),

    ("belief", "Reposting creator content is free proof",
     "You already paid for it. Use it.",
     "A real person choosing you does something your own photography cannot, and it is sitting unused on their grid.\n\nAsk for reposting rights in the brief.",
     "Is your grid all product shots?"),
]

# ------------------------------------------------------------- CREATOR reels
REEL_CREATOR = [
    ("hook", "If every brand says yes, you are too cheap",
     "A healthy rate gets pushback sometimes.",
     "Nobody hesitating means you priced below what the market would have paid.\n\nRaise it 20% on the next enquiry. The good brands still say yes.",
     "When did you last raise it?"),

    ("hook", "Stop pitching info@",
     "Find the marketing manager. Four minutes on LinkedIn.",
     "Generic inboxes are where pitches go to die, because nobody owns them.\n\nOne named person doubles most creators' reply rate.",
     "Where do you send pitches?"),

    ("truth", "Exposure is not payment",
     "Brands with budgets never open with it.",
     "A company that can afford product can afford people. 'Great visibility' is what they say when the budget exists and none of it is for you.\n\nAsk for their rate card.",
     "Worst pitch you have had?"),

    ("truth", "Your media kit does not need to be pretty",
     "Four numbers and one screenshot.",
     "Audience size, top city, gender split, average views - plus an insights screenshot so they know it is real.\n\nOne page. Send the PDF.",
     "Do you have one?"),

    ("mistake", "Accepting every brand that emails",
     "Your feed becomes a catalogue.",
     "The reason brands pay you is that your recommendation means something. Every product you would not use spends a little of that.\n\nSpend enough and there is nothing left to sell.",
     "What did you last turn down?"),

    ("mistake", "Sending your best week",
     "Brands know a cherry-picked screenshot when they see one.",
     "Your 30-day average, quiet weeks included, builds more trust than one viral reel - because it tells them what to expect.\n\nHonest numbers get rebooked.",
     "Averages or highlights?"),

    ("number", "50% upfront. Standard",
     "Every other freelance industry does it.",
     "Half before you shoot, half on delivery. Brands that work with creators properly will not blink.\n\nThe ones that argue are telling you something.",
     "Do you take a deposit?"),

    ("number", "10 hooks before you shoot",
     "The first one you think of is the obvious one.",
     "Everyone thought of it. By the eighth or ninth you are into something specific and surprising.\n\nThat is the one that stops the scroll.",
     "How many do you write?"),

    ("quick", "Face the window",
     "That is most of lighting solved.",
     "A window behind you makes a silhouette. A window in front flatters everything.\n\nBefore buying a ring light, turn around.",
     "Where is your window?"),

    ("quick", "Record a throwaway take first",
     "Your first attempt is a warm-up.",
     "Everyone's opening take is stiff, and creators burn energy trying to make it perfect.\n\nRecord one to bin, then start.",
     "How many takes do you need?"),

    ("contrarian", "Small accounts get paid",
     "Brands are actively hunting 5-15k creators.",
     "Micro creators convert better and cost less, so the smartest brands built their strategy around them.\n\nIf you have been waiting to hit a number, you have been leaving money behind.",
     "How big were you at your first paid collab?"),

    ("contrarian", "Posting more will not fix it",
     "One post people send to a friend beats five nobody saves.",
     "The algorithm rewards sends and saves far above likes, because those are the only signals habit cannot fake.\n\nDifferent question, different account.",
     "Most-shared post you have made?"),

    ("money", "The fee is the easy part",
     "Usage and exclusivity cost you more.",
     "Six months of paid usage plus category exclusivity is your face in their ads and a ban on their competitors.\n\nPrice it, or cap it at 30 days.",
     "Ever given exclusivity away free?"),

    ("money", "Charge a rush fee",
     "48 hours is a service, not a favour.",
     "Rearranging your week is real disruption, and every other freelance field charges for it.\n\n25-50% on top. Brands with a real deadline pay it.",
     "Do you charge for rush?"),

    ("tactic", "Answer questions under bigger creators' posts",
     "Their comments are full of questions nobody answers.",
     "A genuinely useful reply gets seen by everyone reading that thread.\n\nDo it consistently and people follow you from it.",
     "Have you tried this?"),

    ("tactic", "Pin the answer everyone asks",
     "Saves you fifty replies and keeps people on the post.",
     "Every post has one repeated question - price, link, shade.\n\nPin it yourself the moment you publish. Watch time goes up.",
     "Do you pin a comment?"),

    ("tactic", "Pitch a month before the season",
     "Rakhi briefs go out in July. Pitch in June.",
     "Gifting campaigns are planned ahead because product has to ship.\n\nPitch in the month itself and you are competing for leftovers.",
     "How far ahead do you pitch?"),

    ("belief", "Leave your early videos up",
     "Cringing at them means you improved.",
     "Creators delete early work and erase the only evidence of their own growth.\n\nLeave it up. New followers find it reassuring.",
     "Can you watch your first video?"),

    ("belief", "Nobody remembers your flop",
     "You think about it for months. They scrolled past in a second.",
     "The audience has no memory of it by morning and the algorithm moved on.\n\nThe only lasting damage is you not posting.",
     "Still thinking about one?"),

    ("belief", "Send brands their results unprompted",
     "Almost no creator does this.",
     "A short message a week later with reach, saves and a screenshot makes you a partner rather than a vendor.\n\nIt is the single best way to get rebooked.",
     "Do you follow up?"),
]
