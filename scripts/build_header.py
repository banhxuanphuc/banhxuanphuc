#!/usr/bin/env python3
"""Build assets/header.svg  ->  python scripts/build_header.py"""
import random, sys
random.seed(2077)
W, H = 1000, 280
CY, BL, OR = "#00F0FF", "#2D7CFF", "#FF9E00"
MONO = "'Cascadia Mono',Consolas,'SFMono-Regular',Menlo,'Courier New',monospace"
SANS = "'Segoe UI Black','Arial Black','Helvetica Neue',Arial,sans-serif"

HZ = 236  # horizon / skyline base
# skyline
bld, win = [], []
x = 0
while x < W:
    w = random.choice([22, 28, 34, 40, 18, 46])
    edge = abs(x + w / 2 - W / 2) / (W / 2)          # taller at the edges, low in the middle
    h = random.randint(14, 30) + int(edge * random.randint(20, 46))
    bld.append(f'<rect x="{x}" y="{HZ - h}" width="{w - 2}" height="{h}"/>')
    if random.random() < .35 and h > 40:
        bld.append(f'<rect x="{x + w // 2 - 1}" y="{HZ - h - 10}" width="2" height="10"/>')
    for wy in range(HZ - h + 5, HZ - 4, 6):
        for wx in range(x + 4, x + w - 5, 6):
            if random.random() < .16:
                c = OR if random.random() < .3 else CY
                cls = ' class="tw"' if random.random() < .12 else ""
                d = f' style="animation-delay:{random.uniform(0, 4):.1f}s"' if cls else ""
                win.append(f'<rect x="{wx}" y="{wy}" width="2" height="2" fill="{c}" opacity="{random.choice([.35, .55, .8])}"{cls}{d}/>')
    x += w

# perspective grid
vl = []
for i in range(-14, 15):
    vl.append(f'<line x1="{W/2 + i*12:.0f}" y1="{HZ}" x2="{W/2 + i*110:.0f}" y2="{H}"/>')
hl = []
for i in range(5):
    hl.append(f'<line x1="0" y1="{HZ}" x2="{W}" y2="{HZ}" class="hl" style="animation-delay:{i*0.6:.1f}s"/>')

# subtitle layout (monospace pinned with textLength)
fs = 20; cw = fs * 0.6
p1 = "> System.init()"
p2 = "I'm Phúc // Backend · Data · AI"
total = len(p1) + 3 + len(p2) + 1
sx = W / 2 - total * cw / 2
x2 = sx + (len(p1) + 3) * cw
spin_cx = sx + (len(p1) + 1.5) * cw
cur_x = x2 + len(p2) * cw
SY = 168

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="noName25 - I'm Phúc, Backend, Data, AI">
<title>noName25 // System.init()</title>
<defs>
  <linearGradient id="frame" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}"/><stop offset=".55" stop-color="{BL}"/><stop offset="1" stop-color="{OR}"/></linearGradient>
  <linearGradient id="title" gradientUnits="userSpaceOnUse" x1="250" y1="0" x2="750" y2="0" spreadMethod="reflect">
    <stop offset="0" stop-color="{CY}"/><stop offset=".5" stop-color="#5AA9FF"/><stop offset="1" stop-color="{OR}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;500 0;0 0" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <radialGradient id="glow" cx=".5" cy="1" r=".75"><stop offset="0" stop-color="{BL}" stop-opacity=".35"/><stop offset="1" stop-color="{BL}" stop-opacity="0"/></radialGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05070D" stop-opacity="1"/><stop offset="1" stop-color="#05070D" stop-opacity="0"/></linearGradient>
  <pattern id="crt" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".3"/></pattern>
  <clipPath id="floor"><rect x="0" y="{HZ}" width="{W}" height="{H - HZ}"/></clipPath>
  <clipPath id="panel"><path d="M18 1 H{W-34} L{W-1} 34 V{H-18} L{W-18} {H-1} H34 L1 {H-34} V18 Z"/></clipPath>
