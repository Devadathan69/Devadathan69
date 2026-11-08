"""Generate the toolkit and contact SVGs from the vendored brand paths."""

import argparse
from html import escape
from itertools import pairwise
import json
from pathlib import Path

from visuals import MONO, ROOT, svg, write_visuals


SANS = "system-ui, 'Segoe UI', sans-serif"
TEXT = "#E8EEF9"
BLUE = "#58C7FF"
VIOLET = "#A89BFF"
DURATION = 14
REDUCED = '  <style>@media (prefers-reduced-motion: reduce) { .motion { display: none; } }</style>\n'
BRANDS = json.loads(Path(__file__).with_name("brand-paths.json").read_text(encoding="utf-8"))

# Label lines, brand glyph, and a color that remains distinct on the navy tiles.
CLUSTERS = (
    ("Languages", BLUE, 3, (
        (("Python",), "python", "#82B7EA"),
        (("JavaScript",), "javascript", "#F2D87B"),
        (("TypeScript",), "typescript", "#80B5FF"),
        (("Java",), "java", "#F6AD92"),
        (("C",), "c", "#AAB6FF"),
        (("Dart",), "dart", "#76CFF7"),
    )),
    ("Frontend & Backend", "#83D8EB", 3, (
        (("React",), "react", "#83DCF4"),
        (("Next.js",), "nextdotjs", TEXT),
        (("Node.js",), "nodedotjs", "#9CD69B"),
        (("FastAPI",), "fastapi", "#7BDEC6"),
        (("Flask",), "flask", TEXT),
    )),
    ("AI & Agents", VIOLET, 4, (
        (("LangGraph",), "langgraph", "#86DEC9"),
        (("Claude", "Agent SDK"), "claude", "#F0AD95"),
        (("OpenAI", "Agents SDK"), None, "#C7BDFF"),
        (("TensorFlow", "Lite"), "tensorflow", "#F2B583"),
    )),
    ("Mobile & Embedded", "#83D8CF", 3, (
        (("Flutter",), "flutter", "#81D4FB"),
        (("ESP32",), "espressif", "#F39A9C"),
        (("Arduino",), "arduino", "#83DFDA"),
    )),
    ("Databases & Tools", "#98AFE8", 4, (
        (("PostgreSQL",), "postgresql", "#8FBCEB"),
        (("SQLite",), "sqlite", "#9DCEF6"),
        (("Firebase",), "firebase", "#F6C484"),
        (("Supabase",), "supabase", "#85DDB2"),
        (("Git",), "git", "#F1A28D"),
        (("GitHub",), "github", TEXT),
        (("Figma",), "figma", "#C6B0FA"),
    )),
)
CONTACTS = (
    ("GitHub", "github", TEXT),
    ("LinkedIn", "linkedin", "#9DC8FB"),
    ("Email", None, "#A3DDF4"),
    ("X", "x", TEXT),
)


def label(x, y, text, size, color=TEXT, *, align="start", mono=False, bold=False):
    family = MONO if mono else SANS
    weight = ' font-weight="600"' if bold else ""
    return (f'<text x="{x:g}" y="{y:g}" font-family="{family}" font-size="{size}" '
            f'text-anchor="{align}" fill="{color}"{weight}>{escape(text)}</text>')


def glyph(name, x, y, size, color):
    mark = BRANDS[name]
    scale = size / mark["size"]
    return (f'<path d="{mark["path"]}" transform="translate({x:g} {y:g}) scale({scale:.7f})" '
            f'fill="{color}"/>')


def header(width, left, right):
    return f"""  <path d="M30 21v12m-6-6h12" stroke="{BLUE}" stroke-width="1.15"/>
  <circle cx="30" cy="27" r="2.1" fill="#D6F4FF"/>
  {label(44, 32, left, 15, mono=True, bold=True)}
  {label(width - 25, 32, right, 13, VIOLET, align="end", mono=True)}
  <path d="M24 47h{width - 48}" stroke="#34455F"/>"""


def trace(source, target):
    x1, y = source
    x2, _ = target
    return f"M{x1 + 17:g} {y}Q{(x1 + x2) / 2:g} {y - 15} {x2 - 17:g} {y}"


