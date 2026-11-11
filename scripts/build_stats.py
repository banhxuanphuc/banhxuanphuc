#!/usr/bin/env python3
"""
Self-hosted GitHub stats card (no third-party service) in the profile's cyberpunk theme.

Runs in GitHub Actions (see .github/workflows/profile-stats.yml):
    GH_TOKEN=<token> GH_USER=banhxuanphuc python scripts/build_stats.py -o dist/stats.svg

Local preview with fake numbers (watermarked "MOCK DATA"):
    python scripts/build_stats.py --mock -o dist/stats.svg

Only the Python standard library is used.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import random
import urllib.request
from pathlib import Path

CY, BL, OR, TX, DIM = "#00F0FF", "#2D7CFF", "#FF9E00", "#C9D4E3", "#6B7A90"
LANG_COLORS = [CY, BL, OR, "#7AF3FF", "#FFC566", "#9AB8FF"]
MONO = "'Cascadia Mono',Consolas,'SFMono-Regular',Menlo,'Courier New',monospace"
SANS = "'Segoe UI','Helvetica Neue',Arial,sans-serif"
W, H = 1000, 340

QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100, after: $cursor) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}
"""


# ----------------------------------------------------------------------------- data
def gql(token: str, variables: dict) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-stats-card"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


def fetch(user: str, token: str) -> dict:
    cursor, repos, first = None, [], None
    while True:
        u = gql(token, {"login": user, "cursor": cursor})
        first = first or u
        repos += u["repositories"]["nodes"]
        page = u["repositories"]["pageInfo"]
        if not page["hasNextPage"]:
            break
        cursor = page["endCursor"]

    cc = first["contributionsCollection"]
    days = [(d["date"], d["contributionCount"])
            for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    langs: dict[str, int] = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    return {
        "days": days,
        "total": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "repos": first["repositories"]["totalCount"],
        "followers": first["followers"]["totalCount"],
        "langs": langs,
        "mock": False,
    }


def mock() -> dict:
    random.seed(25)
    start = dt.date.today() - dt.timedelta(days=370)
    days = []
    for i in range(371):
        d = start + dt.timedelta(days=i)
        busy = 1 + (i / 371) * 2
        days.append((d.isoformat(), 0 if random.random() < .35 else int(random.expovariate(1 / (2.5 * busy)))))
    return {"days": days, "total": sum(c for _, c in days), "commits": 612, "prs": 41, "issues": 17,
            "stars": 23, "repos": 18, "followers": 12, "mock": True,
            "langs": {"Python": 52000, "PHP": 31000, "Java": 18000, "C++": 12000, "Jupyter Notebook": 9000, "Blade": 4000}}


def streaks(days: list[tuple[str, int]]) -> tuple[int, int]:
    longest = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    cur, seq = 0, [c for _, c in days]
    if seq and seq[-1] == 0:          # today not coded yet -> streak still alive from yesterday
        seq = seq[:-1]
    for c in reversed(seq):
        if not c:
            break
        cur += 1
    return cur, longest


# ----------------------------------------------------------------------------- svg
def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def tile(x: float, y: float, value: str, label: str, unit: str, delay: float) -> str:
    return (
        f'<g class="pop" style="animation-delay:{delay:.2f}s">'
        f'<path d="M{x + 8} {y} H{x + 150} V{y + 78} L{x + 142} {y + 86} H{x} V{y + 8} Z" fill="#0A1020" stroke="{CY}" stroke-opacity=".35"/>'
        f'<text x="{x + 14}" y="{y + 50}" font-family="{SANS}" font-weight="800" font-size="34" fill="url(#txt)">{esc(value)}'
        f'<tspan font-size="13" fill="{DIM}" font-weight="600"> {esc(unit)}</tspan></text>'
        f'<text x="{x + 14}" y="{y + 72}" class="mono" font-size="10.5" letter-spacing="1.5" fill="{DIM}">{esc(label)}</text></g>'
    )


def build(d: dict) -> str:
    cur, longest = streaks(d["days"])
    # weekly totals for the chart (last 52 complete-ish weeks)
    weeks = [sum(c for _, c in d["days"][i:i + 7]) for i in range(0, len(d["days"]), 7)][-52:]
    cx0, cy0, cw, ch = 352, 78, 626, 132          # chart box
    peak = max(weeks) if weeks and max(weeks) > 0 else 1
    step = cw / max(1, len(weeks) - 1)
    pts = [(cx0 + i * step, cy0 + ch - (v / peak) * (ch - 10)) for i, v in enumerate(weeks)]
    line = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    area = f"{line} L{cx0 + cw} {cy0 + ch} L{cx0} {cy0 + ch} Z"
    pi = max(range(len(weeks)), key=weeks.__getitem__) if weeks else 0
    px, py = pts[pi] if pts else (cx0, cy0 + ch)

    # month labels
    first_day = dt.date.fromisoformat(d["days"][-len(weeks) * 7][0]) if weeks else dt.date.today()
    months, last = [], None
    for i in range(len(weeks)):
        m = first_day + dt.timedelta(days=i * 7)
        if m.month != last and m.day <= 7:
            months.append(f'<text x="{cx0 + i * step:.1f}" y="{cy0 + ch + 18}">{m.strftime("%b").upper()}</text>')
            last = m.month
    grid = "".join(f'<path d="M{cx0} {cy0 + ch * f:.1f} H{cx0 + cw}"/>' for f in (0, .25, .5, .75))

    # languages bar
    total_l = sum(d["langs"].values()) or 1
    top = sorted(d["langs"].items(), key=lambda kv: -kv[1])[:6]
    bx, by, bw = 20, 268, 960
    seg, leg, x = [], [], bx
    for i, (name, size) in enumerate(top):
        w = bw * size / total_l
        seg.append(f'<rect x="{x:.1f}" y="{by}" width="{max(w - 2, 1):.1f}" height="10" fill="{LANG_COLORS[i]}"/>')
        x += w
        lx = bx + i * 160
        leg.append(f'<rect x="{lx}" y="{by + 24}" width="8" height="8" fill="{LANG_COLORS[i]}"/>'
                   f'<text x="{lx + 14}" y="{by + 32}" fill="{TX}">{esc(name[:14])} <tspan fill="{DIM}">{size / total_l * 100:.1f}%</tspan></text>')
    if not top:
        leg.append(f'<text x="{bx}" y="{by + 32}" fill="{DIM}">NO PUBLIC CODE YET</text>')

    synced = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    mock_mark = (f'<text x="{W / 2}" y="{H / 2 + 20}" text-anchor="middle" font-family="{SANS}" font-weight="900" '
                 f'font-size="64" fill="{OR}" opacity=".12" transform="rotate(-8 {W / 2} {H / 2})">MOCK DATA</text>') if d["mock"] else ""

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub activity: {d["total"]} contributions in the last year, current streak {cur} days, longest streak {longest} days">
<title>ACTIVITY // TELEMETRY</title>
<defs>
  <linearGradient id="frame" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}"/><stop offset=".55" stop-color="{BL}"/><stop offset="1" stop-color="{OR}"/></linearGradient>
  <linearGradient id="txt" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}"/><stop offset="1" stop-color="#7FB8FF"/></linearGradient>
  <linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CY}" stop-opacity=".35"/><stop offset="1" stop-color="{CY}" stop-opacity="0"/></linearGradient>
  <linearGradient id="ln" gradientUnits="userSpaceOnUse" x1="{cx0}" y1="0" x2="{cx0 + cw}" y2="0"><stop offset="0" stop-color="{CY}"/><stop offset=".6" stop-color="#5AA9FF"/><stop offset="1" stop-color="{OR}"/></linearGradient>
  <pattern id="crt" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".3"/></pattern>
  <clipPath id="reveal"><rect x="{cx0 - 2}" y="{cy0 - 10}" width="{cw + 10}" height="{ch + 12}" class="wipe"/></clipPath>
