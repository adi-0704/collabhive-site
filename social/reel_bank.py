"""CollabHive - reel content bank (aggregator).

Separate from content_bank.py on purpose. The static feed and the reel stream
run side by side every day, so they must never draw from the same copy: a
follower who sees the 18:00 post and the 19:30 reel should see two different
ideas, not one idea twice.

generate_reels.py asserts that separation - it fails the build if any reel
headline or body also appears in the static bank.

To extend: add posts_reel2.py / posts_reel3.py and append them below.
"""

from posts_reel import REEL_BRAND as _RB1, REEL_CREATOR as _RC1
from posts_reel2 import REEL_BRAND_2 as _RB2, REEL_CREATOR_2 as _RC2
from posts_reel3 import REEL_BRAND_3 as _RB3, REEL_CREATOR_3 as _RC3
from posts_reel4 import REEL_BRAND_4 as _RB4, REEL_CREATOR_4 as _RC4
from posts_reel5 import REEL_BRAND_5 as _RB5, REEL_CREATOR_5 as _RC5

REEL_BRAND_POSTS = _RB1 + _RB2 + _RB3 + _RB4 + _RB5
REEL_CREATOR_POSTS = _RC1 + _RC2 + _RC3 + _RC4 + _RC5

__all__ = ["REEL_BRAND_POSTS", "REEL_CREATOR_POSTS"]