</defs>
<style>
  .mono{{font-family:{MONO}}}
  .tw{{animation:tw 3.5s steps(1) infinite}} @keyframes tw{{50%{{opacity:0}}}}
  .hl{{animation:hl 3s cubic-bezier(.55,0,1,.45) infinite;opacity:0}}
  @keyframes hl{{0%{{transform:translateY(0);opacity:0}}15%{{opacity:.7}}100%{{transform:translateY({H - HZ}px);opacity:.9}}}}
  .t{{clip-path:inset(0 100% 0 0);animation:type 1.1s steps(8) .2s forwards}}
  .s1{{clip-path:inset(0 100% 0 0);animation:type .9s steps(15) 1.2s forwards}}
  .s2{{clip-path:inset(0 100% 0 0);animation:type 1.6s steps(31) 3.6s forwards}}
  @keyframes type{{to{{clip-path:inset(0 0 0 0)}}}}
  .spin{{opacity:0;animation:vis 0s 2.1s forwards, hide 0s 3.4s forwards}}
  .spin circle{{transform-box:fill-box;transform-origin:center;animation:rot .7s linear infinite}}
  @keyframes rot{{to{{transform:rotate(360deg)}}}}
  .chk{{opacity:0;animation:vis .2s 3.4s forwards}}
  @keyframes vis{{to{{opacity:1}}}} @keyframes hide{{to{{opacity:0}}}}
  .cur{{opacity:0;animation:vis 0s 5.2s forwards, blink 1s steps(1) 5.2s infinite}}
  @keyframes blink{{50%{{opacity:0}}}}
  .ga{{opacity:0;animation:ga 4.2s steps(1) 1.5s infinite}}
  .gb{{opacity:0;animation:gb 4.2s steps(1) 1.5s infinite}}
  @keyframes ga{{0%,100%{{opacity:0}}88%{{opacity:.85;transform:translate(-6px,0);clip-path:inset(10% 0 55% 0)}}90%{{opacity:.85;transform:translate(4px,0);clip-path:inset(60% 0 8% 0)}}92%{{opacity:0}}}}
  @keyframes gb{{0%,100%{{opacity:0}}88%{{opacity:.85;transform:translate(6px,0);clip-path:inset(50% 0 20% 0)}}90%{{opacity:.85;transform:translate(-5px,0);clip-path:inset(5% 0 70% 0)}}92%{{opacity:0}}}}
  .main{{animation:jit 4.2s steps(1) 1.5s infinite}}
  @keyframes jit{{88%{{transform:translateX(2px)}}90%{{transform:translateX(-2px)}}92%{{transform:none}}}}
  .ring{{transform-box:fill-box;transform-origin:center;animation:rot 9s linear infinite}}
  .ring2{{transform-box:fill-box;transform-origin:center;animation:rot 5s linear infinite reverse}}
  .dot{{animation:blink 1.2s steps(1) infinite}}
  .eq rect{{transform-box:fill-box;transform-origin:bottom;animation:eq 1.1s ease-in-out infinite alternate}}
  @keyframes eq{{from{{transform:scaleY(.25)}}to{{transform:scaleY(1)}}}}
</style>

<g clip-path="url(#panel)">
  <rect width="{W}" height="{H}" fill="#05070D"/>
  <rect y="{HZ - 140}" width="{W}" height="{H - HZ + 140}" fill="url(#glow)"/>
  <g fill="#0B1424">{"".join(bld)}</g>
  <g>{"".join(win)}</g>
  <line x1="0" y1="{HZ}" x2="{W}" y2="{HZ}" stroke="{CY}" stroke-opacity=".8"/>
  <g clip-path="url(#floor)" stroke="{CY}" stroke-width="1">
    <g stroke-opacity=".28">{"".join(vl)}</g>
    <g>{"".join(hl)}</g>
    <rect x="0" y="{HZ}" width="{W}" height="18" fill="url(#fade)" stroke="none"/>
  </g>
  <rect width="{W}" height="{H}" fill="url(#crt)"/>