</defs>
<style>
  .mono{{font-family:{MONO}}}
  .pop{{opacity:0;animation:pop .5s ease-out forwards}}
  @keyframes pop{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
  .wipe{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:wipe 1.8s cubic-bezier(.6,.1,.3,1) .5s forwards}}
  @keyframes wipe{{to{{transform:scaleX(1)}}}}
  .peak{{opacity:0;animation:pop .4s 2.2s forwards}}
  .pulse{{transform-box:fill-box;transform-origin:center;animation:pulse 1.6s ease-out 2.2s infinite;opacity:0}}
  @keyframes pulse{{0%{{opacity:.9;transform:scale(1)}}100%{{opacity:0;transform:scale(3.2)}}}}
  .bar{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:wipe 1.4s cubic-bezier(.6,.1,.3,1) 1s forwards}}
  .blink{{animation:blink 1s steps(1) infinite}} @keyframes blink{{50%{{opacity:0}}}}
</style>
<path d="M16 1 H{W - 30} L{W - 1} 30 V{H - 16} L{W - 16} {H - 1} H30 L1 {H - 30} V16 Z" fill="#05070D" stroke="url(#frame)" stroke-width="1.5"/>
<path d="M1 46 H{W - 1}" stroke="{CY}" stroke-opacity=".25"/>
<g class="mono" font-size="12" letter-spacing="1.5">
  <rect x="18" y="16" width="8" height="14" fill="{OR}"/>
  <text x="34" y="28" fill="{CY}">ACTIVITY // TELEMETRY · LAST 12 MONTHS</text>
  <text x="{W - 40}" y="28" fill="{DIM}" text-anchor="end">SYNC <tspan fill="{OR}">{synced}</tspan></text>
  <circle cx="{W - 28}" cy="24" r="4" fill="{CY}" class="blink"/>
