#!/usr/bin/env python3
"""Fetch GitHub contribution calendar data and write data/contributions.json.

Scrapes the public (no-auth) HTML fragment GitHub serves at
https://github.com/users/<username>/contributions, which profile pages
fetch client-side to render the calendar. Markup notes (verified against
a live fetch):

  <table class="ContributionCalendar-grid js-calendar-graph-table">
    ...
    <td class="ContributionCalendar-day" id="contribution-day-component-R-C"
        data-date="YYYY-MM-DD" data-level="0-4"></td>
    ...
  <tool-tip for="contribution-day-component-R-C">N contributions on Month Day.</tool-tip>

Day cells carry the date + level directly; the exact contribution count
lives in a sibling <tool-tip> element linked by id via its `for` attr
(cells with zero contributions read "No contributions on ..."). If
GitHub changes this markup, re-inspect with dev tools and update the
selectors below.
"""
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "data" / "contributions.json"
DEFAULT_USERNAME = "kiruthick01"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; profile-readme-bot/1.0)",
}


def fetch_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_days(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")

    day_cells = soup.select("td.ContributionCalendar-day")
    if not day_cells:
        raise RuntimeError(
            "No td.ContributionCalendar-day cells found — GitHub's markup "
            "may have changed. Re-inspect the page in dev tools."
        )

    counts_by_id: dict[str, int] = {}
    for tip in soup.find_all("tool-tip"):
        ref = tip.get("for")
        if not ref:
            continue
        text = tip.get_text(strip=True)
        match = re.match(r"(\d+)\s+contributions?", text)
        counts_by_id[ref] = int(match.group(1)) if match else 0

    days = []
    for td in day_cells:
        day_date = td.get("data-date")
        level = td.get("data-level")
        if not day_date or level is None:
            continue
        count = counts_by_id.get(td.get("id"), 0)
        days.append({"date": day_date, "level": int(level), "count": count})

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)

    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    best_day = max(days, key=lambda d: d["count"], default=None)

    monthly = defaultdict(int)
    for d in days:
        month = d["date"][:7]  # YYYY-MM
        monthly[month] += d["count"]

    return {
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": dict(sorted(monthly.items())),
    }


def main() -> None:
    username = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USERNAME
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT

    html = fetch_html(username)
    days = parse_days(html)
    stats = compute_stats(days)

    data = {
        "username": username,
        "generated_at": date.today().isoformat(),
        "days": days,
        "stats": stats,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2))
    print(f"Wrote {output_path} ({len(days)} days, {stats['total_contributions']} contributions)")


if __name__ == "__main__":
    main()
