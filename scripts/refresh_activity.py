"""Refresh public GitHub streaks and the Night Line calendar together."""

from datetime import date, timedelta
from itertools import groupby, takewhile
import json
from pathlib import Path
import subprocess

from night_line import render_night_line


USERNAME = "Devadathan69"
ROOT = Path(__file__).resolve().parent.parent
START = "<!-- public-activity:start -->"
END = "<!-- public-activity:end -->"
LEVELS = ("NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE")


def fetch_activity():
    query = """query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionCount contributionLevel } }
          }
        }
      }
    }"""
    response = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}", "-f", f"login={USERNAME}"],
        capture_output=True, encoding="utf-8", timeout=40, check=False,
    )
    if response.returncode:
        raise RuntimeError(response.stderr.strip() or "GitHub contribution query failed")

    user = json.loads(response.stdout)["data"]["user"]
    recent = user["contributionsCollection"]["contributionCalendar"]
    days = [
        (date.fromisoformat(day["date"]), day["contributionCount"], LEVELS.index(day["contributionLevel"]))
        for week in recent["weeks"]
        for day in week["contributionDays"]
    ]
    if not 365 <= len(days) <= 372:
        raise ValueError("Expected about one year of public contributions")
    if any(day != days[0][0] + timedelta(days=index) for index, (day, _, _) in enumerate(days)):
        raise ValueError("GitHub returned a non-contiguous calendar")
    if sum(count for _, count, _ in days) != recent["totalContributions"]:
        raise ValueError("GitHub contribution totals were inconsistent")
    return days


def update_summary(readme, days):
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("Expected one public activity section in the README")
    before, _, remainder = readme.partition(START)
    _, end, after = remainder.partition(END)
    if not end:
        raise ValueError("The public activity markers are out of order")

    active = [count > 0 for _, count, _ in days]
    recent = active if active[-1] else active[:-1]
    current = sum(1 for _ in takewhile(bool, reversed(recent)))
    longest = max((sum(1 for _ in group) for flag, group in groupby(active) if flag), default=0)
    streaks = f"Public streaks · **{current}d** current · **{longest}d** longest"
    return f"{before}{START}\n\n{streaks}\n\n{END}{after}"


def main():
    days = fetch_activity()
    readme = ROOT / "README.md"
    updated = {
        readme: update_summary(readme.read_text(encoding="utf-8"), days),
        ROOT / "assets/night-line.svg": render_night_line(days),
        ROOT / "assets/night-line-mobile.svg": render_night_line(days, mobile=True),
    }
    for path, content in updated.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Checked {len(days)} public contribution days through {days[-1][0]}.")


if __name__ == "__main__":
    main()
