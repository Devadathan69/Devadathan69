# Constellation Lab visuals

The SVG scenes share a midnight palette, square cells, and blue-violet light. The bio and toolkit text list use Markdown, and each contact badge is its own link.

## Name grid

`scripts/generate_name_grid.py` maps each letter to a 5×7 pixel glyph. Desktop spells **DEVADATHAN M R**, while the compact version spells **DATHAN**. The green squares are decorative lettering.

Eight groups of cells light up in staggered order during the 16-second loop. The name holds while a comet follows a cubic curve. Sampled points along that curve time the brief highlights on nearby cells. The stills show the fully lit lettering.

## Comet Atlas

`data/public-calendar.json` stores the GitHub account and one record per day from the GraphQL contribution calendar. Each record has a date, contribution count, and GitHub intensity level from 0 to 4. The initial period total matched the signed-out web calendar. A few contributions were assigned to adjacent days in the two views, so the atlas uses GraphQL dates and levels consistently. [Contribution rules](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)

The chart preserves Sunday-first calendar weeks. The compact version splits the year across two seven-row bands. Brighter tiles and larger centers indicate higher contribution levels. Each cell has a date and count in its SVG title. The README links to GitHub’s calendar for the full day-by-day view.

A 20-second loop carries a comet along a curved track over the grid. The temporary highlights follow the comet’s proximity to active cells. The underlying activity colors and values remain fixed for the duration of a render.

## Tech Constellation and Signal Beacon

`scripts/generate_constellation_panels.py` lays out five toolkit clusters for desktop, tablet, and mobile. All labels and marks are visible from the start. A 14-second loop sends signals between React and Next.js, ESP32 and Arduino, and Git and GitHub. The signals show common pairings. The toolkit’s expandable text list is available without the image.

The 12-second Signal Beacon loop uses two slowly fading rings. The GitHub, LinkedIn, Email, and X badges are separate static SVGs with accessible names on their links.

`scripts/brand-paths.json` stores normalized SVG paths from [Simple Icons 16.37.0](https://github.com/simple-icons/simple-icons/tree/16.37.0/icons) and the Java and LinkedIn paths from [Devicon v2.18.0](https://github.com/devicons/devicon/tree/v2.18.0/icons). Their [CC0](licenses/simple-icons-CC0.md) and [MIT](licenses/devicon-MIT.txt) licenses are included. ESP32 uses the Espressif mark, and TensorFlow Lite uses the TensorFlow mark. The OpenAI Agents SDK node uses a text monogram. The marks identify technologies and destinations.

The [Git logo](https://git-scm.com/community/logos) is by Jason Long and licensed under [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/). The [JavaScript logo](https://github.com/voodootikigod/logo.js) is by Christopher Williams and licensed under [MIT](licenses/logo-js-MIT.txt). The artwork uses monochrome paths and adjusts their colors to the panel palette.

## Rebuild and check

Use Python 3.10 or later from the repository root. Regeneration from the committed snapshot is offline and uses the standard library.

```sh
python -B scripts/generate_name_grid.py
python -B scripts/generate_comet_atlas.py
python -B scripts/generate_constellation_panels.py
python -B scripts/generate_name_grid.py --check
python -B scripts/generate_comet_atlas.py --check
python -B scripts/generate_constellation_panels.py --check
```

The name grid, atlas, and toolkit have desktop and mobile SVGs. The compact contact scene scales to the available width. The README selects stills with `prefers-reduced-motion`, which the animated images also honor when loaded directly. Each panel carries its own dark background and border for use in either GitHub theme.

The **Comet Atlas** workflow checks the generated files and tests a public calendar refresh in pull requests with read-only permissions. On the default branch it refreshes every six hours and supports manual runs from the **Actions** tab. GitHub schedules can be delayed. The workflow uses GitHub CLI with the repository-scoped `GITHUB_TOKEN`. Only the default-branch refresh job can write changes, and it commits the snapshot and atlas files only when they differ. [Workflow scheduling](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

The artwork is self-contained SVG. GitHub’s `<picture>` support provides responsive image selection, and CSS and SVG motion run within the images. [GitHub image markup](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/quickstart-for-writing-on-github#adding-an-image-to-suit-your-visitors)
