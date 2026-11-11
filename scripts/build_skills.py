#!/usr/bin/env python3
"""
Build assets/skills.svg - the "CYBERWARE // INSTALLED MODULES" tech-stack panel.

Edit the MODULES list below, then run (needs internet once to fetch logos):
    python scripts/build_skills.py

Logos come from Simple Icons (CC0). Brands that Simple Icons no longer ships
(e.g. Microsoft SQL Server, Power BI) and concepts (ML, DL, BPM...) use the
hand-drawn line glyphs in GLYPHS.
"""
from __future__ import annotations

import html
import re
import urllib.request
from pathlib import Path

CY, BL, OR, TX, DIM = "#00F0FF", "#5AA9FF", "#FF9E00", "#C9D4E3", "#6B7A90"
MONO = "'Cascadia Mono',Consolas,'SFMono-Regular',Menlo,'Courier New',monospace"
SI_URL = "https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/{}.svg"

# (category, accent colour, [(label, simple-icons slug OR "glyph:<name>"), ...])
MODULES = [
    ("LANGUAGES", CY, [("Python", "python"), ("C++", "cplusplus"), ("Java", "openjdk"), ("PHP", "php")]),
    ("BACKEND // OPS", BL, [("Laravel", "laravel"), ("Docker", "docker"), ("SQL Server", "glyph:db")]),
    ("DATA // BI", OR, [("Data Warehousing", "glyph:dwh"), ("Power BI", "glyph:bars"), ("BPM", "glyph:flow")]),
    ("AI // ML", "url(#frame)", [("Machine Learning", "glyph:ml"), ("Deep Learning", "glyph:dl"),
                                  ("TensorFlow", "tensorflow"), ("Kaggle", "kaggle"), ("Claude", "claude")]),
]

# 24x24 stroke glyphs
GLYPHS = {
    "db": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "bars": '<path d="M5 21V13M10 21V8M15 21V3M20 21V11" stroke-width="3"/>',
    "dwh": '<path d="M3 7l9-4 9 4-9 4-9-4zM3 12l9 4 9-4M3 17l9 4 9-4"/>',
    "flow": '<rect x="1.5" y="8.5" width="7" height="7"/><path d="M8.5 12h5"/><path d="M17.5 7.5l4.5 4.5-4.5 4.5-4.5-4.5z"/>',
    "ml": '<circle cx="5" cy="6" r="2.4"/><circle cx="5" cy="18" r="2.4"/><circle cx="19" cy="12" r="2.4"/><path d="M7.2 7l9.6 4M7.2 17l9.6-4M5 8.4v7.2"/>',
    "dl": '<circle cx="4" cy="7" r="2"/><circle cx="4" cy="17" r="2"/><circle cx="12" cy="4" r="2"/><circle cx="12" cy="12" r="2"/>'
          '<circle cx="12" cy="20" r="2"/><circle cx="20" cy="12" r="2"/><path d="M6 6.5l4-2M6 7.5l4 4M6 16.5l4-4M6 17.5l4 2M14 5l4.5 5.5M14 12h4M14 19l4.5-5.5"/>',
}

W = 1000
ROW_H, TOP, CHIP_H, X_CHIPS, GAP = 56, 70, 38, 232, 12
FS = 14
CW = FS * 0.6


def fetch_icon(slug: str) -> str:
    svg = urllib.request.urlopen(SI_URL.format(slug), timeout=20).read().decode()
    return re.search(r'<path d="([^"]+)"', svg).group(1)


def icon(spec: str, color: str, x: float, y: float) -> str:
    stroke_col = OR if color.startswith("url") else color
    tr = f'transform="translate({x:.1f} {y:.1f}) scale(.75)"'
    if spec.startswith("glyph:"):
        return (f'<g {tr} fill="none" stroke="{stroke_col}" stroke-width="2" '
                f'stroke-linecap="round" stroke-linejoin="round">{GLYPHS[spec[6:]]}</g>')
    return f'<path {tr} fill="{stroke_col}" d="{fetch_icon(spec)}"/>'


