#!/usr/bin/env python3
"""Build assets/btn-email.svg, assets/btn-repos.svg, assets/footer.svg  ->  python scripts/build_buttons.py"""
import sys, os
CY, BL, OR, TX, DIM = "#00F0FF", "#2D7CFF", "#FF9E00", "#C9D4E3", "#6B7A90"
MONO = "'Cascadia Mono',Consolas,'SFMono-Regular',Menlo,'Courier New',monospace"
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "assets")

def button(label, icon, accent):
    W, H = 240, 46
    n = len(label); cw = 13 * 0.6
    tx = 52
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{label}">
<defs><linearGradient id="f" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}"/><stop offset=".55" stop-color="{BL}"/><stop offset="1" stop-color="{OR}"/></linearGradient></defs>
<style>.mono{{font-family:{MONO}}}.glow{{animation:glow 2.4s ease-in-out infinite}}@keyframes glow{{50%{{stroke-opacity:.35}}}}.arr{{animation:arr 1.2s ease-in-out infinite}}@keyframes arr{{50%{{transform:translateX(4px)}}}}</style>
<path d="M10 1 H{W-1} V{H-11} L{W-11} {H-1} H1 V11 Z" fill="#05070D" stroke="url(#f)" stroke-width="1.5" class="glow"/>
<rect x="1" y="1" width="36" height="{H-2}" fill="{accent}" fill-opacity=".12"/>
<g transform="translate(9 11)" fill="none" stroke="{accent}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{icon}</g>
<text x="{tx}" y="28" class="mono" font-size="13" font-weight="700" letter-spacing="0" fill="{TX}" textLength="{n*cw:.1f}" lengthAdjust="spacingAndGlyphs">{label}</text>
<path d="M{W-26} 17 l6 6 -6 6" fill="none" stroke="{OR}" stroke-width="2" class="arr"/>
</svg>
'''

mail = '<rect x="1" y="4" width="18" height="14" rx="1"/><path d="M1 5l9 7 9-7"/>'
term = '<rect x="1" y="2" width="18" height="18" rx="1"/><path d="M5 8l3 3-3 3M10 15h5"/>'
open(os.path.join(out, "btn-email.svg"), "w", encoding="utf-8").write(button("SEND A MESSAGE", mail, CY))
open(os.path.join(out, "btn-repos.svg"), "w", encoding="utf-8").write(button("EXPLORE REPOS", term, OR))

W, H = 1000, 64
footer = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="End of transmission - thanks for visiting">
<defs>
  <linearGradient id="f" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}" stop-opacity="0"/><stop offset=".2" stop-color="{CY}"/><stop offset=".55" stop-color="{BL}"/><stop offset=".8" stop-color="{OR}"/><stop offset="1" stop-color="{OR}" stop-opacity="0"/></linearGradient>
  <linearGradient id="spark" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<style>.mono{{font-family:{MONO}}}.run{{animation:run 3.5s linear infinite}}@keyframes run{{from{{transform:translateX(-120px)}}to{{transform:translateX({W}px)}}}}.blink{{animation:blink 1s steps(1) infinite}}@keyframes blink{{50%{{opacity:0}}}}</style>
<rect width="{W}" height="2" y="18" fill="url(#f)"/>
<rect width="120" height="2" y="18" fill="url(#spark)" class="run"/>
<text x="{W/2}" y="48" text-anchor="middle" class="mono" font-size="13" letter-spacing="3" fill="{DIM}">// END_OF_TRANSMISSION <tspan fill="{CY}">·</tspan> THANKS FOR VISITING <tspan fill="{OR}">·</tspan> SEE YOU IN 2077<tspan fill="{CY}" class="blink">_</tspan></text>
</svg>
'''
open(os.path.join(out, "footer.svg"), "w", encoding="utf-8").write(footer)
print("ok")
