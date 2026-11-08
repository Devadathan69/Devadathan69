"""Shared SVG primitives for the profile's two observatory scenes."""

from html import escape
from itertools import pairwise
from math import hypot
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MONO = "Consolas, 'Liberation Mono', monospace"
COMET_DEFS = """
    <linearGradient id="tail" x1="0" y1="1" x2="1" y2="0">
      <stop stop-color="#A89BFF" stop-opacity="0"/>
      <stop offset=".63" stop-color="#58C7FF" stop-opacity=".46"/>
      <stop offset="1" stop-color="#D8F6FF"/>
    </linearGradient>
    <radialGradient id="halo">
      <stop stop-color="#DEF8FF" stop-opacity=".82"/>
      <stop offset=".35" stop-color="#58C7FF" stop-opacity=".39"/>
      <stop offset="1" stop-color="#58C7FF" stop-opacity="0"/>
    </radialGradient>
"""
COMET = """<path d="M-158 19Q-60 17-5-8Q8-7 8 3Q-45 31-158 19Z" fill="url(#tail)" opacity=".22"/>
    <path d="M-134 14Q-56 13-4-3Q5-4 4 2Q-44 21-134 14Z" fill="url(#tail)" opacity=".72"/>
    <path d="M-91 13Q-32 8-2 0M-113 23Q-42 20-5 2M-70 0Q-35 1-5-2" fill="none" stroke="url(#tail)" stroke-width="1.05"/>
    <ellipse cx="-4" rx="23" ry="14" fill="url(#halo)"/>
    <path d="M-27 4Q-13 2 1-1" stroke="#C7F2FF" stroke-width="1.35" stroke-linecap="round" opacity=".8"/>
    <ellipse rx="4.3" ry="2.6" fill="#F4FDFF"/>"""


def svg(width, height, title, description, content, defs="", css=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{escape(title)}</title>
  <desc id="desc">{escape(description)}</desc>
  <defs>
    <linearGradient id="sky" x2="1" y2="1">
      <stop stop-color="#0B1020"/><stop offset="1" stop-color="#111B30"/>
    </linearGradient>
    <clipPath id="panel"><rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="15"/></clipPath>
{defs}  </defs>
{css}  <g clip-path="url(#panel)">
    <rect width="{width}" height="{height}" fill="url(#sky)"/>
{content}
  </g>
  <rect x=".6" y=".6" width="{width - 1.2:g}" height="{height - 1.2:g}" rx="15" fill="none" stroke="#4A5873" stroke-width="1.2"/>
</svg>
"""


def flight(points, duration, start, end):
    def xy(point):
        return f"{point[0]:g} {point[1]:g}"

    path = f"M{xy(points[0])} C{' '.join(map(xy, points[1:]))}"
    return f"""  <g class="motion" opacity="0">
    <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{start:g};{start + .035:g};{end - .04:g};{end:g};1" dur="{duration}s" repeatCount="indefinite"/>
    <animateMotion path="{path}" keyPoints="0;0;1;1" keyTimes="0;{start:g};{end:g};1" calcMode="linear" dur="{duration}s" repeatCount="indefinite" rotate="auto"/>
    {COMET}
  </g>"""


def flight_samples(points, start, end):
    """Sample a cubic at approximately constant distance, as SVG motion does."""
    curve = []
    for index in range(121):
        t = index / 120
        weights = ((1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t**2, t**3)
        curve.append(tuple(sum(weight * point[axis] for weight, point in zip(weights, points)) for axis in (0, 1)))
    distance = [0]
    for (x1, y1), (x2, y2) in pairwise(curve):
        distance.append(distance[-1] + hypot(x2 - x1, y2 - y1))
    return [(x, y, start + (end - start) * arc / distance[-1]) for (x, y), arc in zip(curve, distance)]


def wake(x, y, radius, samples, duration, size):
    cx, cy = x + size / 2, y + size / 2
    near_x, near_y, phase = min(samples, key=lambda point: (point[0] - cx) ** 2 + (point[1] - cy) ** 2)
    distance = hypot(near_x - cx, near_y - cy)
    if distance >= radius:
        return ""
    peak = .44 * (1 - distance / radius)
    return f"""  <rect class="motion" x="{x:.2f}" y="{y:.2f}" width="{size:g}" height="{size:g}" rx="2" fill="#C1F2FF" opacity="0">
    <animate attributeName="opacity" values="0;0;{peak:.3f};0;0" keyTimes="0;{phase - .025:.4f};{phase:.4f};{phase + .045:.4f};1" dur="{duration}s" repeatCount="indefinite"/>
  </rect>"""


def write_visuals(files, check):
    for path, content in files.items():
        if check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Generated file differs: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                path.write_text(content, encoding="utf-8", newline="\n")
