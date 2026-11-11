"""
Shared look & timing for every profile panel.

Colour budget ~ 70 : 20 : 10
  70  black background + cyan/blue frames & text
  20  orange - only for the important bits (name, CONNECTED, VERIFIED, key numbers)
  10  brand colours (skill badges, language bar)
"""
from __future__ import annotations

import re
import urllib.request

BG = "#0d1117"        # = GitHub dark canvas, so panels sit naturally on the page
PANEL = "#0d1117"
CY = "#00E5FF"        # primary
BLUE = "#3D8BFF"      # gradient partner of CY
SOFT = "#7DD3FC"      # light blue (404 ghost, easter egg)
OR = "#FF9E00"        # accent - use sparingly
TX = "#C9D4E3"
DIM = "#6B7A90"
LINE = "#30363d"      # GitHub border colour
MONO = "'Cascadia Mono','Cascadia Code',Consolas,'SFMono-Regular',Menlo,'Courier New',monospace"

RADIUS = 12
T_READY = 9.0         # seconds: header finishes "...call me noName25", then the panels load

SI_URL = "https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/{}.svg"


def fetch_icon(slug: str) -> str:
    """Return the <path d> of a Simple Icons logo (24x24 viewBox)."""
    svg = urllib.request.urlopen(SI_URL.format(slug), timeout=20).read().decode()
    return re.search(r'<path d="([^"]+)"', svg).group(1)


def defs() -> str:
    return f'''<linearGradient id="frame" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CY}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
  <pattern id="crt" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".22"/></pattern>'''


def frame(w: float, h: float) -> str:
    return (f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="{RADIUS}" '
            f'fill="{PANEL}" stroke="url(#frame)" stroke-width="1.3" stroke-opacity=".8"/>')


def title_bar(w: float, left: str, right: str = "") -> str:
    """Thin header row used by every panel."""
    return f'''<g font-family="{MONO}" font-size="12" letter-spacing="1.5">
  <rect x="18" y="17" width="3" height="13" rx="1.5" fill="{CY}"/>
  <text x="30" y="28" fill="{CY}">{left}</text>
  <text x="{w - 36}" y="28" fill="{DIM}" text-anchor="end">{right}</text>
  <circle cx="{w - 24}" cy="24" r="3.5" fill="{CY}" class="blink"/>
</g>
<path d="M1 44 H{w - 1}" stroke="{CY}" stroke-opacity=".16"/>'''


def base_css() -> str:
    return f'''.mono{{font-family:{MONO}}}
  .blink{{animation:blink 1s steps(1) infinite}}
  @keyframes blink{{50%{{opacity:0}}}}
  @keyframes show{{to{{opacity:1}}}}
  @keyframes hide{{to{{opacity:0}}}}'''


def loader_css(t: float = T_READY) -> str:
    """404 ghost until the header is done, then flicker the real content in."""
    return f'''.nf{{animation:nfout .7s steps(1) {t:.2f}s forwards}}
  @keyframes nfout{{0%{{opacity:1}}20%{{opacity:0}}35%{{opacity:1}}55%{{opacity:0}}75%{{opacity:.5}}88%,100%{{opacity:0}}}}
  .nfa{{opacity:0;animation:nfa 2.3s steps(1) infinite}}
  .nfb{{opacity:0;animation:nfb 2.3s steps(1) .4s infinite}}
  @keyframes nfa{{0%,100%{{opacity:0}}70%{{opacity:.5;transform:translate(-7px,0);clip-path:inset(18% 0 52% 0)}}74%{{opacity:.5;transform:translate(5px,0);clip-path:inset(58% 0 12% 0)}}78%{{opacity:0}}}}
  @keyframes nfb{{0%,100%{{opacity:0}}60%{{opacity:.45;transform:translate(6px,0);clip-path:inset(40% 0 35% 0)}}64%{{opacity:.45;transform:translate(-4px,0);clip-path:inset(8% 0 72% 0)}}68%{{opacity:0}}}}
  .content{{opacity:0;animation:cin .8s steps(1) {t + .45:.2f}s forwards}}
  @keyframes cin{{0%{{opacity:0}}15%{{opacity:.7}}30%{{opacity:0}}50%{{opacity:1}}65%{{opacity:.35}}82%,100%{{opacity:1}}}}'''


def not_found(cx: float, cy: float, size: float = 96) -> str:
    """Faint glitchy '404 / PAGE NOT FOUND' placeholder (light blue, sunk into the background)."""
    s = size / 96
    dashes = "".join(
        f'<rect x="{cx + dx * s:.0f}" y="{cy + dy * s:.0f}" width="{w * s:.0f}" height="2" fill="{c}"/>'
        for dx, dy, w, c in [(-190, -40, 34, SOFT), (150, -28, 22, CY), (-170, 2, 18, BLUE),
                             (128, 10, 40, SOFT), (-140, 24, 26, CY), (170, -6, 14, BLUE)]
    )
    big = (f'font-size="{size:.0f}" font-weight="700" textLength="{size * 2.4:.0f}" '
           f'lengthAdjust="spacingAndGlyphs"')
    return f'''<g class="nf" font-family="{MONO}" text-anchor="middle">
  <g opacity=".2" fill="{SOFT}">
    <text x="{cx}" y="{cy - size * .62:.0f}" font-size="{16 * s:.0f}" letter-spacing="5">ERROR</text>
    <text x="{cx}" y="{cy + size * .34:.0f}" {big}>404</text>
    <text x="{cx}" y="{cy + size * .74:.0f}" font-size="{16 * s:.0f}" letter-spacing="5">PAGE NOT FOUND</text>
    {dashes}
  </g>
  <text x="{cx}" y="{cy + size * .34:.0f}" {big} fill="{CY}" class="nfa">404</text>
  <text x="{cx}" y="{cy + size * .34:.0f}" {big} fill="{BLUE}" class="nfb">404</text>
</g>'''
