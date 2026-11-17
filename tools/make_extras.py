#!/usr/bin/env python3
"""Generate the profile README's contact buttons, stat cards and How-I-work pipeline.

Run from the repo root:  python3 tools/make_extras.py
Writes light + dark SVGs into assets/.

What to edit:
  STATS    the four stat cards (number and two label lines)
  STAGES   the five How-I-work steps
  BUTTONS  contact button labels
"""
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
SERIF = "Charter, 'Iowan Old Style', Georgia, Cambria, 'Times New Roman', serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "light": dict(bg="#ffffff", card="#ffffff", border="#d0d7de", fg="#1f2328", muted="#656d76",
                  faint="#d8dee4", floor="#eef1f4", accent="#800000", tint="#fbf3f3",
                  atlas="#2f6fd6", cie="#0f766e", home="#b7791f", linkedin="#0a66c2"),
    "dark": dict(bg="#0d1117", card="#0d1117", border="#30363d", fg="#e6edf3", muted="#8d96a0",
                 faint="#30363d", floor="#161b22", accent="#f47c7c", tint="#2a1517",
                 atlas="#58a6ff", cie="#3ec1ae", home="#e3b341", linkedin="#2f81f7"),
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


if __name__ == "__main__":
    for theme in THEMES:
        for i, (name, label, icon, style, w) in enumerate(BUTTONS):
            write(ASSETS, f"{name}-{theme}.svg", button(theme, label, icon, style, w))
        for i, (name, number, l1, l2, tag, key) in enumerate(STATS):
            write(ASSETS, f"{name}-{theme}.svg", stat_tile(theme, number, l1, l2, tag, key, i))
        write(ASSETS, f"pipeline-{theme}.svg", pipeline(theme))
    print("done")
