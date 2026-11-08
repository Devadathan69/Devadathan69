"""Refresh public GitHub counts and the Night Line calendar together."""

from datetime import date, datetime, timedelta, timezone
from itertools import groupby, takewhile
import json
from pathlib import Path
import subprocess

from night_line import render_night_line


USERNAME = "Devadathan69"
FIRST_YEAR = 2024
ROOT = Path(__file__).resolve().parent.parent
START = "<!-- public-activity:start -->"
END = "<!-- public-activity:end -->"
LEVELS = ("NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE")


def fetch_activity():
    years = range(FIRST_YEAR, datetime.now(timezone.utc).year + 1)
    annual_fields = "\n".join(
        f'y{year}: contributionsCollection(from:"{year}-01-01T00:00:00Z", to:"{year}-12-31T23:59:59Z") '
        "{ contributionCalendar { totalContributions } }"
        for year in years
    )
    query = f"""query($login: String!) {{
      user(login: $login) {{
        recent: contributionsCollection {{
          contributionCalendar {{
            totalContributions
            weeks {{ contributionDays {{ date contributionCount contributionLevel }} }}
          }}
        }}
        {annual_fields}
      }}
    }}"""
    response = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}", "-f", f"login={USERNAME}"],
        capture_output=True, encoding="utf-8", timeout=40, check=False,
    )
    if response.returncode:
        raise RuntimeError(response.stderr.strip() or "GitHub contribution query failed")

    user = json.loads(response.stdout)["data"]["user"]
    recent = user["recent"]["contributionCalendar"]
    days = [
        (date.fromisoformat(day["date"]), day["contributionCount"], LEVELS.index(day["contributionLevel"]))
        for week in recent["weeks"]
        for day in week["contributionDays"]
    ]
    if not 365 <= len(days) <= 372:
        raise ValueError("Expected about one year of public contributions")
    if any(day != days[0][0] + timedelta(days=index) for index, (day, _, _) in enumerate(days)):
        raise ValueError("GitHub returned a non-contiguous calendar")
    rolling = recent["totalContributions"]
    lifetime = sum(user[f"y{year}"]["contributionCalendar"]["totalContributions"] for year in years)
    if sum(count for _, count, _ in days) != rolling or lifetime < rolling:
        raise ValueError("GitHub contribution totals were inconsistent")
    return days, rolling, lifetime


def update_summary(readme, days, rolling, lifetime):
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
    lines = (
        f"**{lifetime:,}** lifetime public contributions · **{rolling:,}** in the past year\n\n"
        f"Public streaks · **{current}d** current · **{longest}d** longest"
    )
    return f"{before}{START}\n\n{lines}\n\n{END}{after}"


def main():
    days, rolling, lifetime = fetch_activity()
    readme = ROOT / "README.md"
    updated = {
        readme: update_summary(readme.read_text(encoding="utf-8"), days, rolling, lifetime),
        ROOT / "assets/night-line.svg": render_night_line(days),
        ROOT / "assets/night-line-mobile.svg": render_night_line(days, mobile=True),
    }
    for path, content in updated.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Checked {lifetime} lifetime and {rolling} rolling public contributions through {days[-1][0]}.")


if __name__ == "__main__":
    main()
