#!/usr/bin/env python3
"""Build assets/footer.svg  ->  python scripts/build_footer.py"""
from pathlib import Path

from theme import BLUE, CY, DIM, MONO, T_READY, base_css

W, H = 1000, 64
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="End of transmission - thanks for visiting">
<defs>
  <linearGradient id="f" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}" stop-opacity="0"/><stop offset=".25" stop-color="{CY}"/><stop offset=".75" stop-color="{BLUE}"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>
  <linearGradient id="spark" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<style>
  {base_css()}
  .wrap{{opacity:0;animation:show .8s ease {T_READY + 2:.1f}s forwards}}
  .run{{animation:run 3.5s linear infinite}}
  @keyframes run{{from{{transform:translateX(-120px)}}to{{transform:translateX({W}px)}}}}
</style>
<g class="wrap">
  <rect width="{W}" height="1.5" y="18" fill="url(#f)" opacity=".8"/>
  <rect width="120" height="1.5" y="18" fill="url(#spark)" class="run"/>
  <text x="{W / 2}" y="48" text-anchor="middle" font-family="{MONO}" font-size="13" letter-spacing="3" fill="{DIM}">// END_OF_TRANSMISSION <tspan fill="{CY}">·</tspan> THANKS FOR VISITING <tspan fill="{CY}">·</tspan> SEE YOU IN 2077<tspan fill="{CY}" class="blink">_</tspan></text>
</g>
</svg>
'''
out = Path(__file__).resolve().parent.parent / "assets" / "footer.svg"
out.write_text(svg, encoding="utf-8")
print(f"wrote {out}")
