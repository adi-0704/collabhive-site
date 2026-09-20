"""CollabHive — Instagram content bank (aggregator).

Copy lives in numbered batch files, one set per audience, so no single file
becomes unmanageable as the calendar grows:

    posts_brand.py    + posts_brand2.py     -> @collabhive.in   (brands)
    posts_creator.py  + posts_creator2.py   -> @collabvibe.in   (creators)

Everything is authored rather than templated. generate_calendar.py asserts that
no body copy and no headline repeats anywhere in the calendar, so a recycled
post fails the build instead of quietly shipping.

To extend: add posts_brand3.py / posts_creator3.py and append them below.
"""

from posts_brand import BRAND_POSTS as _B1
from posts_brand2 import BRAND_POSTS_2 as _B2
from posts_brand3 import BRAND_POSTS_3 as _B3
from posts_brand4 import BRAND_POSTS_4 as _B4
from posts_creator import CREATOR_POSTS as _C1
from posts_creator2 import CREATOR_POSTS_2 as _C2
from posts_creator3 import CREATOR_POSTS_3 as _C3
from posts_creator4 import CREATOR_POSTS_4 as _C4

BRAND_POSTS = _B1 + _B2 + _B3 + _B4
CREATOR_POSTS = _C1 + _C2 + _C3 + _C4

__all__ = ["BRAND_POSTS", "CREATOR_POSTS"]
