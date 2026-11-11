#!/usr/bin/env python3
"""
Build an animated ASCII avatar (SVG) for the GitHub profile.

  From an ASCII text file (no dependencies):
      python scripts/ascii_avatar.py --text scripts/avatar.txt
  From a photo (pip install pillow):
      python scripts/ascii_avatar.py --image me.jpg --cols 100 [--invert]

Output: assets/ascii-avatar.svg (480 x 640, same height as assets/about.svg)

Animation (pure CSS, works inside a GitHub <img>):
  - 404 ghost until the header finishes (theme.T_READY), then flicker in
  - boot  : rows decode top -> bottom with a scanner beam
  - glitch: horizontal, vertical and diagonal slices jump a few pixels
  - every 15 s the eyes flash red/white as an (X 0) glitch face
"""
from __future__ import annotations

import argparse
import html
from pathlib import Path

from theme import BG, BLUE, CY, DIM, OR, T_READY, base_css, defs, frame, loader_css, not_found, title_bar

RAMP = " .:^~!7?JY5PGB#&@"      # dense last: on black, dense = bright
W, H = 480, 640
ART_BOX = (20, 58, 440, 530)     # x, y, w, h for the art
RED = "#FF2A3D"

# horizontal glitch bands as fractions of the art height: (from, to, keyframe, duration, delay)
H_BANDS = [(0.16, 0.21, "gl-a", 4.3, 2.6), (0.38, 0.42, "gl-b", 5.9, 3.4),
           (0.60, 0.65, "gl-a", 6.7, 4.1), (0.83, 0.86, "gl-b", 3.7, 2.9)]
# vertical / diagonal slices: (kind, x_frac, width_px, dx, dy, duration, delay)
SLICES = [("v", 0.22, 22, 0, -9, 5.3, 3.0), ("v", 0.63, 16, 0, 7, 7.1, 5.2),
          ("d", 0.40, 18, 6, -6, 6.3, 4.4)]
# eye positions (row, col) in the text grid for the (X 0) flash - tuned for scripts/avatar.txt
EYES = [(24.6, 30.0, "X"), (23.4, 62.0, "0")]
EYE_EVERY = 15


