#!/usr/bin/env python3
"""Generate the animated profile header (light + dark) for the GitHub profile README.

Run from the repo root:  python3 tools/make_header.py
Writes assets/header-light.svg and assets/header-dark.svg.

Edit PHRASES to change the typed lines. The chart on the right is a stylised
"time to access" curve per country, shaped after the Pharma Access Atlas medians.
"""
import math
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
SLOT = 5.0            # seconds each phrase owns
TYPE_S = 1.9          # seconds to type a phrase
FS = 24               # typed-line font size
CHAR_W = 14.4         # forced advance per character (textLength)
TYPE_X, TYPE_Y = 100, 252

# Atlas medians (days from EU approval) and long-run plateau of each curve
COUNTRIES = [  # label, median days, plateau, colour key
    ("FR", 212, 0.93, "blue"),
    ("DE", 232, 0.97, "amber"),
    ("EN", 399, 0.86, "pink"),
    ("IT", 522, 0.80, "green"),
]
CH_X0, CH_X1 = 790, 1110   # chart area
CH_Y0, CH_Y1 = 250, 78     # bottom (0%) / top (100%)
DAYS = 900

THEMES = {
    "light": dict(bg="#ffffff", border="#d0d7de", fg="#1f2328", muted="#656d76",
                  faint="#d8dee4", accent="#800000",
                  blue="#2f6fd6", amber="#d99a06", pink="#d6508f", green="#1a7f37"),
    "dark": dict(bg="#0d1117", border="#30363d", fg="#e6edf3", muted="#8d96a0",
                 faint="#30363d", accent="#f47c7c",
                 blue="#58a6ff", amber="#e3b341", pink="#f778ba", green="#3fb950"),
}


def step_curve(median, plateau, phase=0):
    """Rising step curve: share of drugs that reached the milestone by day t."""
    lam = math.log(2) / median
    pts, t = [], 0
    # irregular but deterministic step widths, like real event times
    widths = [38, 55, 30, 70, 45, 60, 35, 80, 50, 65, 90, 75, 110, 95]
    x = lambda d: CH_X0 + (CH_X1 - CH_X0) * d / DAYS
    y = lambda p: CH_Y0 + (CH_Y1 - CH_Y0) * p
    d = [f"M{x(0):.1f},{y(0):.1f}"]
    length, cx, cy = 0.0, x(0), y(0)
    i = 0
    while t < DAYS:
        t = min(DAYS, t + widths[(i + phase) % len(widths)])
        i += 1
        nx = x(t)
        d.append(f"H{nx:.1f}")
        length += nx - cx
        cx = nx
        if t < DAYS:
            # exponential CDF crosses 50 % exactly at the median, capped at the plateau
            p = min(plateau, 1 - math.exp(-lam * t))
            ny = y(p)
            d.append(f"V{ny:.1f}")
            length += abs(ny - cy)
            cy = ny
    return " ".join(d), length, cy


