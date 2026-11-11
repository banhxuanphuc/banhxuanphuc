#!/usr/bin/env python3
"""
Build assets/header.svg - the "artificial human boot sequence" banner.

    python scripts/build_header.py

Timeline (seconds):
  0.3  > System.init()  types, spinner, check
  2.6  init line drifts up + shrinks, NEURAL LINK download bar slides into focus
  2.9  bar runs 0 -> 100 % in 3 s, then CONNECTED (orange)
  6.2  everything drifts up again, ">> (check) I am Phuc, you can call me noName25" types
  9.0  = theme.T_READY, the other panels start loading
"""
from __future__ import annotations

import random
from pathlib import Path

from theme import BG, BLUE, CY, DIM, MONO, OR, RADIUS, T_READY, TX, base_css, defs, frame

W, H = 1000, 300
SHIFT = 60                       # px the stack drifts up at each stage
INIT_Y, BAR_Y, FINAL_Y = 174, 236, 314
T_SHIFT1, T_BAR, BAR_DUR, T_SHIFT2 = 2.6, 2.9, 3.0, 6.2
T_FINAL = 6.5


def skyline() -> str:
    random.seed(2077)
    bld, win, x = [], [], 0
    while x < W:
        w = random.choice([22, 28, 34, 40, 18, 46])
        edge = abs(x + w / 2 - W / 2) / (W / 2)            # low in the middle, tall at the edges
        h = random.randint(16, 32) + int(edge ** 1.4 * random.randint(24, 62))
        top = H - h
        bld.append(f'<rect x="{x}" y="{top}" width="{w - 2}" height="{h}"/>')
        if random.random() < .3 and h > 50:
            bld.append(f'<rect x="{x + w // 2 - 1}" y="{top - 10}" width="2" height="10"/>')
        for wy in range(top + 5, H - 4, 6):
            for wx in range(x + 4, x + w - 5, 6):
                if random.random() < .15:
                    c = OR if random.random() < .08 else CY
                    tw = random.random() < .12
                    win.append(f'<rect x="{wx}" y="{wy}" width="2" height="2" fill="{c}" '
                               f'opacity="{random.choice([.3, .5, .75])}"'
                               + (f' class="tw" style="animation-delay:{random.uniform(0, 4):.1f}s"' if tw else "")
                               + "/>")
        x += w
    return f'<g fill="#111927">{"".join(bld)}</g><g>{"".join(win)}</g>'


def main() -> None:
    # init line  "> System.init()"  + spinner slot
    fs1, cw1 = 30, 18
    p1 = "> System.init()"
    x1 = W / 2 - (len(p1) + 2) * cw1 / 2
    spin_x = x1 + len(p1) * cw1 + cw1

    # neural link bar
    bw, bx = 440, W / 2 - 220
    pct = "".join(
        f'<text x="{bx + bw}" y="{BAR_Y - 10}" text-anchor="end" class="pc" '
        f'style="animation:show 0s {T_BAR + i * BAR_DUR / 10:.2f}s forwards'
        + (f', hide 0s {T_BAR + (i + 1) * BAR_DUR / 10:.2f}s forwards' if i < 10 else "")
        + f'">{i * 10}%</text>'
        for i in range(11)
    )
    t_conn = T_BAR + BAR_DUR + .1

    # final line  ">> (check) I am Phúc, you can call me noName25"
    fs3, cw3 = 26, 15.6
    msg = "I am Phúc, you can call me noName25"
    x3 = W / 2 - (3 + 2 + len(msg) + 1) * cw3 / 2
    chk_cx = x3 + 3 * cw3 + cw3 * .8
    tx3 = x3 + 5 * cw3
    t_type = T_FINAL + .4
    type_dur = T_READY - .4 - t_type
    cur_x = tx3 + len(msg) * cw3 + 4

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="System.init() - neural link connected - I am Phúc, you can call me noName25">
<title>System.init() // I am Phúc, you can call me noName25</title>
<defs>
  {defs()}
  <radialGradient id="glow" cx=".5" cy="1" r=".7"><stop offset="0" stop-color="{BLUE}" stop-opacity=".22"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
  <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
  <clipPath id="panel"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="{RADIUS}"/></clipPath>