def cluster(number, name, accent, items, cols, bounds, compact):
    x, y, width, height = bounds
    parts = [
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="10" fill="#131E32" stroke="#2D3D57"/>',
        f'<rect x="{x + 14}" y="{y + 13}" width="6" height="6" rx="1.2" fill="{accent}"/>',
        label(x + 28, y + 22, name, 16, bold=True),
        label(x + width - 14, y + 21, f"{number:02}", 12, accent, align="end", mono=True),
    ]
    positions = {}
    for row, first in enumerate(range(0, len(items), cols)):
        members = items[first:first + cols]
        centers = [x + width * (column + .5) / len(members) for column in range(len(members))]
        cy = y + 53 + row * 61
        for left, right in pairwise(centers):
            path = trace((left, cy), (right, cy))
            parts.append(f'<path d="{path}" fill="none" stroke="{accent}" stroke-opacity=".28"/>')
        for cx, (lines, icon, color) in zip(centers, members):
            positions[" ".join(lines)] = (cx, cy)
            parts.append(f'<rect x="{cx - 17:g}" y="{cy - 17}" width="34" height="34" rx="7" '
                         'fill="#1B2942" stroke="#405472"/>')
            if icon:
                parts.append(glyph(icon, cx - 10, cy - 10, 20, color))
            else:
                parts.append(label(cx, cy + 4, "OAI", 12, color, align="middle", mono=True, bold=True))
            parts.extend(
                label(cx, cy + 36 + line * 17, text, 18 if compact else 16, align="middle")
                for line, text in enumerate(lines)
            )
    return "\n  ".join(parts), positions


def node_pulse(position, phase, color):
    x, y = position
    return f"""  <rect class="motion" x="{x - 17:g}" y="{y - 17}" width="34" height="34" rx="7"
    fill="none" stroke="{color}" stroke-width="1.5" opacity="0">
    <animate attributeName="opacity" values="0;0;.76;0;0"
      keyTimes="0;{phase - .04:g};{phase:g};{phase + .11:g};1" dur="{DURATION}s" repeatCount="indefinite"/>
  </rect>"""


def signal(source, target, start, end):
    assert source[1] == target[1]
    path = trace(source, target)
    return f"""  <g class="motion" opacity="0">
    <animate attributeName="opacity" values="0;0;.9;.9;0;0"
      keyTimes="0;{start:g};{start + .025:g};{end - .025:g};{end:g};1" dur="{DURATION}s" repeatCount="indefinite"/>
    <animateMotion path="{path}" keyPoints="0;0;1;1" keyTimes="0;{start:g};{end:g};1"
      calcMode="linear" dur="{DURATION}s" repeatCount="indefinite" rotate="auto"/>
    <circle r="8" fill="url(#signal-halo)"/>
    <path d="M-12 0H0" stroke="{BLUE}" stroke-opacity=".6" stroke-linecap="round"/>
    <circle r="2" fill="#DAF5FF"/>
  </g>"""


def toolkit(size, animated):
    width = {"mobile": 480, "tablet": 640, "desktop": 960}[size]
    compact = size != "desktop"
    desktop_bounds = (
        (24, 62, 498, 113), (534, 62, 402, 113),
        (24, 186, 498, 113), (534, 186, 402, 113),
        (24, 310, 912, 113),
    )
    layout = [header(width, "TECH CONSTELLATION", "TOOLKIT / 03")]
    positions = {}
    next_y = 58
    for index, (name, accent, columns, items) in enumerate(CLUSTERS):
        if compact:
            if size == "tablet":
                columns = len(items)
            rows = (len(items) + columns - 1) // columns
            height = 113 + (rows - 1) * 61
            bounds = (16, next_y, width - 32, height)
            next_y += height + 9
        else:
            columns, bounds = len(items), desktop_bounds[index]
        markup, nodes = cluster(index + 1, name, accent, items, columns, bounds, compact)
        layout.append(markup)
        positions.update(nodes)
    height = next_y + 7 if compact else 445

    defs = ""
    if animated:
        defs = """
    <radialGradient id="signal-halo">
      <stop stop-color="#6ED4FF" stop-opacity=".68"/>
      <stop offset="1" stop-color="#58C7FF" stop-opacity="0"/>
    </radialGradient>
"""
        for source, target, start, end in (
            ("React", "Next.js", .13, .25),
            ("ESP32", "Arduino", .36, .47),
            ("Git", "GitHub", .58, .7),
        ):
            layout.append(signal(positions[source], positions[target], start, end))
            layout.append(node_pulse(positions[target], end, BLUE))
        layout.append(node_pulse(positions["Python"], .08, BLUE))
        layout.append(node_pulse(positions["LangGraph"], .81, VIOLET))
    return svg(width, height, "Tech Constellation",
               "Five groups of languages, frameworks, AI tools, embedded systems, and databases.",
               "\n  ".join(layout), defs, REDUCED if animated else "")


