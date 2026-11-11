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
# "hacked" overexposure flash: an X-shaped white/red splash over the eye.
# HACK_AT is (row, col) in the text grid - tuned for scripts/avatar.txt
HACK_AT = (23.0, 66.0)
HACK_HALF = (128, 100)           # half width / half height of the X in px
HACK_EVERY = 15                  # seconds between flashes
DARK_RED = "#9B0018"


def hack_overlay(cx: float, cy: float) -> tuple[str, str]:
    """Return (defs, markup) for the X-shaped overexposed splash centred on (cx, cy)."""
    import math
    import random
    rnd = random.Random(2077)
    hx, hy = HACK_HALF
    arms = [((cx - hx, cy - hy), (cx + hx, cy + hy)), ((cx + hx * .9, cy - hy), (cx - hx * .9, cy + hy))]

    def stroke(a, b, jitter, width, color, op):
        pts, n = [], 7
        for k in range(n + 1):
            t = k / n
            px = a[0] + (b[0] - a[0]) * t + rnd.uniform(-jitter, jitter)
            py = a[1] + (b[1] - a[1]) * t + rnd.uniform(-jitter, jitter)
            pts.append(f"{px:.1f} {py:.1f}")
        return (f'<path d="M{" L".join(pts)}" fill="none" stroke="{color}" stroke-width="{width:.1f}" '
                f'stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>')

    # white blown-out X (blurred), then red ink strokes on top
    white = "".join(stroke(a, b, 8, 62, "#fff", 1) for a, b in arms)
    white += f'<ellipse cx="{cx}" cy="{cy}" rx="70" ry="54" fill="url(#blowout)"/>'
    reds = []
    for a, b in arms:
        for _ in range(5):
            reds.append(stroke(a, b, 22, rnd.uniform(3, 16), rnd.choice([RED, RED, DARK_RED]), rnd.choice([.75, .9, 1])))
    # thorn-like scratches flying out of the centre
    thorns = []
    for _ in range(26):
        ang = rnd.uniform(0, 2 * math.pi)
        r0, r1 = rnd.uniform(10, 40), rnd.uniform(60, 165)
        x0, y0 = cx + math.cos(ang) * r0, cy + math.sin(ang) * r0 * .8
        x1, y1 = cx + math.cos(ang) * r1, cy + math.sin(ang) * r1 * .8
        bend = rnd.uniform(-30, 30)
        mx, my = (x0 + x1) / 2 + bend, (y0 + y1) / 2 - bend
        thorns.append(f'<path d="M{x0:.1f} {y0:.1f} Q{mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" '
                      f'stroke="{rnd.choice([RED, RED, DARK_RED, "#fff"])}" stroke-width="{rnd.uniform(.8, 3.2):.1f}" '
                      f'stroke-linecap="round"/>')
    drops = "".join(f'<circle cx="{cx + rnd.uniform(-hx, hx):.1f}" cy="{cy + rnd.uniform(-hy, hy):.1f}" '
                    f'r="{rnd.uniform(1, 4):.1f}" fill="{rnd.choice([RED, DARK_RED, "#fff"])}"/>' for _ in range(30))
    xclip = "".join(stroke(a, b, 0, 70, "#fff", 1) for a, b in arms)

    d = f'''<filter id="ink" x="-30%" y="-30%" width="160%" height="160%">
    <feTurbulence type="fractalNoise" baseFrequency=".045" numOctaves="3" seed="9"/>
    <feDisplacementMap in="SourceGraphic" scale="18" xChannelSelector="R" yChannelSelector="G"/></filter>
  <filter id="burn" x="-30%" y="-30%" width="160%" height="160%">
    <feTurbulence type="fractalNoise" baseFrequency=".03" numOctaves="2" seed="4"/>
    <feDisplacementMap in="SourceGraphic" scale="24" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="2.5"/></filter>
  <radialGradient id="blowout"><stop offset="0" stop-color="#fff"/><stop offset=".6" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <mask id="xmask"><rect width="{W}" height="{H}" fill="#000"/>{xclip}</mask>'''
    m = f'''<g class="hack">
      <rect x="{ART_BOX[0]}" y="{ART_BOX[1]}" width="{ART_BOX[2]}" height="{ART_BOX[3]}" fill="{RED}" opacity=".07"/>
      <g mask="url(#xmask)"><use href="#rows" fill="{RED}" transform="translate(4 1)"/></g>
      <g filter="url(#burn)" opacity=".92">{white}</g>
      <g mask="url(#xmask)"><use href="#rows" fill="#fff"/></g>
      <g filter="url(#ink)">{"".join(reds)}{"".join(thorns)}</g>
      {drops}
    </g>'''
    return d, m


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
    hack_defs, hack = hack_overlay(ox + HACK_AT[1] * cw, oy + HACK_AT[0] * lh)
    t_hack = T + 7

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
  {hack_defs}
