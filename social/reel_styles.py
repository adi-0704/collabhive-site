"""CollabHive — reel animation styles.

Five distinct 1080x1920 treatments so the feed does not look like one template
with the words swapped. generate picks a style per post, rotating so the same
one never runs twice in a row on a page.

    classic   restrained: logo, accent bar, text rises in sequence
    kinetic   word-by-word typography, the format that dominates short-form
    meme      high-contrast, punchy, conversational - built for mass reach
    stat      a single number slams in, then the context
    reveal    the question holds, then the answer drops

All motion is CSS. No external footage or audio is used: stock video and music
both need licensing, and an unlicensed track on a business account risks a
copyright strike rather than a better reel.
"""
from __future__ import annotations

from layouts import HONEY, INK, PURPLE, _esc, _logo_uri

W, H = 1080, 1920
_FONT = ("https://fonts.googleapis.com/css2?"
         "family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap")

STYLES = ["classic", "kinetic", "meme", "stat", "reveal"]


def _logo_css(size: int = 280) -> str:
    """mix-blend-mode drops logo.png's white background. The fade must live on
    the image itself — opacity on a parent makes a stacking context and the
    white box comes back."""
    return (f".logo{{width:{size}px;margin:0 auto;display:block;"
            f"mix-blend-mode:multiply;opacity:0;animation:fade .6s .15s forwards}}")


def _shell(body: str, css: str, bg: str) -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="{_FONT}" rel="stylesheet">
<style>
 *{{margin:0;padding:0;box-sizing:border-box}}
 body{{width:{W}px;height:{H}px;background:{bg};overflow:hidden;position:relative;
      font-family:'Plus Jakarta Sans',sans-serif}}
 @keyframes fade{{to{{opacity:1}}}}
 @keyframes rise{{to{{opacity:1;transform:translateY(0)}}}}
 @keyframes pop{{0%{{opacity:0;transform:scale(.6)}}70%{{transform:scale(1.08)}}
                100%{{opacity:1;transform:scale(1)}}}}
 @keyframes wipe{{to{{width:220px}}}}
 {css}
