"""Refresh the README graphics from GitHub's signed-out contribution calendar."""

from datetime import date, timedelta
from html import escape
from html.parser import HTMLParser
from itertools import groupby, takewhile
from pathlib import Path
import re
from urllib.request import Request, urlopen


USERNAME = "Devadathan69"
ASSETS = Path(__file__).resolve().parent.parent / "assets"
COLORS = ("#222644", "#3c407a", "#605bc1", "#8a76ee", "#bd9aff")
MONO = "Consolas, 'Liberation Mono', monospace"


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
        if any(not 0 <= level < len(COLORS) or bool(level) != bool(count) for _, level, count in days):
            raise ValueError("GitHub returned inconsistent contribution counts")
        return days


def svg(height, title, content):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" viewBox="0 0 960 {height}" role="img" aria-labelledby="title">
  <title id="title">{escape(title)}</title>
  <rect x=".5" y=".5" width="959" height="{height - 1}" rx="13" fill="#12152b" stroke="#484367"/>
{content}
</svg>
"""


def contribution_grid(days):
    first, last = days[0][0], days[-1][0]
    origin = first - timedelta(days=(first.weekday() + 1) % 7)
    columns = (last - origin).days // 7 + 1
    left, top, dx, dy = 36, 56, 17, 15
    right = left + (columns - 1) * dx
    row_length = right - left
    path_length = 7 * row_length + 6 * dy
    travel = .94
    duration = "36s"

    route = [f"M{left} {top}"]
    for row in range(7):
        route.append(f"H{right if row % 2 == 0 else left}")
        if row < 6:
            route.append(f"V{top + (row + 1) * dy}")
    path = " ".join(route)
    cells = []
    eaten = []
    for day, level, _ in days:
        column, row = divmod((day - origin).days, 7)
        x, y = left + column * dx - 6, top + row * dy - 6
        cell = f'x="{x}" y="{y}" width="12" height="12" rx="2"'
        cells.append(f'    <rect {cell} fill="{COLORS[level]}"/>')
        if level:
            progress = (row * (row_length + dy) + (column * dx if row % 2 == 0 else row_length - column * dx)) / path_length
            phase = max(.0001, progress * travel)
            eaten.append(f"""    <rect {cell} fill="{COLORS[0]}" opacity="0">
      <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;{phase:.5f};.985;1" calcMode="discrete" dur="{duration}" repeatCount="indefinite"/>
    </rect>""")

    snake = []
    for index in reversed(range(6)):
        color = ("#78f9de", "#59e6ce", "#49ccb9", "#3cb6a8", "#329a98", "#2e7f88")[index]
        face = '<path d="M1 -2.4h1.6m-1.6 4.8h1.6" stroke="#133448" stroke-width="1.6" stroke-linecap="round"/>' if index == 0 else ""
        delay = f"{index * .086:.3f}s"
        snake.append(f"""    <g visibility="hidden">
      <rect x="-6.5" y="-6.5" width="13" height="13" rx="3" fill="{color}"/>{face}
      <set attributeName="visibility" to="visible" begin="{delay}" dur="indefinite"/>
      <animateMotion path="{path}" rotate="auto" begin="{delay}" keyPoints="0;1;1" keyTimes="0;{travel};1" calcMode="linear" dur="{duration}" repeatCount="indefinite"/>
    </g>""")

    cell_markup = "\n".join(cells)
    motion_markup = "\n".join(eaten + snake)
    legend = "\n".join(
        f'  <rect x="{728 + 17 * index}" y="168" width="12" height="12" rx="2" fill="{color}"/>'
        for index, color in enumerate(COLORS)
    )
    return svg(198, f"Contribution replay for {USERNAME}, {first:%b %Y} to {last:%b %Y}", f"""  <style>
    .motion {{ display: none; }}
    @media (prefers-reduced-motion: no-preference) {{ .motion {{ display: inline; }} }}
  </style>
  <g font-family="{MONO}" font-size="15" font-weight="700" letter-spacing="1.4">
    <text x="30" y="33" fill="#9afbe8">CONTRIBUTION REPLAY</text>
    <text x="930" y="33" text-anchor="end" fill="#c8c4ef">{first:%b %Y} → {last:%b %Y}</text>
  </g>
  <g>
{cell_markup}
  </g>
  <g class="motion">
{motion_markup}
  </g>
  <path d="M30 159h900" stroke="#343252"/>
  <g font-family="{MONO}" font-size="13" fill="#c8c4ef">
    <text x="30" y="179">PUBLIC GITHUB CALENDAR</text>
    <text x="714" y="179" text-anchor="end">LESS</text>
    <text x="827" y="179">MORE</text>
  </g>
{legend}""")


def statistics(days):
    active = [count > 0 for _, _, count in days]
    recent = active if active[-1] else active[:-1]
    current = sum(1 for _ in takewhile(bool, reversed(recent)))
    longest = max((sum(1 for _ in group) for flag, group in groupby(active) if flag), default=0)
    total = sum(count for _, _, count in days)
    last = days[-1][0]
    cards = []
    for index, (value, label, color) in enumerate((
        (f"{total:,}", "Contributions", "#c6a7ff"),
        (f"{current}d", "Current streak", "#83f5df"),
        (f"{longest}d", "Longest streak", "#ffbdaa"),
    )):
        x = 27 + 306 * index
        cards.append(f"""  <rect x="{x}" y="57" width="294" height="124" rx="10" fill="#1d2040" stroke="#454268"/>
  <text x="{x + 147}" y="119" text-anchor="middle" fill="{color}" font-size="48" font-weight="700">{value}</text>
  <text x="{x + 147}" y="151" text-anchor="middle" fill="#e1dff6" font-size="23">{label}</text>""")
    card_markup = "\n".join(cards)
    return svg(207, f"{total} contributions, {current}-day current streak and {longest}-day longest streak in the displayed GitHub calendar", f"""  <g font-family="{MONO}" font-size="15" fill="#c8c4ef">
    <text x="29" y="34" letter-spacing="1.5" fill="#9afbe8">GITHUB ACTIVITY</text>
    <text x="931" y="34" text-anchor="end">THROUGH {last:%d %b %Y}</text>
  </g>
  <g font-family="Arial, 'Liberation Sans', sans-serif">
{card_markup}
  </g>""")


def main():
    request = Request(
        f"https://github.com/users/{USERNAME}/contributions",
        headers={"User-Agent": "GitHub Profile README Activity", "Accept-Language": "en-US"},
    )
    with urlopen(request, timeout=30) as response:
        calendar = Calendar()
        calendar.feed(response.read().decode("utf-8"))
    days = calendar.days()
    graphics = {"contribution-grid.svg": contribution_grid(days), "stats.svg": statistics(days)}
    for name, content in graphics.items():
        (ASSETS / name).write_text(content, encoding="utf-8", newline="\n")
    print(f"Rendered {len(days)} days through {days[-1][0]} for {USERNAME}")


if __name__ == "__main__":
    main()
