"""Draw the Comet Atlas contribution calendar from dated contribution counts."""

from datetime import timedelta


STAR_COLORS = ("#303851", "#615986", "#8678b0", "#b5a4df", "#f4d1bd")
MONO = "Consolas, 'Liberation Mono', monospace"


def draw_grid(band, left, top, pitch):
    labels = []
    cells = []
    previous_month = None
    previous_label = -3
    for column, week in enumerate(band):
        x = left + column * pitch
        month = week[-1][0].month
        if month != previous_month and column - previous_label >= 3 and column < len(band) - 1:
            labels.append(f'    <text x="{x:.1f}" y="{top - 9}">{week[-1][0]:%b}</text>')
            previous_label = column
            previous_month = month
        for day, row, count, level in week:
            y = top + 15 * row
            cells.append(
                f'  <rect x="{x:.1f}" y="{y}" width="12" height="12" rx="2.2" fill="{STAR_COLORS[level]}">'
                f'<title>{day:%d %b %Y} · {count}</title></rect>'
            )
            if level >= 2:
                core = "#473753" if level == 4 else "#f6ebff"
                cells.append(
                    f'  <path d="M{x + 6:.1f} {y + 3}l2.5 3-2.5 3-2.5-3Z" fill="{core}" opacity=".76"/>'
                )
    label_markup = "\n".join(labels)
    cell_markup = "\n".join(cells)
    return f"""  <g font-family="{MONO}" font-size="13" fill="#c8ccda">
{label_markup}
  </g>
{cell_markup}"""


def draw_horizon(width, top):
    return f"""  <g clip-path="url(#horizon)">
    <g transform="translate(0 {top})">
      <rect width="{width}" height="63" fill="url(#afterglow)"/>
      <g transform="scale({width / 960:g} 1)">
        <g fill="#eee1fa" opacity=".62">
          <circle cx="66" cy="15" r="1"/><circle cx="121" cy="30" r=".8"/>
          <circle cx="206" cy="9" r="1.3"/><circle cx="344" cy="20" r=".8"/>
          <circle cx="432" cy="12" r="1"/><circle cx="534" cy="32" r=".9"/>
          <circle cx="672" cy="10" r="1.1"/><circle cx="813" cy="21" r="1.2"/>
          <circle cx="892" cy="9" r=".8"/><circle cx="923" cy="28" r="1.1"/>
        </g>
        <path d="M0 51 42 44 89 47 143 36 194 42 232 47 275 43 320 48 384 50 443 40 495 43 551 37 603 45 655 43 710 48 771 38 822 41 885 33 960 46v17H0Z"
          fill="#45405e"/>
        <path d="M0 57 55 54 111 58 157 49 196 52 245 56 301 48 353 55 405 53 468 58 528 50 597 54 650 49 706 54 759 56 824 47 886 52 960 55v8H0Z"
          fill="#22243b"/>
      </g>
      <g transform="translate(0 22)">
        <g class="comet">
          <path d="M-165 19Q-76 16-2-3Q4-4 3 1Q-55 18-165 19Z" fill="url(#tail)"/>
          <path d="M-132 18Q-56 13-5 0" fill="none" stroke="url(#filament)" stroke-width="1.3"/>
          <path d="M-97 26Q-39 19-2 1" fill="none" stroke="url(#filament)" stroke-opacity=".65"/>
          <circle r="13" fill="url(#comet-glow)"/>
          <circle r="3.3" fill="#fff3df"/>
          <circle cx="-22" cy="6.5" r="1" fill="#e3ceff"/>
        </g>
      </g>
    </g>
  </g>"""


