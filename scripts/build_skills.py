#!/usr/bin/env python3
"""
Build assets/skills.svg - "INSTALLED MODULES": brand-coloured badges with a
cyberpunk chromatic-aberration / noise treatment.

Edit MODULES, then (needs internet once for the logos):
    python scripts/build_skills.py

Logos: Simple Icons (CC0). Brands it no longer ships (SQL Server, Power BI)
and concepts (ML, DL, BPM, DWH) use the line glyphs in GLYPHS.
"""
from __future__ import annotations

import functools
import html
import random
from pathlib import Path

from theme import CY, MONO, OR, T_READY, TX, base_css, defs, frame
from theme import fetch_icon as _fetch, loader_css, not_found, title_bar

MAGENTA, ICE = "#FF2A6D", "#00E5FF"     # aberration colours

# (category, [(label, icon, brand colour)])  icon = simple-icons slug or "glyph:<name>"
MODULES = [
    ("LANGUAGES", [("Python", "python", "#FFD43B"), ("C++", "cplusplus", "#659AD2"),
                   ("Java", "openjdk", "#F89820"), ("PHP", "php", "#8892BF")]),
    ("BACKEND // OPS", [("Laravel", "laravel", "#FF2D20"), ("Docker", "docker", "#2496ED"),
                        ("SQL Server", "glyph:db", "#E8473F")]),
    ("DATA // BI", [("Data Warehousing", "glyph:dwh", "#05FFA1"), ("Power BI", "glyph:bars", "#F2C811"),
                    ("BPM", "glyph:flow", "#B967FF")]),
    ("AI // ML", [("Machine Learning", "glyph:ml", "#FF2A6D"), ("Deep Learning", "glyph:dl", "#A06BFF"),
                  ("TensorFlow", "tensorflow", "#FF8F00"), ("Kaggle", "kaggle", "#20BEFF"),
                  ("Claude", "claude", "#D97757")]),
]

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
ROW_H, TOP, CHIP_H, X_CHIPS, GAP = 58, 72, 38, 220, 10
FS = 14
CW = FS * 0.6


fetch_icon = functools.lru_cache(maxsize=None)(_fetch)


def icon_markup(spec: str, color: str) -> str:
    """Icon at the origin (24x24 scaled to 18px)."""
    if spec.startswith("glyph:"):
        return (f'<g transform="scale(.75)" fill="none" stroke="{color}" stroke-width="2" '
                f'stroke-linecap="round" stroke-linejoin="round">{GLYPHS[spec[6:]]}</g>')
    return f'<path transform="scale(.75)" fill="{color}" d="{fetch_icon(spec)}"/>'


def chip(x: float, y: float, label: str, spec: str, color: str, n: int) -> str:
    w = 12 + 18 + 8 + len(label) * CW + 12
    cy = y + CHIP_H / 2
    ix, iy = x + 12, cy - 9
    lab = html.escape(label)
    tl = f'textLength="{len(label) * CW:.1f}" lengthAdjust="spacingAndGlyphs"'
    rnd = random.Random(label)
    return f'''<g class="chip" style="animation-delay:{T_READY + .7 + n * .07:.2f}s">
  <rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{CHIP_H}" rx="7" fill="{color}" opacity=".2" filter="url(#blur)"/>
  <rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{CHIP_H}" rx="7" fill="{color}" fill-opacity=".09" stroke="{color}" stroke-opacity=".85"/>
  <rect x="{x + 1:.1f}" y="{y + 1}" width="{w - 2:.1f}" height="{CHIP_H - 2}" rx="6" fill="url(#noise)" opacity=".5"/>
  <g class="gx" style="animation-delay:{T_READY + 2 + rnd.uniform(0, 6):.2f}s;animation-duration:{rnd.uniform(3.5, 7):.2f}s">
    <g transform="translate({ix - 1.4:.1f} {iy:.1f})" opacity=".7">{icon_markup(spec, MAGENTA)}</g>
    <g transform="translate({ix + 1.4:.1f} {iy:.1f})" opacity=".55">{icon_markup(spec, ICE)}</g>
    <g transform="translate({ix:.1f} {iy:.1f})">{icon_markup(spec, color)}</g>
    <text x="{x + 38 - 1:.1f}" y="{cy + 5:.1f}" font-size="{FS}" fill="{MAGENTA}" opacity=".45" {tl}>{lab}</text>
    <text x="{x + 38 + 1:.1f}" y="{cy + 5:.1f}" font-size="{FS}" fill="{ICE}" opacity=".35" {tl}>{lab}</text>
    <text x="{x + 38:.1f}" y="{cy + 5:.1f}" font-size="{FS}" font-weight="600" fill="#E9F1FA" {tl}>{lab}</text>
  </g>
</g>''', w


def main() -> None:
    H = TOP + len(MODULES) * ROW_H + 18
    total = sum(len(m[1]) for m in MODULES)
    parts, n = [], 0
    for r, (cat, items) in enumerate(MODULES):
        y = TOP + r * ROW_H
        cy = y + CHIP_H / 2
        parts.append(
            f'<g class="in" style="animation-delay:{T_READY + .6 + r * .1:.2f}s">'
            f'<text x="28" y="{cy + 7:.1f}" font-size="20" font-weight="700" fill="{CY}" fill-opacity=".9">{r + 1:02d}</text>'
            f'<text x="62" y="{cy + 4:.1f}" font-size="11.5" letter-spacing="2" fill="{TX}">{html.escape(cat)}</text>'
            f'<path d="M{X_CHIPS - 32} {cy:.1f} H{X_CHIPS - 10}" stroke="{CY}" stroke-opacity=".35" stroke-dasharray="2 3"/></g>')
        x = X_CHIPS
        for label, spec, color in items:
            svg, w = chip(x, y, label, spec, color, n)
            parts.append(svg)
            x += w + GAP
            n += 1

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Installed modules: {html.escape(", ".join(l for _, items in MODULES for l, _, _ in items))}">
<title>INSTALLED MODULES</title>
<defs>
  {defs()}
  <filter id="blur" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>
    <feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .35 0"/></filter>
  <pattern id="noise" width="120" height="40" patternUnits="userSpaceOnUse"><rect width="120" height="40" filter="url(#grain)"/></pattern>
  <filter id="jit" x="-10%" y="-40%" width="120%" height="180%"><feTurbulence type="turbulence" baseFrequency=".02 .6" numOctaves="1" seed="7"/>
    <feDisplacementMap in="SourceGraphic" scale="9" xChannelSelector="R" yChannelSelector="G"/></filter>
</defs>
<style>
  {base_css()}
  {loader_css()}
  text{{font-family:{MONO}}}
  .chip,.in{{opacity:0;animation:in .4s ease-out forwards}}
  @keyframes in{{from{{opacity:0;transform:translateX(-10px)}}to{{opacity:1;transform:none}}}}
  .gx{{animation-name:gx;animation-timing-function:steps(1);animation-iteration-count:infinite}}
  @keyframes gx{{0%,100%{{filter:none;transform:none}}90%{{filter:url(#jit);transform:translateX(-2px)}}92%{{filter:url(#jit);transform:translateX(2px)}}94%{{filter:none;transform:none}}}}
</style>

{frame(W, H)}
{not_found(W / 2, H / 2 + 6, 80)}
<g class="content">
  {title_bar(W, "INSTALLED MODULES", f'<tspan fill="{OR}">{total}</tspan> ONLINE')}
  {chr(10).join(parts)}
</g>
</svg>
'''
    out = Path(__file__).resolve().parent.parent / "assets" / "skills.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
