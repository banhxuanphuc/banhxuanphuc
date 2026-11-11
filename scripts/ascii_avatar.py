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

from theme import BG, BLUE, CY, DIM, MONO, OR, T_READY, base_css, defs, frame, loader_css, not_found, title_bar

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
# "hacked" glitch: every HACK_EVERY s the whole card flickers to an inverted
# (white) state for HACK_LEN s and a skewed ERROR bar covers the eyes.
HACK_EVERY = 15                  # seconds between glitches
HACK_LEN = 1.5                   # seconds the glitch lasts
# ERROR bar: parallelogram corners (x, y) - tuned for scripts/avatar.txt
BAR = [(246, 252), (470, 243), (458, 313), (234, 322)]


def _pct(t: float) -> str:
    """seconds inside the glitch window -> keyframe percentage of the HACK_EVERY cycle"""
    return f"{(HACK_EVERY - HACK_LEN + t) / HACK_EVERY * 100:.2f}%"


def _frames(windows: list[tuple[float, float]], on: str, off: str) -> str:
    """keyframes that are `on` inside each (start, end) window (seconds into the glitch) and `off` elsewhere"""
    out = [f"0%,100%{{{{{off}}}}}"]
    for a, b in windows:
        out.append(f"{_pct(a)}{{{{{on}}}}}{_pct(b)}{{{{{off}}}}}")
    return "".join(out)