def main() -> None:
    H = TOP + len(MODULES) * ROW_H + 26
    total = sum(len(m[2]) for m in MODULES)
    parts, n = [], 0
    for r, (cat, color, items) in enumerate(MODULES):
        y = TOP + r * ROW_H
        cy = y + CHIP_H / 2
        parts.append(
            f'<g class="mono"><text x="28" y="{cy + 8:.1f}" font-size="24" font-weight="700" fill="{OR}">{r + 1:02d}</text>'
            f'<text x="66" y="{cy + 4:.1f}" font-size="12" letter-spacing="2" fill="{TX}">{html.escape(cat)}</text></g>'
            f'<path d="M{X_CHIPS - 34} {cy:.1f} H{X_CHIPS - 8}" stroke="{CY}" stroke-opacity=".4" stroke-dasharray="2 3"/>'
        )
        x = X_CHIPS
        for label, spec in items:
            w = 12 + 18 + 10 + len(label) * CW + 14
            stroke = color
            parts.append(
                f'<g class="chip" style="animation-delay:{0.25 + n * 0.07:.2f}s">'
                f'<path d="M{x + 8:.1f} {y} H{x + w:.1f} V{y + CHIP_H - 8} L{x + w - 8:.1f} {y + CHIP_H} H{x:.1f} V{y + 8} Z" '
                f'fill="#0A1020" stroke="{stroke}" stroke-opacity=".75"/>'
                f'{icon(spec, color, x + 12, cy - 9)}'
                f'<text class="mono" x="{x + 40:.1f}" y="{cy + 5:.1f}" font-size="{FS}" fill="{TX}" '
                f'textLength="{len(label) * CW:.1f}" lengthAdjust="spacingAndGlyphs">{html.escape(label)}</text></g>'
            )
            x += w + GAP
            n += 1
        parts.append(f'<rect class="scan" x="{X_CHIPS}" y="{y}" width="60" height="{CHIP_H}" fill="url(#scan)" '
                     f'style="animation-delay:{2 + r * 0.9:.1f}s"/>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Tech stack: {html.escape(", ".join(l for m in MODULES for l, _ in m[2]))}">
<title>CYBERWARE // INSTALLED MODULES</title>
<defs>
  <linearGradient id="frame" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}"/><stop offset=".55" stop-color="#2D7CFF"/><stop offset="1" stop-color="{OR}"/></linearGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}" stop-opacity="0"/><stop offset=".5" stop-color="{CY}" stop-opacity=".22"/><stop offset="1" stop-color="{CY}" stop-opacity="0"/></linearGradient>
  <pattern id="crt" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".3"/></pattern>
</defs>
<style>
  .mono{{font-family:{MONO}}}
  .chip{{opacity:0;animation:in .4s ease-out forwards}}
  @keyframes in{{from{{opacity:0;transform:translateX(-10px)}}to{{opacity:1;transform:none}}}}
  .scan{{opacity:0;animation:scan 4.5s ease-in-out infinite}}
  @keyframes scan{{0%{{opacity:0;transform:translateX(0)}}5%{{opacity:1}}40%{{opacity:1;transform:translateX({W - X_CHIPS - 80}px)}}45%,100%{{opacity:0;transform:translateX({W - X_CHIPS - 80}px)}}}}
  .blink{{animation:blink 1s steps(1) infinite}} @keyframes blink{{50%{{opacity:0}}}}
</style>
<path d="M16 1 H{W - 30} L{W - 1} 30 V{H - 16} L{W - 16} {H - 1} H30 L1 {H - 30} V16 Z" fill="#05070D" stroke="url(#frame)" stroke-width="1.5"/>
<path d="M1 46 H{W - 1}" stroke="{CY}" stroke-opacity=".25"/>
<g class="mono" font-size="12" letter-spacing="1.5">
  <rect x="18" y="16" width="8" height="14" fill="{CY}"/>
  <text x="34" y="28" fill="{CY}">CYBERWARE // INSTALLED MODULES</text>
  <text x="{W - 40}" y="28" fill="{OR}" text-anchor="end">{total} MODULES ONLINE</text>
  <circle cx="{W - 28}" cy="24" r="4" fill="{CY}" class="blink"/>
</g>
{chr(10).join(parts)}
<rect x="2" y="47" width="{W - 4}" height="{H - 60}" fill="url(#crt)"/>
</svg>
'''
    out = Path(__file__).resolve().parent.parent / "assets" / "skills.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
