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
        if any(not 0 <= level <= 4 or bool(level) != bool(count) for _, level, count in days):
            raise ValueError("GitHub returned inconsistent contribution counts")
        return days


def svg(height, title, content):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" viewBox="0 0 960 {height}" role="img" aria-labelledby="title">
  <title id="title">{escape(title)}</title>
  <rect x=".5" y=".5" width="959" height="{height - 1}" rx="13" fill="#12152b" stroke="#484367"/>
{content}
</svg>
"""


def build_rhythm(days):
    first, last = days[0][0], days[-1][0]
    origin = first - timedelta(days=(first.weekday() + 1) % 7)
    weekly = [0] * ((last - origin).days // 7 + 1)
    for day, _, count in days:
        weekly[(day - origin).days // 7] += count

    peak_index = max(range(len(weekly)), key=weekly.__getitem__)
    peak = weekly[peak_index]
    bars = []
    rests = []
    for index, count in enumerate(weekly):
        x = 38 + index * 884 / (len(weekly) - 1)
        if count:
            amplitude = max(2, 48 * count / peak)
            bars.append(f"M{x:.1f} {112 - amplitude:.1f}V{112 + amplitude:.1f}")
        else:
            rests.append(f"M{x:.1f} 111v2")
    wave = " ".join(bars)
    silence = " ".join(rests)
    marker = ""
    if peak:
        x = 38 + peak_index * 884 / (len(weekly) - 1)
        marker = f"""  <path d="M{x:.1f} 64v96" stroke="#ffc5ab" stroke-width="7" stroke-linecap="round"/>
  <circle cx="{x:.1f}" cy="54" r="2.4" fill="#ffc5ab"/>"""
    title = f"Build Rhythm, weekly GitHub contributions for {USERNAME}. Peak week: {peak} contributions."
    return svg(211, title, f"""  <defs>
    <linearGradient id="rhythm" gradientUnits="userSpaceOnUse" x1="30" x2="930" y1="112" y2="112">
      <stop stop-color="#70efda"/>
      <stop offset=".45" stop-color="#809dfc"/>
      <stop offset="1" stop-color="#c998ff"/>
    </linearGradient>
    <linearGradient id="playback">
      <stop stop-color="#92c3fb" stop-opacity="0"/>
      <stop offset="1" stop-color="#a1f9eb" stop-opacity=".26"/>
    </linearGradient>
    <radialGradient id="plot-glow" cx=".64" cy=".56" r=".62">
      <stop stop-color="#574caa" stop-opacity=".29"/>
      <stop offset="1" stop-color="#574caa" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="plot"><rect x="26" y="50" width="908" height="122" rx="8"/></clipPath>
    <clipPath id="played"><rect class="playhead" x="-80" y="50" width="80" height="122"/></clipPath>
    <path id="bars" d="{wave}"/>
  </defs>
  <style>
    .motion {{ display: none; }}
    @media (prefers-reduced-motion: no-preference) {{
      .motion {{ display: inline; }}
      .playhead {{ animation: scan 10s linear infinite; }}
      @keyframes scan {{ from {{ transform: translateX(26px); }} to {{ transform: translateX(1014px); }} }}
    }}
  </style>
  <g font-family="{MONO}">
    <path d="M30 27v8m6-12v16m6-20v24m6-19v14m6-10v6" stroke="#8af5de" stroke-width="2.2" stroke-linecap="round"/>
    <text x="70" y="37" fill="#9afbe8" font-size="22" font-weight="700" letter-spacing="2">BUILD RHYTHM</text>
    <text x="930" y="35" text-anchor="end" fill="#c8c4ef" font-size="16" letter-spacing="1">WEEKLY GITHUB ACTIVITY</text>
  </g>
  <rect x="26" y="50" width="908" height="122" rx="8" fill="#101327" stroke="#2c304e"/>
  <rect x="26" y="50" width="908" height="122" rx="8" fill="url(#plot-glow)"/>
  <path d="M26 80h908M26 144h908" stroke="#363754" stroke-dasharray="2 5"/>
  <path d="M26 112h908" stroke="#414563"/>
  <path d="{silence}" fill="none" stroke="#626584" stroke-width="3" stroke-linecap="round"/>
  <g fill="none" stroke-linecap="round">
    <use href="#bars" stroke="url(#rhythm)" stroke-width="13" opacity=".13"/>
    <use href="#bars" stroke="url(#rhythm)" stroke-width="6"/>
{marker}
    <g class="motion" clip-path="url(#plot)">
      <g class="playhead">
        <rect x="-80" y="50" width="80" height="122" fill="url(#playback)"/>
        <path d="M0 50v122" stroke="#b9fff0" stroke-width="1.3"/>
        <circle cy="112" r="3" fill="#b9fff0"/>
      </g>
      <use href="#bars" clip-path="url(#played)" stroke="#d1fff5" stroke-width="6" opacity=".76"/>
    </g>
  </g>
  <g font-family="{MONO}" font-size="16" fill="#c8c4ef">
    <text x="30" y="195">{first:%b %Y}</text>
    <text x="480" y="195" text-anchor="middle" fill="#ffc5ab">PEAK WEEK · {peak:,} CONTRIBUTIONS</text>
    <text x="930" y="195" text-anchor="end">{last:%b %Y}</text>
  </g>""")


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
    graphics = {"build-rhythm.svg": build_rhythm(days), "stats.svg": statistics(days)}
    for name, content in graphics.items():
        (ASSETS / name).write_text(content, encoding="utf-8", newline="\n")
    print(f"Rendered {len(days)} days through {days[-1][0]} for {USERNAME}")


if __name__ == "__main__":
    main()
