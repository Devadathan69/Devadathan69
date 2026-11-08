"""Frame authentic project captures supplied from the sources in docs/VISUALS.md."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from visuals import ROOT


PLATES = (
    ("maatriwatch", "HARDWARE & HEALTH", ("Wearable", "+ companion"), "DEMO RECORDING", "#75D9CA",
     (("maatri-16.png", None, (.5, .48), .59), ("maatri-94.png", None, (.5, .15), .41))),
    ("jobsathi", "VOICE & ACCESSIBILITY", ("A résumé", "by voice"), "LOCAL BUILD", "#80BFFF",
     (("jobsathi-home.png", (0, 76, 537, 578), (.45, .28), .57),
      ("jobsathi-ui.png", (320, 45, 832, 705), (.5, .07), .43))),
    ("ghostwire", "CREATIVE COMPUTING", ("Cooperative", "boss raid"), "GAMEPLAY CAPTURE", "#B0E58B",
     (("coop-arena.png", (73, 551, 1086, 1119), (.51, .52), 1),)),
    ("loopledger", "FULL-STACK SYSTEMS", ("Subscription", "operations"), "DEMO FIXTURES", "#AEDDC3",
     (("loopledger-dashboard.png", (0, 0, 1440, 720), (.5, 0), 1),)),
    ("devdayhack", "VOICE & GAME MODDING", ("Malayalam", "NPC dialogue"), "DEMO RECORDING", "#F1C092",
     (("npc-91.png", None, (.52, .98), 1),)),
)


def capture(path, crop, size, center):
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        if crop:
            image = image.crop(crop)
        return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=center)


def label(draw, position, value, color, size, anchor=None):
    draw.text(position, value, fill=color, font=ImageFont.load_default(size=size), anchor=anchor)


def plate(index, category, heading, provenance, accent, views, input_dir, mobile):
    width, height = (640, 378) if mobile else (960, 330)
    canvas = Image.new("RGB", (width, height), "#0B1020")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((1, 1, width - 2, height - 2), radius=16, fill="#111B30", outline="#40516B", width=2)
    if mobile:
        draw.rounded_rectangle((18, 19, 28, 29), radius=2, fill=accent)
        label(draw, (39, 12), f"{index:02} / {category}", "#E8EEF9", 20)
        label(draw, (width - 18, 12), provenance, "#A5B6CD", 17, "ra")
        left, top = 15, 47
    else:
        draw.rounded_rectangle((20, 22, 29, 31), radius=2, fill=accent)
        label(draw, (39, 17), f"EXPERIMENT {index:02}", accent, 15)
        draw.line((20, 49, 185, 49), fill="#3A4B67")
        for row, line in enumerate(heading):
            label(draw, (20, 101 + row * 35), line, "#E8EEF9", 27)
        label(draw, (20, 216), category, "#AFBED4", 14)
        draw.line((20, 261, 185, 261), fill="#3A4B67")
        label(draw, (20, 280), provenance, accent, 14)
        left, top = 204, 14

    available = width - left - 14
    media_height = height - top - 14
    gap = 8 if len(views) > 1 else 0
    media_width = available - gap
    right = left + available
    for i, (filename, crop, center, fraction) in enumerate(views):
        view_width = right - left if i == len(views) - 1 else round(media_width * fraction)
        media = capture(input_dir / filename, crop, (view_width, media_height), center)
        mask = Image.new("L", media.size)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, view_width - 1, media_height - 1), radius=9, fill=255)
        canvas.paste(media, (left, top), mask)
        draw.rounded_rectangle((left, top, left + view_width - 1, height - 15), radius=9, outline="#53637C")
        left += view_width + gap
    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path, help="directory holding the original captures")
    args = parser.parse_args()
    output = ROOT / "assets/projects"
    output.mkdir(exist_ok=True)
    for i, (slug, category, heading, provenance, accent, views) in enumerate(PLATES, start=1):
        for mobile in (False, True):
            image = plate(i, category, heading, provenance, accent, views, args.input_dir, mobile)
            suffix = "-mobile" if mobile else ""
            image.save(output / f"{slug}{suffix}.webp", quality=86, method=6)


if __name__ == "__main__":
    main()
