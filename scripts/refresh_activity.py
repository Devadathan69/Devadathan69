"""Refresh public GitHub streaks in the profile README."""

from datetime import date, timedelta
from itertools import groupby, takewhile
import json
from pathlib import Path
import subprocess

USERNAME = "Devadathan69"
ROOT = Path(__file__).resolve().parent.parent
START = "<!-- public-activity:start -->"
END = "<!-- public-activity:end -->"


def fetch_activity():
    query = """query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionCount } }
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
        (date.fromisoformat(day["date"]), day["contributionCount"])
        for week in recent["weeks"]
        for day in week["contributionDays"]
    ]
    if not 365 <= len(days) <= 372:
        raise ValueError("Expected about one year of public contributions")
    if any(day != days[0][0] + timedelta(days=index) for index, (day, _) in enumerate(days)):
        raise ValueError("GitHub returned a non-contiguous calendar")
    if sum(count for _, count in days) != recent["totalContributions"]:
        raise ValueError("GitHub contribution totals were inconsistent")
    return days


def update_summary(readme, days):
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("Expected one public activity section in the README")
    before, _, remainder = readme.partition(START)
    _, end, after = remainder.partition(END)
    if not end:
        raise ValueError("The public activity markers are out of order")

    active = [count > 0 for _, count in days]
    recent = active if active[-1] else active[:-1]
    current = sum(1 for _ in takewhile(bool, reversed(recent)))
    longest = max((sum(1 for _ in group) for flag, group in groupby(active) if flag), default=0)
    streaks = f"Public streaks · **{current}d** current · **{longest}d** longest"
    return f"{before}{START}\n\n{streaks}\n\n{END}{after}"


def main():
    days = fetch_activity()
    path = ROOT / "README.md"
    readme = path.read_text(encoding="utf-8")
    updated = update_summary(readme, days)
    if readme != updated:
        path.write_text(updated, encoding="utf-8", newline="\n")
    print(f"Checked {len(days)} public contribution days through {days[-1][0]}.")


if __name__ == "__main__":
    main()
