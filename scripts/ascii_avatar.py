#!/usr/bin/env python3
"""
Build an animated, cyberpunk-styled ASCII avatar (SVG) for a GitHub profile.

Two input modes:
  1) From an existing ASCII text file (no dependencies):
       python scripts/ascii_avatar.py --text scripts/avatar.txt
  2) From a photo (needs Pillow:  pip install pillow):
       python scripts/ascii_avatar.py --image me.jpg --cols 100
       python scripts/ascii_avatar.py --image me.jpg --cols 100 --invert

Output: assets/ascii-avatar.svg (480 x 640, same height as assets/about.svg)

Animation (pure CSS inside the SVG, works in GitHub <img>):
  - boot  : rows decode top -> bottom with a scanner beam + progress bar
  - glitch: a few horizontal bands jump a few pixels and flash orange
  - CRT   : static scanlines + a slow sweeping light band
"""
from __future__ import annotations

import argparse
import html
from pathlib import Path

# Dense characters last. On a black background dense = bright.
RAMP = " .:^~!7?JY5PGB#&@"

W, H = 480, 640                     # panel size (keep in sync with about.svg height)
ART_BOX = (20, 58, 440, 520)       # x, y, w, h available for the art
CYAN, BLUE, ORANGE = "#00F0FF", "#2D7CFF", "#FF9E00"

# (first_row, last_row, keyframe, duration_s, delay_s) for glitch bands,
# expressed as fractions of the art height so it works for any row count.
GLITCH_BANDS = [
    (0.16, 0.21, "gl-a", 4.3, 2.6),
    (0.38, 0.42, "gl-b", 5.9, 3.4),
    (0.60, 0.65, "gl-a", 6.7, 4.1),
    (0.83, 0.86, "gl-b", 3.7, 2.9),
]


def load_text(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    # drop empty lines at top/bottom
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    # remove common left indent
    indent = min((len(l) - len(l.lstrip(" ")) for l in lines if l.strip()), default=0)
    return [l[indent:].rstrip() for l in lines]


def load_image(path: Path, cols: int, invert: bool) -> list[str]:
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("Pillow is required for --image:  pip install pillow") from exc
    img = Image.open(path).convert("L")
    img = ImageOps.autocontrast(img)
    w, h = img.size
    rows = max(1, int(cols * h / w * 0.5))      # chars are ~2x taller than wide
    img = img.resize((cols, rows))
    px = img.load()
    out = []
    for y in range(rows):
        line = []
        for x in range(cols):
            v = px[x, y] / 255
            if invert:
                v = 1 - v
            line.append(RAMP[min(len(RAMP) - 1, int(v * len(RAMP)))])
        out.append("".join(line).rstrip())
    return out


def build_svg(lines: list[str]) -> str:
    rows = len(lines)
    cols = max(len(l) for l in lines)
    bx, by, bw, bh = ART_BOX
    # monospace cell: width = 0.6 em, height = 1.2 em
    fs = min(bw / (cols * 0.6), bh / (rows * 1.2))
    cw, lh = fs * 0.6, fs * 1.2
    art_w, art_h = cols * cw, rows * lh
    ox = bx + (bw - art_w) / 2
    oy = by + (bh - art_h) / 2
    boot_step, boot_start = 0.022, 0.35
    boot_end = boot_start + rows * boot_step + 0.45

    def row_svg(i: int, line: str) -> str:
        if not line.strip():
            return ""
        y = oy + (i + 0.85) * lh
        text = html.escape(line, quote=False)
        return (
            f'<text class="r" x="{ox:.2f}" y="{y:.2f}" textLength="{len(line) * cw:.2f}" '
            f'lengthAdjust="spacingAndGlyphs" style="animation-delay:{boot_start + i * boot_step:.3f}s">'
            f"{text}</text>"
        )

    # group rows into glitch bands
    band_of = {}
    for b, (f0, f1, *_rest) in enumerate(GLITCH_BANDS):
        for r in range(int(f0 * rows), int(f1 * rows) + 1):
            band_of[r] = b
    body, i = [], 0
    while i < rows:
        b = band_of.get(i)
        if b is None:
            body.append(row_svg(i, lines[i]))
            i += 1
            continue
        _, _, kf, dur, delay = GLITCH_BANDS[b]
        chunk = []
        while i < rows and band_of.get(i) == b:
            chunk.append(row_svg(i, lines[i]))
            i += 1
        body.append(
            f'<g style="animation:{kf} {dur}s steps(1) {delay}s infinite">' + "".join(chunk) + "</g>"
        )

    beam_y0 = oy - 4
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Animated ASCII avatar">
<title>ASCII avatar</title>
<defs>
  <linearGradient id="frame" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".55" stop-color="{BLUE}"/><stop offset="1" stop-color="{ORANGE}"/>
  </linearGradient>
  <linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="{ox:.1f}" y1="{oy:.1f}" x2="{ox + art_w:.1f}" y2="{oy + art_h:.1f}">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="#4FA8FF"/><stop offset="1" stop-color="{ORANGE}"/>
  </linearGradient>
  <linearGradient id="sweep" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN}" stop-opacity=".16"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
  </linearGradient>
  <pattern id="crt" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".35"/></pattern>
  <clipPath id="art"><rect x="{bx}" y="{by - 6}" width="{bw}" height="{bh + 12}"/></clipPath>
