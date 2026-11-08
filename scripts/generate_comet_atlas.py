"""Generate Comet Atlas from a verified public calendar snapshot."""

import argparse
from datetime import date, timedelta
import json
from random import Random

from github_calendar import USERNAME, fetch_activity, validate_days
from visuals import COMET, COMET_DEFS, MONO, ROOT, flight, flight_samples, svg, wake, write_visuals


SNAPSHOT = ROOT / "data/public-calendar.json"
COLORS = ("#1D293C", "#1A593D", "#238636", "#3FB950", "#69D67D")
MOTION_CSS = "  <style>@media (prefers-reduced-motion: reduce) { .motion { display: none; } }</style>\n"


def calendar_weeks(days):
    first = days[0][0]
    sunday = first - timedelta(days=(first.weekday() + 1) % 7)
    weeks = [[] for _ in range((days[-1][0] - sunday).days // 7 + 1)]
    for day, count, level in days:
        week, row = divmod((day - sunday).days, 7)
        weeks[week].append((day, row, count, level))
    return weeks


def draw_band(weeks, left, top, pitch, samples):
    cells, labels, glints = [], [], []
    previous_month, last_label = 0, -3
    for column, week in enumerate(weeks):
        x = left + pitch * column
        month = week[-1][0]
        if month.month != previous_month and column - last_label >= 3 and column < len(weeks) - 1:
            labels.append(f'  <text x="{x:.2f}" y="{top - 10}">{month:%b}</text>')
            previous_month, last_label = month.month, column
        for day, row, count, level in week:
            y = top + 15 * row
            mark = f'<circle cx="{x + 6:.2f}" cy="{y + 6}" r="{.45 + .46 * level:.2f}" fill="#D3FAE0" opacity=".68"/>' if level else ""
            unit = "contribution" if count == 1 else "contributions"
            cells.append(
                f'  <g><title>{day:%d %b %Y} · {count} {unit}</title>'
                f'<rect x="{x:.2f}" y="{y}" width="12" height="12" rx="2" fill="{COLORS[level]}"/>{mark}</g>'
            )
            if samples and count:
                glint = wake(x, y, 23, samples, 20, 12)
                if glint:
                    glints.append(glint)
    for row, label in ((1, "M"), (3, "W"), (5, "F")):
        labels.append(f'  <text x="{left - 18}" y="{top + 15 * row + 10}">{label}</text>')
    label_markup = "\n".join(labels)
    star_markup = "\n".join(cells + glints)
    return f"""  <g font-family="{MONO}" font-size="12" fill="#AAB8D0">
{label_markup}
  </g>
{star_markup}"""


def observatory(width, height):
    rng = Random(374)
    stars = []
    for _ in range(32):
        x, y = 24 + rng.random() * (width - 48), height - 128 + rng.random() * 63
        stars.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{.5 + rng.random() * .75:.2f}" fill="#D4E0FF" opacity="{.28 + rng.random() * .44:.2f}"/>')
    star_markup = "\n".join(stars)
    return f"""  <ellipse cx="{width * .76:g}" cy="{height - 74}" rx="{width * .5:g}" ry="116" fill="url(#violet)"/>
  <ellipse cx="{width * .29:g}" cy="{height - 41}" rx="{width * .45:g}" ry="105" fill="url(#teal)"/>
{star_markup}
  <g transform="translate(0 {height - 88}) scale({width / 960:g} 1)">
    <path d="M0 30 53 29 112 19 170 27 225 14 279 20 330 14 392 22 447 21 507 27 552 17 611 25 671 18 736 21 802 14 864 19 917 12 960 20v43H0Z" fill="#1D2B45"/>
    <path d="M0 40 57 33 115 35 176 32 232 39 291 33 347 36 399 31 460 39 522 32 580 36 645 32 696 35 740 29 791 31 842 26 899 32 960 27v36H0Z" fill="#132037"/>
    <path d="M0 45 57 39 115 41 176 38 232 45 291 39 347 42 399 37 460 45 522 38 580 42 645 38 696 41 740 35 791 37 842 32 899 38 960 33" fill="none" stroke="#36506D" stroke-opacity=".48"/>
  </g>
  <g transform="translate({width - 96} {height - 85})" stroke="#6987A5" stroke-width="1" fill="#1D2C45">
    <path d="M0 21v-5a16 16 0 0 1 32 0v5Z"/>
    <rect x="-2" y="21" width="36" height="11" rx="1"/>
    <path d="M16 0c5 4 8 10 8 20M-7 32h45" fill="none"/>
    <path d="M4 24h7m14 0h4" stroke="#85D5DE" opacity=".75"/>
  </g>"""


def render(days, mobile, animated):
    width, height = (480, 455) if mobile else (960, 322)
    weeks = calendar_weeks(days)
    split = (len(weeks) + 1) // 2
    bands = (weeks[:split], weeks[split:]) if mobile else (weeks,)
    left = 48
    pitch = (width - left - 29 - 12) / (len(bands[0]) - 1)
    track = ((-110, height - 110), (width * .21, height - 74),
             (width * .61, 87), (width + 137, 100))
    samples = flight_samples(track, .21, .64) if animated else ()
    chart = "\n".join(
        draw_band(band, left, 82 + 127 * index, pitch, samples)
        for index, band in enumerate(bands)
    )
    legend = "\n".join(
        f'  <rect x="{width - 116 + 12 * index}" y="{height - 23}" width="8" height="8" rx="1.4" fill="{color}"/>'
        for index, color in enumerate(COLORS)
    )
    still = f'<g class="still" transform="translate({width - 168} {height - 111}) rotate(-9)">{COMET}</g>'
    comet = flight(track, 20, .21, .64) if animated else ""
    css = MOTION_CSS + "  <style>@media (prefers-reduced-motion: no-preference) { .still { display: none; } }</style>\n" if animated else ""
    defs = """
    <radialGradient id="violet">
      <stop stop-color="#7665AB" stop-opacity=".44"/><stop offset="1" stop-color="#7665AB" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="teal">
      <stop stop-color="#32828E" stop-opacity=".31"/><stop offset="1" stop-color="#32828E" stop-opacity="0"/>
    </radialGradient>
""" + COMET_DEFS
    body = f"""{observatory(width, height)}
  <path d="M24 48h{width - 48}M24 {height - 35}h{width - 48}" stroke="#34455F"/>
  <path d="M32 17q0 9 8 9-8 0-8 9 0-9-8-9 8 0 8-9Z" fill="none" stroke="#A89BFF" stroke-width="1.3"/>
  <g font-family="{MONO}" font-size="13" letter-spacing="1.15">
    <text x="49" y="31" font-weight="700" fill="#E8EEF9">COMET ATLAS</text>
    <text x="{width - 25}" y="31" text-anchor="end" fill="#98A7C2">PUBLIC CALENDAR / 02</text>
  </g>
{chart}
{still}
{comet}
  <g font-family="{MONO}" font-size="12" fill="#C7D5E9">
    <text x="25" y="{height - 15}">{days[0][0]:%d %b %Y} – {days[-1][0]:%d %b %Y}</text>
    <text x="{width - 124}" y="{height - 15}" text-anchor="end">Less</text>
    <text x="{width - 25}" y="{height - 15}" text-anchor="end">More</text>
  </g>
{legend}"""
    description = (f"Public GitHub calendar from {days[0][0]:%d %b %Y} to {days[-1][0]:%d %b %Y}. "
                   "Each day is a tile. Brighter tiles and larger centers represent more contributions.")
    return svg(width, height, "Comet Atlas", description, body, defs, css)


def read_snapshot():
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if payload["user"] != USERNAME:
        raise ValueError("Snapshot is for a different GitHub profile")
    days = [(date.fromisoformat(day), count, level) for day, count, level in payload["days"]]
    validate_days(days)
    return days


def snapshot_text(days):
    rows = ",\n".join(f'    ["{day.isoformat()}", {count}, {level}]' for day, count, level in days)
    return f'{{\n  "user": "{USERNAME}",\n  "days": [\n{rows}\n  ]\n}}\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="compare against the committed SVGs")
    mode.add_argument("--refresh", action="store_true", help="fetch the public calendar with GitHub CLI")
    args = parser.parse_args()
    days = fetch_activity() if args.refresh else read_snapshot()
    directory = ROOT / "assets/comet-atlas"
    files = {
        directory / f"{size}{'' if animated else '-static'}.svg": render(days, size == "mobile", animated)
        for size in ("desktop", "mobile")
        for animated in (True, False)
    }
    if args.refresh:
        files[SNAPSHOT] = snapshot_text(days)
    write_visuals(files, args.check)
    print(f"Atlas calendar covers {len(days)} public contribution days through {days[-1][0]}.")


if __name__ == "__main__":
    main()