def load_text(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    indent = min((len(l) - len(l.lstrip(" ")) for l in lines if l.strip()), default=0)
    return [l[indent:].rstrip() for l in lines]


def load_image(path: Path, cols: int, invert: bool) -> list[str]:
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("Pillow is required for --image:  pip install pillow") from exc
    img = ImageOps.autocontrast(Image.open(path).convert("L"))
    w, h = img.size
    rows = max(1, int(cols * h / w * 0.5))
    img = img.resize((cols, rows))
    px = img.load()
    out = []
    for y in range(rows):
        line = ""
        for x in range(cols):
            v = px[x, y] / 255
            v = 1 - v if invert else v
            line += RAMP[min(len(RAMP) - 1, int(v * len(RAMP)))]
        out.append(line.rstrip())
    return out


def build_svg(lines: list[str]) -> str:
    T = T_READY
    rows, cols = len(lines), max(len(l) for l in lines)
    bx, by, bw, bh = ART_BOX
    fs = min(bw / (cols * 0.6), bh / (rows * 1.2))
    cw, lh = fs * 0.6, fs * 1.2
    art_w, art_h = cols * cw, rows * lh
    ox, oy = bx + (bw - art_w) / 2, by + (bh - art_h) / 2
    step, start = 0.022, T + 0.6
    boot_end = start + rows * step + 0.45

    def row_svg(i: int, line: str) -> str:
        if not line.strip():
            return ""
        return (f'<text class="r" x="{ox:.2f}" y="{oy + (i + .85) * lh:.2f}" textLength="{len(line) * cw:.2f}" '
                f'lengthAdjust="spacingAndGlyphs" style="animation-delay:{start + i * step:.3f}s">'
                f'{html.escape(line, quote=False)}</text>')

    band_of = {r: b for b, (f0, f1, *_r) in enumerate(H_BANDS) for r in range(int(f0 * rows), int(f1 * rows) + 1)}
    body, i = [], 0
    while i < rows:
        b = band_of.get(i)
        if b is None:
            body.append(row_svg(i, lines[i]))
            i += 1
            continue
        _, _, kf, dur, delay = H_BANDS[b]
        chunk = []
        while i < rows and band_of.get(i) == b:
            chunk.append(row_svg(i, lines[i]))
            i += 1
        body.append(f'<g style="animation:{kf} {dur}s steps(1) {T + delay:.1f}s infinite">{"".join(chunk)}</g>')

    # vertical / diagonal slices = clipped, shifted copies of the art
    clips, slices = [], []
    for k, (kind, xf, sw, dx, dy, dur, delay) in enumerate(SLICES):
        x = ox + xf * art_w
        shape = (f'<rect x="{x:.1f}" y="{oy:.1f}" width="{sw}" height="{art_h:.1f}"/>' if kind == "v" else
                 f'<path d="M{x:.1f} {oy:.1f} h{sw} L{x + sw - art_h * .35:.1f} {oy + art_h:.1f} h-{sw} Z"/>')
        clips.append(f'<clipPath id="sl{k}">{shape}</clipPath>')
        slices.append(f'<g clip-path="url(#sl{k})" class="sl" style="animation-duration:{dur}s;animation-delay:{T + delay:.1f}s">'
                      f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{BG}"/>'
                      f'<use href="#rows" transform="translate({dx} {dy})"/></g>')

    # (X 0) eye flash
    eye_fs = lh * 3.2
    eyes = "".join(
        f'<text x="{ox + c * cw + 2:.1f}" y="{oy + r * lh + eye_fs * .35:.1f}" fill="{RED}" opacity=".85">{g}</text>'
        f'<text x="{ox + c * cw:.1f}" y="{oy + r * lh + eye_fs * .35:.1f}" fill="#fff">{g}</text>'
        for r, c, g in EYES)
    ey0 = oy + (min(r for r, _, _ in EYES) - 2) * lh
    ey1 = oy + (max(r for r, _, _ in EYES) + 2) * lh

    beam_y0 = oy - 4
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Animated ASCII avatar">
<title>ASCII avatar</title>
<defs>
  {defs()}
  <linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="{ox:.1f}" y1="{oy:.1f}" x2="{ox + art_w:.1f}" y2="{oy + art_h:.1f}">
    <stop offset="0" stop-color="{CY}"/><stop offset=".55" stop-color="#4FA8FF"/><stop offset="1" stop-color="{BLUE}"/>
  </linearGradient>
  <linearGradient id="sweep" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{CY}" stop-opacity="0"/><stop offset=".5" stop-color="{CY}" stop-opacity=".14"/><stop offset="1" stop-color="{CY}" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="art"><rect x="{bx}" y="{by - 6}" width="{bw}" height="{bh + 12}"/></clipPath>
  {"".join(clips)}
</defs>
<style>
  {base_css()}
  {loader_css()}
  .r{{opacity:0;white-space:pre;animation:boot .45s ease-out forwards}}
  @keyframes boot{{0%{{opacity:0;transform:translateX(-14px)}}55%{{opacity:1;transform:translateX(4px)}}100%{{opacity:1;transform:translateX(0)}}}}
  @keyframes gl-a{{0%,100%{{transform:translateX(0);fill:url(#ink)}}91%{{transform:translateX(-7px);fill:{RED}}}93%{{transform:translateX(5px);fill:#fff}}95%{{transform:translateX(-2px);fill:url(#ink)}}97%{{transform:translateX(0)}}}}
  @keyframes gl-b{{0%,100%{{transform:translateX(0);fill:url(#ink)}}88%{{transform:translateX(6px);fill:#fff}}90%{{transform:translateX(-4px);fill:{CY}}}92%{{transform:translateX(0);fill:url(#ink)}}}}
  .sl{{opacity:0;animation-name:sl;animation-timing-function:steps(1);animation-iteration-count:infinite}}
  @keyframes sl{{0%,100%{{opacity:0}}90%{{opacity:1}}92%{{opacity:0}}94%{{opacity:1}}95%{{opacity:0}}}}
  .eye{{opacity:0;animation:eye {EYE_EVERY}s steps(1) {T + 7:.1f}s infinite}}
  @keyframes eye{{0%,100%{{opacity:0}}93%{{opacity:1;transform:translateX(-3px)}}94%{{opacity:1;transform:translateX(3px)}}95%{{opacity:0}}96%{{opacity:1;transform:none}}97.5%{{opacity:0}}}}
  .beam{{opacity:0;animation:beam {rows * step + 0.5:.2f}s linear {start:.2f}s forwards}}
  @keyframes beam{{0%{{opacity:1;transform:translateY(0)}}96%{{opacity:1}}100%{{opacity:0;transform:translateY({art_h + 8:.1f}px)}}}}
  .sweep{{opacity:0;animation:sweep 5s linear {boot_end:.2f}s infinite}}
  @keyframes sweep{{0%{{opacity:1;transform:translateY(-120px)}}100%{{opacity:1;transform:translateY({H}px)}}}}
  .dec{{animation:hide 0s {boot_end:.2f}s forwards}}
  .ok{{opacity:0;animation:show .3s {boot_end:.2f}s forwards}}
</style>

{frame(W, H)}
{not_found(W / 2, H / 2, 92)}
<g class="content">
  {title_bar(W, "SUBJECT_SCAN", f"{rows}&#215;{cols}")}
  <g clip-path="url(#art)">
    <g class="mono" font-size="{fs:.3f}" fill="url(#ink)" xml:space="preserve"><g id="rows">
{chr(10).join("      " + b for b in body if b)}
    </g></g>
    {"".join(slices)}
    <g class="eye">
      <rect x="{bx}" y="{ey0:.1f}" width="{bw}" height="{ey1 - ey0:.1f}" fill="{RED}" opacity=".22"/>
      <rect x="{bx}" y="{(ey0 + ey1) / 2:.1f}" width="{bw}" height="1.5" fill="#fff" opacity=".7"/>
      <g class="mono" font-size="{eye_fs:.1f}" font-weight="700" text-anchor="middle">{eyes}</g>
    </g>
    <rect x="{bx}" y="0" width="{bw}" height="120" fill="url(#sweep)" class="sweep"/>
    <g class="beam"><rect x="{bx}" y="{beam_y0:.1f}" width="{bw}" height="2" fill="{CY}"/><rect x="{bx}" y="{beam_y0 - 14:.1f}" width="{bw}" height="14" fill="{CY}" opacity=".12"/></g>
  </g>
  <rect x="2" y="45" width="{W - 4}" height="{H - 92}" fill="url(#crt)"/>
  <path d="M1 {H - 44} H{W - 1}" stroke="{CY}" stroke-opacity=".16"/>
  <g class="mono" font-size="12" letter-spacing="1.5" text-anchor="end">
    <text x="{W - 20}" y="{H - 18}" fill="{DIM}" class="dec">DECODING<tspan class="blink">_</tspan></text>
    <text x="{W - 20}" y="{H - 18}" fill="{DIM}" class="ok">IDENTITY &#9656; <tspan fill="{OR}">VERIFIED</tspan></text>
  </g>
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
    ap.add_argument("-o", "--out", type=Path, default=Path(__file__).resolve().parent.parent / "assets" / "ascii-avatar.svg")
    a = ap.parse_args()
    lines = load_text(a.text) if a.text else load_image(a.image, a.cols, a.invert)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(build_svg(lines), encoding="utf-8")
    print(f"wrote {a.out}  ({len(lines)} rows x {max(map(len, lines))} cols)")


if __name__ == "__main__":
    main()