</style></head><body>{body}</body></html>"""


def _words(text: str, delay: float = 1.2, step: float = 0.16, cls: str = "w") -> str:
    """Word-by-word reveal. Each word gets its own delay so the line assembles
    rather than appearing — the motion that carries most short-form typography."""
    out = []
    for i, word in enumerate(text.split()):
        out.append(f'<span class="{cls}" style="animation-delay:{delay + i * step:.2f}s">'
                   f'{_esc(word)}</span>')
    return " ".join(out)


# ---------------------------------------------------------------- styles
def classic(headline, sub, cta, accent):
    logo = _logo_uri()
    body = f"""
 <div class="bg"></div>
 <div class="wrap">
   {'<img class="logo" src="%s">' % logo if logo else ''}
   <div class="bar"></div>
   <h1>{_esc(headline)}</h1>
   <div class="sub">{_esc(sub)}</div>
 </div>
 <div class="cta"><span class="pill">{_esc(cta)}</span></div>"""
    css = f"""
 .bg{{position:absolute;inset:0;background:
     radial-gradient(circle at 20% 15%, {accent}22 0%, transparent 45%),
     radial-gradient(circle at 85% 80%, {PURPLE}1a 0%, transparent 45%);
     animation:zoom 7s ease-out forwards}}
 @keyframes zoom{{from{{transform:scale(1)}}to{{transform:scale(1.12)}}}}
 {_logo_css()}
 .wrap{{position:absolute;inset:0;padding:150px 90px;display:flex;flex-direction:column;
       justify-content:center;align-items:center;text-align:center}}
 .bar{{height:12px;width:0;background:{accent};border-radius:99px;margin:52px 0;
      animation:wipe .8s 1.0s forwards}}
 h1{{font-size:104px;font-weight:800;line-height:1.05;color:{INK};letter-spacing:-3.5px;
    opacity:0;transform:translateY(34px);animation:rise .9s 1.3s forwards}}
 .sub{{font-size:44px;font-weight:400;line-height:1.38;color:#5A6480;margin-top:44px;
      max-width:850px;opacity:0;transform:translateY(28px);animation:rise .9s 2.2s forwards}}
 .cta{{position:absolute;bottom:190px;left:0;right:0;text-align:center;opacity:0;
      animation:fade .8s 3.4s forwards}}
 .pill{{display:inline-block;background:#111;color:{HONEY};font-size:46px;font-weight:800;
       padding:32px 72px;border-radius:22px}}"""
    return _shell(body, css, "#fff")


def kinetic(headline, sub, cta, accent):
    body = f"""
 <div class="wrap">
   <div class="head">{_words(headline, 0.6, 0.14)}</div>
   <div class="sub">{_words(sub, 0.6 + len(headline.split()) * 0.14 + 0.4, 0.06, "s")}</div>
 </div>
 <div class="cta"><span class="pill">{_esc(cta)}</span></div>"""
    css = f"""
 body{{background:{INK}}}
 .wrap{{position:absolute;inset:0;padding:160px 88px;display:flex;flex-direction:column;
       justify-content:center}}
 .head{{font-size:110px;font-weight:800;line-height:1.08;color:#fff;letter-spacing:-4px}}
 .head .w{{display:inline-block;opacity:0;transform:translateY(40px);
          animation:rise .5s forwards}}
 .head .w:nth-child(3n){{color:{accent}}}
 .sub{{margin-top:56px;font-size:46px;font-weight:400;line-height:1.4;
      color:rgba(255,255,255,.72)}}
 .sub .s{{display:inline-block;opacity:0;animation:fade .4s forwards}}
 .cta{{position:absolute;bottom:200px;left:0;right:0;text-align:center;opacity:0;
      animation:fade .7s 4.6s forwards}}
 .pill{{display:inline-block;background:{accent};color:{INK};font-size:46px;
       font-weight:800;padding:32px 72px;border-radius:22px}}"""
    return _shell(body, css, INK)


def meme(headline, sub, cta, accent):
    """Deliberately louder: heavy type, hard colour blocks, a snap into place.
    Built for reach rather than polish — the register mass audiences respond to
    without tipping into someone else's meme template."""
    body = f"""
 <div class="top">{_esc(headline)}</div>
 <div class="mid"><div class="emoji">👀</div></div>
 <div class="bot">{_esc(sub)}</div>
 <div class="cta"><span class="pill">{_esc(cta)}</span></div>"""
    css = f"""
 body{{background:{accent}}}
 .top{{position:absolute;top:0;left:0;right:0;padding:150px 70px 60px;text-align:center;
      font-size:96px;font-weight:800;line-height:1.06;color:{INK};letter-spacing:-3px;
      opacity:0;transform:scale(.7);animation:pop .55s .25s forwards}}
 .mid{{position:absolute;top:47%;left:0;right:0;text-align:center;opacity:0;
      animation:pop .5s 1.1s forwards}}
 .emoji{{font-size:190px;line-height:1}}
 .bot{{position:absolute;bottom:330px;left:0;right:0;padding:0 70px;text-align:center;
      font-size:62px;font-weight:700;line-height:1.24;color:#fff;background:{INK};
      padding:52px 60px;opacity:0;transform:scale(.8);animation:pop .55s 1.8s forwards}}
 .cta{{position:absolute;bottom:170px;left:0;right:0;text-align:center;opacity:0;
      animation:fade .6s 2.9s forwards}}
 .pill{{display:inline-block;background:{INK};color:{accent};font-size:42px;
       font-weight:800;padding:26px 60px;border-radius:999px}}"""
    return _shell(body, css, accent)


def stat(headline, sub, cta, accent):
    first, *rest = headline.split()
    body = f"""
 <div class="wrap">
   <div class="big">{_esc(first)}</div>
   <div class="rest">{_esc(' '.join(rest))}</div>
   <div class="sub">{_esc(sub)}</div>
 </div>
 <div class="cta"><span class="pill">{_esc(cta)}</span></div>"""
    css = f"""
 body{{background:{INK}}}
 .wrap{{position:absolute;inset:0;padding:150px 88px;display:flex;flex-direction:column;
       justify-content:center;align-items:center;text-align:center}}
 .big{{font-size:300px;font-weight:800;line-height:.88;color:{accent};letter-spacing:-14px;
      opacity:0;transform:scale(.5);animation:pop .7s .3s forwards}}
 .rest{{margin-top:30px;font-size:80px;font-weight:800;line-height:1.08;color:#fff;
       letter-spacing:-2.5px;opacity:0;transform:translateY(34px);
       animation:rise .7s 1.2s forwards}}
 .sub{{margin-top:44px;font-size:44px;line-height:1.38;color:rgba(255,255,255,.7);
      max-width:820px;opacity:0;transform:translateY(26px);animation:rise .7s 2.1s forwards}}
 .cta{{position:absolute;bottom:200px;left:0;right:0;text-align:center;opacity:0;
      animation:fade .7s 3.3s forwards}}
 .pill{{display:inline-block;background:{accent};color:{INK};font-size:46px;
       font-weight:800;padding:32px 72px;border-radius:22px}}"""
    return _shell(body, css, INK)


def reveal(headline, sub, cta, accent):
    body = f"""
 <div class="q">{_esc(headline)}</div>
 <div class="curtain"></div>
 <div class="a">{_esc(sub)}</div>
 <div class="cta"><span class="pill">{_esc(cta)}</span></div>"""
    css = f"""
 body{{background:#fff}}
 .q{{position:absolute;top:0;left:0;right:0;height:100%;padding:0 88px;display:flex;
    align-items:center;justify-content:center;text-align:center;font-size:104px;
    font-weight:800;line-height:1.06;color:{INK};letter-spacing:-3.5px;
    opacity:0;transform:translateY(30px);animation:rise .8s .3s forwards,
    fadeout .5s 3.2s forwards}}
 @keyframes fadeout{{to{{opacity:0;transform:translateY(-30px)}}}}
 .curtain{{position:absolute;inset:0;background:{accent};transform:translateY(100%);
          animation:sweep .7s 3.1s forwards}}
 @keyframes sweep{{to{{transform:translateY(0)}}}}
 .a{{position:absolute;inset:0;padding:0 88px;display:flex;align-items:center;
    justify-content:center;text-align:center;font-size:76px;font-weight:700;
    line-height:1.22;color:{INK};opacity:0;animation:fade .6s 3.9s forwards}}
 .cta{{position:absolute;bottom:190px;left:0;right:0;text-align:center;opacity:0;
      animation:fade .6s 5.1s forwards}}
 .pill{{display:inline-block;background:{INK};color:{accent};font-size:44px;
       font-weight:800;padding:30px 66px;border-radius:999px}}"""
    return _shell(body, css, "#fff")


RENDERERS = {"classic": classic, "kinetic": kinetic, "meme": meme,
             "stat": stat, "reveal": reveal}


def _is_stat(headline: str) -> bool:
    first = headline.split()[0] if headline.split() else ""
    return any(c.isdigit() for c in first)


def pick_style(headline: str, index: int, recent: list[str]) -> str:
    """Rotate styles, never repeating the previous one.

    'stat' is gated on a numeric opening word — blowing a non-number up to 300px
    reads as a mistake, which is exactly what happened when the still layouts
    turned "You're" into a giant headline."""
    order = [s for s in STYLES if s != "stat" or _is_stat(headline)]
    if "reveal" in order and not headline.rstrip().endswith("?"):
        # The reveal treatment only makes sense when something is being asked.
        order = [s for s in order if s != "reveal"]
    for offset in range(len(order)):
        cand = order[(index + offset) % len(order)]
        if not recent or cand != recent[-1]:
            return cand
    return order[0]


def render(style: str, headline: str, sub: str, cta: str, audience: str) -> str:
    accent = HONEY if audience == "brand" else PURPLE
    return RENDERERS.get(style, classic)(headline, sub, cta, accent)
