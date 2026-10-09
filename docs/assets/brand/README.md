# Brand Assets

> **Status: Draft.** A trademark check for the project name is pending (see [TRADEMARKS.md](../../../TRADEMARKS.md)). The licenses of this repository do not grant rights to use any project name or wordmark as a trademark.

| File | Use |
|---|---|
| [selfkin-mark.svg](selfkin-mark.svg) | Organisation avatar (500 x 500): the wordmark "SK" in white on black. Square, full-bleed background, safe for circular cropping (all letters lie inside the inscribed circle), legible at 64 px and below |
| [selfkin-social-preview.svg](selfkin-social-preview.svg) | Repository social preview (1280 x 640): the headline "Open Standards for SI Edge Devices" in white on black, with the line "github.com/selfkin" in grey |
| [../architecture.svg](../architecture.svg) | Architecture overview used in the README and on the project page |

**Style.** Flat and typographic: wordmark only, no symbol, no colour.

**Colours.**

| Colour | Use | Contrast on `#000000` |
|---|---|---|
| `#000000` black | Background | |
| `#FFFFFF` white | Wordmark and headline | 21:1 |
| `#A3A3A3` grey | Secondary line only (and the subtitle in the site header) | 8.3:1 |

**Type.** Inter (SIL Open Font License 1.1), weights 800 (avatar), 700 (headline), and 450 (secondary line). All text is converted to outlines (SVG paths), so the SVGs load no fonts and render the same everywhere. Each SVG has a `<title>` and `<desc>` with the text it shows.

**Rendering.** The PNGs (500 x 500 and 64 x 64 avatar, 1280 x 640 social preview) are rendered from these SVGs, for example with `cairosvg` or `rsvg-convert`. They are not stored in the repository; the owner uploads them in the GitHub settings.
