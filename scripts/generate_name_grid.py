"""Generate responsive contribution-grid lettering with a 16-second motion loop."""

import argparse
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
GREENS = ("#238636", "#2EA043", "#3FB950", "#56D364")


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
    width, height, pitch, size = (480, 194, 11.5, 9.2) if mobile else (960, 217, 11.6, 9.3)
    label = "DATHAN" if mobile else "DEVADATHAN M R"
    pixels, columns = lettering(label)
    left = (width - columns * pitch + pitch - size) / 2
    top = 66 if mobile else 77
    track = ((-120, 181), (width * .24, 213), (width * .70, 65), (width + 135, 113))
    samples = flight_samples(track, .44, .74)
    rng = Random(69)
    cells, glints = [], []
    for col, row in pixels:
        x, y = left + pitch * col, top + pitch * row
        color = GREENS[rng.randrange(len(GREENS))]
        bucket = rng.randrange(8)
        motion_class = f' class="reveal-{bucket}"' if animated else ""
        cells.append(f'  <rect{motion_class} x="{x:.2f}" y="{y:.2f}" width="{size:g}" height="{size:g}" rx="2.1" fill="{color}"/>')
        if animated:
            glint = wake(x, y, 18, samples, 16, size)
            if glint:
                glints.append(glint)

    rules = []
    if animated:
        for bucket in range(8):
            start = 2 + 1.5 * bucket
            rules.append(
                f".reveal-{bucket} {{ animation: wake-{bucket} 16s ease-in-out infinite; }}\n"
                f"@keyframes wake-{bucket} {{ 0%, {start:g}% {{opacity:0}} "
                f"{start + 7:g}%, 68% {{opacity:1}} {75 + bucket:g}% {{opacity:.91}} "
                "88%, 94% {opacity:1} 100% {opacity:0} }"
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
    <radialGradient id="sky-glow" cx=".65" cy=".35" r=".68">
      <stop stop-color="#476483" stop-opacity=".23"/><stop offset="1" stop-color="#476483" stop-opacity="0"/>
    </radialGradient>
{COMET_DEFS if animated else ""}"""
    type_cells = "\n".join(cells + glints)
    moving_comet = flight(track, 16, .44, .74) if animated else ""
    content = f"""  <rect width="{width}" height="{height}" fill="url(#sky-glow)"/>
  <rect x="20" y="{top - pitch:.2f}" width="{width - 40}" height="{pitch * 9:.2f}" rx="8" fill="url(#grid)"/>
  <path d="M24 48h{width - 48}M24 {height - 35}h{width - 48}" stroke="#34455F"/>
  <circle cx="30" cy="27" r="3" fill="#58C7FF"/>
  <g font-family="{MONO}" font-size="13" letter-spacing="1.35">
    <text x="44" y="32" font-weight="700" fill="#E8EEF9">CONSTELLATION LAB</text>
    <text x="{width - 25}" y="32" text-anchor="end" fill="#98A7C2">DEVADATHAN69</text>
    <text x="25" y="{height - 14}" fill="#98A7C2">PROFILE / NAME GRID</text>
    <text x="{width - 25}" y="{height - 14}" text-anchor="end" fill="#98A7C2">01</text>
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
