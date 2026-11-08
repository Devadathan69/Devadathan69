"""Generate Comet Atlas from a verified public calendar snapshot."""

import argparse
from datetime import date, timedelta
import json
from random import Random

from github_calendar import USERNAME, fetch_activity, validate_days
from visuals import COMET, COMET_DEFS, MONO, ROOT, flight, flight_samples, svg, wake, write_visuals


SNAPSHOT = ROOT / "data/public-calendar.json"
COLORS = ("#1D293C", "#1A593D", "#238636", "#3FB950", "#69D67D")
DURATION = 22
PASS = (.14, .57)
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
            labels.append(f'  <text x="{x:.2f}" y="{top - 12}">{month:%b}</text>')
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
                glint = wake(x, y, 22, samples, DURATION, 12)
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


def observatory(width, height, animated):
    rng = Random(374)
    stars = []
    for _ in range(48):
        x, y = 24 + rng.random() * (width - 48), height - 157 + rng.random() * 88
        stars.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{.4 + rng.random() * .82:.2f}" fill="#C3D6FF" opacity="{.17 + rng.random() * .48:.2f}"/>')
    star_markup = "\n".join(stars)
    drift = (
        f'<g class="motion"><animateTransform attributeName="transform" type="translate" '
        f'values="0 0;17 -4;0 0" keyTimes="0;.5;1" calcMode="spline" keySplines=".4 0 .6 1;.4 0 .6 1" '
        f'dur="{DURATION}s" repeatCount="indefinite"/>'
        f'<ellipse cx="{width * .77:g}" cy="{height - 112}" rx="{width * .57:g}" ry="143" fill="url(#violet)"/></g>'
        if animated else ""
    )
    return f"""  <ellipse cx="{width * .77:g}" cy="{height - 112}" rx="{width * .57:g}" ry="143" fill="url(#violet)" opacity=".63"/>
  <ellipse cx="{width * .28:g}" cy="{height - 82}" rx="{width * .58:g}" ry="94" fill="url(#teal)"/>
{drift}
  <g transform="translate({width * .23:g} {height - 119}) rotate(-13)">
    <ellipse rx="{width * .17:g}" ry="22" fill="none" stroke="#7496C3" stroke-opacity=".21"/>
    <ellipse rx="{width * .20:g}" ry="30" fill="none" stroke="#7496C3" stroke-opacity=".13" stroke-dasharray="2 5"/>
    <circle cx="{width * .104:g}" cy="-17.3" r="1.7" fill="#A1DFFF" opacity=".78"/>
  </g>
{star_markup}
  <g transform="translate(0 {height - 122}) scale({width / 960:g} 1)">
    <path d="M0 40Q48 22 91 34T180 29Q232 13 274 30T366 37Q418 23 462 42T567 37Q624 18 660 34T758 41Q839 17 880 24T960 18V90H0Z" fill="#23304E"/>
    <path d="M0 57Q78 37 134 52T234 46Q278 34 319 49T423 52Q475 39 524 56T625 53Q686 43 743 50T834 41Q898 30 960 37V90H0Z" fill="#1A2943"/>
    <path d="M0 73Q66 50 131 61T263 67Q337 49 422 61T575 73Q642 55 693 57T801 48Q848 43 881 52T960 45V90H0Z" fill="#111D32"/>
    <path d="M0 73Q66 50 131 61T263 67Q337 49 422 61T575 73Q642 55 693 57T801 48Q848 43 881 52T960 45" fill="none" stroke="#59719C" stroke-opacity=".52"/>
  </g>
  <g transform="translate({width - (102 if width < 600 else 142)} {height - 129})"
     stroke="#6683A9" stroke-width="1.15" fill="#14213A" stroke-linejoin="round">
    <path d="M-21 56v-13l15-7h59l14 7v13Z"/>
    <path d="M0 42V28a23 23 0 0 1 46 0v14Z"/>
    <path d="M12 39V26q0-11 7-20l5-1q-5 12-5 21v13Z" fill="#0A1427"/>
    <path d="M6 33c0-13 4-22 10-26M39 31c0-10-4-18-10-22M-24 56h95" fill="none" opacity=".62"/>
    <path d="M-12 47h9m14 0h6m13 0h6m14 0h9" stroke="#AADFF1" opacity=".74"/>
    <path d="M29 12l10-9" stroke="#B1DDF8" stroke-width="2.5"/>
    <path d="M37 4l4-3" stroke="#E2F8FF" stroke-width="2"/>
  </g>
  <path d="M27 {height - 38}h{width - 54}" stroke="#34455F"/>"""


def render(days, mobile, animated):
    width, height = (480, 505) if mobile else (960, 370)
    weeks = calendar_weeks(days)
    split = (len(weeks) + 1) // 2
    bands = (weeks[:split], weeks[split:]) if mobile else (weeks,)
    left = 48
    pitch = (width - left - 29 - 12) / (len(bands[0]) - 1)
    track = ((-125, height - 147), (width * .16, height - 62),
             (width * .62, 74), (width + 158, 102))
    samples = flight_samples(track, *PASS) if animated else ()
    chart = "\n".join(
        draw_band(band, left, 86 + 136 * index, pitch, samples)
        for index, band in enumerate(bands)
    )
    legend = "\n".join(
        f'  <rect x="{width - 116 + 12 * index}" y="{height - 23}" width="8" height="8" rx="1.4" fill="{color}"/>'
        for index, color in enumerate(COLORS)
    )
    still = f'<g class="still" transform="translate({width * .66:g} {height - 131}) rotate(-14)">{COMET}</g>'
    comet = flight(track, DURATION, *PASS) if animated else ""
    css = MOTION_CSS + "  <style>@media (prefers-reduced-motion: no-preference) { .still { display: none; } }</style>\n" if animated else ""
    defs = """
    <radialGradient id="violet">
      <stop stop-color="#8174BE" stop-opacity=".48"/><stop offset="1" stop-color="#7665AB" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="teal">
      <stop stop-color="#359AA5" stop-opacity=".32"/><stop offset="1" stop-color="#32828E" stop-opacity="0"/>
    </radialGradient>
""" + COMET_DEFS
    body = f"""{observatory(width, height, animated)}
  <path d="M24 48h{width - 48}" stroke="#34455F"/>
  <path d="M32 17q0 9 8 9-8 0-8 9 0-9-8-9 8 0 8-9Z" fill="none" stroke="#A89BFF" stroke-width="1.3"/>
  <g font-family="{MONO}" font-size="{15 if mobile else 14}" letter-spacing="1.15">
    <text x="49" y="31" font-weight="700" fill="#E8EEF9">COMET ATLAS</text>
    <text x="{width - 25}" y="31" text-anchor="end" fill="#A89BFF">PUBLIC CALENDAR / 02</text>
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
