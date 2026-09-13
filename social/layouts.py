"""CollabHive — Instagram post layouts (1080x1350 HTML, rendered to PNG).

Ten visually distinct layouts. The calendar generator never uses the same
layout twice within a 7-day window, so the grid never looks like a template
farm — which is the whole point.

Theme is lifted from assets/css (the live site):
    honey  hsl(45,100%,50%)   purple hsl(263,70%,58%)   ink hsl(0,0%,8%)
    font   Plus Jakarta Sans
"""

HONEY = "hsl(45,100%,50%)"
HONEY_D = "hsl(45,100%,40%)"
PURPLE = "hsl(263,70%,58%)"
PURPLE_D = "hsl(263,70%,48%)"
INK = "hsl(0,0%,8%)"
MUTED = "hsl(0,0%,45%)"

_FONT = ("https://fonts.googleapis.com/css2?"
         "family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap")

LAYOUTS = ["bold_statement", "myth_fact", "stat_hero", "checklist", "quote_card",
           "question", "tip_card", "split_compare", "minimal_type", "gradient_band"]


def _esc(s) -> str:
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _shell(body: str, bg: str, extra_css: str = "") -> str:
    """Common 1080x1350 canvas."""
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="{_FONT}" rel="stylesheet">
<style>
 *{{margin:0;padding:0;box-sizing:border-box}}
 body{{width:1080px;height:1350px;font-family:'Plus Jakarta Sans',sans-serif;
      background:{bg};overflow:hidden;position:relative}}
 .pad{{position:absolute;inset:0;padding:96px 88px;display:flex;
      flex-direction:column;justify-content:center}}
 .brand{{position:absolute;left:88px;bottom:72px;display:flex;align-items:center;gap:14px;
        font-size:30px;font-weight:800;letter-spacing:-.5px}}
 .dot{{width:16px;height:16px;border-radius:50%;background:{HONEY}}}
 {extra_css}
</style></head><body>{body}</body></html>"""


def _mark(color=INK) -> str:
    return f'<div class="brand" style="color:{color}"><span class="dot"></span>CollabHive</div>'


# ---------------------------------------------------------------- layouts
def bold_statement(headline, sub, **_):
    body = f"""<div class="pad">
      <div style="font-size:104px;font-weight:800;line-height:1.02;color:#fff;
                  letter-spacing:-3.5px">{_esc(headline)}</div>
      <div style="margin-top:40px;font-size:36px;font-weight:400;line-height:1.4;
                  color:rgba(255,255,255,.82)">{_esc(sub)}</div>
    </div>{_mark('#fff')}"""
    return _shell(body, f"linear-gradient(150deg,{PURPLE} 0%,{PURPLE_D} 55%,{INK} 100%)")


def myth_fact(headline, sub, **_):
    body = f"""<div class="pad">
      <div style="display:inline-block;background:#ff4d4f;color:#fff;font-size:26px;
           font-weight:800;padding:12px 26px;border-radius:999px;align-self:flex-start;
           letter-spacing:2px">MYTH</div>
      <div style="margin-top:30px;font-size:78px;font-weight:800;line-height:1.08;
           color:{INK};letter-spacing:-2.5px">{_esc(headline)}</div>
      <div style="margin:52px 0;height:3px;background:hsl(0,0%,90%)"></div>
      <div style="display:inline-block;background:#16a34a;color:#fff;font-size:26px;
           font-weight:800;padding:12px 26px;border-radius:999px;align-self:flex-start;
           letter-spacing:2px">REALITY</div>
      <div style="margin-top:30px;font-size:40px;font-weight:500;line-height:1.38;
           color:{MUTED}">{_esc(sub)}</div>
    </div>{_mark()}"""
    return _shell(body, "#fff")


def stat_hero(headline, sub, **_):
    big = headline.split()[0]
    rest = " ".join(headline.split()[1:])
    body = f"""<div class="pad" style="justify-content:center">
      <div style="font-size:230px;font-weight:800;line-height:.86;color:{HONEY};
           letter-spacing:-10px">{_esc(big)}</div>
      <div style="margin-top:34px;font-size:66px;font-weight:800;line-height:1.1;
           color:#fff;letter-spacing:-2px">{_esc(rest)}</div>
      <div style="margin-top:34px;font-size:34px;font-weight:400;line-height:1.42;
           color:rgba(255,255,255,.7);max-width:800px">{_esc(sub)}</div>
    </div>{_mark('#fff')}"""
    return _shell(body, INK)


def checklist(headline, sub, **_):
    items = [s.strip() for s in sub.split(".") if s.strip()][:4] or [sub]
    rows = "".join(
        f"""<div style="display:flex;gap:22px;align-items:flex-start;margin-bottom:30px">
             <div style="min-width:52px;height:52px;border-radius:14px;background:{HONEY};
                  color:{INK};font-size:28px;font-weight:800;display:flex;
                  align-items:center;justify-content:center">{i}</div>
             <div style="font-size:36px;font-weight:500;line-height:1.34;color:{INK};
                  padding-top:6px">{_esc(t)}</div></div>"""
        for i, t in enumerate(items, 1))
    body = f"""<div class="pad">
      <div style="font-size:72px;font-weight:800;line-height:1.08;color:{INK};
           letter-spacing:-2.5px;margin-bottom:56px">{_esc(headline)}</div>{rows}
    </div>{_mark()}"""
    return _shell(body, "hsl(45,100%,97%)")


