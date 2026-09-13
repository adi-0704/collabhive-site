"""CollabHive — Instagram content bank (aggregator).

The actual copy lives in two files, one per audience, so each can be edited
without scrolling past the other:

    posts_brand.py    -> @collabhive.in   (brands: ROI, briefing, budgets)
    posts_creator.py  -> @collabvibe.in   (creators: rates, pitching, growth)

Everything is authored rather than templated. generate_calendar.py asserts that
no body copy and no headline repeats, so a recycled post fails the build
instead of quietly shipping.
"""

from posts_brand import BRAND_POSTS      # noqa: F401
from posts_creator import CREATOR_POSTS  # noqa: F401

__all__ = ["BRAND_POSTS", "CREATOR_POSTS"]
