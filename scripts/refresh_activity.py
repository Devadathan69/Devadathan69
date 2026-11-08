"""Refresh public GitHub streaks in the profile README."""

from datetime import date, timedelta
from html.parser import HTMLParser
from itertools import groupby, takewhile
from pathlib import Path
import re
from urllib.request import Request, urlopen


USERNAME = "Devadathan69"
README = Path(__file__).resolve().parent.parent / "README.md"
START = "<!-- public-streaks:start -->"
END = "<!-- public-streaks:end -->"


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.counts = {}
        self.tooltip = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "td" and "ContributionCalendar-day" in attrs.get("class", "").split():
            self.cells[attrs["id"]] = (date.fromisoformat(attrs["data-date"]), int(attrs["data-level"]))
        if tag == "tool-tip":
            self.tooltip = attrs.get("for")

    def handle_data(self, data):
        if self.tooltip in self.cells:
            match = re.match(r"\s*(No|[\d,]+) contributions? on\b", data)
            if match:
                count = match[1]
                self.counts[self.tooltip] = 0 if count == "No" else int(count.replace(",", ""))

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self.tooltip = None

    def days(self):
        days = sorted((day, level, self.counts[cell]) for cell, (day, level) in self.cells.items())
        if not 365 <= len(days) <= 372:
            raise ValueError("Expected about one year of contributions")
        if any(day != days[0][0] + timedelta(days=index) for index, (day, _, _) in enumerate(days)):
            raise ValueError("GitHub returned a non-contiguous calendar")
        if any(not 0 <= level <= 4 or bool(level) != bool(count) for _, level, count in days):
            raise ValueError("GitHub returned inconsistent contribution counts")
        return days


def update_streaks(readme, days):
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("Expected one public streak section in the README")
    before, _, remainder = readme.partition(START)
    _, end, after = remainder.partition(END)
    if not end:
        raise ValueError("The public streak markers are out of order")

    active = [count > 0 for _, _, count in days]
    recent = active if active[-1] else active[:-1]
    current = sum(1 for _ in takewhile(bool, reversed(recent)))
    longest = max((sum(1 for _ in group) for flag, group in groupby(active) if flag), default=0)
    line = f"Public streaks · **{current}d** current · **{longest}d** longest"
    return f"{before}{START}\n\n{line}\n\n{END}{after}"


def main():
    request = Request(
        f"https://github.com/users/{USERNAME}/contributions",
        headers={"User-Agent": "GitHub Profile README Activity", "Accept-Language": "en-US"},
    )
    with urlopen(request, timeout=30) as response:
        calendar = Calendar()
        calendar.feed(response.read().decode("utf-8"))
    days = calendar.days()
    readme = README.read_text(encoding="utf-8")
    updated = update_streaks(readme, days)
    if readme != updated:
        README.write_text(updated, encoding="utf-8", newline="\n")
    print(f"Checked {len(days)} public contribution days through {days[-1][0]} for {USERNAME}")


if __name__ == "__main__":
    main()
