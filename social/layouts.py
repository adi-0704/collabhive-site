"""CollabHive — Instagram post layouts (1080x1350 HTML, rendered to PNG).

Built to match the real brand identity, not a generic template:
    * the actual bee logo (assets/img/logo.png) embedded on every card
    * yellow corner-bracket frames
    * black pill CTA with yellow text
    * navy ink headlines on white, purple + honey accents

Ten visually distinct layouts. generate_calendar.py never reuses one inside a
7-day window, so the grid never looks like the same card with new words.

Feed cards are 1080x1350 (4:5) rather than square: 4:5 occupies more of the
screen in-feed, which is free reach.
"""
from __future__ import annotations

import base64
import pathlib

_ROOT = pathlib.Path(__file__).parent.parent.resolve()
_LOGO_FILE = _ROOT / "assets" / "img" / "logo.png"

# Brand tokens sampled from the logo + site CSS.
HONEY = "#FFD100"
HONEY_D = "#F0B400"
PURPLE = "#9747FF"
INK = "#16203A"          # the navy in the wordmark, not pure black
BLACK = "#111111"
MUTED = "#5A6480"

_FONT = ("https://fonts.googleapis.com/css2?"
         "family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap")

LAYOUTS = ["hero_cta", "bullet_list", "myth_fact", "stat_hero", "statement_frame",
           "quote_card", "question", "split_compare", "checklist", "bold_dark"]

_logo_cache: str | None = None


def _logo_uri() -> str:
    """Embed the logo as a data URI so the HTML renders standalone."""
    global _logo_cache
    if _logo_cache is None:
        if _LOGO_FILE.exists():
            b64 = base64.b64encode(_LOGO_FILE.read_bytes()).decode()
            _logo_cache = f"data:image/png;base64,{b64}"
        else:                                    # never break a render over art
            _logo_cache = ""
    return _logo_cache


def _esc(s) -> str:
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _logo(width: int = 300, center: bool = True, dark_bg: bool = False) -> str:
    """Logo lockup.

    logo.png has a solid white background, so dropping it straight onto a dark
    card renders a white box around the bee. On dark backgrounds we use the
    knockout wordmark instead, which is what the brand does on its own art.
    """
    if dark_bg:
        align = "margin:0 auto;" if center else ""
        return (f'<div style="{align}display:flex;align-items:center;gap:16px;'
                f'font-size:{int(width * 0.17)}px;font-weight:800;color:#fff;'
                f'letter-spacing:-1px">'
                f'<span style="width:{int(width * 0.09)}px;height:{int(width * 0.09)}px;'
                f'border-radius:50%;background:{HONEY};display:inline-block"></span>'
                f'Collab<span style="color:{PURPLE}">Hive</span></div>')
    uri = _logo_uri()
    if not uri:
        return (f'<div style="font-size:40px;font-weight:800;color:{INK};'
                f'text-align:{"center" if center else "left"}">CollabHive</div>')
    align = "margin:0 auto" if center else ""
    return f'<img src="{uri}" style="width:{width}px;display:block;{align}">'


def _pill(text: str = "Link in Bio") -> str:
    return (f'<div style="display:inline-block;background:{BLACK};color:{HONEY};'
            f'font-size:40px;font-weight:800;padding:26px 58px;border-radius:18px;'
            f'letter-spacing:-.5px">{_esc(text)}</div>')


def _brackets() -> str:
    """The yellow corner frame used across the brand's own posts."""
    c = f"4px solid {HONEY}"
    s = "position:absolute;width:150px;height:150px"
    return (f'<div style="{s};top:52px;left:52px;border-top:{c};border-left:{c}"></div>'
            f'<div style="{s};top:52px;right:52px;border-top:{c};border-right:{c}"></div>'
            f'<div style="{s};bottom:52px;left:52px;border-bottom:{c};border-left:{c}"></div>'
            f'<div style="{s};bottom:52px;right:52px;border-bottom:{c};border-right:{c}"></div>')


def _footer_bar() -> str:
    return (f'<div style="position:absolute;left:0;right:0;bottom:0;height:96px;'
            f'background:{INK};display:flex;align-items:center;justify-content:center;'
            f'gap:14px;color:#fff;font-size:26px;font-weight:700;letter-spacing:3px">'
            f'<span style="color:{HONEY}">COLLABHIVE</span>'
            f'<span style="opacity:.55;font-weight:400">INFLUENCER MARKETING AGENCY</span></div>')


