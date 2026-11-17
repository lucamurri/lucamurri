#!/usr/bin/env python3
"""Generate the animated profile header (light + dark) for the GitHub profile README.

Run from the repo root:  python3 tools/make_header.py
Writes assets/header-light.svg and assets/header-dark.svg.

Edit PHRASES to change the typed lines. The artwork on the right is a stylised
Chicago skyline (Willis Tower, the John Hancock Center, Trump Tower, Aon Center,
Two Prudential Plaza, 311 South Wacker, Marina City) over Lake Michigan: it is
drawn as blueprint outlines, then filled in and lit. Edit the `back` and `front`
lists in skyline() to change the buildings.
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

W, H = 1200, 320
EYEBROW = "MASTER IN MANAGEMENT  ·  CHICAGO BOOTH  ·  CLASS OF 2027"
NAME = "Luca Murri"
PHRASES = [
    "Business strategist who builds.",
    "From business question to shipped product.",
    "Strategy · Product · Healthcare · AI",
]
SLOT, TYPE_S, FS, CHAR_W = 5.0, 1.9, 24, 14.4
TYPE_X, TYPE_Y = 100, 252

THEMES = {
    "light": dict(bg="#ffffff", border="#d0d7de", fg="#1f2328", muted="#656d76",
                  faint="#d8dee4", accent="#800000",
                  back="#eef1f4", mid="#d5dce3", edge="#b3bdc7", icon="#2d333b", brace="#6e7781",
                  lit="#f2c14e", glass="#ffffff", red="#e5534b", sun=0.085, refl=0.20,
                  stars=False),
    "dark": dict(bg="#0d1117", border="#30363d", fg="#e6edf3", muted="#8d96a0",
                 faint="#30363d", accent="#f47c7c",
                 back="#141920", mid="#1f252d", edge="#3a424c", icon="#2f363f", brace="#5c6670",
                 lit="#e3b341", glass="#e3b341", red="#ff6a69", sun=0.10, refl=0.55,
                 stars=True),
}


# --------------------------------------------------------------------------
# Chicago skyline: drawn as a blueprint, then built and lit
# --------------------------------------------------------------------------
SX0, G = 774, 234          # left edge of the skyline, waterline

def stepped(x, cols):
    pts, cx = [(x, 0)], x
    for w, h in cols:
        pts += [(cx, h), (cx + w, h)]
        cx += w
    return pts + [(cx, 0)]

def mirror_tiers(x, tiers):
    """Centred setbacks: tiers = [(width, top height), ...] from the base up."""
    full = tiers[0][0]
    left, right = [(x, 0)], []
    prev_h = 0
    for w, h in tiers:
        inset = (full - w) / 2
        left += [(x + inset, prev_h), (x + inset, h)]
        right = [(x + full - inset, h), (x + full - inset, prev_h)] + right
        prev_h = h
    return left + right + [(x + full, 0)]

def arc_top(x, w, h, cw, ch, r):
    """Body to h, narrower crown to ch, then a semicircle of radius r."""
    i = (w - cw) / 2
    pts = [(x, 0), (x, h), (x + i, h), (x + i, ch)]
    cx = x + w / 2
    for k in range(9):
        a = math.pi - math.pi * k / 8
        pts.append((cx + r * math.cos(a), ch + r * math.sin(a)))
    return pts + [(x + w - i, ch), (x + w - i, h), (x + w, h), (x + w, 0)]

def P(x, h):
    return SX0 + x, G - h

def path_d(pts):
    return "M" + " L".join(f"{P(x, h)[0]:.1f},{P(x, h)[1]:.1f}" for x, h in pts) + " Z"

def perim(pts):
    return sum(math.dist(pts[i - 1], pts[i]) for i in range(len(pts)))

def skyline(c, theme):
    rnd = random.Random(11)
    css, out = [], []
    # back layer: plain towers that rise
    back = [(0, 22, 86), (40, 18, 104), (60, 18, 120), (114, 16, 96), (150, 20, 126),
            (192, 16, 110), (206, 20, 92), (262, 18, 120), (294, 16, 132), (318, 16, 98),
            (354, 20, 76), (370, 14, 58)]
    # front layer: (name, outline points, tone)
    WH = 152
    front = [
        ("generic", stepped(8, [(22, 64)]), "mid"),
        ("hancock", [(22, 0), (28, 124), (52, 124), (58, 0)], "icon"),
        ("generic", stepped(64, [(22, 82)]), "mid"),
        ("trump", mirror_tiers(90, [(30, 78), (26, 104), (21, 120), (15, 132)]), "mid"),
        ("aon", stepped(126, [(26, 140)]), "mid"),
        ("pru", [(166, 0), (166, 110), (177, 131), (188, 110), (188, 0)], "mid"),
        ("generic", stepped(196, [(26, 74)]), "mid"),
        ("willis", stepped(228, [(10, round(WH * .56)), (20, WH), (10, round(WH * .8))]), "icon"),
        ("wacker", arc_top(276, 24, 102, 16, 110, 8), "mid"),
        ("generic", stepped(304, [(18, 86)]), "mid"),
        ("marina", stepped(326, [(12, 58)]), "mid"),
        ("marina", stepped(342, [(12, 58)]), "mid"),
        ("generic", stepped(358, [(22, 44)]), "mid"),
    ]
    # extras: thin lines (antennas, spires, bracing, stripes)
    lines, lights, spires = [], [], []
    def line(x1, h1, x2, h2, color, w=1.0, cls=""):
        a, b = P(x1, h1), P(x2, h2)
        lines.append((a, b, color, w, cls))
    for name, pts, tone in front:
        if name == "hancock":
            for x, top in ((32, 156), (48, 150)):
                spires.append((x, 124, top)); lights.append((x, top))
            L = lambda h: 22 + 6 * h / 124
            R = lambda h: 58 - 6 * h / 124
            hs = [6 + 112 * k / 5 for k in range(6)]
            for a, b in zip(hs, hs[1:]):
                line(L(a), a, R(b), b, c["brace"], 1.1, "br")
                line(R(a), a, L(b), b, c["brace"], 1.1, "br")
        if name == "willis":
            for x, top in ((241, WH + 38), (255, WH + 33)):
                spires.append((x, WH, top)); lights.append((x, top))
        if name == "trump":
            spires.append((105, 132, 172))
        if name == "pru":
            spires.append((177, 131, 150))
        if name == "aon":
            for k in range(1, 8):
                x = 126 + 26 * k / 8
                line(x, 2, x, 138, c["edge"], .8, "br")
        if name == "marina":
            x0 = pts[0][0]
            for hh in range(6, 56, 4):
                line(x0 + 1, hh, x0 + 11, hh, c["edge"], 1.0, "br")

    # light: a soft sun disc behind the city; dark: a small moon with a halo
    out.append(f'<clipPath id="above"><rect x="{SX0 - 30}" y="0" width="460" height="{G}"/></clipPath>')
    if theme == "light":
        out.append(f'<g clip-path="url(#above)"><circle class="sun" cx="{SX0 + 206}" cy="{G - 58}" r="96" fill="{c["accent"]}" fill-opacity="{c["sun"]}"/></g>')
    else:
        mx, my = SX0 + 352, 62
        out.append(f'<g class="sun"><circle cx="{mx}" cy="{my}" r="26" fill="{c["fg"]}" fill-opacity=".05"/>'
                   f'<circle cx="{mx}" cy="{my}" r="17" fill="{c["fg"]}" fill-opacity=".07"/>'
                   f'<circle cx="{mx}" cy="{my}" r="10.5" fill="#e9eef4"/>'
                   f'<circle cx="{mx + 4.5}" cy="{my - 3}" r="9" fill="{c["bg"]}"/></g>')

    if c["stars"]:
        for k in range(18):
            x = SX0 + rnd.uniform(0, 320); y = rnd.uniform(30, 100)
            r = rnd.choice((0.8, 1.0, 1.2))
            dl = rnd.uniform(0, 4)
            out.append(f'<circle class="star" style="animation-delay:{dl:.2f}s" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c["fg"]}"/>')

    # reflection (static fills, mirrored and squashed), revealed after the build
    refl = [path_d(stepped(x, [(w, h)])) for x, w, h in back] + [path_d(p) for _n, p, _t in front]
    out.append(f"""<mask id="fadeR"><rect x="{SX0 - 10}" y="{G}" width="420" height="70" fill="url(#gR)"/></mask>
  <linearGradient id="gR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <g class="refl" mask="url(#fadeR)"><g transform="translate(0,{G}) scale(1,-0.42) translate(0,{-G})" fill="{c['icon']}" fill-opacity="{c['refl']}">{''.join(f'<path d="{d}"/>' for d in refl)}</g></g>""")
    # water: bg-coloured streaks give the reflection a rippled look, short breaks drift across
    for k in range(16):
        y = G + 3 + k * 3.4
        out.append(f'<line x1="{SX0 - 10}" y1="{y:.1f}" x2="{SX0 + 400}" y2="{y:.1f}" stroke="{c["bg"]}" stroke-width="{1.1 + k * 0.05:.2f}"/>')
    for k in range(7):
        y = G + 5 + k * 6.2
        dash = f"{4 + k % 3 * 2} {38 + k * 9}"
        dur = 6 + k * 1.3
        d = -1 if k % 2 else 1
        css.append(f".w{k} {{ stroke-dasharray:{dash}; animation: wave{k} {dur:.1f}s linear infinite; }}"
                   f"@keyframes wave{k} {{ to {{ stroke-dashoffset:{d * 240}; }} }}")
        out.append(f'<line class="w{k}" x1="{SX0 - 10}" y1="{y:.1f}" x2="{SX0 + 400}" y2="{y:.1f}" stroke="{c["bg"]}" stroke-width="2.4"/>')

    # back towers rise
    for k, (x, w, h) in enumerate(back):
        out.append(f'<path class="rise" style="animation-delay:{0.25 + 0.06 * k:.2f}s" d="{path_d(stepped(x, [(w, h)]))}" fill="{c["back"]}"/>')

    # front towers: blueprint stroke, then fill
    for k, (name, pts, tone) in enumerate(front):
        dl = 0.35 + 0.09 * k
        L = perim(pts)
        d = path_d(pts)
        out.append(f'<path class="fill" style="animation-delay:{dl + 1.05:.2f}s" d="{d}" fill="{c[tone]}"/>')
        out.append(f'<path class="ol" style="stroke-dasharray:{L:.0f};stroke-dashoffset:{L:.0f};animation-delay:{dl:.2f}s,{dl + 1.05:.2f}s" d="{d}" fill="none" stroke="{c["accent"]}" stroke-width="1.3" stroke-linejoin="round"/>')
    # spires and antennas
    for k, (x, h0, h1) in enumerate(spires):
        (x1, y1), (_x2, y2) = P(x, h0), P(x, h1)
        L = y1 - y2
        out.append(f'<line class="sp" style="stroke-dasharray:{L:.0f};stroke-dashoffset:{L:.0f};animation-delay:{1.6 + 0.08 * k:.2f}s" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x1:.1f}" y2="{y2:.1f}" stroke="{c["icon"] if theme == "light" else c["edge"]}" stroke-width="1.8" stroke-linecap="round"/>')
    for (a, b, color, w, cls) in lines:
        out.append(f'<line class="{cls}" x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{color}" stroke-width="{w}"/>')

    # windows: sparse, some twinkle
    wins = []
    for name, pts, tone in front:
        if name in ("marina",):
            continue
        xs = [p[0] for p in pts]; x0, x1 = min(xs), max(xs)
        top = sorted(set(p[1] for p in pts))[-1]
        if name == "hancock":
            continue
        body_top = {"willis": round(WH * .56), "trump": 78, "pru": 110, "wacker": 102}.get(name, top)
        p = 0.26 if tone == "icon" else 0.10
        for hh in range(8, int(body_top) - 6, 6):
            for xx in range(int(x0) + 3, int(x1) - 3, 4):
                if rnd.random() < p:
                    wins.append((xx, hh, tone))
        if name == "willis":
            for hh in range(body_top + 4, WH - 6, 6):
                for xx in range(241, 256, 4):
                    if rnd.random() < p:
                        wins.append((xx, hh, tone))
    # Hancock windows follow the taper
    for hh in range(10, 118, 6):
        for xx in range(int(22 + 6 * hh / 124) + 4, int(58 - 6 * hh / 124) - 4, 4):
            if rnd.random() < 0.22:
                wins.append((xx, hh, "icon"))
    for (x, h, tone) in wins:
        X, Y = P(x, h)
        col = c["lit"] if tone == "icon" or theme == "dark" else c["glass"]
        tw = rnd.random() < 0.35
        dl = 2.3 + rnd.uniform(0, 1.2)
        cls = "win tw" if tw else "win"
        dur = rnd.uniform(3, 7)
        style = f"animation-delay:{dl:.2f}s" + (f",{dl + rnd.uniform(0, 5):.2f}s;animation-duration:.5s,{dur:.1f}s" if tw else "")
        out.append(f'<rect class="{cls}" style="{style}" x="{X:.1f}" y="{Y - 2.4:.1f}" width="1.8" height="2.4" fill="{col}"/>')

    # aircraft warning lights
    for k, (x, h) in enumerate(lights):
        X, Y = P(x, h)
        out.append(f'<circle class="lamp" style="animation-delay:{2.6 + 0.5 * k:.2f}s,{2.6 + 0.5 * k:.2f}s" cx="{X:.1f}" cy="{Y:.1f}" r="1.9" fill="{c["red"]}"/>')

    out.append(f'<line x1="{SX0 - 10}" y1="{G + .5}" x2="{SX0 + 400}" y2="{G + .5}" stroke="{c["border"]}" stroke-width="1"/>')
    out.append(f'<text class="mono cap" x="{SX0 + 390}" y="{G + 64}" font-size="11.5" fill="{c["muted"]}" text-anchor="end">CHICAGO, IL  ·  41.88° N  87.63° W</text>')

    css.append(f"""
  .sun {{ animation: sunrise 1.8s cubic-bezier(.3,.7,.2,1) .1s both; }}
  @keyframes sunrise {{ from {{ transform: translateY(46px); opacity: 0; }} to {{ transform: none; opacity: 1; }} }}
  .rise {{ transform-box: fill-box; transform-origin: 50% 100%; animation: rise .9s cubic-bezier(.3,.7,.2,1) both; }}
  @keyframes rise {{ from {{ transform: scaleY(0); }} to {{ transform: none; }} }}
  .ol {{ animation-name: draw, settle; animation-duration: 1.2s, .8s; animation-timing-function: cubic-bezier(.3,.7,.2,1), ease-out; animation-fill-mode: both, both; }}
  @keyframes settle {{ to {{ stroke: {c['edge']}; stroke-opacity: {0.9 if theme == 'light' else 0.8}; }} }}
  .fill {{ animation: fade .8s ease-out both; }}
  .sp {{ animation: draw .7s ease-out both; }}
  .br {{ animation: fadeonly .8s ease-out 1.8s both; }}
  .win {{ animation: fadeonly .5s ease-out both; }}
  .win.tw {{ animation-name: fadeonly, twinkle; animation-iteration-count: 1, infinite; animation-timing-function: ease-out, steps(1, end); animation-fill-mode: both, none; }}
  @keyframes twinkle {{ 0% {{ opacity: 1; }} 40% {{ opacity: .15; }} 55% {{ opacity: 1; }} }}
  .lamp {{ animation-name: fadeonly, lamp; animation-duration: .3s, 2.4s; animation-timing-function: ease-out, linear; animation-iteration-count: 1, infinite; animation-fill-mode: both, none; }}
  @keyframes lamp {{ 0%, 82% {{ opacity: .15; }} 88%, 94% {{ opacity: 1; }} 100% {{ opacity: .15; }} }}
  .star {{ animation: star 4s ease-in-out infinite; }}
  @keyframes star {{ 0%, 100% {{ opacity: .25; }} 50% {{ opacity: .9; }} }}
  .refl {{ animation: fadeonly 1.2s ease-out 2.2s both; }}
  .cap {{ animation: fade .6s ease-out 2.6s both; }}
  @keyframes fadeonly {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}""")
    reduce = ".ol { stroke-dashoffset: 0 !important; stroke: " + c["edge"] + " !important; } .sp { stroke-dashoffset: 0 !important; }"
    desc = "Line drawing of the Chicago skyline, with Willis Tower and the John Hancock Center, built up and lit at night over Lake Michigan."
    return "".join(css), "\n  ".join(out), reduce, desc


def svg(theme):
    c = THEMES[theme]
    css = []
    cycle = SLOT * len(PHRASES)
    type_pct = TYPE_S / cycle * 100
    hold_pct = (SLOT - 0.45) / cycle * 100
    gone_pct = SLOT / cycle * 100 - 0.01
    groups = []
    for i, text in enumerate(PHRASES):
        n = len(text); w = n * CHAR_W
        delay = 0 if i == 0 else -(cycle - SLOT * i)
        css.append(f"""
  @keyframes show{i} {{ 0% {{opacity:1}} {hold_pct:.2f}% {{opacity:1}} {gone_pct:.2f}% {{opacity:0}} 100% {{opacity:0}} }}
  @keyframes wipe{i} {{ 0% {{transform:scaleX(0); animation-timing-function:steps({n},end)}} {type_pct:.2f}% {{transform:scaleX(1)}} 100% {{transform:scaleX(1)}} }}
  @keyframes caret{i} {{ 0% {{transform:translateX(0px); animation-timing-function:steps({n},end)}} {type_pct:.2f}% {{transform:translateX({w:.1f}px)}} 100% {{transform:translateX({w:.1f}px)}} }}
  .p{i} {{ animation: show{i} {cycle}s linear {delay}s infinite; }}
  .p{i} .clip {{ animation: wipe{i} {cycle}s linear {delay}s infinite; }}
  .p{i} .caret {{ animation: caret{i} {cycle}s linear {delay}s infinite; }}""")
        hidden = ' opacity="0"' if i else ""
        groups.append(f"""
    <g class="p{i}"{hidden}>
      <clipPath id="c{i}"><rect class="clip" x="0" y="-30" width="{w + 4:.1f}" height="44"/></clipPath>
      <text class="mono" x="0" y="0" textLength="{w:.1f}" font-size="{FS}" fill="{c['fg']}" clip-path="url(#c{i})">{text}</text>
      <g class="caret" transform="translate({w:.1f},0)"><rect class="blink" x="3" y="-21" width="11" height="26" rx="1.5" fill="{c['accent']}"/></g>
    </g>""")
    art_css, art_svg, reduce, desc = skyline(c, theme)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
  <title id="t">Luca Murri</title>
  <desc id="d">Master in Management, Chicago Booth, Class of 2027. Business strategist who builds. {desc}</desc>
  <style>
  .serif {{ font-family: Charter, 'Iowan Old Style', Georgia, Cambria, 'Times New Roman', serif; }}
  .sans  {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif; }}
  .mono  {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace; }}
  @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
  @keyframes fade {{ from {{ opacity: 0; transform: translateY(4px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
  @keyframes blink {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: 0; }} }}
  .eyebrow {{ animation: fade .7s ease-out .1s both; }}
  .name {{ animation: fade .8s ease-out .25s both; }}
  .rule {{ transform-origin: 64px 0; animation: grow .9s cubic-bezier(.3,.7,.2,1) .6s both; }}
  .blink {{ animation: blink 1.05s linear infinite; }}{''.join(css)}
  {art_css}
  @media (prefers-reduced-motion: reduce) {{
    *, .clip, .caret, .blink {{ animation: none !important; }}
    .p1, .p2 {{ opacity: 0 !important; }}
    {reduce}
  }}
  </style>

  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="{c['bg']}" stroke="{c['border']}" stroke-width="1.5"/>
  <text class="sans eyebrow" x="64" y="86" font-size="14" font-weight="600" letter-spacing="2.2" fill="{c['accent']}">{EYEBROW}</text>
  <text class="serif name" x="60" y="168" font-size="76" font-weight="700" fill="{c['fg']}" letter-spacing="-1">{NAME}</text>
  <rect class="rule" x="64" y="190" width="72" height="4" rx="2" fill="{c['accent']}"/>
  <text class="mono" x="64" y="{TYPE_Y}" font-size="{FS}" font-weight="700" fill="{c['accent']}">›</text>
  <g transform="translate({TYPE_X},{TYPE_Y})">{''.join(groups)}
  </g>
  {art_svg}
</svg>
"""


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (OUT / f"header-{theme}.svg").write_text(svg(theme), encoding="utf-8")
        print("wrote", OUT / f"header-{theme}.svg")