</g>

{tile(20, 62, f"{d['total']:,}", "CONTRIBUTIONS", "", .2)}
{tile(180, 62, str(cur), "CURRENT STREAK", "days", .35)}
{tile(20, 158, str(longest), "LONGEST STREAK", "days", .5)}
{tile(180, 158, str(d["stars"]), "STARS EARNED", "★", .65)}

<g stroke="{CY}" stroke-opacity=".1">{grid}</g>
<g clip-path="url(#reveal)">
  <path d="{area}" fill="url(#area)"/>
  <path d="{line}" fill="none" stroke="url(#ln)" stroke-width="2.2" stroke-linejoin="round"/>
</g>
<path d="M{cx0} {cy0 + ch} H{cx0 + cw}" stroke="{CY}" stroke-opacity=".6"/>
<g class="mono" font-size="10" letter-spacing="1" fill="{DIM}">{"".join(months)}</g>
<text x="{cx0}" y="{cy0 - 8}" class="mono" font-size="10.5" letter-spacing="1.5" fill="{DIM}">WEEKLY CONTRIBUTIONS</text>
<g class="peak">
  <circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{OR}"/>
  <text x="{min(px, cx0 + cw - 70):.1f}" y="{max(py - 10, cy0 + 4):.1f}" class="mono" font-size="11" fill="{OR}" text-anchor="middle">PEAK {weeks[pi] if weeks else 0}</text>
</g>
<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="none" stroke="{OR}" class="pulse"/>

<text x="20" y="258" class="mono" font-size="10.5" letter-spacing="1.5" fill="{DIM}">TOP LANGUAGES // PUBLIC REPOS</text>
<text x="{W - 20}" y="258" class="mono" font-size="10.5" letter-spacing="1.5" fill="{DIM}" text-anchor="end">COMMITS <tspan fill="{TX}">{d["commits"]}</tspan> · PRS <tspan fill="{TX}">{d["prs"]}</tspan> · ISSUES <tspan fill="{TX}">{d["issues"]}</tspan> · REPOS <tspan fill="{TX}">{d["repos"]}</tspan> · FOLLOWERS <tspan fill="{TX}">{d["followers"]}</tspan></text>
<rect x="{bx}" y="{by}" width="{bw}" height="10" fill="#0A1020"/>
<g class="bar">{"".join(seg)}</g>
<g class="mono" font-size="11.5">{"".join(leg)}</g>
<rect x="2" y="47" width="{W - 4}" height="{H - 62}" fill="url(#crt)"/>
{mock_mark}
</svg>
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true", help="render with fake data for local preview")
    ap.add_argument("-o", "--out", type=Path, default=Path("dist/stats.svg"))
    a = ap.parse_args()
    if a.mock:
        data = mock()
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        user = os.environ.get("GH_USER") or os.environ.get("GITHUB_REPOSITORY_OWNER")
        if not token or not user:
            raise SystemExit("Set GH_TOKEN and GH_USER (or run with --mock)")
        data = fetch(user, token)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(build(data), encoding="utf-8")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