def quote_card(headline, sub, **_):
    body = f"""<div class="pad">
      <div style="font-size:200px;line-height:.6;color:{PURPLE};font-weight:800;
           height:110px">&ldquo;</div>
      <div style="font-size:80px;font-weight:700;line-height:1.14;color:{INK};
           letter-spacing:-2.5px">{_esc(headline)}</div>
      <div style="margin-top:44px;padding-left:26px;border-left:6px solid {HONEY};
           font-size:34px;font-weight:400;line-height:1.4;color:{MUTED}">{_esc(sub)}</div>
    </div>{_mark()}"""
    return _shell(body, "#fff")


def question(headline, sub, **_):
    body = f"""<div class="pad" style="justify-content:center;text-align:center;
         align-items:center">
      <div style="font-size:92px;font-weight:800;line-height:1.06;color:#fff;
           letter-spacing:-3px">{_esc(headline)}</div>
      <div style="margin-top:44px;font-size:36px;font-weight:400;line-height:1.4;
           color:{HONEY};max-width:780px">{_esc(sub)}</div>
      <div style="margin-top:60px;font-size:28px;font-weight:600;color:rgba(255,255,255,.55);
           letter-spacing:3px">TELL US BELOW &darr;</div>
    </div>{_mark('#fff')}"""
    return _shell(body, f"linear-gradient(200deg,{INK} 0%,hsl(263,40%,18%) 100%)")


def tip_card(headline, sub, **_):
    body = f"""<div class="pad">
      <div style="display:inline-block;align-self:flex-start;background:{PURPLE};
           color:#fff;font-size:24px;font-weight:800;padding:12px 26px;
           border-radius:999px;letter-spacing:2px">QUICK TIP</div>
      <div style="margin-top:40px;font-size:84px;font-weight:800;line-height:1.06;
           color:{INK};letter-spacing:-3px">{_esc(headline)}</div>
      <div style="margin-top:40px;font-size:38px;font-weight:400;line-height:1.4;
           color:{MUTED}">{_esc(sub)}</div>
      <div style="margin-top:54px;height:10px;width:180px;border-radius:99px;
           background:{HONEY}"></div>
    </div>{_mark()}"""
    return _shell(body, "#fff")


def split_compare(headline, sub, **_):
    body = f"""<div style="position:absolute;inset:0;display:flex;flex-direction:column">
      <div style="flex:1;background:{INK};padding:88px;display:flex;
           flex-direction:column;justify-content:center">
        <div style="font-size:26px;font-weight:800;color:{HONEY};letter-spacing:3px;
             margin-bottom:26px">THE PROBLEM</div>
        <div style="font-size:64px;font-weight:800;line-height:1.1;color:#fff;
             letter-spacing:-2px">{_esc(headline)}</div>
      </div>
      <div style="flex:1;background:{HONEY};padding:88px;display:flex;
           flex-direction:column;justify-content:center">
        <div style="font-size:26px;font-weight:800;color:{INK};letter-spacing:3px;
             margin-bottom:26px;opacity:.6">THE FIX</div>
        <div style="font-size:44px;font-weight:600;line-height:1.28;color:{INK}">
             {_esc(sub)}</div>
      </div></div>
      <div class="brand" style="color:{INK}"><span class="dot" style="background:{INK}"></span>CollabHive</div>"""
    return _shell(body, "#fff")


def minimal_type(headline, sub, **_):
    body = f"""<div class="pad">
      <div style="font-size:30px;font-weight:800;color:{PURPLE};letter-spacing:4px;
           margin-bottom:44px">COLLABHIVE</div>
      <div style="font-size:88px;font-weight:300;line-height:1.12;color:{INK};
           letter-spacing:-3px">{_esc(headline)}</div>
      <div style="margin-top:48px;font-size:34px;font-weight:400;line-height:1.45;
           color:{MUTED};max-width:820px">{_esc(sub)}</div>
    </div>
    <div style="position:absolute;right:-120px;top:-120px;width:460px;height:460px;
         border-radius:50%;background:{HONEY};opacity:.16"></div>{_mark()}"""
    return _shell(body, "hsl(0,0%,98%)")


def gradient_band(headline, sub, **_):
    body = f"""<div class="pad">
      <div style="font-size:88px;font-weight:800;line-height:1.06;color:{INK};
           letter-spacing:-3px">{_esc(headline)}</div>
      <div style="margin-top:46px;background:linear-gradient(135deg,{HONEY},{HONEY_D});
           padding:44px;border-radius:26px">
        <div style="font-size:38px;font-weight:600;line-height:1.34;color:{INK}">
             {_esc(sub)}</div></div>
    </div>{_mark()}"""
    return _shell(body, "#fff")


RENDERERS = {
    "bold_statement": bold_statement, "myth_fact": myth_fact, "stat_hero": stat_hero,
    "checklist": checklist, "quote_card": quote_card, "question": question,
    "tip_card": tip_card, "split_compare": split_compare,
    "minimal_type": minimal_type, "gradient_band": gradient_band,
}


def render_html(layout: str, headline: str, sub: str) -> str:
    return RENDERERS[layout](headline=headline, sub=sub)
