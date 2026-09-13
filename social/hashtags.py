"""CollabHive — hashtag sets for Instagram reach.

Instagram down-ranks accounts that paste the identical hashtag block every day,
so build_tags() mixes three tiers and rotates the selection per day:

  core   - always-on brand/identity tags (a few, every post)
  broad  - high-volume discovery tags (big reach, high competition)
  niche  - lower-volume intent tags (smaller reach, much better conversion)

Roughly 12-18 tags per post, which is where reach plateaus in practice.
"""
import random

CORE = ["CollabHive", "CreatorEconomy", "InfluencerMarketing"]

BRAND_BROAD = [
    "DigitalMarketing", "MarketingTips", "BrandStrategy", "SocialMediaMarketing",
    "EcommerceMarketing", "D2CBrands", "MarketingStrategy", "BrandBuilding",
    "SmallBusinessMarketing", "ContentMarketing", "GrowthMarketing", "AdvertisingTips",
]
BRAND_NICHE = [
    "D2CIndia", "IndianStartups", "BeautyBrandIndia", "FashionBrandIndia",
    "InfluencerMarketingIndia", "UGCCreator", "CreatorPartnerships", "BrandCollabs",
    "MarketingIndia", "StartupIndia", "IndianEcommerce", "ShopifyIndia",
    "IndianBrands", "MadeInIndia", "BrandAwareness", "SocialMediaIndia",
]

CREATOR_BROAD = [
    "ContentCreator", "InfluencerLife", "CreatorTips", "SocialMediaTips",
    "ContentCreatorTips", "InstagramTips", "CreatorCommunity", "ReelsCreator",
    "InfluencerTips", "GrowOnInstagram", "ContentStrategy", "CreatorLife",
]
CREATOR_NICHE = [
    "IndianCreators", "IndianInfluencer", "MicroInfluencer", "UGCCreatorIndia",
    "CreatorsOfIndia", "DelhiInfluencer", "MumbaiInfluencer", "BangaloreCreator",
    "BeautyCreator", "FashionCreator", "LifestyleInfluencer", "NanoInfluencer",
    "PaidCollab", "BrandDeals", "InfluencerIndia", "CreatorMoney",
]


def build_tags(audience: str, day: int, count: int = 15) -> list[str]:
    """Deterministic per-day hashtag mix — same day always yields the same set,
    but consecutive days never share the full block."""
    rng = random.Random(f"{audience}-{day}")
    broad = BRAND_BROAD if audience == "brand" else CREATOR_BROAD
    niche = BRAND_NICHE if audience == "brand" else CREATOR_NICHE

    n_core = len(CORE)
    n_broad = max(1, (count - n_core) // 3)
    n_niche = count - n_core - n_broad

    tags = list(CORE)
    tags += rng.sample(broad, min(n_broad, len(broad)))
    tags += rng.sample(niche, min(n_niche, len(niche)))
    rng.shuffle(tags)
    return tags


def tag_block(audience: str, day: int, count: int = 15) -> str:
    return " ".join("#" + t for t in build_tags(audience, day, count))
