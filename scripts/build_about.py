#!/usr/bin/env python3
"""Build assets/about.svg  ->  python scripts/build_about.py"""
import html, sys
W, H = 696, 640
CY, BL, OR, TX, DIM = "#00F0FF", "#2D7CFF", "#FF9E00", "#C9D4E3", "#6B7A90"
MONO = "'Cascadia Mono',Consolas,'SFMono-Regular',Menlo,'Courier New',monospace"
FS = 15; CW = FS * 0.6; X0 = 26

P = [("noName25", CY), ("@", DIM), ("neo-saigon", OR), (":~$ ", DIM)]
def kv(k, v, vc=TX):
    return [("  " + k.ljust(10), BL), (": ", DIM)] + (v if isinstance(v, list) else [(v, vc)])

# (y, segments, kind)  kind: cmd = typed slowly, out = streamed
L = [
    (88,  P + [("whoami", TX)], "cmd"),
    (120, [("Phúc", "url(#g)"), ("  ·  a.k.a ", DIM), ("noName25", "url(#g)")], "big"),
    (148, [("Information Systems undergrad @ UIT · VNU-HCM", TX)], "out"),
    (194, P + [("cat profile.yml", TX)], "cmd"),
    (222, kv("education", "UIT · University of Information Technology"), "out"),
    (250, kv("major", [("Information Systems", TX), (" · ", DIM), ("3rd-year", OR)]), "out"),
    (278, kv("focus", [("Backend", CY), (" · ", DIM), ("Data Warehousing", CY), (" · ", DIM), ("BPM", CY)]), "out"),
    (306, kv("exploring", [("ML", OR), (" · ", DIM), ("Deep Learning", OR), (" · ", DIM), ("TensorFlow", OR), (" · ", DIM), ("Kaggle", OR)]), "out"),
    (334, kv("stack", "Python · PHP/Laravel · SQL Server · Docker"), "out"),
    (362, kv("contact", "phuc2006aka@gmail.com", CY), "out"),
    (408, P + [("./quests --active", TX)], "cmd"),
    (436, [("  ▸ MAIN QUEST ", OR), (": ", DIM), ("ship reliable backend & data systems", TX)], "out"),
    (464, [("  ▸ SIDE QUEST ", CY), (": ", DIM), ("level up in ML / DL, one Kaggle at a time", TX)], "out"),
    (510, P, "cmd"),
]

def esc(s): return html.escape(s, quote=False)

rows, t = [], 0.5
for y, segs, kind in L:
    n = sum(len(s) for s, _ in segs)
    fs = 22 if kind == "big" else FS
    cw = fs * 0.6
    dur = max(.25, n * (0.022 if kind == "cmd" else 0.005))
    steps = n if kind == "cmd" else max(4, n // 4)
    spans = "".join(f'<tspan fill="{c}">{esc(s)}</tspan>' for s, c in segs)
    weight = ' font-weight="700"' if kind == "big" else ""
    rows.append(f'<text x="{X0}" y="{y}" font-size="{fs}"{weight} textLength="{n*cw:.1f}" lengthAdjust="spacingAndGlyphs" '
                f'style="animation:type {dur:.2f}s steps({steps}) {t:.2f}s forwards">{spans}</text>')
    if kind == "cmd" and y == 510:
        cur_x, cur_t = X0 + n * cw + 2, t + dur
    t += dur + (0.15 if kind == "cmd" else 0.05)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="About Phúc (noName25): Information Systems student at UIT, VNU-HCM. Focus: Backend, Data Warehousing, BPM.">
<title>DOSSIER // noName25</title>
<defs>
  <linearGradient id="frame" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CY}"/><stop offset=".55" stop-color="{BL}"/><stop offset="1" stop-color="{OR}"/></linearGradient>
  <linearGradient id="g" gradientUnits="userSpaceOnUse" x1="{X0}" y1="0" x2="{X0 + 330}" y2="0"><stop offset="0" stop-color="{CY}"/><stop offset=".5" stop-color="#5AA9FF"/><stop offset="1" stop-color="{OR}"/></linearGradient>
  <pattern id="crt" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".3"/></pattern>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{CY}" opacity=".12"/></pattern>
