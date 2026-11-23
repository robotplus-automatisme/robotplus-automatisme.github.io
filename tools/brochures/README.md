# Brochures PDF (A4 and tri-fold)

This folder builds the PDF brochures linked from the **Documents** box of every category page
(`assets/brochures/brochure-<name>-a4.pdf` and `brochure-<name>-pliable.pdf`). It is not published on the site
(`tools/` is excluded in `_config.yml`). The data sheets (`fiche-technique-*.pdf`) are your own documents and are not
made here.

## What is built

| Content file | Brochure | Linked from the page(s) |
|---|---|---|
| `content/robotique-industrielle.json` | Robotique industrielle | robotique-industrielle |
| `content/controle-vision.json` | Machines de contrôle + Contrôle laser (A4: 2 pages) | machines-controle, machines-controle-laser |
| `content/machines-speciales-bureau-etudes.json` | Machines spéciales | machines-speciales |
| `content/retrofit-machines.json` | Rétrofit machines | retrofit-machines |
| `content/dewatering-degraissage.json` | Lavage, dewatering & dégraissage | lavage-dewatering-degraissage |
| `content/postes-de-travail.json` | Postes de travail | postes-de-travail |
| `content/alimentation-convoyage-stockage.json` | Alimentations, convoyage, stockage (the 7 families; A4: 2 pages) | bols-vibrants, tremies, convoyeurs, elevateurs-a-lames, tremies-pour-axes, stockage-de-pieces, tables-rotatives-stockage |

Each content file gives two PDFs: the **tri-fold** (A4 landscape, 2 pages) and the **A4** (portrait). Both use the same
texts and photos, in French. The texts are condensed from the pages of the site; when a page changes, change the
content file as well (the brochures are not updated automatically).

## Rebuilding

1. Once: `python3 -m pip install Pillow segno playwright` then `python3 -m playwright install chromium`.
2. From the root of the repository:

   ```
   python3 -I tools/brochures/make_brochures.py --originals "/path/to/the/folder/that/contains/Photos site"
   python3 -I tools/brochures/make_brochures.py --originals "..." robotique-industrielle --formats a4
   ```

   The PDFs are written to `assets/brochures/` (`--out` chooses another folder). The first command rebuilds the 14
   PDFs in about 20 seconds. The script prints, for each panel or column, the free space left and `OVER` when a text
   does not fit.
3. The photos are **not** taken from `assets/photos/` (they carry the filigrane) but from your full-resolution
   originals, the `Photos site/...` files listed in `tools/photo-sources.csv`, at 220 dpi in the PDF.

## Printing the tri-fold

- A4 **landscape**, **double-sided**, "flip on the **short edge**". Page 1 is the outside (flap | back cover | front
  cover), page 2 the inside (3 panels). Fold the narrower right panel of page 2 (97 mm) in first, then the left one.
- Panels are 100 / 100 / 97 mm. There is no bleed: the dark covers and the yellow bands go to the edge of the sheet,
  which a desktop printer cannot do (white border). For a printed run, ask the printer for a version with bleed or
  print on a printer that handles borderless A4.

## Editing a content file

A content file is JSON (double quotes, no trailing comma). The main parts:

- `title`, `subtitle`, `highlight` (the entries of "Nos solutions" shown in white), `cover` (cover photo), `page` (the
  page of the site shown by the QR code).
- `blocks`: the pieces of content, each with a type `t`: `title`, `lead` (bold introduction), `p` (paragraph),
  `h3` (sub-heading), `rows` (white lines with a yellow edge, `"plain": true` for a simple list), `apps` (the dark
  Applications box), `quote`, `steps`, `cta` (yellow contact band), `photo`, `photos` (grid), `cards` (picture +
  title + text), `solutions` (list of the solutions of the company). `**bold**` in a text gives bold.
  A block can carry `"a4": {...}` or `"tri": {...}` with values used for that format only (for instance a shorter text).
- `tri`: the blocks of the three inside panels `A`, `B`, `C`. `a4`: the blocks of the `left` and `right` columns, the
  photo `strip`, or `pages` when the A4 has several pages.
- Photos are named like in `assets/photos/` (`robotique-industrielle/04-robotplus.fr-robotique-4.jpg`). `focus`
  ([x, y] between 0 and 1) says which part to keep when a photo is cropped, `zoom` crops closer, `crop`
  ([x0, y0, x1, y1]) keeps a part of the picture first (the Rétrofit pictures are two photos side by side: one half is
  used). `"fill": true` makes a photo take all the free space of its panel.

## Fonts

`fonts/` holds the two fonts of the brochures, embedded in the PDFs: Barlow Condensed (titles) and Inter (texts), both
free under the SIL Open Font License 1.1.
