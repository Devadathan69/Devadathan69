"""Read the public contribution calendar using GitHub's GraphQL API."""

from datetime import date, timedelta
import json
import subprocess

USERNAME = "Devadathan69"
LEVELS = ("NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE")


def validate_days(days):
    if not 365 <= len(days) <= 372:
        raise ValueError("Expected about one year of public contributions")
    for index, (day, count, level) in enumerate(days):
        if day != days[0][0] + timedelta(days=index):
            raise ValueError("Expected consecutive contribution dates")
        if type(count) is not int or count < 0 or type(level) is not int or not 0 <= level <= 4 or bool(count) != bool(level):
            raise ValueError(f"Inconsistent contribution count or level for {day}")


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
    validate_days(days)
    if sum(count for _, count, _ in days) != recent["totalContributions"]:
        raise ValueError("GitHub contribution totals were inconsistent")
    return days
