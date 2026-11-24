# Brochures PDF (A4 and tri-fold), in 7 languages

This folder builds the PDF brochures linked from the **Documents** box of every category page
(`assets/brochures/brochure-<name>-<format>-<language>.pdf`: format `a4` or `pliable`, language `fr en it de es pt ro`).
It is not published on the site (`tools/` is excluded in `_config.yml`). The Documents box has only these two brochures
(the old data sheets, `fiche-technique-*.pdf`, are removed; they stay in the git history).

## What is built

| Content file (`content/`) | Brochure, titled like the card of the home page | Linked from the page(s) |
|---|---|---|
| `robotique-industrielle.json` | Robotique | robotique-industrielle |
| `machines-controle.json` | Machines de contrôle | machines-controle |
| `machines-controle-laser.json` | Contrôle laser | machines-controle-laser |
| `machines-speciales.json` | Machines spéciales | machines-speciales |
| `alimentation-convoyage-stockage.json` | Alimentations, convoyage, stockage (the 7 families; A4: 2 pages) | bols-vibrants, tremies, convoyeurs, elevateurs-a-lames, tremies-pour-axes, stockage-de-pieces, tables-rotatives-stockage |
| `retrofit-machines.json` | Rétrofit machines | retrofit-machines |
| `lavage-dewatering-degraissage.json` | Lavage, dewatering, dégraissage | lavage-dewatering-degraissage |
| `postes-de-travail.json` | Postes de travail | postes-de-travail |

8 brochures x 2 formats x 7 languages = 112 PDFs. The file name of a content file is the name of the page of the site
(`solutions/<name>.html`). The **title** of a brochure is the title of the card of the home page ("Nos solutions") in
the language of the brochure; it is read from the site, never typed here. The page titles of the site are the same.

The **tri-fold** is A4 landscape, 2 pages; the **A4** is portrait. Both use the same texts and photos. The texts are
condensed from the pages of the site; when a page changes, change the content file as well (the brochures are not
updated automatically).

## Languages

- The French texts are in `content/*.json`. The six other languages are in `translations/<lang>.json`: a table
  "French sentence -> translation" (the French sentence is the key, `|` separates the lines of a title, `**bold**` is
  kept). If a French sentence is also on the site with the same wording, the translation of the site
  (`assets/js/i18n.js`) is used and does not need to be in the table.
- The fixed texts of the brochures (statement of the flap, back cover, "Scan this code…", country, legal line, name of
  the solutions, title of the cover) come from the site too (`common.eyebrow`, `footer.company`, `card.<name>.title`, …)
  or from the `UI_FR` table of `localize.py`.
- `python3 -I tools/brochures/localize.py` checks the translations and prints, for each language, the texts that are
  missing or unused. A brochure whose texts are not all translated is **not built** (the script says which ones),
  so a French sentence never stays in the middle of a translated brochure.
- After changing a French text in a content file, change its key in the six `translations/*.json` files too.
- The QR code of each brochure points to the page itself on GitHub Pages,
  `https://robotplus-automatisme.github.io/<page>#<language>` (`SITE_URL` at the top of `make_brochures.py`), because
  `www.robotplus.fr` only redirects to the home page of the site. The web address printed on the brochures is
  `www.robotplus.fr` (`COMPANY['web']`), a link to `https://www.robotplus.fr` in the PDF (`COMPANY['web_href']`). If the
  site gets a domain of its own that keeps the path, change `SITE_URL` and rebuild.
- Long words (German, Romanian) are hyphenated with `pyphen` if it is installed (`python3 -m pip install pyphen`);
  without it the PDFs are still built, with fewer hyphenations. A text that does not fit its panel is shrunk
  automatically, down to 80 %; the script prints `SHRUNK` and the panel when it happens, and `OVER` when it still does
  not fit.

## Rebuilding