def render_comet_atlas(days, mobile=False):
    first, last = days[0][0], days[-1][0]
    origin = first - timedelta(days=(first.weekday() + 1) % 7)
    weeks = [[] for _ in range((last - origin).days // 7 + 1)]
    for day, count, level in days:
        column, row = divmod((day - origin).days, 7)
        weeks[column].append((day, row, count, level))

    width, height, horizon = (480, 407, 319) if mobile else (960, 281, 193)
    middle = (len(weeks) + 1) // 2
    bands = [weeks[:middle], weeks[middle:]] if mobile else [weeks]
    left = 36
    pitch = (width - 2 * left - 12) / (len(bands[0]) - 1)
    calendar = "\n".join(
        draw_grid(band, left, 77 + 126 * index, pitch) for index, band in enumerate(bands)
    )
    legend = "\n".join(
        f'  <rect x="{width - 121 + 12 * index}" y="{height - 24}" width="8" height="8" rx="1.7" fill="{color}"/>'
        for index, color in enumerate(STAR_COLORS)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Comet Atlas · GitHub contributions</title>
  <desc id="desc">Daily contributions from {first:%d %b %Y} to {last:%d %b %Y} as stars over a twilight horizon. Brighter tiles represent more contributions.</desc>
  <defs>
    <linearGradient id="sky" x2="1" y2="1">
      <stop stop-color="#151b35"/><stop offset=".6" stop-color="#202340"/><stop offset="1" stop-color="#352a47"/>
    </linearGradient>
    <linearGradient id="afterglow" x2="1" y2="1">
      <stop stop-color="#242943"/><stop offset=".6" stop-color="#4a3c63"/><stop offset="1" stop-color="#96616b"/>
    </linearGradient>
    <linearGradient id="tail">
      <stop stop-color="#a99bf0" stop-opacity="0"/><stop offset=".72" stop-color="#bdaaff" stop-opacity=".52"/>
      <stop offset="1" stop-color="#ffd5c5"/>
    </linearGradient>
    <linearGradient id="filament">
      <stop stop-color="#c3adff" stop-opacity="0"/><stop offset="1" stop-color="#efd6ff"/>
    </linearGradient>
    <radialGradient id="comet-glow">
      <stop stop-color="#fbd7f7" stop-opacity=".57"/><stop offset="1" stop-color="#fbd7f7" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="horizon">
      <rect x="24" y="{horizon}" width="{width - 48}" height="63" rx="8"/>
    </clipPath>
  </defs>
  <style>
    .comet {{ transform: translateX({width * .64:g}px); }}
    @media (prefers-reduced-motion: no-preference) {{
      .comet {{ animation: pass 18s linear -6s infinite; }}
      @keyframes pass {{
        0%, 14% {{ transform: translate(-30px, 14px); opacity: 0; }}
        24%, 67% {{ opacity: 1; }}
        82%, 100% {{ transform: translate({width + 160}px, -8px); opacity: 0; }}
      }}
    }}
  </style>
  <rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="url(#sky)" stroke="#515369"/>
  <path d="M24 48h{width - 48}" stroke="#687491" stroke-opacity=".45"/>
  <g fill="none" stroke="#e7c7f3" stroke-width="1.3" stroke-linecap="round">
    <path d="M33 18q0 8 7 8-7 0-7 8 0-8-7-8 7 0 7-8Z"/>
  </g>
  <g font-family="{MONO}">
    <text x="50" y="32" fill="#e9d8ff" font-size="18" font-weight="700" letter-spacing="2">COMET ATLAS</text>
    <text x="{width - 25}" y="31" fill="#c8ccda" text-anchor="end" font-size="12" letter-spacing="1">GITHUB CONTRIBUTIONS</text>
  </g>
{calendar}
{draw_horizon(width, horizon)}
  <g font-family="{MONO}" font-size="12" fill="#c8ccda">
    <text x="30" y="{height - 16}">{first:%b %Y} – {last:%b %Y}</text>
    <text x="{width - 128}" y="{height - 16}" text-anchor="end">Less</text>
    <text x="{width - 25}" y="{height - 16}" text-anchor="end">More</text>
  </g>
{legend}
</svg>
"""
