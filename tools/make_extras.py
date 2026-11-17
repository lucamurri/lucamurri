#!/usr/bin/env python3
"""Generate the profile README's buttons, stat tiles and the snake-replacement options.

Run from the repo root:  python3 tools/make_extras.py
Writes light + dark SVGs into assets/: contact buttons, stat cards,
the How-I-work pipeline and the shipping-log timeline.

What to edit:
  EVENTS   shipping-log milestones (date, title, subtitle, project colour)
  STATS    the four stat cards (number and two label lines)
  STAGES   the five How-I-work steps
  BUTTONS  contact button labels

Optional: pass a JSON file of [{"date": "YYYY-MM-DD", "count": n}, ...]
to also draw the unused 3D commit skyline (assets/skyline-*.svg).
"""
import datetime as dt
import json
import math
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
SERIF = "Charter, 'Iowan Old Style', Georgia, Cambria, 'Times New Roman', serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "light": dict(bg="#ffffff", card="#ffffff", border="#d0d7de", fg="#1f2328", muted="#656d76",
                  faint="#d8dee4", floor="#eef1f4", accent="#800000", tint="#fbf3f3",
                  atlas="#2f6fd6", cie="#0f766e", home="#b7791f", linkedin="#0a66c2",
                  green=["#9be9a8", "#40c463", "#30a14e", "#216e39"]),
    "dark": dict(bg="#0d1117", card="#0d1117", border="#30363d", fg="#e6edf3", muted="#8d96a0",
                 faint="#30363d", floor="#161b22", accent="#f47c7c", tint="#2a1517",
                 atlas="#58a6ff", cie="#3ec1ae", home="#e3b341", linkedin="#2f81f7",
                 green=["#0e4429", "#006d32", "#26a641", "#39d353"]),
}

BASE_CSS = f"""
  .sans {{ font-family: {SANS}; }}
  .serif {{ font-family: {SERIF}; }}
  .mono {{ font-family: {MONO}; }}
  @keyframes fade {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: none; }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}"""


def doc(w, h, title, body, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">\n'
            f"  <title>{title}</title>\n  <style>{BASE_CSS}{css}\n  </style>\n{body}\n</svg>\n")


def write(folder, name, svg):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(svg, encoding="utf-8")


# --------------------------------------------------------------------------- icons (24x24)
ICON_IN = ('<circle cx="5" cy="5" r="2.6"/><rect x="2.6" y="9" width="4.8" height="12.5"/>'
           '<path d="M10 9h4.6v1.9c.7-1.2 2.2-2.3 4.4-2.3 3.6 0 4.5 2.3 4.5 5.4v7.5h-4.8v-6.6c0-1.6-.4-2.6-1.8-2.6-1.6 0-2.1 1.2-2.1 2.8v6.4H10z"/>')
