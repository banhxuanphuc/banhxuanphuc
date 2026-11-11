#!/usr/bin/env python3
"""
Build assets/about.svg - the DOSSIER panel (plain info list + a small Claude easter egg).

Edit NAME / FIELDS / NOW below, then:
    python scripts/build_about.py
"""
from __future__ import annotations

import html
from pathlib import Path

from theme import CY, DIM, MONO, OR, SOFT, T_READY, TX, base_css, defs, fetch_icon, frame, loader_css, not_found, title_bar

W, H = 696, 640
FS, CW = 15.5, 15.5 * 0.6
KEY_X, VAL_X = 28, 170

FIELDS = [
    ("EDUCATION", [("University of Information Technology (UIT), VNU-HCM", TX)]),
    ("MAJOR", [("Information Systems", TX), (" · ", DIM), ("3rd-year", TX)]),
    ("FOCUS", [("Backend", TX), (" · ", DIM), ("Data Warehousing", TX), (" · ", DIM), ("BPM", TX)]),
    ("EXPLORING", [("ML", TX), (" · ", DIM), ("Deep Learning", TX), (" · ", DIM), ("TensorFlow", TX), (" · ", DIM), ("Kaggle", TX)]),
    ("STACK", [("Python", TX), (" · ", DIM), ("PHP/Laravel", TX), (" · ", DIM), ("SQL Server", TX), (" · ", DIM), ("Docker", TX)]),
    ("CONTACT", [("phuc2006aka@gmail.com", CY)]),
]
NOW = ["building backend & data systems", "levelling up in ML / DL on Kaggle"]


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def line(x: float, y: float, segs: list[tuple[str, str]], fs: float, delay: float, extra: str = "") -> str:
    n = sum(len(s) for s, _ in segs)
    spans = "".join(f'<tspan fill="{c}">{esc(s)}</tspan>' for s, c in segs)
    return (f'<text x="{x}" y="{y}" font-size="{fs}" textLength="{n * fs * .6:.1f}" lengthAdjust="spacingAndGlyphs"{extra} '
            f'class="in" style="animation-delay:{delay:.2f}s">{spans}</text>')


def main() -> None:
    t = T_READY + .6
    rows = [
        line(KEY_X, 106, [("Phúc", TX)], 36, t, ' font-weight="700"'),
        line(KEY_X, 140, [("a.k.a ", DIM), ("noName25", OR)], 18, t + .08, ' font-weight="600"'),
        line(KEY_X, 170, [("Information Systems undergrad @ UIT · VNU-HCM", DIM)], 14, t + .16),
    ]
    y = 240
    for i, (k, segs) in enumerate(FIELDS):
        d = t + .3 + i * .08
        rows.append(f'<text x="{KEY_X}" y="{y}" font-size="11.5" letter-spacing="2" fill="{CY}" fill-opacity=".8" '
                    f'class="in" style="animation-delay:{d:.2f}s">{k}</text>')
        rows.append(line(VAL_X, y, segs, FS, d))
        y += 40
    y += 34
    rows.append(f'<text x="{KEY_X}" y="{y}" font-size="11.5" letter-spacing="2" fill="{CY}" fill-opacity=".8" '
                f'class="in" style="animation-delay:{t + .9:.2f}s">NOW</text>')
    for i, s in enumerate(NOW):
        rows.append(line(VAL_X, y + i * 34, [("▸ ", CY), (s, TX)], FS, t + .95 + i * .08))

    claude = fetch_icon("claude")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Dossier - Phúc a.k.a noName25. Information Systems, UIT VNU-HCM. Focus: Backend, Data Warehousing, BPM. Exploring ML, Deep Learning, TensorFlow, Kaggle.">
<title>DOSSIER // Phúc a.k.a noName25</title>
<defs>{defs()}</defs>
<style>
  {base_css()}
  {loader_css()}
  text{{white-space:pre}}
  .in{{opacity:0;animation:in .45s ease-out forwards}}
  @keyframes in{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:none}}}}
  .egg{{opacity:0;animation:egg 1.2s ease-out {t + 1.2:.2f}s forwards}}
  @keyframes egg{{to{{opacity:.55}}}}
  .spin{{transform-box:fill-box;transform-origin:center;animation:rot 28s linear infinite}}
  @keyframes rot{{to{{transform:rotate(360deg)}}}}
  .glow{{transform-box:fill-box;transform-origin:center;animation:glow 4s ease-in-out infinite}}
  @keyframes glow{{50%{{opacity:.35;transform:scale(1.15)}}}}
</style>

{frame(W, H)}
{not_found(W / 2, H / 2, 110)}
<g class="content">
  {title_bar(W, "DOSSIER")}
  <g class="egg">
    <circle cx="592" cy="122" r="40" fill="{SOFT}" opacity=".08" class="glow"/>
    <g class="spin"><path transform="translate(564 94) scale(2.333)" fill="{SOFT}" d="{claude}"/></g>
  </g>
  <g font-family="{MONO}">
    {(chr(10) + "    ").join(rows)}
  </g>
  <path d="M{KEY_X} 200 H{W - 28}" stroke="{CY}" stroke-opacity=".14"/>
  <path d="M{KEY_X} 474 H{W - 28}" stroke="{CY}" stroke-opacity=".14"/>
</g>
</svg>
'''
    out = Path(__file__).resolve().parent.parent / "assets" / "about.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