def beacon(animated):
    waves = ""
    if animated:
        for delay in (0, 1.4):
            waves += f"""    <circle class="motion" r="12" fill="none" stroke="{BLUE}" opacity="0">
      <animate attributeName="r" values="12;12;49;49" keyTimes="0;.12;.66;1" begin="{delay}s" dur="12s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0;.38;0;0" keyTimes="0;.12;.22;.66;1"
        begin="{delay}s" dur="12s" repeatCount="indefinite"/>
    </circle>
"""
    body = f"""  <path d="M23 60H567" stroke="#3A5171" stroke-opacity=".75" stroke-dasharray="2 7"/>
  <path d="M170 60h64m122 0h64" stroke="#506489" stroke-opacity=".6"/>
  <circle cx="170" cy="60" r="2" fill="{VIOLET}" opacity=".65"/>
  <circle cx="420" cy="60" r="2" fill="{BLUE}" opacity=".65"/>
  <g transform="translate(295 60)">
    <ellipse rx="68" ry="26" transform="rotate(-17)" fill="none" stroke="#688CC3" stroke-opacity=".27"/>
    <circle r="35" fill="url(#beacon-halo)"/>
    <circle r="18" fill="none" stroke="{BLUE}" stroke-opacity=".38"/>
    <circle r="31" fill="none" stroke="{VIOLET}" stroke-opacity=".22"/>
{waves}    <path d="M0-9 7 0 0 9-7 0Z" fill="#1B4766" stroke="#8CE1FF"/>
    <circle r="2.5" fill="#E6F7FF"/>
  </g>
  {label(24, 27, "SIGNAL BEACON", 14, mono=True, bold=True)}
  {label(566, 99, "CONTACT / 04", 13, VIOLET, align="end", mono=True)}"""
    defs = """
    <radialGradient id="beacon-halo">
      <stop stop-color="#58C7FF" stop-opacity=".28"/>
      <stop offset="1" stop-color="#58C7FF" stop-opacity="0"/>
    </radialGradient>
"""
    return svg(590, 120, "Signal Beacon", "Decorative signal radiating from a point in orbit.",
               body, defs, REDUCED if animated else "")


def badge(name, icon, color):
    mark = glyph(icon, 14, 16, 18, color) if icon else (
        f'<rect x="14" y="18" width="18" height="14" rx="2" fill="none" stroke="{color}" stroke-width="1.4"/>'
        f'<path d="m15 20 8 6 8-6" fill="none" stroke="{color}" stroke-width="1.4" stroke-linecap="round"/>'
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="124" height="50" viewBox="0 0 124 50">
  <title>{name}</title>
  <rect x=".6" y="3.6" width="122.8" height="42.8" rx="9" fill="#111B30" stroke="#4A5873" stroke-width="1.2"/>
  {mark}
  {label(42, 30, name, 15, bold=True)}
  <path d="M104 28l6-6m-5 0h5v5" fill="none" stroke="#8EADD0" stroke-width="1.2" stroke-linecap="round"/>
</svg>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare against committed SVGs")
    args = parser.parse_args()
    toolkit_dir, contact_dir = ROOT / "assets/toolkit", ROOT / "assets/contact"
    files = {
        toolkit_dir / f"{size}{'' if animated else '-static'}.svg": toolkit(size, animated)
        for size in ("desktop", "tablet", "mobile")
        for animated in (True, False)
    }
    files.update({contact_dir / f"beacon{'' if animated else '-static'}.svg": beacon(animated)
                  for animated in (True, False)})
    files.update({contact_dir / f"{name.lower()}.svg": badge(name, icon, color)
                  for name, icon, color in CONTACTS})
    write_visuals(files, args.check)


if __name__ == "__main__":
    main()
