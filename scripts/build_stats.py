#!/usr/bin/env python3
"""
ACTIVITY card from real GitHub data (no third-party service), in the profile theme.

  - WORKING ON : commits per repository over the last 30 days (bar chart)
  - mini contribution calendar of the last 30 days, active days ticked
  - language bar of public repos (GitHub's own language colours)

GitHub Actions (see .github/workflows/profile-stats.yml):
    GH_TOKEN=<token> GH_USER=banhxuanphuc python scripts/build_stats.py -o dist/stats.svg
Local preview with fake numbers (watermarked "MOCK DATA"):
    python scripts/build_stats.py --mock -o dist/stats.svg
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

from theme import BG, BLUE, CY, DIM, LINE, MONO, OR, T_READY, TX, base_css, defs, frame, loader_css, not_found, title_bar

W, H = 1000, 368
DAYS = 30

QUERY = """
query($login: String!, $cursor: String, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes { languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } } }
    }
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      commitContributionsByRepository(maxRepositories: 10) { repository { name } contributions { totalCount } }
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
    now = dt.datetime.now(dt.timezone.utc)
    start = (now - dt.timedelta(days=DAYS - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    v = {"login": user, "cursor": None, "from": start.isoformat(), "to": now.isoformat()}
    langs: dict[str, list] = {}
    first = None
    while True:
        u = gql(token, v)
        first = first or u
        for repo in u["repositories"]["nodes"]:
            for e in repo["languages"]["edges"]:
                cur = langs.setdefault(e["node"]["name"], [0, e["node"]["color"]])
                cur[0] += e["size"]
        page = u["repositories"]["pageInfo"]
        if not page["hasNextPage"]:
            break
        v["cursor"] = page["endCursor"]
    cc = first["contributionsCollection"]
    days = [(d["date"], d["contributionCount"])
            for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    return {
        "days": days[-DAYS:],
        "total": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "repos": [(r["repository"]["name"], r["contributions"]["totalCount"])
                  for r in cc["commitContributionsByRepository"]],
        "langs": langs,
        "mock": False,
    }


def mock() -> dict:
    rnd = random.Random(25)
    today = dt.date.today()
    days = [((today - dt.timedelta(days=DAYS - 1 - i)).isoformat(), 0 if rnd.random() < .45 else rnd.randint(1, 9))
            for i in range(DAYS)]
    return {"days": days, "total": sum(c for _, c in days), "commits": 74, "mock": True,
            "repos": [("SQL-UIT_backend", 31), ("SQL-UIT-Frontend", 18), ("banhxuanphuc", 12),
                      ("Scrum-Algile", 9), ("Beyond11-me.github.io", 4)],
            "langs": {"TypeScript": [52000, "#3178c6"], "Python": [31000, "#3572A5"], "CSS": [18000, "#663399"],
                      "JavaScript": [6000, "#f1e05a"], "HTML": [2000, "#e34c26"], "Dockerfile": [500, "#384d54"]}}


# ----------------------------------------------------------------------------- svg
def esc(s) -> str:
    return html.escape(str(s), quote=True)


def build(d: dict) -> str:
    T = T_READY + .6
    # --- working on (bar chart)
    repos = sorted(d["repos"], key=lambda r: -r[1])[:5]
    top = repos[0][1] if repos else 1
    bx, bmax, y0, pitch = 222, 300, 100, 32
    bars = []
    for i, (name, n) in enumerate(repos):
        y = y0 + i * pitch
        w = max(6, bmax * n / top)
        nm = name if len(name) <= 22 else name[:21] + "…"
        bars.append(
            f'<g class="in" style="animation-delay:{T + .1 + i * .08:.2f}s">'
            f'<text x="28" y="{y + 9}" font-size="13" fill="{TX}">{esc(nm)}</text>'
            f'<rect x="{bx}" y="{y}" width="{bmax}" height="10" rx="5" fill="#161b22"/>'
            f'<rect x="{bx}" y="{y}" width="{w:.1f}" height="10" rx="5" fill="url(#bar)" class="grow" style="animation-delay:{T + .3 + i * .08:.2f}s"/>'
            f'<text x="{bx + w + 10:.1f}" y="{y + 9}" font-size="12" fill="{OR if i == 0 else DIM}">{n}</text></g>')
    if not repos:
        bars.append(f'<text x="28" y="{y0 + 9}" font-size="13" fill="{DIM}">no public commits in the last {DAYS} days</text>')

    # --- mini calendar (Mon..Sun columns)
    days = [(dt.date.fromisoformat(s), c) for s, c in d["days"]]
    first = days[0][0] if days else dt.date.today()
    monday = first - dt.timedelta(days=first.weekday())
    peak = max([c for _, c in days] + [1])
    gx, gy, px, py, cs = 742, 92, 34, 30, 26
    head = "".join(f'<text x="{gx + i * px + cs / 2}" y="{gy - 8}">{c}</text>' for i, c in enumerate("MTWTFSS"))
    cells = []
    for k, (day, c) in enumerate(days):
        col, row = day.weekday(), (day - monday).days // 7
        x, y = gx + col * px, gy + row * py
        last = k == len(days) - 1
        dly = f'style="animation-delay:{T + .4 + k * .025:.3f}s"'
        if c:
            cells.append(
                f'<g class="pop" {dly}><rect x="{x}" y="{y}" width="{cs}" height="{cs}" rx="5" fill="{CY}" '
                f'fill-opacity="{.35 + .65 * c / peak:.2f}"' + (f' stroke="{OR}" stroke-width="1.6"' if last else "") + "/>"
                f'<path d="M{x + 7} {y + 13.5} l4.5 4.5 l8 -9" fill="none" stroke="{BG}" stroke-width="2.4" '
                f'stroke-linecap="round" stroke-linejoin="round"/></g>')
        else:
            cells.append(
                f'<g class="pop" {dly}><rect x="{x + .5}" y="{y + .5}" width="{cs - 1}" height="{cs - 1}" rx="5" fill="#161b22" '
                f'stroke="{OR if last else LINE}"/>'
                f'<text x="{x + cs / 2}" y="{y + 17}" text-anchor="middle" font-size="9.5" fill="{DIM}" fill-opacity=".7">{day.day}</text></g>')
    active = sum(1 for _, c in days if c)

    # --- languages
    total_l = sum(v[0] for v in d["langs"].values()) or 1
    langs = sorted(d["langs"].items(), key=lambda kv: -kv[1][0])[:6]
    ly = 312
    seg, leg, x = [], [], 28.0
    for i, (name, (size, color)) in enumerate(langs):
        w = 944 * size / total_l
        seg.append(f'<rect x="{x:.1f}" y="{ly}" width="{max(w - 2, 1.5):.1f}" height="8" fill="{color or DIM}"/>')
        x += w
        lx = 28 + i * 157
        leg.append(f'<circle cx="{lx + 4}" cy="{ly + 28}" r="4" fill="{color or DIM}"/>'
                   f'<text x="{lx + 14}" y="{ly + 32}" fill="{TX}">{esc(name[:13])} '
                   f'<tspan fill="{DIM}">{size / total_l * 100:.1f}%</tspan></text>')

    synced = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    mock_mark = (f'<text x="{W / 2}" y="{H / 2 + 20}" text-anchor="middle" font-family="{MONO}" font-weight="700" '
                 f'font-size="60" fill="{OR}" opacity=".1" transform="rotate(-6 {W / 2} {H / 2})">MOCK DATA</text>'
                 if d["mock"] else "")

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Activity in the last {DAYS} days: {active} active days, {d["total"]} contributions">
<title>ACTIVITY // LAST {DAYS} DAYS</title>
<defs>
  {defs()}
  <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
  <clipPath id="lang"><rect x="28" y="{ly}" width="944" height="8" rx="4"/></clipPath>
</defs>
<style>
  {base_css()}
  {loader_css()}
  text{{font-family:{MONO}}}
  .in{{opacity:0;animation:in .4s ease-out forwards}}
  @keyframes in{{from{{opacity:0;transform:translateY(5px)}}to{{opacity:1;transform:none}}}}
  .grow,.wipe{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:grow .9s cubic-bezier(.5,0,.2,1) forwards}}
  .wipe{{animation-delay:{T + .8:.2f}s;animation-duration:1.3s}}
  @keyframes grow{{to{{transform:scaleX(1)}}}}
  .pop{{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .3s ease-out forwards}}
  @keyframes pop{{from{{opacity:0;transform:scale(.4)}}to{{opacity:1;transform:none}}}}
</style>

{frame(W, H)}
{not_found(W / 2, H / 2 + 6, 86)}
<g class="content">
  {title_bar(W, f"ACTIVITY // LAST {DAYS} DAYS", f"SYNC {synced}")}
  <g font-size="11" letter-spacing="2" fill="{DIM}">
    <text x="28" y="78">WORKING ON · COMMITS PER REPO</text>
    <text x="28" y="{ly - 12}">LANGUAGES · PUBLIC REPOS</text>
  </g>
  {"".join(bars)}

  <path d="M590 70 V268" stroke="{CY}" stroke-opacity=".12"/>
  <g class="in" style="animation-delay:{T + .3:.2f}s">
    <text x="612" y="100" font-size="11" letter-spacing="2" fill="{DIM}">ACTIVE DAYS</text>
    <text x="612" y="140" font-size="36" font-weight="700" fill="{OR}">{active}<tspan font-size="15" fill="{DIM}" font-weight="400">/{DAYS}</tspan></text>
    <text x="612" y="184" font-size="11" letter-spacing="2" fill="{DIM}">CONTRIBUTIONS</text>
    <text x="612" y="224" font-size="36" font-weight="700" fill="{CY}">{d["total"]}</text>
  </g>
  <g font-size="10" fill="{DIM}" text-anchor="middle" letter-spacing="1">{head}</g>
  {"".join(cells)}

  <rect x="28" y="{ly}" width="944" height="8" rx="4" fill="#161b22"/>
  <g clip-path="url(#lang)"><g class="wipe">{"".join(seg)}</g></g>
  <g font-size="11.5" class="in" style="animation-delay:{T + 1:.2f}s">{"".join(leg)}</g>
  {mock_mark}
</g>
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