</defs>
<style>
  {base_css()}
  {loader_css()}
  .r{{opacity:0;white-space:pre;animation:boot .45s ease-out forwards}}
  @keyframes boot{{0%{{opacity:0;transform:translateX(-14px)}}55%{{opacity:1;transform:translateX(4px)}}100%{{opacity:1;transform:translateX(0)}}}}
  @keyframes gl-a{{0%,100%{{transform:translateX(0)}}91%{{transform:translateX(-7px);fill:{RED}}}93%{{transform:translateX(5px);fill:#fff}}95%{{transform:translateX(-2px)}}97%{{transform:translateX(0)}}}}
  @keyframes gl-b{{0%,100%{{transform:translateX(0)}}88%{{transform:translateX(6px);fill:#fff}}90%{{transform:translateX(-4px);fill:{CY}}}92%{{transform:translateX(0)}}}}
  .sl{{opacity:0;animation-name:sl;animation-timing-function:steps(1);animation-iteration-count:infinite}}
  @keyframes sl{{0%,100%{{opacity:0}}90%{{opacity:1}}92%{{opacity:0}}94%{{opacity:1}}95%{{opacity:0}}}}
  .hack,.alien{{opacity:0;animation:hack {HACK_EVERY}s steps(1) {t_hack:.1f}s infinite}}
  .human{{animation:human {HACK_EVERY}s steps(1) {t_hack:.1f}s infinite}}
  @keyframes hack{{0%,100%{{opacity:0}}88%{{opacity:1;transform:translate(-4px,1px)}}88.6%{{opacity:.15}}89.2%{{opacity:1;transform:translate(3px,-2px)}}90%{{opacity:1;transform:none}}94.5%{{opacity:1;transform:translate(-2px,0)}}95%{{opacity:.3}}95.4%{{opacity:1;transform:none}}96.6%{{opacity:0}}97%{{opacity:.7}}97.4%{{opacity:0}}}}
  @keyframes human{{0%,100%{{opacity:1}}88%{{opacity:0}}97.4%{{opacity:1}}}}
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
    {hack}
    <rect x="{bx}" y="0" width="{bw}" height="120" fill="url(#sweep)" class="sweep"/>
    <g class="beam"><rect x="{bx}" y="{beam_y0:.1f}" width="{bw}" height="2" fill="{CY}"/><rect x="{bx}" y="{beam_y0 - 14:.1f}" width="{bw}" height="14" fill="{CY}" opacity=".12"/></g>
  </g>
  <rect x="2" y="45" width="{W - 4}" height="{H - 92}" fill="url(#crt)"/>
  <path d="M1 {H - 44} H{W - 1}" stroke="{CY}" stroke-opacity=".16"/>
  <g class="mono" font-size="12" letter-spacing="1.5" text-anchor="end">
    <text x="{W - 20}" y="{H - 18}" fill="{DIM}" class="dec">DECODING<tspan class="blink">_</tspan></text>
    <text x="{W - 20}" y="{H - 18}" fill="{DIM}" class="ok">IDENTITY &#9656; <tspan fill="{OR}">VERIFIED</tspan></text>
  </g>
  <g class="mono ok" font-size="12" letter-spacing="1.5">
    <text x="20" y="{H - 18}" fill="{DIM}" class="human">RACE: <tspan fill="{CY}">human</tspan></text>
    <text x="20" y="{H - 18}" fill="{DIM}" class="alien">RACE: <tspan fill="{RED}" font-weight="700">???</tspan></text>
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