ICON_MAIL = ('<rect x="2.5" y="5" width="19" height="14" rx="2.5" fill="none" stroke-width="2"/>'
             '<path d="M3.5 6.5 12 13l8.5-6.5" fill="none" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
ICON_PIN = ('<path fill-rule="evenodd" d="M12 1.8a7.4 7.4 0 0 0-7.4 7.4c0 5.4 7.4 13 7.4 13s7.4-7.6 7.4-13A7.4 7.4 0 0 0 12 1.8zm0 10.2a2.8 2.8 0 1 1 0-5.6 2.8 2.8 0 0 1 0 5.6z"/>')


# --------------------------------------------------------------------------- 1. contact buttons
BUTTONS = [  # file, label, icon, style, width
    ("btn-linkedin", "Connect on LinkedIn", ICON_IN, "primary", 228),
    ("btn-email", "Email me", ICON_MAIL, "outline", 140),
    ("btn-location", "Chicago, IL", ICON_PIN, "quiet", 144),
]


def button(theme, label, icon, style, w):
    c = THEMES[theme]
    h = 46
    if style == "primary":
        bg, stroke, fg, ic = c["linkedin"], "none", "#ffffff", "#ffffff"
    elif style == "outline":
        bg, stroke, fg, ic = c["card"], c["border"], c["fg"], c["accent"]
    else:
        bg, stroke, fg, ic = "none", "none", c["muted"], c["muted"]
    icon_svg = icon.replace("<rect x=\"2.5\"", f"<rect stroke=\"{ic}\" x=\"2.5\"").replace(
        "<path d=\"M3.5", f"<path stroke=\"{ic}\" d=\"M3.5")
    sheen = ""
    css = ""
    if style == "primary":
        css = """
  @keyframes sheen { 0%, 70% { transform: translateX(-120px) skewX(-20deg); } 100% { transform: translateX(380px) skewX(-20deg); } }
  .sheen { animation: sheen 7s ease-in-out 1.2s infinite; }"""
        sheen = (f'<clipPath id="b"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{h / 2 - 1}"/></clipPath>'
                 f'<g clip-path="url(#b)"><rect class="sheen" x="0" y="-10" width="46" height="{h + 20}" fill="#ffffff" opacity=".18"/></g>')
    body = f"""  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{h / 2 - 1}" fill="{bg}" stroke="{stroke}" stroke-width="1.5"/>
  {sheen}
  <g transform="translate(20,{(h - 18) / 2}) scale(.75)" fill="{ic}">{icon_svg}</g>
  <text class="sans" x="{48}" y="{h / 2 + 5.5}" font-size="15.5" font-weight="600" fill="{fg}">{label}</text>"""
    return doc(w, h, label, body, css)


# --------------------------------------------------------------------------- 2. stat tiles (odometer)
STATS = [  # file, number, line1, line2, project tag, colour key
    ("stat-drugs", "209", "new drugs tracked from", "approval to patient access", "PHARMA ACCESS ATLAS", "atlas"),
    ("stat-agencies", "7", "public agencies merged", "into one sourced dataset", "PHARMA ACCESS ATLAS", "atlas"),
    ("stat-cases", "80", "original consulting", "cases, free for everyone", "CASE INTERVIEW ENGINE", "cie"),
    ("stat-checks", "2,091", "case numbers verified", "by automated tests", "CASE INTERVIEW ENGINE", "cie"),
]


TAG_WIDTHS = {"PHARMA ACCESS ATLAS": 177, "CASE INTERVIEW ENGINE": 183}


def stat_tile(theme, number, l1, l2, tag, key, index):
    c = THEMES[theme]
    W, H = 300, 176
    fs, line = 62, 72
    digit_w, comma_w = fs * 0.60, fs * 0.30
    total = sum(comma_w if ch == "," else digit_w for ch in number)
    x = (W - total) / 2
    base_y = 106
    cols, css = [], []
    delay0 = 0.25 + 0.12 * index
    tag_w = TAG_WIDTHS.get(tag, len(tag) * 9.4)  # measured in the browser at 12px bold
    tag_x = (W - (16 + tag_w)) / 2
    for j, ch in enumerate(number):
        if ch == ",":
            cols.append(f'<text class="sans" x="{x + comma_w / 2:.1f}" y="{base_y}" font-size="{fs}" font-weight="700" fill="{c[key]}" text-anchor="middle">,</text>')
            x += comma_w
            continue
        d = int(ch)
        spins = 10 + d  # roll through a full 0-9 lap, then land on the digit
        stack = "".join(
            f'<text x="{x + digit_w / 2:.1f}" y="{base_y + k * line}" text-anchor="middle">{k % 10}</text>'
            for k in range(spins + 1))
        cls = f"r{j}"
        css.append(f"""
  .{cls} {{ animation: {cls} {1.5 + 0.18 * j:.2f}s cubic-bezier(.2,.75,.25,1) {delay0:.2f}s both; }}
  @keyframes {cls} {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-{spins * line}px); }} }}""")
        cols.append(f'<g class="{cls} sans" font-size="{fs}" font-weight="700" fill="{c[key]}" transform="translate(0,-{spins * line})">{stack}</g>')
        x += digit_w
    css.append(f"""
  .lbl {{ animation: fade .7s ease-out {delay0 + 0.6:.2f}s both; }}""")
    body = f"""  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{c['card']}" stroke="{c['border']}" stroke-width="1.5"/>
  <circle cx="{tag_x + 4:.1f}" cy="31" r="4" fill="{c[key]}"/>
  <text class="sans" x="{tag_x + 16:.1f}" y="35.5" font-size="12" font-weight="700" letter-spacing="1.4" fill="{c['muted']}">{tag}</text>
  <clipPath id="clip"><rect x="0" y="{base_y - fs * 0.80:.1f}" width="{W}" height="{fs * 1.02:.1f}"/></clipPath>
  <g clip-path="url(#clip)">
    {''.join(cols)}
  </g>
  <g class="lbl sans" font-size="16" fill="{c['muted']}" text-anchor="middle">
    <text x="{W / 2}" y="138">{l1}</text>
    <text x="{W / 2}" y="159">{l2}</text>
  </g>"""
    return doc(W, H, f"{number} {l1} {l2}", body, "".join(css))


# --------------------------------------------------------------------------- option A: pipeline
STAGES = [
    ("01", "Question", "Start from a real", "business problem"),
    ("02", "Data", "Public sources,", "every value cited"),
    ("03", "Analysis", "Survival curves,", "tested math"),
    ("04", "Product", "Live web apps and", "an iOS app"),
    ("05", "People", "Free to use, shaped", "by real feedback"),
]


def pipeline(theme):
    c = THEMES[theme]
    W, H = 1200, 200
    n = len(STAGES)
    cw, ch, top = 196, 130, 24
    gap = (W - 2 * 52 - n * cw) / (n - 1)
    xs = [52 + i * (cw + gap) for i in range(n)]
    mid = top + ch / 2
    rail = top + ch + 22
    x0, x1 = xs[0] + cw / 2, xs[-1] + cw / 2
    travel, cycle = 4.8, 6.0
    css = [f"""
  @keyframes run {{ 0% {{ transform: translateX(0); opacity: 0; }} 4% {{ opacity: 1; }} {travel / cycle * 100 - 3:.1f}% {{ opacity: 1; }} {travel / cycle * 100:.1f}%, 100% {{ transform: translateX({x1 - x0:.1f}px); opacity: 0; }} }}
  @keyframes glow {{ 0%, 100% {{ opacity: 0; }} 4% {{ opacity: 1; }} 30% {{ opacity: 0; }} }}
  .dot {{ animation: run {cycle}s cubic-bezier(.45,.05,.55,.95) 1s infinite both; }}
  .intro {{ animation: fade .6s ease-out both; }}"""]
    cards = []
    for i, (num, title, s1, s2) in enumerate(STAGES):
        x = xs[i]
        t = 1 + travel * (x + cw / 2 - x0) / (x1 - x0) - 0.15
        css.append(f"""
  .g{i} {{ animation: glow {cycle}s ease-out {t:.2f}s infinite both; }}
  .c{i} {{ animation-delay: {0.1 + 0.12 * i:.2f}s; }}""")
        cards.append(f"""
  <g class="intro c{i}">
    <rect x="{x}" y="{top}" width="{cw}" height="{ch}" rx="14" fill="{c['card']}" stroke="{c['border']}" stroke-width="1.5"/>
    <rect class="g{i}" x="{x}" y="{top}" width="{cw}" height="{ch}" rx="14" fill="{c['tint']}" stroke="{c['accent']}" stroke-width="2"/>
    <text class="mono" x="{x + 20}" y="{top + 32}" font-size="13" font-weight="700" fill="{c['accent']}">{num}</text>
    <text class="sans" x="{x + 20}" y="{top + 62}" font-size="21" font-weight="700" fill="{c['fg']}">{title}</text>
    <text class="sans" x="{x + 20}" y="{top + 88}" font-size="14" fill="{c['muted']}">{s1}</text>
    <text class="sans" x="{x + 20}" y="{top + 107}" font-size="14" fill="{c['muted']}">{s2}</text>
  </g>""")
    arrows = "".join(
        f'<path d="M{xs[i] + cw + gap / 2 - 5:.1f},{mid - 6} l7,6 l-7,6" fill="none" stroke="{c["muted"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        for i in range(n - 1))
    body = f"""  <line x1="{x0}" y1="{rail}" x2="{x1}" y2="{rail}" stroke="{c['faint']}" stroke-width="2" stroke-dasharray="2 6" stroke-linecap="round"/>
  {''.join(f'<circle cx="{xs[i] + cw / 2:.1f}" cy="{rail}" r="3.5" fill="{c["faint"]}"/>' for i in range(n))}
  {arrows}
  {''.join(cards)}
  <g class="dot"><circle cx="{x0}" cy="{rail}" r="6" fill="{c['accent']}"/><circle cx="{x0}" cy="{rail}" r="12" fill="{c['accent']}" opacity=".18"/></g>"""
    # the dot travels on top of the cards, so draw it last; cards glow as it passes
    return doc(W, H, "How I work: question, data, analysis, product, people", body, "".join(css))


# --------------------------------------------------------------------------- option B: timeline
EVENTS = [  # date, title, subtitle, colour key
    ("JUL 2026", "Started HomeDef", "joined GitHub, first commit", "home"),
    ("OCT 2026", "HomeDef tenant portal", "bills, chat, ROI reports", "home"),
    ("NOV 4", "Pharma Access Atlas live", "FDA × EU access dashboard", "atlas"),
    ("NOV 4", "Case Interview Engine live", "free, no sign-up", "cie"),
    ("NOV 5", "Atlas in four languages", "EN · IT · DE · FR", "atlas"),
    ("NOV 5", "Fit-interview practice", "43 behavioral questions", "cie"),
    ("NOV 11", "80 original cases", "up from 60 a week earlier", "cie"),
]


def timeline(theme):
    c = THEMES[theme]
    W, H = 1200, 330
    axis_y = 168
    xs0, xs1 = 92, 1050
    n = len(EVENTS)
    step = (xs1 - xs0) / (n - 1)
    css = ["""
  @keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
  @keyframes pop { 0% { transform: scale(0); } 70% { transform: scale(1.25); } 100% { transform: scale(1); } }
  @keyframes ping { 0% { transform: scale(.6); opacity: .9; } 100% { transform: scale(2.6); opacity: 0; } }
  .axis { transform-origin: 60px 0; animation: grow 1.6s cubic-bezier(.3,.7,.2,1) .2s both; }
  .pop { transform-box: fill-box; transform-origin: center; }
  .ping { transform-box: fill-box; transform-origin: center; animation: ping 1.8s ease-out 2.4s infinite both; }"""]
    items = []
    for i, (date, title, sub, key) in enumerate(EVENTS):
        x = xs0 + i * step
        up = i % 2 == 0
        dl = 0.45 + 0.2 * i
        css.append(f"""
  .e{i} .pop {{ animation: pop .5s ease-out {dl:.2f}s both; }}
  .e{i} .t {{ animation: fade .5s ease-out {dl + 0.15:.2f}s both; }}""")
        if up:
            y_line, y_date, y_title, y_sub = axis_y - 16, 70, 94, 115
            stem = f'<line x1="{x:.1f}" y1="{y_sub + 12}" x2="{x:.1f}" y2="{axis_y - 12}" stroke="{c["faint"]}" stroke-width="1.5"/>'
        else:
            y_date, y_title, y_sub = 238, 262, 283
            stem = f'<line x1="{x:.1f}" y1="{axis_y + 12}" x2="{x:.1f}" y2="{y_date - 20}" stroke="{c["faint"]}" stroke-width="1.5"/>'
        items.append(f"""
  <g class="e{i}">
    <g class="t">{stem}
      <text class="mono" x="{x:.1f}" y="{y_date}" font-size="12.5" font-weight="700" letter-spacing="1" fill="{c[key]}" text-anchor="middle">{date}</text>
      <text class="sans" x="{x:.1f}" y="{y_title}" font-size="16" font-weight="700" fill="{c['fg']}" text-anchor="middle">{title}</text>
      <text class="sans" x="{x:.1f}" y="{y_sub}" font-size="13.5" fill="{c['muted']}" text-anchor="middle">{sub}</text>
    </g>
    <circle class="pop" cx="{x:.1f}" cy="{axis_y}" r="9" fill="{c['card']}" stroke="{c[key]}" stroke-width="4"/>
  </g>""")
    now_x = xs1 + 78
    legend = "".join(
        f'<circle cx="{lx}" cy="{H - 22}" r="4.5" fill="{c[k]}"/><text class="sans" x="{lx + 10}" y="{H - 17.5}" font-size="12.5" fill="{c["muted"]}">{name}</text>'
        for lx, k, name in [(W - 470, "home", "HomeDef"), (W - 370, "atlas", "Pharma Access Atlas"), (W - 210, "cie", "Case Interview Engine")])
    body = f"""  <text class="sans t0" x="48" y="38" font-size="13" font-weight="700" letter-spacing="2.2" fill="{c['accent']}">SHIPPING LOG  ·  2026</text>
  <line class="axis" x1="60" y1="{axis_y}" x2="{now_x}" y2="{axis_y}" stroke="{c['faint']}" stroke-width="3" stroke-linecap="round"/>
  {''.join(items)}
  <g class="enow">
    <circle class="ping" cx="{now_x}" cy="{axis_y}" r="8" fill="{c['accent']}"/>
    <circle cx="{now_x}" cy="{axis_y}" r="7" fill="{c['accent']}"/>
    <text class="mono" x="{now_x}" y="{axis_y - 22}" font-size="12.5" font-weight="700" letter-spacing="1" fill="{c['accent']}" text-anchor="middle">NOW</text>
    <text class="sans" x="{now_x}" y="{axis_y + 34}" font-size="13.5" fill="{c['muted']}" text-anchor="middle">building</text>
  </g>
  {legend}"""
    return doc(W, H, "Shipping log 2026: HomeDef, Pharma Access Atlas and Case Interview Engine milestones", body, "".join(css))


# --------------------------------------------------------------------------- option C: 3D skyline
def shade(hex_colour, f):
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(v * f))) for v in (r, g, b))