</defs>
<style>
  .mono{{font-family:'Cascadia Mono',Consolas,'SFMono-Regular',Menlo,'Courier New',monospace}}
  .r{{opacity:0;white-space:pre;animation:boot .45s ease-out forwards}}
  @keyframes boot{{0%{{opacity:0;transform:translateX(-14px)}}55%{{opacity:1;transform:translateX(4px)}}100%{{opacity:1;transform:translateX(0)}}}}
  @keyframes gl-a{{0%,100%{{transform:translateX(0);fill:url(#ink)}}91%{{transform:translateX(-7px);fill:{ORANGE}}}93%{{transform:translateX(5px);fill:{CYAN}}}95%{{transform:translateX(-2px);fill:url(#ink)}}97%{{transform:translateX(0)}}}}
  @keyframes gl-b{{0%,100%{{transform:translateX(0);fill:url(#ink)}}88%{{transform:translateX(6px);fill:{CYAN}}}90%{{transform:translateX(-4px);fill:{ORANGE}}}92%{{transform:translateX(0);fill:url(#ink)}}}}
  .beam{{animation:beam {rows * boot_step + 0.5:.2f}s linear {boot_start:.2f}s forwards;opacity:0}}
  @keyframes beam{{0%{{opacity:1;transform:translateY(0)}}96%{{opacity:1}}100%{{opacity:0;transform:translateY({art_h + 8:.1f}px)}}}}
  .sweep{{opacity:0;animation:sweep 5s linear {boot_end:.2f}s infinite}}
  @keyframes sweep{{0%{{opacity:1;transform:translateY(-120px)}}100%{{opacity:1;transform:translateY({H}px)}}}}
  .bar{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:bar {boot_end - boot_start:.2f}s cubic-bezier(.6,.1,.3,1) {boot_start:.2f}s forwards}}
  @keyframes bar{{to{{transform:scaleX(1)}}}}
  .dec{{animation:hide 0s {boot_end:.2f}s forwards}}
  .ok{{opacity:0;animation:show .3s {boot_end:.2f}s forwards}}
  @keyframes hide{{to{{opacity:0}}}}
  @keyframes show{{to{{opacity:1}}}}
  .blink{{animation:blink 1s steps(1) infinite}}
  @keyframes blink{{50%{{opacity:0}}}}
  .flick{{animation:flick 7s steps(1) {boot_end:.2f}s infinite}}
  @keyframes flick{{0%,100%{{opacity:1}}42%{{opacity:.82}}43%{{opacity:1}}77%{{opacity:.9}}78%{{opacity:1}}}}
</style>

<path d="M16 1 H{W - 30} L{W - 1} 30 V{H - 16} L{W - 16} {H - 1} H30 L1 {H - 30} V16 Z" fill="#05070D" stroke="url(#frame)" stroke-width="1.5"/>
<path d="M1 46 H{W - 1}" stroke="{CYAN}" stroke-opacity=".25"/>
<path d="M1 {H - 52} H{W - 1}" stroke="{CYAN}" stroke-opacity=".25"/>
<g class="mono" font-size="12" letter-spacing="1.5">
  <rect x="18" y="16" width="8" height="14" fill="{CYAN}"/>
  <text x="34" y="28" fill="{CYAN}">SUBJECT_SCAN.ascii</text>
  <text x="{W - 40}" y="28" fill="{ORANGE}" text-anchor="end">{rows}&#215;{cols}</text>
  <circle cx="{W - 28}" cy="24" r="4" fill="{ORANGE}" class="blink"/>
</g>

<g clip-path="url(#art)">
  <g class="mono flick" font-size="{fs:.3f}" fill="url(#ink)" xml:space="preserve">
{chr(10).join("    " + b for b in body if b)}
  </g>
  <rect x="{bx}" y="0" width="{bw}" height="120" fill="url(#sweep)" class="sweep"/>
  <g class="beam"><rect x="{bx}" y="{beam_y0:.1f}" width="{bw}" height="2" fill="{CYAN}"/><rect x="{bx}" y="{beam_y0 - 14:.1f}" width="{bw}" height="14" fill="{CYAN}" opacity=".12"/></g>
</g>
<rect x="1" y="47" width="{W - 2}" height="{H - 100}" fill="url(#crt)"/>

<g class="mono" font-size="12" letter-spacing="1.5">
  <text x="20" y="{H - 30}" fill="#7f8ea3" class="dec">DECODING<tspan class="blink">_</tspan></text>
  <text x="20" y="{H - 30}" fill="{ORANGE}" class="ok">IDENTITY &#9656; VERIFIED</text>
  <rect x="{W - 200}" y="{H - 40}" width="180" height="12" fill="none" stroke="{CYAN}" stroke-opacity=".5"/>
  <rect x="{W - 198}" y="{H - 38}" width="176" height="8" fill="url(#frame)" class="bar"/>
</g>
</svg>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", type=Path, help="ASCII art text file")
    src.add_argument("--image", type=Path, help="photo to convert (needs Pillow)")
    ap.add_argument("--cols", type=int, default=100, help="characters per row for --image")
    ap.add_argument("--invert", action="store_true", help="dark pixels -> dense chars")
    ap.add_argument("-o", "--out", type=Path, default=Path("assets/ascii-avatar.svg"))
    a = ap.parse_args()

    lines = load_text(a.text) if a.text else load_image(a.image, a.cols, a.invert)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(build_svg(lines), encoding="utf-8")
    print(f"wrote {a.out}  ({len(lines)} rows x {max(map(len, lines))} cols)")


if __name__ == "__main__":
    main()