</g>
<path d="M18 1 H{W-34} L{W-1} 34 V{H-18} L{W-18} {H-1} H34 L1 {H-34} V18 Z" fill="none" stroke="url(#frame)" stroke-width="1.6"/>

<!-- top HUD -->
<g class="mono" font-size="12" letter-spacing="2">
  <path d="M22 18 h10 l-6 12 h-10 Z" fill="{CY}"/><path d="M36 18 h10 l-6 12 h-10 Z" fill="{OR}"/>
  <text x="56" y="29" fill="{CY}">SYS://BANHXUANPHUC</text>
  <text x="{W - 64}" y="29" fill="#7f8ea3" text-anchor="end">UTC+7 // NEO-SAIGON //<tspan fill="{OR}"> ONLINE</tspan></text>
  <circle cx="{W - 48}" cy="25" r="4" fill="{OR}" class="dot"/>
</g>

<!-- left HUD: equalizer -->
<g class="eq" fill="{CY}" fill-opacity=".75">
  {"".join(f'<rect x="{40 + i*9}" y="{80}" width="5" height="60" style="animation-delay:-{random.uniform(0,1.1):.2f}s"/>' for i in range(7))}
</g>
<text x="40" y="160" class="mono" font-size="10" letter-spacing="2" fill="#7f8ea3">NEURAL LINK</text>

<!-- right HUD: reticle -->
<g transform="translate({W - 90} 112)">
  <circle r="34" fill="none" stroke="{CY}" stroke-opacity=".35"/>
  <circle r="34" fill="none" stroke="{CY}" stroke-width="2" stroke-dasharray="30 24" class="ring"/>
  <circle r="24" fill="none" stroke="{OR}" stroke-width="2" stroke-dasharray="8 10" class="ring2"/>
  <circle r="3" fill="{OR}"/>
  <path d="M-46 0 h8 M38 0 h8 M0 -46 v8 M0 38 v8" stroke="{CY}"/>
</g>
<text x="{W - 90}" y="172" class="mono" font-size="10" letter-spacing="2" fill="#7f8ea3" text-anchor="middle">LOCK // 2077</text>

<!-- title -->
<g font-family="{SANS}" font-weight="900" font-size="78" text-anchor="middle" font-style="italic">
  <text x="{W/2}" y="122" fill="{CY}" class="ga" textLength="430" lengthAdjust="spacingAndGlyphs">noName25</text>
  <text x="{W/2}" y="122" fill="{OR}" class="gb" textLength="430" lengthAdjust="spacingAndGlyphs">noName25</text>
  <g class="main"><text x="{W/2}" y="122" fill="url(#title)" class="t" textLength="430" lengthAdjust="spacingAndGlyphs">noName25</text></g>
</g>

<!-- subtitle -->
<g class="mono" font-size="{fs}" font-weight="600">
  <text x="{sx:.1f}" y="{SY}" fill="#a0aec0" class="s1" textLength="{len(p1)*cw:.1f}" lengthAdjust="spacingAndGlyphs">{p1}</text>
  <g class="spin"><circle cx="{spin_cx:.1f}" cy="{SY - 7}" r="7" fill="none" stroke="{CY}" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="26 18"/></g>
  <path class="chk" d="M{spin_cx - 7:.1f} {SY - 7} l5 6 l10 -12" fill="none" stroke="{OR}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="{x2:.1f}" y="{SY}" fill="#a0aec0" class="s2" textLength="{len(p2)*cw:.1f}" lengthAdjust="spacingAndGlyphs">I'm <tspan fill="{OR}">Phúc</tspan> <tspan fill="{CY}">//</tspan> Backend · Data · AI</text>
  <rect x="{cur_x + 2:.1f}" y="{SY - 16}" width="10" height="19" fill="{CY}" class="cur"/>
</g>
</svg>
'''
open(sys.argv[1] if len(sys.argv) > 1 else __import__('os').path.join(__import__('os').path.dirname(__file__), '..', 'assets', 'header.svg'), "w", encoding="utf-8").write(svg)
print("ok", len(svg))