def skyline(theme, days):
    c = THEMES[theme]
    W, H = 1200, 400
    start = dt.date(2026, 6, 29)  # Monday of the week GitHub was joined
    end = dt.date(2026, 11, 16)
    weeks = (end - start).days // 7 + 1
    counts = {dt.date.fromisoformat(d["date"]): d["count"] for d in days}
    total = sum(v for k, v in counts.items() if k >= start)
    active = sum(1 for k, v in counts.items() if k >= start and v)
    busiest = max(((k, v) for k, v in counts.items() if k >= start), key=lambda kv: kv[1])
    tw, th = 30, 15  # tile width/height in iso
    ox, oy = 760, 118  # origin of week 0 / day 0
    maxc = max(counts.values())
    cells = []
    for w in range(weeks):
        for d in range(7):
            day = start + dt.timedelta(days=7 * w + d)
            if day > end:
                continue
            n = counts.get(day, 0)
            cx = ox + (w - d) * tw / 2
            cy = oy + (w + d) * th / 2
            cells.append((w + d, w, d, cx, cy, n))
    cells.sort()
    css = ["""
  @keyframes rise { from { transform: scaleY(0.02); } to { transform: scaleY(1); } }
  .bar { transform-box: fill-box; transform-origin: 50% 100%; }"""]
    shapes = []
    for _, w, d, cx, cy, n in cells:
        top = f"{cx},{cy - th / 2} {cx + tw / 2},{cy} {cx},{cy + th / 2} {cx - tw / 2},{cy}"
        if n == 0:
            shapes.append(f'<polygon points="{top}" fill="{c["floor"]}" stroke="{c["bg"]}" stroke-width="1"/>')
            continue
        level = min(3, int(math.log(n, 3.2)))
        col = c["green"][level]
        hgt = 10 + 120 * math.log1p(n) / math.log1p(maxc)
        t = f"{cx},{cy - th / 2 - hgt} {cx + tw / 2},{cy - hgt} {cx},{cy + th / 2 - hgt} {cx - tw / 2},{cy - hgt}"
        left = f"{cx - tw / 2},{cy - hgt} {cx},{cy + th / 2 - hgt} {cx},{cy + th / 2} {cx - tw / 2},{cy}"
        right = f"{cx + tw / 2},{cy - hgt} {cx},{cy + th / 2 - hgt} {cx},{cy + th / 2} {cx + tw / 2},{cy}"
        k = len(css)
        css.append(f"\n  .b{k} {{ animation: rise 1.1s cubic-bezier(.2,.8,.25,1) {0.3 + 0.07 * w:.2f}s both; }}")
        f_l, f_r = (0.82, 0.66) if theme == "light" else (0.72, 0.55)
        shapes.append(f'<g class="bar b{k}"><polygon points="{left}" fill="{shade(col, f_l)}"/><polygon points="{right}" fill="{shade(col, f_r)}"/><polygon points="{t}" fill="{col}"/></g>')
    # month labels along the front-left edge (day 6 row)
    months = []
    for m in range(7, 12):
        first = dt.date(2026, m, 1)
        w = (first - start).days // 7
        cx = ox + (w - 7.6) * tw / 2
        cy = oy + (w + 7.6) * th / 2
        months.append(f'<text class="mono" x="{cx:.1f}" y="{cy + 10:.1f}" font-size="12" fill="{c["muted"]}" text-anchor="middle">{first.strftime("%b").upper()}</text>')
    body = f"""  <g class="sans" style="animation: fade .7s ease-out .1s both">
    <text x="56" y="92" font-size="13" font-weight="700" letter-spacing="2.2" fill="{c['accent']}">2026 IN COMMITS  ·  ALL REPOSITORIES</text>
    <text class="serif" x="52" y="178" font-size="88" font-weight="700" fill="{c['fg']}">{total}</text>
    <text x="56" y="210" font-size="17" fill="{c['muted']}">commits since joining GitHub in July</text>
    <text x="56" y="262" font-size="15" fill="{c['fg']}"><tspan font-weight="700">{active}</tspan> active days</text>
    <text x="56" y="288" font-size="15" fill="{c['fg']}">Busiest day: <tspan font-weight="700">{busiest[0].strftime('%b')} {busiest[0].day}</tspan>, {busiest[1]} commits</text>
    <text x="56" y="314" font-size="15" fill="{c['fg']}">Two public launches in one week</text>
  </g>
  {''.join(shapes)}
  {''.join(months)}"""
    return doc(W, H, f"{total} commits in 2026 shown as a 3D contribution skyline", body, "".join(css))


if __name__ == "__main__":
    days = json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) > 1 else []
    for theme in THEMES:
        for i, (name, label, icon, style, w) in enumerate(BUTTONS):
            write(ASSETS, f"{name}-{theme}.svg", button(theme, label, icon, style, w))
        for i, (name, number, l1, l2, tag, key) in enumerate(STATS):
            write(ASSETS, f"{name}-{theme}.svg", stat_tile(theme, number, l1, l2, tag, key, i))
        write(ASSETS, f"pipeline-{theme}.svg", pipeline(theme))
        write(ASSETS, f"timeline-{theme}.svg", timeline(theme))
        if days:
            write(ASSETS, f"skyline-{theme}.svg", skyline(theme, days))
    print("done")
