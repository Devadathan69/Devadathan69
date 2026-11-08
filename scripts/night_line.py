"""Draw the Night Line contribution calendar from dated contribution counts."""

from datetime import timedelta


WINDOW_COLORS = ("#303b4d", "#855f58", "#ae7c64", "#d6a176", "#f6d79f")
MONO = "Consolas, 'Liberation Mono', monospace"


def draw_windows(band, left, top, pitch):
    labels = []
    windows = []
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
            windows.append(
                f'  <rect x="{x:.1f}" y="{y}" width="12" height="12" rx="2.2" fill="{WINDOW_COLORS[level]}">'
                f'<title>{day:%d %b %Y} · {count}</title></rect>'
            )
    label_markup = "\n".join(labels)
    window_markup = "\n".join(windows)
    return f"""  <g font-family="{MONO}" font-size="13" fill="#c8ccda">
{label_markup}
  </g>
{window_markup}"""


def draw_train(width, rail):
    coach_windows = "\n".join(
        f'    <rect x="{x}" y="8" width="6" height="5" rx="1.1" fill="#f5c98e"/>'
        for x in (9, 19, 29, 39, 60, 70, 80, 90, 110, 120, 130)
    )
    wheels = "\n".join(
        f'    <circle cx="{x}" cy="22" r="2.6" fill="#141b2a" stroke="#687790"/>'
        for x in (12, 40, 63, 91, 112, 140)
    )
    ties = " ".join(f"M{x} {rail + 3}l-5 4" for x in range(42, width - 30, 25))
    return f"""  <rect x="24" y="{rail - 32}" width="{width - 48}" height="56" rx="8" fill="url(#water)"/>
  <g clip-path="url(#rail-window)">
    <circle cx="{width - 96}" cy="{rail - 21}" r="13" fill="#e9b6a6" opacity=".24"/>
    <path d="M24 {rail - 3}h{width - 48}" stroke="#8793ad" stroke-opacity=".33"/>
    <path d="{ties}" stroke="#77778c" stroke-opacity=".48"/>
    <path d="M24 {rail}h{width - 48}m0 4H24" stroke="#8292b0" stroke-opacity=".74"/>
    <path d="M39 {rail + 14}h48m22 4h32m48-7h47m31 6h42m32-4h19m29 6h32"
      stroke="#879bb2" stroke-opacity=".34"/>
    <g transform="translate(0 {rail - 24})">
      <g class="train">
        <path d="M3 18h146M47 16h10m39 0h11" stroke="#9a94aa" stroke-width="1.7"/>
        <path d="M4 4h40a4 4 0 0 1 4 4v12H2V7q0-3 2-3Zm50 0h40a4 4 0 0 1 4 4v12H52V7q0-3 2-3Z"
          fill="#3c435d" stroke="#8793af"/>
        <path d="M104 4h30q12 0 16 9v7h-48V7q0-3 2-3Z" fill="#484961" stroke="#a0a1b7"/>
        <path d="M6 17h38m12 0h38m12 0h37" stroke="#cb8a70" stroke-opacity=".85"/>
{coach_windows}
{wheels}
        <circle cx="147" cy="16" r="1.9" fill="#ffdfab"/>
        <path d="m150 15 19-3v10l-19-5Z" fill="url(#headlight)"/>
        <path d="M12 32h22m34 2h18m26-2h25" stroke="#e7ad7c" stroke-opacity=".42" stroke-linecap="round"/>
      </g>
    </g>
  </g>"""


def render_night_line(days, mobile=False):
    first, last = days[0][0], days[-1][0]
    origin = first - timedelta(days=(first.weekday() + 1) % 7)
    weeks = [[] for _ in range((last - origin).days // 7 + 1)]
    for day, count, level in days:
        column, row = divmod((day - origin).days, 7)
        weeks[column].append((day, row, count, level))

    width, height, rail = (480, 411, 359) if mobile else (960, 285, 233)
    middle = (len(weeks) + 1) // 2
    bands = [weeks[:middle], weeks[middle:]] if mobile else [weeks]
    left = 36
    pitch = (width - 2 * left - 12) / (len(bands[0]) - 1)
    calendar = "\n".join(
        draw_windows(band, left, 77 + 126 * index, pitch) for index, band in enumerate(bands)
    )
    legend = "\n".join(
        f'  <rect x="{width - 121 + 12 * index}" y="{height - 24}" width="8" height="8" rx="1.7" fill="{color}"/>'
        for index, color in enumerate(WINDOW_COLORS)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Night Line · GitHub contributions</title>
  <desc id="desc">Daily contribution windows from {first:%d %b %Y} to {last:%d %b %Y}, above an illustrated train. Brighter windows represent more contributions.</desc>
  <defs>
    <linearGradient id="sky" x2="1" y2="1">
      <stop stop-color="#141e30"/><stop offset="1" stop-color="#25283c"/>
    </linearGradient>
    <linearGradient id="water" x2="1" y2="0">
      <stop stop-color="#182b43"/><stop offset=".6" stop-color="#21334e"/><stop offset="1" stop-color="#49384d"/>
    </linearGradient>
    <linearGradient id="headlight">
      <stop stop-color="#f3ce97" stop-opacity=".37"/><stop offset="1" stop-color="#f3ce97" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="rail-window">
      <rect x="24" y="{rail - 32}" width="{width - 48}" height="56" rx="8"/>
    </clipPath>
  </defs>
  <style>
    .train {{ transform: translateX({width * .42:g}px); }}
    @media (prefers-reduced-motion: no-preference) {{
      .train {{ animation: cross 22s linear -7s infinite; }}
      @keyframes cross {{
        from {{ transform: translateX(-170px); }}
        to {{ transform: translateX({width}px); }}
      }}
    }}
  </style>
  <rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="url(#sky)" stroke="#515369"/>
  <path d="M24 48h{width - 48}" stroke="#687491" stroke-opacity=".45"/>
  <g fill="none" stroke="#e6bb94" stroke-width="1.5" stroke-linecap="round">
    <path d="M31 18v17m7-17v17m-9-12h11m-11 7h11"/>
  </g>
  <g font-family="{MONO}">
    <text x="50" y="32" fill="#f6d6ad" font-size="18" font-weight="700" letter-spacing="2">NIGHT LINE</text>
    <text x="{width - 25}" y="31" fill="#c8ccda" text-anchor="end" font-size="12" letter-spacing="1">GITHUB CONTRIBUTIONS</text>
  </g>
{calendar}
{draw_train(width, rail)}
  <g font-family="{MONO}" font-size="12" fill="#c8ccda">
    <text x="30" y="{height - 16}">{first:%b %Y} – {last:%b %Y}</text>
    <text x="{width - 128}" y="{height - 16}" text-anchor="end">Less</text>
    <text x="{width - 25}" y="{height - 16}" text-anchor="end">More</text>
  </g>
{legend}
</svg>
"""
