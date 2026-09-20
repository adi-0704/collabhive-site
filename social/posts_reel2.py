"""CollabHive - reel content, batch 2. See posts_reel.py for the format.

Headlines opening on a number unlock the `stat` treatment and headlines ending
in a question unlock `reveal`, so each batch deliberately carries a few of both
- otherwise the renderer falls back to the same three styles all month.

    (pillar, headline, sub, caption, cta)
"""

REEL_BRAND_2 = [
    ("number", "90% of your brief is ignored",
     "Creators read the first paragraph and the deliverables.",
     "A fourteen-page deck does not get read. One page does.\n\nWho it is for, what to avoid, what you want them to feel, deliverables, deadline. That is the whole brief.",
     "How long is yours?"),

    ("hook", "Gifting is not a campaign",
     "It is a lottery ticket with a courier receipt.",
     "Sending free product and hoping is not a strategy - it has no deadline, no brief and no obligation.\n\nGift to test fit. Pay to run a campaign. Do not confuse the two.",
     "Gifting or paid?"),

    ("truth", "The creator knows their audience better than you",
     "That is the entire thing you are buying.",
     "Brands who hand over a word-for-word script are paying a specialist rate for a reading service.\n\nGive them the message. Let them choose the words.",
     "Do you script?"),

    ("mistake", "Briefing on a Friday for a Monday",
     "You will get Friday-evening work.",
     "Good creator content needs a shoot day, an edit day and a day to sit on it.\n\nTwo working days produces exactly what two working days produces.",
     "What notice do you give?"),

    ("money", "7 days is a fair payment window",
     "Not 30. Not 60. Not on receipt of invoice plus approval.",
     "Creators are individuals, not vendors with a credit line. A week is generous and it costs you nothing but process.\n\nThe ones you want will remember.",
     "How fast do you pay?"),

    ("quick", "Put the link in the brief",
     "Not in a follow-up email three days later.",
     "Half of all broken creator campaigns are a tracking link that arrived after the content was already built.\n\nOne field. Fill it in first.",
     "Ever shipped a dead link?"),

    ("contrarian", "Aesthetic feeds sell less",
     "Polished reads as an advert. Rough reads as a recommendation.",
     "The content that converts looks like something a friend filmed, because that is the register people trust.\n\nStop asking creators to match your grid.",
     "Polished or real?"),

    ("tactic", "Rebook your best creator immediately",
     "Before a competitor sees the numbers you just saw.",
     "A creator who performed once will perform again, and right now you are the only brand who knows.\n\nThat window closes the moment the post goes up.",
     "Who would you rebook?"),

    ("belief", "One good creator beats a media buy",
     "Trust is the only thing you cannot purchase at auction.",
     "You can buy impressions at any volume you like. You cannot buy someone's audience believing them.\n\nThat is what a partnership is for.",
     "Ads or creators?"),

    ("hook", "Does your product survive a close-up?",
     "Reels are shot in daylight at arm's length.",
     "Packaging that photographs well in a studio can look cheap on a phone camera in someone's kitchen.\n\nFilm it yourself before you ship a hundred units.",
     "Have you tested it?"),

    ("mistake", "Asking for a discount on their rate",
     "Then asking for extra deliverables.",
     "Negotiating down and scoping up in the same email is the fastest way to be quietly deprioritised.\n\nPick one.",
     "Do you negotiate?"),

    ("number", "2 weeks minimum from brief to live",
     "Anything faster is a favour, not a timeline.",
     "Brief, shoot, edit, review, schedule. Compressing it does not remove the steps, it just removes the care.\n\nPlan backwards from the launch date.",
     "How far ahead do you plan?"),

    ("truth", "Every collab is a hiring decision",
     "You are putting someone else's judgement in front of your customers.",
     "Rate, reach and aesthetic are the easy filters. The real question is whether you would trust this person to answer a customer's question.\n\nScreen for that.",
     "What is your real filter?"),

    ("tactic", "Give creators the FAQ",
     "They will be asked. Decide what the answer is.",
     "Price, shipping, ingredients, sizing, returns. Someone asks all five under every collab post.\n\nA one-page FAQ turns those comments into conversions.",
     "Do you send one?"),

    ("quick", "Seed a week before launch",
     "So the content exists on day one.",
     "Launching and then briefing means your loudest week has nothing in it.\n\nShip product early, hold the posts, go live together.",
     "When do you seed?"),

    ("money", "Rate cards are a starting point",
     "Scope moves the number. Followers do not.",
     "Three deliverables plus usage plus exclusivity is a different job to one story.\n\nPrice the work, not the account.",
     "How do you price?"),

    ("contrarian", "Do not run a giveaway to grow",
     "You will buy followers who leave the moment it ends.",
     "Giveaway audiences are optimised for free things, not for your product.\n\nRun them to reward customers. Never to inflate a number.",
     "Have giveaways worked for you?"),

    ("belief", "Your brief is your brand voice",
     "Creators read it as a sample of what you are like to work with.",
     "A cold, clause-heavy brief produces cold, careful content. A human one produces human work.\n\nWrite it like a person.",
     "Read yours back lately?"),

    ("mistake", "Measuring a collab on likes",
     "Saves, sends and site traffic are the ones that matter.",
     "Likes are the cheapest signal on the platform and the least correlated with anything you care about.\n\nAsk for the insights screenshot instead.",
     "What do you measure?"),

    ("hook", "Your best creator is already a customer",
     "Check your order history against your follower list.",
     "Someone who bought before you asked will always make better content than someone discovering you on a brief.\n\nThe list is sitting in your dashboard.",
     "Have you cross-checked?"),
]