def _shell(body: str, bg: str = "#fff") -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="{_FONT}" rel="stylesheet">
<style>
 *{{margin:0;padding:0;box-sizing:border-box}}
 body{{width:1080px;height:1350px;font-family:'Plus Jakarta Sans',sans-serif;
      background:{bg};overflow:hidden;position:relative}}
 .stack{{position:absolute;inset:0;padding:118px 104px;display:flex;
        flex-direction:column;align-items:center;text-align:center}}
 .h1{{font-size:88px;font-weight:800;line-height:1.06;color:{INK};letter-spacing:-3px}}
 .sub{{font-size:36px;font-weight:400;line-height:1.38;color:{MUTED}}}
</style></head><body>{body}</body></html>"""


# ---------------------------------------------------------------- layouts
def hero_cta(headline, sub, **_):
    body = f"""{_brackets()}<div class="stack" style="justify-content:center">
      {_logo(320)}
      <div class="h1" style="margin-top:72px">{_esc(headline)}</div>
      <div class="sub" style="margin-top:34px;max-width:800px">{_esc(sub)}</div>
      <div style="margin-top:74px">{_pill()}</div>
    </div>"""
    return _shell(body)


def bullet_list(headline, sub, **_):
    items = [s.strip() for s in sub.split(".") if s.strip()][:3] or [sub]
    icons = ["🚀", "🤝", "📋", "✨"]
    rows = "".join(
        f"""<div style="display:flex;gap:26px;align-items:center;margin-bottom:40px;
             text-align:left">
             <div style="min-width:76px;height:76px;border-radius:20px;background:{HONEY};
                  display:flex;align-items:center;justify-content:center;font-size:38px">
                  {icons[i % len(icons)]}</div>
             <div style="font-size:40px;font-weight:700;line-height:1.26;color:{INK}">
                  {_esc(t)}</div></div>"""
        for i, t in enumerate(items))
    body = f"""{_brackets()}<div class="stack" style="justify-content:center">
      {_logo(270)}
      <div class="h1" style="margin:56px 0 60px;font-size:74px">{_esc(headline)}</div>
      <div style="width:100%">{rows}</div>
    </div>"""
    return _shell(body)


def myth_fact(headline, sub, **_):
    body = f"""<div class="stack" style="justify-content:center;align-items:flex-start;
         text-align:left">
      {_logo(250, center=False)}
      <div style="display:inline-block;background:#FF4D4F;color:#fff;font-size:25px;
           font-weight:800;padding:12px 30px;border-radius:999px;letter-spacing:3px;
           margin-top:56px">MYTH</div>
      <div class="h1" style="margin-top:26px;font-size:74px">{_esc(headline)}</div>
      <div style="margin:44px 0;height:4px;width:100%;background:{HONEY}"></div>
      <div style="display:inline-block;background:#16A34A;color:#fff;font-size:25px;
           font-weight:800;padding:12px 30px;border-radius:999px;letter-spacing:3px">REALITY</div>
      <div class="sub" style="margin-top:26px;font-size:38px">{_esc(sub)}</div>
    </div>{_footer_bar()}"""
    return _shell(body)


def stat_hero(headline, sub, **_):
    big, rest = headline.split()[0], " ".join(headline.split()[1:])
    body = f"""<div class="stack" style="justify-content:center">
      {_logo(260, dark_bg=True)}
      <div style="font-size:210px;font-weight:800;line-height:.9;color:{HONEY};
           letter-spacing:-9px;margin-top:50px">{_esc(big)}</div>
      <div class="h1" style="margin-top:24px;font-size:68px;color:#fff">{_esc(rest)}</div>
      <div class="sub" style="margin-top:30px;color:rgba(255,255,255,.72);max-width:820px">
           {_esc(sub)}</div>
    </div>"""
    return _shell(body, INK)


def statement_frame(headline, sub, **_):
    deco = "".join(
        f'<div style="position:absolute;{pos};width:{d}px;height:{d}px;border-radius:50%;'
        f'background:{HONEY};opacity:.22"></div>'
        for pos, d in (("top:190px;left:92px", 70), ("top:250px;right:120px", 44),
                       ("bottom:250px;left:140px", 52), ("bottom:190px;right:96px", 78)))
    body = f"""{deco}<div class="stack" style="justify-content:center">
      {_logo(300)}
      <div class="h1" style="margin-top:70px;font-size:92px">{_esc(headline)}</div>
      <div class="sub" style="margin-top:36px;max-width:790px">{_esc(sub)}</div>
    </div>"""
    return _shell(body)


def quote_card(headline, sub, **_):
    body = f"""<div class="stack" style="justify-content:center;align-items:flex-start;
         text-align:left">
      {_logo(250, center=False)}
      <div style="font-size:190px;line-height:.62;color:{PURPLE};font-weight:800;
           height:104px;margin-top:44px">&ldquo;</div>
      <div class="h1" style="font-size:76px;font-weight:700">{_esc(headline)}</div>
      <div style="margin-top:40px;padding-left:28px;border-left:8px solid {HONEY};
           font-size:34px;line-height:1.4;color:{MUTED}">{_esc(sub)}</div>
    </div>{_footer_bar()}"""
    return _shell(body)


def question(headline, sub, **_):
    body = f"""{_brackets()}<div class="stack" style="justify-content:center">
      {_logo(280, dark_bg=True)}
      <div class="h1" style="margin-top:66px;font-size:86px;color:#fff">{_esc(headline)}</div>
      <div class="sub" style="margin-top:38px;color:{HONEY};max-width:780px">{_esc(sub)}</div>
      <div style="margin-top:56px;font-size:27px;font-weight:700;
           color:rgba(255,255,255,.5);letter-spacing:4px">TELL US BELOW &darr;</div>
    </div>"""
    return _shell(body, f"linear-gradient(200deg,{INK} 0%,#2A1B4D 100%)")


def split_compare(headline, sub, **_):
    body = f"""<div style="position:absolute;inset:0;display:flex;flex-direction:column">
      <div style="flex:1;background:{INK};padding:96px;display:flex;flex-direction:column;
           justify-content:center">
        <div style="font-size:25px;font-weight:800;color:{HONEY};letter-spacing:4px;
             margin-bottom:26px">THE PROBLEM</div>
        <div style="font-size:64px;font-weight:800;line-height:1.08;color:#fff;
             letter-spacing:-2px">{_esc(headline)}</div></div>
      <div style="flex:1;background:{HONEY};padding:96px;display:flex;flex-direction:column;
           justify-content:center">
        <div style="font-size:25px;font-weight:800;color:{INK};letter-spacing:4px;
             margin-bottom:26px;opacity:.65">THE FIX</div>
        <div style="font-size:44px;font-weight:600;line-height:1.26;color:{INK}">
             {_esc(sub)}</div></div></div>
      <div style="position:absolute;top:44px;right:48px">{_logo(200, center=False, dark_bg=True)}</div>"""
    return _shell(body)


def checklist(headline, sub, **_):
    items = [s.strip() for s in sub.split(".") if s.strip()][:4] or [sub]
    rows = "".join(
        f"""<div style="display:flex;gap:24px;align-items:flex-start;margin-bottom:32px;
             text-align:left">
             <div style="min-width:58px;height:58px;border-radius:16px;background:{INK};
                  color:{HONEY};font-size:28px;font-weight:800;display:flex;
                  align-items:center;justify-content:center">{i}</div>
             <div style="font-size:37px;font-weight:500;line-height:1.3;color:{INK};
                  padding-top:8px">{_esc(t)}</div></div>"""
        for i, t in enumerate(items, 1))
    body = f"""<div class="stack" style="justify-content:center">
      {_logo(260)}
      <div class="h1" style="margin:52px 0 54px;font-size:70px">{_esc(headline)}</div>
      <div style="width:100%">{rows}</div>
    </div>"""
    return _shell(body, "#FFFBEB")


def bold_dark(headline, sub, **_):
    body = f"""<div class="stack" style="justify-content:center;align-items:flex-start;
         text-align:left">
      {_logo(260, center=False, dark_bg=True)}
      <div style="margin-top:76px;font-size:100px;font-weight:800;line-height:1.02;
           color:#fff;letter-spacing:-3.5px">{_esc(headline)}</div>
      <div style="margin-top:38px;font-size:36px;line-height:1.4;
           color:rgba(255,255,255,.8);max-width:820px">{_esc(sub)}</div>
      <div style="margin-top:64px">{_pill()}</div>
    </div>"""
    return _shell(body, f"linear-gradient(150deg,{PURPLE} 0%,#6B21D6 55%,{INK} 100%)")


RENDERERS = {
    "hero_cta": hero_cta, "bullet_list": bullet_list, "myth_fact": myth_fact,
    "stat_hero": stat_hero, "statement_frame": statement_frame, "quote_card": quote_card,
    "question": question, "split_compare": split_compare, "checklist": checklist,
    "bold_dark": bold_dark,
}


def render_html(layout: str, headline: str, sub: str) -> str:
    return RENDERERS[layout](headline=headline, sub=sub)
