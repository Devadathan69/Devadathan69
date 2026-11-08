# Constellation Lab visuals

The two SVG scenes and five project plates share the midnight palette, square markers, and thin blue-gray borders. The bio, project descriptions, milestone and toolkit tables, and links use regular Markdown.

## Name grid

`scripts/generate_name_grid.py` maps each letter to a 5×7 pixel glyph. Desktop spells **DEVADATHAN M R**, while the compact version spells **DATHAN**. The green squares are decorative lettering.

Ten groups light up in overlapping fronts from three points on the grid. The full name resolves in about two seconds of the 16-second loop. The name holds while a comet follows a cubic curve. Sampled points along that curve time the brief highlights on nearby cells. The stills show the fully lit lettering.

## Comet Atlas

`data/public-calendar.json` stores the GitHub account and one record per day from the GraphQL contribution calendar. Each record has a date, contribution count, and GitHub intensity level from 0 to 4. The initial period total matched the signed-out web calendar. A few contributions were assigned to adjacent days in the two views, so the atlas uses GraphQL dates and levels consistently. [Contribution rules](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)

The chart preserves Sunday-first calendar weeks. The compact version splits the year across two seven-row bands. Brighter tiles and larger centers indicate higher contribution levels. Each cell has a date and count in its SVG title. The README links to GitHub’s calendar for the full day-by-day view.

A 22-second loop carries a layered comet from the horizon up through the grid. A slow haze drift moves behind the hills and observatory. The temporary highlights follow the comet’s proximity to active cells. The underlying activity colors and values remain fixed for the duration of a render.

## Rebuild and check

Use Python 3.10 or later from the repository root. Regeneration from the committed snapshot is offline and uses the standard library.

```sh
python -B scripts/generate_name_grid.py
python -B scripts/generate_comet_atlas.py
python -B scripts/generate_name_grid.py --check
python -B scripts/generate_comet_atlas.py --check
```

Both generators create desktop and mobile SVGs plus a still for each size. The README selects the stills with `prefers-reduced-motion`. The animated images also respond to that preference when loaded directly. Each panel carries its own dark background and border for use in either GitHub theme.

The **Comet Atlas** workflow checks the generated files and tests a public calendar refresh in pull requests with read-only permissions. On the default branch it refreshes every six hours and supports manual runs from the **Actions** tab. GitHub schedules can be delayed. The workflow uses GitHub CLI with the repository-scoped `GITHUB_TOKEN`. Only the default-branch refresh job can write changes, and it commits the snapshot and atlas files only when they differ. [Workflow scheduling](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

The artwork is self-contained SVG. GitHub’s `<picture>` support provides responsive image selection, and CSS and SVG motion run within the images. [GitHub image markup](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/quickstart-for-writing-on-github#adding-an-image-to-suit-your-visitors)

## Project plates

The WebP plates are cropped captures with a shared frame. GitHub selects a separate compact plate on small screens. Descriptions and links sit outside the image so they stay readable at every width.

To regenerate the plates, use Python with Pillow 10.1 or later. Put the following captures in a local directory and run `python -B scripts/generate_project_plates.py path/to/captures`. Crop coordinates in the script correspond to the source sizes below. Adjust those coordinates when replacing a capture.

| Plate | Capture source |
| :--- | :--- |
| MaatriWatch | `maatri-16.png` and `maatri-94.png` are 480 × 854 stills at 00:16 and 01:34 from the [team’s recorded demo](https://github.com/Devadathan69/MaatriWatch/blob/35bc91b30b8148cd31dcbc995597daa894072fe7/docs/demo/maatriwatch-demo.mp4). The app shows sample reports. |
| JobSathi | `jobsathi-home.png` and `jobsathi-ui.png` are 1152 × 750 captures of the landing screen and first-run language picker from [the local Vite frontend](https://github.com/Devadathan69/jobsathi/tree/0e4c8ebbd8f099996b92c366f1b203ee9fbf0c8e/frontend). |
| GhostWire | `coop-arena.png` is the [published arena capture](https://github.com/Devadathan69/GhostWire/blob/5333d6bc60b25f0ac6e9f96c479620ca3a33c1dc/docs/screenshots/coop-arena.png), cropped to the game viewport. |
| LoopLedger | `loopledger-dashboard.png` is a 1440 × 860 capture of the finance dashboard running with [local demo fixtures](https://github.com/Devadathan69/make-a-ton/blob/dc5b2c0b2172cd6008f88a83466d212d4b2da164/docs/LOCAL_DEMO.md). The hosted dashboard requires sign-in. |
| Malayalam NPC Companion | `npc-91.png` is a 1280 × 800 still at 01:31 in the [public demo recording](https://github.com/Devadathan69/DevDayHack/blob/c2d57a6b921393111c582eeda85ea44cdda7d653/demo/demo.mp4). The clip shows the real mod running locally. |