def hack_overlay() -> tuple[str, str, str]:
    """Return (defs, css, markup) for the ERROR bar + desynced slices."""
    pts = " ".join(f"{x},{y}" for x, y in BAR)
    cx = sum(x for x, _ in BAR) / 4
    cy = sum(y for _, y in BAR) / 4
    ang = -2.3
    d = f'''<filter id="invert" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="-1 0 0 0 1  0 -1 0 0 1  0 0 -1 0 1  0 0 0 1 0"/></filter>
  <g id="errbar">
    <polygon points="{pts}" fill="#05070a" stroke="#fff" stroke-width="1.6"/>
    <polygon points="{pts}" fill="url(#crt)"/>
    <g font-family="{MONO}" font-weight="800" font-size="46" text-anchor="middle" letter-spacing="3" transform="rotate({ang} {cx:.0f} {cy:.0f})">
      <g class="etxt"><text x="{cx - 9:.0f}" y="{cy + 16:.0f}" fill="{CY}" opacity=".85" textLength="178" lengthAdjust="spacingAndGlyphs">ERROR</text>
        <text x="{cx - 6:.0f}" y="{cy + 16:.0f}" fill="{RED}" textLength="178" lengthAdjust="spacingAndGlyphs">ERROR</text></g>
      <g class="qtxt"><text x="{cx - 3:.0f}" y="{cy + 16:.0f}" fill="{CY}" opacity=".85">???</text>
        <text x="{cx:.0f}" y="{cy + 16:.0f}" fill="{RED}">???</text></g>
    </g>
  </g>
  <clipPath id="cut1"><rect x="0" y="{cy - 10:.0f}" width="{W}" height="13"/></clipPath>
  <clipPath id="cut2"><rect x="0" y="{cy + 10:.0f}" width="{W}" height="11"/></clipPath>'''
    G = HACK_LEN
    css = f'''.inv{{{{animation:inv {HACK_EVERY}s steps(1) {{t_hack:.1f}}s infinite}}}}
  @keyframes inv{{{{{_frames([(0, .1), (.18, .23), (.32, .5), (.56, .62), (.74, .95), (1.0, 1.06), (1.18, 1.3), (1.36, 1.43)], "filter:url(#invert)", "filter:none;transform:none")}}}}}
  .shake{{{{animation:shake {HACK_EVERY}s steps(1) {{t_hack:.1f}}s infinite}}}}
  @keyframes shake{{{{{_frames([(.2, .26), (.6, .66), (1.12, 1.18)], "transform:translate(-4px,1px)", "transform:none")}{_frames([(.4, .45), (.9, .96)], "transform:translate(3px,-1px)", "transform:none")[len("0%,100%{{transform:none}}"):]}}}}}
  .err{{{{opacity:0;animation:err {HACK_EVERY}s steps(1) {{t_hack:.1f}}s infinite}}}}
  @keyframes err{{{{{_frames([(.03, .58), (.64, 1.47)], "opacity:1", "opacity:0")}}}}}
  .ej{{{{animation:ej {HACK_EVERY}s steps(1) {{t_hack:.1f}}s infinite}}}}
  @keyframes ej{{{{{_frames([(.15, .21), (.7, .76), (1.25, 1.3)], "transform:translate(7px,-2px)", "transform:none")}}}}}
  .etxt{{{{animation:etxt {HACK_EVERY}s steps(1) {{t_hack:.1f}}s infinite}}}}
  @keyframes etxt{{{{{_frames([(.78, .9), (1.2, 1.28)], "opacity:0", "opacity:1")}}}}}
  .qtxt{{{{opacity:0;animation:qtxt {HACK_EVERY}s steps(1) {{t_hack:.1f}}s infinite}}}}
  @keyframes qtxt{{{{{_frames([(.78, .9), (1.2, 1.28)], "opacity:1", "opacity:0")}}}}}
  .s1{{{{opacity:0;animation:s1 {HACK_EVERY}s steps(1) {{t_hack:.1f}}s infinite}}}}
  @keyframes s1{{{{{_frames([(.08, .25), (.75, .9), (1.2, 1.32)], "opacity:1", "opacity:0")}}}}}
  .s2{{{{opacity:0;animation:s2 {HACK_EVERY}s steps(1) {{t_hack:.1f}}s infinite}}}}
  @keyframes s2{{{{{_frames([(.18, .29), (.6, .68), (1.08, 1.19)], "opacity:1", "opacity:0")}}}}}
  .s3{{{{opacity:0;animation:s3 {HACK_EVERY}s steps(1) {{t_hack:.1f}}s infinite}}}}
  @keyframes s3{{{{{_frames([(.36, .47), (.98, 1.05), (1.35, 1.41)], "opacity:1", "opacity:0")}}}}}
  .s4{{{{opacity:0;animation:s4 {HACK_EVERY}s steps(1) {{t_hack:.1f}}s infinite}}}}
  @keyframes s4{{{{{_frames([(.13, .3), (.87, 1.0)], "opacity:1", "opacity:0")}}}}}
  .alien{{{{opacity:0;animation:alien {HACK_EVERY}s steps(1) {{t_hack:.1f}}s infinite}}}}
  @keyframes alien{{{{{_frames([(0, 1.45)], "opacity:1", "opacity:0")}}}}}
  .human{{{{animation:human {HACK_EVERY}s steps(1) {{t_hack:.1f}}s infinite}}}}
  @keyframes human{{{{{_frames([(0, 1.45)], "opacity:0", "opacity:1")}}}}}'''
    css = css.replace("{{", "{").replace("}}", "}")
    (x0, y0), (x1, y1) = BAR[0], BAR[3]
    m = f'''<g class="err"><g class="ej">
    <use href="#errbar"/>
    <g class="s1"><polygon points="12,{y0 + 3} {x0 + 6},{y0} {x0 + 3},{y0 + 15} 10,{y0 + 18}" fill="#05070a"/>
      <path d="M12 {y0 + 3} L{x0 + 6} {y0}" stroke="{RED}" stroke-width="2"/><path d="M10 {y0 + 18} L{x0 + 3} {y0 + 15}" stroke="{CY}" stroke-width="1.5"/></g>
    <g class="s2" clip-path="url(#cut1)"><use href="#errbar" transform="translate(24 0)"/></g>
    <g class="s3" clip-path="url(#cut2)"><use href="#errbar" transform="translate(-32 0)"/></g>
    <g class="s4"><rect x="134" y="{y0 - 48}" width="7" height="46" fill="#05070a"/><rect x="134" y="{y0 - 48}" width="2" height="46" fill="{RED}"/>
      <polygon points="166,{y1 - 14} {x1 - 14},{y1 - 44} {x1 - 8},{y1 - 37} 172,{y1 - 7}" fill="#05070a"/>
      <path d="M166 {y1 - 14} L{x1 - 14} {y1 - 44}" stroke="{CY}" stroke-width="1.5"/></g>
  </g></g>
<text x="20" y="{H - 18}" font-family="{MONO}" font-size="12" letter-spacing="1.5" fill="{DIM}" class="alien">RACE: <tspan fill="{RED}" font-weight="700">???</tspan></text>'''
    return d, css, m


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
    hack_defs, hack_css, hack = hack_overlay()
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
  {hack_css.replace("{t_hack:.1f}", f"{t_hack:.1f}")}
  .beam{{opacity:0;animation:beam {rows * step + 0.5:.2f}s linear {start:.2f}s forwards}}
  @keyframes beam{{0%{{opacity:1;transform:translateY(0)}}96%{{opacity:1}}100%{{opacity:0;transform:translateY({art_h + 8:.1f}px)}}}}
  .sweep{{opacity:0;animation:sweep 5s linear {boot_end:.2f}s infinite}}
  @keyframes sweep{{0%{{opacity:1;transform:translateY(-120px)}}100%{{opacity:1;transform:translateY({H}px)}}}}
  .dec{{animation:hide 0s {boot_end:.2f}s forwards}}
  .ok{{opacity:0;animation:show .3s {boot_end:.2f}s forwards}}
</style>

<g class="inv"><g class="shake">
{frame(W, H)}
{not_found(W / 2, H / 2, 92)}
<g class="content">
  {title_bar(W, "SUBJECT_SCAN", f"{rows}&#215;{cols}")}
  <g clip-path="url(#art)">
    <g class="mono" font-size="{fs:.3f}" fill="url(#ink)" xml:space="preserve"><g id="rows">
{chr(10).join("      " + b for b in body if b)}
    </g></g>
    {"".join(slices)}
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
  </g>
</g>
</g></g>
{hack}
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