REEL_CREATOR_2 = [
    ("money", "3 rates. Always",
     "Basic, recommended, full. Most brands pick the middle.",
     "A single number is a yes or no. Three numbers turns the conversation into which one, which is a conversation you win.\n\nPut the one you want in the middle.",
     "One price or three?"),

    ("hook", "Never send a rate without a deliverable",
     "'25k' means nothing. '25k for one reel plus two stories' does.",
     "A bare number invites a brand to imagine everything it might include, and then be disappointed.\n\nScope first, price second.",
     "How do you quote?"),

    ("truth", "Brands ghost because of process, not you",
     "Budgets move, people leave, quarters close.",
     "A silent brand almost never made a judgement about your work. Something internal changed and nobody updated you.\n\nFollow up twice, then move on.",
     "Been ghosted recently?"),

    ("mistake", "Deleting a post that underperformed",
     "You just told the algorithm it was a mistake too.",
     "Reels keep surfacing for weeks and some of the best performers start slow.\n\nGive it a fortnight before you judge anything.",
     "Do you delete flops?"),

    ("tactic", "Reply to every comment in hour one",
     "That window decides how far the post travels.",
     "Early engagement is the strongest signal short-form has, and replies count as engagement.\n\nBlock twenty minutes after you post. Nothing else.",
     "Do you sit with your posts?"),

    ("number", "5 second hook or nothing",
     "Most people leave before you finish your first sentence.",
     "Say the interesting thing immediately. Context can come after they have decided to stay.\n\nYour intro is costing you the video.",
     "How do you open?"),

    ("quick", "Shoot three at once",
     "Same lighting, same outfit, three videos.",
     "The setup is the expensive part, not the recording. Batching turns one hour into a week of content.\n\nChange one thing between takes.",
     "Do you batch?"),

    ("contrarian", "Niche down after you grow, not before",
     "Post widely, watch what lands, then commit.",
     "Picking a lane on day one is guessing. Your audience will tell you which posts they want more of if you give them a choice.\n\nLet the data pick.",
     "Have you found your lane?"),

    ("belief", "You are allowed to say no",
     "A collab that embarrasses you costs more than it pays.",
     "Every creator remembers one brand deal they wish they had declined, and none of them remember the fee.\n\nYour feed is the asset.",
     "What would you decline?"),

    ("hook", "Is your bio doing any work?",
     "Most read like a job title and a city.",
     "Someone lands on your profile for four seconds. Tell them what they get if they stay.\n\nOne line. What you make and who it is for.",
     "What does yours say?"),

    ("truth", "Consistency beats quality early on",
     "Then quality beats consistency.",
     "You cannot find your voice in ten posts, and nobody's early work is good. Volume is how you get to good.\n\nThen slow down and make it count.",
     "Which stage are you in?"),

    ("money", "Invoice the same day you deliver",
     "Memory and urgency both fade after 48 hours.",
     "The longer the gap between the work and the invoice, the longer the gap before payment.\n\nSend it while the content is still in their feed.",
     "How fast do you invoice?"),

    ("tactic", "Keep a running list of brands you use",
     "That is your pitch list, and it is honest.",
     "Open your bathroom shelf and your kitchen. Every one of those is a brand you can pitch with a genuine reason.\n\nAuthenticity is not a tone, it is a fact.",
     "How many are on yours?"),

    ("mistake", "Pitching with 'I love your brand'",
     "Every email opens that way.",
     "Open with something only you could say - a specific product, a real result, an idea for a post.\n\nSpecific gets read.",
     "How do you open a pitch?"),

    ("quick", "Subtitle everything",
     "Most of your audience is watching on mute.",
     "A reel without captions is a reel most people scroll past without ever hearing the point.\n\nIt takes thirty seconds and it is the single highest-return habit in short-form.",
     "Do you caption?"),

    ("number", "20 minutes of engaging beats 2 hours of scrolling",
     "Comment on accounts your audience already follows.",
     "Reach is not only what you post. It is where you show up.\n\nTwenty deliberate minutes a day changes an account in a month.",
     "How do you spend your app time?"),

    ("contrarian", "Buying followers costs you money",
     "Brands check engagement rate before they check size.",
     "An inflated account has a broken ratio, and that ratio is the first thing on a media kit.\n\nYou will price yourself out of your own market.",
     "Would you spot a fake account?"),

    ("belief", "Your rate is not your worth",
     "It is a number for a job, and jobs differ.",
     "Discounting once for a brand you love is a business decision, not a statement about you.\n\nKeep the two separate and negotiating gets much easier.",
     "Do you take it personally?"),

    ("tactic", "Ask for the brief in writing",
     "A call is not a scope.",
     "Everything agreed verbally is everything that can be remembered differently later.\n\nOne email summarising what was said. That is your contract.",
     "Do you confirm in writing?"),

    ("mistake", "Working without a deadline",
     "Open-ended means it drifts and then it dies.",
     "A collab with no delivery date competes with everything else in your week and loses every time.\n\nPut a date on it before you start.",
     "Do you set deadlines?"),
]