1. Once: `python3 -m pip install Pillow segno playwright pyphen` then `python3 -m playwright install chromium`.
2. From the root of the repository:

   ```
   python3 -I tools/brochures/make_brochures.py --originals "/path/to/the/folder/that/contains/Photos site"
   python3 -I tools/brochures/make_brochures.py --originals "..." robotique-industrielle --formats a4 --lang fr,de
   ```

   The PDFs are written to `assets/brochures/` (`--out` chooses another folder). Without options everything is built:
   112 PDFs in about a minute (the first run is slower: it crops the photos). The script prints, for each panel or
   column, the free space left and `OVER` when a text does not fit. **A rebuild writes about 70 MB of new PDFs, which
   Git keeps for good: rebuild only when a brochure has changed.**
3. The photos are **not** taken from `assets/photos/` (they carry the filigrane) but from your full-resolution
   originals, the `Photos site/...` files listed in `tools/photo-sources.csv`, at 220 dpi in the PDF.
4. `python3 tools/update_site.py` checks that every brochure linked from a page exists in the 7 languages. The links
   are written in French (`...-fr.pdf`) in the pages with `data-brochure="<name>-<format>"`; `assets/js/site.js`
   changes them to the language chosen by the visitor.

## Checks made by the script (and the rule for the yellow slashes)

After drawing each PDF, the script measures it in the browser. Every `GEOMETRY <file>: ...` line it prints is a problem
and is counted in `problems:` at the end (the exit status is 1); `OVER` is a text that does not fit its panel.

- **A yellow slash is never placed by hand.** It is a parallelogram slanted by 18 degrees, so it overhangs its box by
  0.1625 x its height on each side. `slash_fit()` places it so that the text that follows starts at least its width + that
  overhang + `SLASH_GAP` (2.2 mm) later, and makes it shorter if it would leave its block. The text of a cover starts
  `COVER_TEXT_LEFT` (12 mm) from the edge, the one of an A4 header `A4_TEXT_LEFT` (9.5 mm). In a content file `slash_h` is only
  the *maximum* height of a slash (cover or A4 header), not its position.
- Checked on every PDF (limits in `GEOM_LIMITS`): distance slash -> text (at least 1.5 mm), margin of a text against its
  panel (7 mm) and the page (10 mm), tip of a slash against the edge (3 mm), text against a photo (2.5 mm) and against the
  yellow stripe of the A4 header (3 mm), two texts that overlap, and the resolution of the photos (it prints a note under
  150 dpi). A paragraph ending in a very short line is only counted.
- The last line of the output summarises: `geometry: 9580 lines of text and 287 slashes measured; smallest gap between a
  slash and a text 2.2 mm ... problems: 0`. `SHOW_WIDOWS=1 python3 -I tools/brochures/make_brochures.py ...` lists the
  paragraphs that end in a very short line, `SHOW_FILLS=1` the photos that fill their panel with the least room.
- When you change the CSS of a panel, rebuild everything and read this summary: a smaller gap than before means that
  something moved. The titles of the covers and panels that had to shrink are printed as `TITLE [... x0.76]`.

## Printing the tri-fold

- A4 **landscape**, **double-sided**, "flip on the **short edge**". Page 1 is the outside (flap | back cover | front
  cover), page 2 the inside (3 panels). Fold the narrower right panel of page 2 (97 mm) in first, then the left one.
- Panels are 100 / 100 / 97 mm. There is no bleed: the dark covers and the yellow bands go to the edge of the sheet,
  which a desktop printer cannot do (white border). For a printed run, ask the printer for a version with bleed or
  print on a printer that handles borderless A4.

## Editing a content file

A content file is JSON (double quotes, no trailing comma). The main parts:

- `title`, `title_plain` (the name of the solution in French: it is replaced by the title of the card of the home page
  in each language), `subtitle`, `highlight` (the entries of "Nos solutions" shown in white), `cover` (cover photo), `page`
  (the page of the site shown by the QR code).
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
