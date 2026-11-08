"""Generate responsive contribution-grid lettering with a 16-second motion loop."""

import argparse
from math import hypot, sin
from random import Random

from visuals import COMET_DEFS, MONO, ROOT, flight, flight_samples, svg, wake, write_visuals


FONT = {
    "A": ("01110", "11011", "10001", "11111", "10001", "10001", "10001"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "V": ("10001", "10001", "10001", "10001", "01010", "01010", "00100"),
}
GREENS = ("#31954B", "#3FB950", "#56D364", "#79E38B")
DURATION = 16
PASS = (.34, .70)


def lettering(label):
    column = 0
    pixels = []
    for char in label:
        if char == " ":
            column += 2
        else:
            pixels.extend(
                (column + offset, row)
                for row, line in enumerate(FONT[char])
                for offset, value in enumerate(line)
                if value == "1"
            )
            column += 6
    return pixels, column - 1


def render(mobile, animated):
    width, height, pitch, size = (480, 215, 12.2, 10.0) if mobile else (960, 249, 11.9, 9.9)
    label = "DATHAN" if mobile else "DEVADATHAN M R"
    pixels, columns = lettering(label)
    left = (width - columns * pitch + pitch - size) / 2
    top = 74 if mobile else 87
    track = ((-105, top + 77), (width * .21, top + 99), (width * .64, top - 46), (width + 135, top + 18))
    samples = flight_samples(track, *PASS)
    rng = Random(69)
    cells, glints = [], []
    for col, row in pixels:
        x, y = left + pitch * col, top + pitch * row
        # Three overlapping fronts move out from different points in the wordmark.
        u = col / columns
        front = min(hypot((u - seed) * 2.6, (row - origin) / 10)
                    for seed, origin in ((.09, 1), (.44, 5), (.87, 2)))
        bucket = min(9, int(front * 12 + rng.random() * 3))
        intensity = (sin(13 * u - row * .44) + 1) * .7 + rng.random() * 1.85
        color = GREENS[min(3, int(intensity))]
        motion_class = f' class="reveal-{bucket}"' if animated else ""
        cells.append(f'  <rect{motion_class} x="{x:.2f}" y="{y:.2f}" width="{size:g}" height="{size:g}" rx="2.1" fill="{color}"/>')
        if animated:
            glint = wake(x, y, 23, samples, DURATION, size)
            if glint:
                glints.append(glint)

    rules = []
    if animated:
        for bucket in range(10):
            start = .8 + .86 * bucket
            rules.append(
                f".reveal-{bucket} {{ animation: wake-{bucket} {DURATION}s cubic-bezier(.25,.6,.4,1) infinite; }}\n"
                f"@keyframes wake-{bucket} {{ 0%, {start:g}% {{opacity:.05}} "
                f"{start + 4.2:g}%, 70% {{opacity:1}} {77 + bucket * .75:g}% {{opacity:.91}} "
                "89%, 95% {opacity:1} 100% {opacity:.05} }"
            )
    css = "" if not animated else f"""  <style>
    @media (prefers-reduced-motion: no-preference) {{
      {''.join(rules)}
    }}
    @media (prefers-reduced-motion: reduce) {{ .motion {{ display: none; }} }}
  </style>
"""
    defs = f"""
    <pattern id="grid" width="{pitch:g}" height="{pitch:g}" x="{left:.2f}" y="{top}" patternUnits="userSpaceOnUse">
      <rect width="{size:g}" height="{size:g}" rx="2.1" fill="#1D2A3C"/>
    </pattern>
    <radialGradient id="sky-glow" cx=".75" cy=".43" r=".74">
      <stop stop-color="#353B6D" stop-opacity=".45"/><stop offset="1" stop-color="#353B6D" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="grid-glow" cx=".25" cy=".48">
      <stop stop-color="#2F805F" stop-opacity=".18"/><stop offset="1" stop-color="#2F805F" stop-opacity="0"/>
    </radialGradient>
{COMET_DEFS if animated else ""}"""
    type_cells = "\n".join(cells + glints)
    moving_comet = flight(track, DURATION, *PASS) if animated else ""
    stars = "\n".join(
        f'  <circle cx="{30 + rng.random() * (width - 60):.1f}" cy="{54 + rng.random() * (height - 102):.1f}" r="{.45 + rng.random() * .75:.2f}" fill="#B0C6E9" opacity="{.15 + rng.random() * .3:.2f}"/>'
        for _ in range(21)
    )
    content = f"""  <rect width="{width}" height="{height}" fill="url(#sky-glow)"/>
{stars}
  <rect x="22" y="{top - pitch - 6:.2f}" width="{width - 44}" height="{pitch * 9 + 12:.2f}" rx="9" fill="#0B1324" stroke="#2D3F58"/>
  <rect x="28" y="{top - pitch:.2f}" width="{width - 56}" height="{pitch * 9:.2f}" rx="5" fill="url(#grid)"/>
  <rect x="23" y="{top - pitch - 5:.2f}" width="{width - 46}" height="{pitch * 9 + 10:.2f}" rx="8" fill="url(#grid-glow)"/>
  <path d="M26 47h{width - 52}M26 {height - 37}h{width - 52}" stroke="#34455F"/>
  <path d="M30 21v14m-7-7h14" stroke="#58C7FF" stroke-width="1.2"/>
  <circle cx="30" cy="28" r="3" fill="#A1E5FF"/>
  <g font-family="{MONO}" font-size="{15 if mobile else 14}" letter-spacing="1.3">
    <text x="45" y="33" font-weight="700" fill="#E8EEF9">CONSTELLATION LAB</text>
    <text x="{width - 27}" y="33" text-anchor="end" fill="#ADBBD4">DEVADATHAN69</text>
    <text x="26" y="{height - 16}" fill="#98A7C2">01 / CONTRIBUTION GRID</text>
    <text x="{width - 27}" y="{height - 16}" text-anchor="end" fill="#A89BFF">PROFILE</text>
  </g>
{type_cells}
{moving_comet}"""
    return svg(width, height, "Devadathan M R",
               f"Decorative contribution-square lettering spelling {label}.", content, defs, css)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare against the committed SVGs")
    args = parser.parse_args()
    directory = ROOT / "assets/name-grid"
    files = {
        directory / f"{size}{'' if animated else '-static'}.svg": render(size == "mobile", animated)
        for size in ("desktop", "mobile")
        for animated in (True, False)
    }
    write_visuals(files, args.check)


if __name__ == "__main__":
    main()