</defs>
<style>
  {base_css()}
  text{{white-space:pre}}
  .tw{{animation:blink 3.5s steps(1) infinite}}
  .up1{{animation:up .55s cubic-bezier(.5,0,.2,1) {T_SHIFT1}s forwards}}
  .up2{{animation:up .55s cubic-bezier(.5,0,.2,1) {T_SHIFT2}s forwards}}
  @keyframes up{{to{{transform:translateY(-{SHIFT}px)}}}}
  .shrink1,.shrink2,.dim{{transform-box:fill-box;transform-origin:center}}
  .shrink1{{animation:shrink1 .55s ease {T_SHIFT1}s forwards}}
  @keyframes shrink1{{to{{transform:scale(.72);opacity:.6}}}}
  .shrink2{{animation:shrink2 .55s ease {T_SHIFT2}s forwards}}
  @keyframes shrink2{{to{{transform:scale(.85);opacity:.6}}}}
  .dim{{animation:dim .55s ease {T_SHIFT2}s forwards}}
  @keyframes dim{{to{{transform:scale(.82);opacity:.7}}}}
  .type1{{clip-path:inset(0 100% 0 0);animation:type .8s steps({len(p1)}) .3s forwards}}
  .type3{{clip-path:inset(0 100% 0 0);animation:type {type_dur:.2f}s steps({len(msg)}) {t_type:.2f}s forwards}}
  @keyframes type{{to{{clip-path:inset(0 0 0 0)}}}}
  .spin{{opacity:0;animation:show 0s 1.15s forwards, hide 0s 2.35s forwards}}
  .spin circle{{transform-box:fill-box;transform-origin:center;animation:rot .7s linear infinite}}
  @keyframes rot{{to{{transform:rotate(360deg)}}}}
  .ok1{{opacity:0;animation:show .15s 2.35s forwards}}
  .neural{{opacity:0;animation:rise .45s ease-out {T_SHIFT1 + .1}s forwards}}
  @keyframes rise{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}
  .fill{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:fill {BAR_DUR}s steps(30) {T_BAR}s forwards}}
  @keyframes fill{{to{{transform:scaleX(1)}}}}
  .pc{{opacity:0}}
  .hs{{opacity:0;animation:show 0s {T_BAR}s forwards, hide 0s {t_conn:.2f}s forwards}}
  .conn{{opacity:0;animation:show .2s {t_conn:.2f}s forwards}}
  .final{{opacity:0;animation:show .2s {T_FINAL}s forwards}}
  .ok3{{transform-box:fill-box;transform-origin:center;transform:scale(0);animation:pop .35s cubic-bezier(.3,1.6,.5,1) {T_FINAL + .1}s forwards}}
  @keyframes pop{{to{{transform:scale(1)}}}}
  .cur{{opacity:0;animation:show 0s {T_READY - .4:.2f}s forwards, blink 1s steps(1) {T_READY - .4:.2f}s infinite}}
</style>

{frame(W, H)}
<g clip-path="url(#panel)">
  <rect y="{H - 170}" width="{W}" height="170" fill="url(#glow)"/>
  {skyline()}
  <rect width="{W}" height="{H}" fill="url(#crt)"/>
</g>

<g class="mono" font-size="12" letter-spacing="2">
  <text x="{W - 40}" y="30" fill="{DIM}" text-anchor="end">UTC+7 // NEO-SAIGON // <tspan fill="{OR}">ONLINE</tspan></text>
  <circle cx="{W - 26}" cy="26" r="4" fill="{OR}" class="blink"/>
</g>

<g class="mono up1"><g class="up2">
  <!-- stage 1 : > System.init() -->
  <g class="shrink1"><g class="shrink2">
    <text x="{x1:.1f}" y="{INIT_Y}" font-size="{fs1}" font-weight="600" fill="{TX}" class="type1"
          textLength="{len(p1) * cw1}" lengthAdjust="spacingAndGlyphs"><tspan fill="{CY}">&gt;</tspan> System.init()</text>
    <g class="spin"><circle cx="{spin_x:.1f}" cy="{INIT_Y - 10}" r="10" fill="none" stroke="{CY}" stroke-width="3" stroke-linecap="round" stroke-dasharray="36 28"/></g>
    <path class="ok1" d="M{spin_x - 10:.1f} {INIT_Y - 10} l7 8 l13 -16" fill="none" stroke="{CY}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>
  </g></g>

  <!-- stage 2 : neural link -->
  <g class="dim"><g class="neural" font-size="14" letter-spacing="3">
    <text x="{bx}" y="{BAR_Y - 10}" fill="{CY}">NEURAL LINK</text>
    <g fill="{TX}">{pct}</g>
    <rect x="{bx}" y="{BAR_Y}" width="{bw}" height="12" rx="6" fill="none" stroke="{CY}" stroke-opacity=".45"/>
    <rect x="{bx + 3}" y="{BAR_Y + 3}" width="{bw - 6}" height="6" rx="3" fill="url(#bar)" class="fill"/>
    <text x="{W / 2}" y="{BAR_Y + 34}" text-anchor="middle" fill="{DIM}" font-size="12" class="hs">handshaking with cortex<tspan class="blink">_</tspan></text>
    <text x="{W / 2}" y="{BAR_Y + 36}" text-anchor="middle" fill="{OR}" font-size="16" font-weight="700" letter-spacing="6" class="conn">CONNECTED</text>
  </g></g>

  <!-- stage 3 : hello -->
  <g class="final" font-size="{fs3}" font-weight="600">
    <text x="{x3:.1f}" y="{FINAL_Y}" fill="{CY}" textLength="{2 * cw3}" lengthAdjust="spacingAndGlyphs">&gt;&gt;</text>
    <g class="ok3">
      <circle cx="{chk_cx:.1f}" cy="{FINAL_Y - 9}" r="12" fill="{OR}" fill-opacity=".14" stroke="{OR}" stroke-width="2.2"/>
      <path d="M{chk_cx - 6:.1f} {FINAL_Y - 9} l4.5 5 l8 -10" fill="none" stroke="{OR}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
    </g>
    <text x="{tx3:.1f}" y="{FINAL_Y}" fill="{TX}" class="type3" textLength="{len(msg) * cw3:.1f}" lengthAdjust="spacingAndGlyphs">I am <tspan fill="{CY}">Phúc</tspan>, you can call me <tspan fill="{OR}" font-weight="700">noName25</tspan></text>
    <rect x="{cur_x:.1f}" y="{FINAL_Y - 22}" width="12" height="26" rx="1" fill="{CY}" class="cur"/>
  </g>
</g></g>
</svg>
'''
    out = Path(__file__).resolve().parent.parent / "assets" / "header.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