def svg(theme):
    c = THEMES[theme]
    css, body = [], []

    # ---- typed phrases -------------------------------------------------
    cycle = SLOT * len(PHRASES)
    type_pct = TYPE_S / cycle * 100
    hold_pct = (SLOT - 0.45) / cycle * 100
    gone_pct = SLOT / cycle * 100 - 0.01
    phrase_groups = []
    for i, text in enumerate(PHRASES):
        n = len(text)
        w = n * CHAR_W
        delay = 0 if i == 0 else -(cycle - SLOT * i)
        css.append(f"""
  @keyframes show{i} {{ 0% {{opacity:1}} {hold_pct:.2f}% {{opacity:1}} {gone_pct:.2f}% {{opacity:0}} 100% {{opacity:0}} }}
  @keyframes wipe{i} {{ 0% {{transform:scaleX(0); animation-timing-function:steps({n},end)}} {type_pct:.2f}% {{transform:scaleX(1)}} 100% {{transform:scaleX(1)}} }}
  @keyframes caret{i} {{ 0% {{transform:translateX(0px); animation-timing-function:steps({n},end)}} {type_pct:.2f}% {{transform:translateX({w:.1f}px)}} 100% {{transform:translateX({w:.1f}px)}} }}
  .p{i} {{ animation: show{i} {cycle}s linear {delay}s infinite; }}
  .p{i} .clip {{ animation: wipe{i} {cycle}s linear {delay}s infinite; }}
  .p{i} .caret {{ animation: caret{i} {cycle}s linear {delay}s infinite; }}""")
        start_hidden = ' opacity="0"' if i else ""
        phrase_groups.append(f"""
    <g class="p{i}"{start_hidden}>
      <clipPath id="c{i}"><rect class="clip" x="0" y="-30" width="{w + 4:.1f}" height="44"/></clipPath>
      <text class="mono" x="0" y="0" textLength="{w:.1f}" font-size="{FS}" fill="{c['fg']}" clip-path="url(#c{i})">{text}</text>
      <g class="caret" transform="translate({w:.1f},0)"><rect class="blink" x="3" y="-21" width="11" height="26" rx="1.5" fill="{c['accent']}"/></g>
    </g>""")

    # ---- chart ----------------------------------------------------------
    curves, ys = [], []
    for k, (lab, med, plat, key) in enumerate(COUNTRIES):
        path, length, end_y = step_curve(med, plat, phase=3 * k)
        dl = 0.5 + 0.35 * k
        css.append(f"""
  .k{k} {{ stroke-dasharray:{length:.0f}; stroke-dashoffset:{length:.0f}; animation: draw 2.4s cubic-bezier(.3,.7,.2,1) {dl:.2f}s both; }}
  .l{k} {{ animation: fade .6s ease-out {dl + 2.0:.2f}s both; }}""")
        curves.append(f'<path class="k{k}" d="{path}" fill="none" stroke="{c[key]}" stroke-width="3.2" stroke-linejoin="round"/>')
        ys.append(end_y + 4)

    # nudge overlapping end labels apart
    order = sorted(range(len(ys)), key=lambda j: ys[j])
    for a, b in zip(order, order[1:]):
        if ys[b] - ys[a] < 14:
            ys[b] = ys[a] + 14
    labels = [f'<text class="mono l{k}" x="{CH_X1 + 10}" y="{ys[k]:.1f}" font-size="12" fill="{c[key]}">{lab}</text>'
              for k, (lab, _m, _p, key) in enumerate(COUNTRIES)]

    mid_y = CH_Y0 + (CH_Y1 - CH_Y0) * 0.5
    chart = f"""
  <g class="chart">
    <line x1="{CH_X0}" y1="{CH_Y1 - 8}" x2="{CH_X0}" y2="{CH_Y0}" stroke="{c['faint']}" stroke-width="1.5"/>
    <line x1="{CH_X0}" y1="{CH_Y0}" x2="{CH_X1}" y2="{CH_Y0}" stroke="{c['faint']}" stroke-width="1.5"/>
    <line x1="{CH_X0}" y1="{mid_y:.1f}" x2="{CH_X1}" y2="{mid_y:.1f}" stroke="{c['faint']}" stroke-width="1" stroke-dasharray="4 5"/>
    <text class="mono" x="{CH_X0 - 8}" y="{mid_y + 4:.1f}" font-size="11" fill="{c['muted']}" text-anchor="end">50%</text>
    {chr(10).join('    ' + p for p in curves)}
    {chr(10).join('    ' + l for l in labels)}
    <text class="mono" x="{CH_X0}" y="{CH_Y0 + 24}" font-size="11.5" fill="{c['muted']}">days from EU approval to national access →</text>
  </g>"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
  <title id="t">Luca Murri</title>
  <desc id="d">Master in Management, Chicago Booth, Class of 2027. Business strategist who builds. Animated chart of time to drug access in France, Germany, England and Italy.</desc>
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
  @media (prefers-reduced-motion: reduce) {{
    *, .clip, .caret, .blink {{ animation: none !important; }}
    [class^="k"] {{ stroke-dashoffset: 0 !important; }}
    .p1, .p2 {{ opacity: 0 !important; }}
  }}
  </style>

  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="{c['bg']}" stroke="{c['border']}" stroke-width="1.5"/>

  <text class="sans eyebrow" x="64" y="86" font-size="14" font-weight="600" letter-spacing="2.2" fill="{c['accent']}">{EYEBROW}</text>
  <text class="serif name" x="60" y="168" font-size="76" font-weight="700" fill="{c['fg']}" letter-spacing="-1">{NAME}</text>
  <rect class="rule" x="64" y="190" width="72" height="4" rx="2" fill="{c['accent']}"/>

  <text class="mono" x="64" y="{TYPE_Y}" font-size="{FS}" font-weight="700" fill="{c['accent']}">›</text>
  <g transform="translate({TYPE_X},{TYPE_Y})">{''.join(phrase_groups)}
  </g>
{chart}
</svg>
"""


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (OUT / f"header-{theme}.svg").write_text(svg(theme), encoding="utf-8")
        print("wrote", OUT / f"header-{theme}.svg")