</defs>
<style>
  .mono{{font-family:{MONO}}}
  text{{white-space:pre}}
  .body text{{clip-path:inset(0 100% 0 0)}}
  @keyframes type{{to{{clip-path:inset(0 0 0 0)}}}}
  .cur{{opacity:0;animation:show 0s {cur_t:.2f}s forwards, blink 1s steps(1) {cur_t:.2f}s infinite}}
  @keyframes show{{to{{opacity:1}}}} @keyframes blink{{50%{{opacity:0}}}}
  .blink{{animation:blink 1s steps(1) infinite}}
  .bar{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:bar {t:.2f}s cubic-bezier(.6,.1,.3,1) .4s forwards}}
  @keyframes bar{{to{{transform:scaleX(1)}}}}
  .pct{{opacity:0;animation:show .2s {t + .4:.2f}s forwards}}
  .sweep{{animation:sweep 6s linear {t:.2f}s infinite;opacity:0}}
  @keyframes sweep{{0%{{opacity:1;transform:translateY(-80px)}}100%{{opacity:1;transform:translateY({H}px)}}}}
</style>

<path d="M16 1 H{W-30} L{W-1} 30 V{H-16} L{W-16} {H-1} H30 L1 {H-30} V16 Z" fill="#05070D" stroke="url(#frame)" stroke-width="1.5"/>
<rect x="2" y="47" width="{W-4}" height="{H-100}" fill="url(#dots)"/>
<path d="M1 46 H{W-1}" stroke="{CY}" stroke-opacity=".25"/>
<path d="M1 {H-52} H{W-1}" stroke="{CY}" stroke-opacity=".25"/>
<rect x="2" y="0" width="{W-4}" height="80" fill="{CY}" fill-opacity=".04" class="sweep"/>

<g class="mono" font-size="12" letter-spacing="1.5">
  <rect x="18" y="16" width="8" height="14" fill="{OR}"/>
  <text x="34" y="28" fill="{CY}">DOSSIER // noName25.yml</text>
  <text x="{W-40}" y="28" fill="{OR}" text-anchor="end">SECURE LINK</text>
  <circle cx="{W-28}" cy="24" r="4" fill="{CY}" class="blink"/>
</g>

<g class="mono body">
  {chr(10).join("  " + r for r in rows)}
</g>
<rect x="{cur_x:.1f}" y="{510 - 13}" width="9" height="17" fill="{CY}" class="cur"/>

<g class="mono" font-size="12" letter-spacing="1.5">
  <text x="20" y="{H-30}" fill="{DIM}">LOC <tspan fill="{TX}">HCMC, VN</tspan>  ·  TZ <tspan fill="{TX}">UTC+7</tspan></text>
  <text x="{W-236}" y="{H-30}" fill="{DIM}" text-anchor="end">SYNC</text>
  <rect x="{W-226}" y="{H-40}" width="160" height="12" fill="none" stroke="{CY}" stroke-opacity=".5"/>
  <rect x="{W-224}" y="{H-38}" width="156" height="8" fill="url(#frame)" class="bar"/>
  <text x="{W-20}" y="{H-30}" fill="{OR}" text-anchor="end" class="pct">100%</text>
</g>
<rect x="2" y="47" width="{W-4}" height="{H-100}" fill="url(#crt)"/>
</svg>
'''
open(sys.argv[1] if len(sys.argv) > 1 else __import__('os').path.join(__import__('os').path.dirname(__file__), '..', 'assets', 'about.svg'), "w", encoding="utf-8").write(svg)
print("ok", len(svg), "typing ends at", round(t, 2))
