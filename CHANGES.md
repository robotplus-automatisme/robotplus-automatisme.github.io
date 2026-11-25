# Update — 25 November 2026 (gallery order, one sentence, text of the Alimentations page and brochures, contact strip, Documents box, cover photo)

Seven changes asked on 25 November. Of the 112 brochures only the 14 of *Alimentations, convoyage, stockage* were rebuilt
(for their text, then for the crop of their cover photo, see the two sections about them): **the 98 other PDFs are
unchanged**. The last three sections are the contact strip and the Documents box on the page with the tiles, then the
cover photo of the brochures.

## Machines spéciales: photo 7 is now the first one

- In the gallery of *Machines spéciales*, the photo that was 7th (original `IMG_20230427_092647.jpg`) is now the first;
  the six photos before it each moved down one place, photos 8, 9 and 10 stay where they were. The gallery shows the
  photos in file-name order, so only the two-digit prefix of 7 files changed: `07-robotplus.fr-machines-speciales-7.jpg`
  became `01-…-7.jpg`, and `01-…-1.jpg` to `06-…-6.jpg` became `02-…-1.jpg` to `07-…-6.jpg`. The rest of each name is kept,
  so a photo keeps its name whatever its place (list in `tools/picture-renames-2026-11-25.csv`). The counter says *Photo 1
  sur 10* and the alt texts (*Machines spéciales — photo N*) follow the new order.
- The files that quote these names were updated: `tools/photo-sources.csv`, `tools/watermark-2026-11-21.csv` and
  `tools/brochures/content/machines-speciales.json`. Checked: every picture of the brochures of *Machines spéciales* still
  points to the same original photo, so a future rebuild gives the same brochures.

## Machines de contrôle: sentence corrected

- Second bullet of the list of applications (key `page.machines-controle.item2`):
  before, *Contrôle en sortie de rectifieuse, avec mesure des pièces et asservissement de la rectifieuse pour un pilotage en
  temps réel des dimensions*; now, *Contrôle en sortie de rectifieuse, avec asservissement de la machine pour un pilotage des
  cotes en temps réel* (the first part stays in bold). The six translations are rewritten (English *with feedback control of
  the machine for real-time dimension control*, Italian *con regolazione della macchina per una gestione delle quote in
  tempo reale*, German *mit Rückkopplung an die Maschine für eine Maßsteuerung in Echtzeit*, Spanish, Portuguese and Romanian
  likewise). This is the wording the brochures of *Machines de contrôle* already had, so the page and the brochures now agree.

## Alimentations, convoyage, stockage: new text above the 7 tiles

- The paragraph above the tiles (*ROBOTPLUS propose différentes solutions… Sélectionnez une sous-catégorie ci-dessous.*) is
  replaced by the text of 25 November: two paragraphs, *Découvrez nos sept domaines de compétences :*, a list of the seven
  families and a closing sentence. Keys `page.alimentation-convoyage-stockage.intro`, `.intro2`, `.intro3`, `.item1` to
  `.item7`, `.outro`; the 6 translations are mine, not proofread by a professional translator. The label of each item is the
  title of its tile, in each language.
- **Presentation**: the family names are in bold, the list uses the white boxes with a yellow edge of the other pages, all in a
  block `<div class="hub-intro">` (CSS `.hub-intro`; the old `.intro` rule was only used here and is gone). Seen on a phone, a
  tablet and a desktop; `tools/check_layout.py`: 1,568 page views, 0 problems; every translated text of the page checked in a
  browser in the 7 languages.
- **Two small liberties**: the typographic apostrophe ’ of the rest of the site replaces the straight one, and the typo *pour la
  distributions pièces cylindriques* (Élévateurs à lames) is now *pour la distribution de pièces cylindriques*. The line
  under the page title (*Choisissez une famille de produits pour découvrir nos solutions.*) is unchanged.
- The brochures of this family follow the page for the three paragraphs, without the list of the seven families: see the next
  section.

## Alimentations, convoyage, stockage: the 14 brochures follow the page

- **Text**: the three old paragraphs (*ROBOTPLUS propose différentes solutions…*, *En tant que **fabricant**…*, *Du modèle
  standard à la solution sur mesure…*) are replaced by the three paragraphs of 25 November, **without the list of the seven
  domains** (as asked): *De l’alimentation des pièces au stockage…* and *Grâce à nos différents savoir-faire…* at the start,
  *Chaque solution est pensée pour répondre à vos besoins spécifiques…* as the closing sentence (bold, yellow edge) just
  above the yellow *Un besoin particulier ?* box. Nothing else changed in the text of these brochures.
- **A4**: same places as before (the two paragraphs under the first line of page 1, the closing sentence on page 2).
  **Tri-fold**: the two paragraphs are in the first panel; the closing sentence takes the place of the photo of a conveyor belt
  that was between the *Applications* box and the yellow box (`ph_c` removed from `tri.C` in
  `tools/brochures/content/alimentation-convoyage-stockage.json`), and the card *Tables rotatives de stockage*, which absorbs
  the free height (`"fill": true`), is a little taller. No text is shrunk.
- **Translations**: the six languages reuse the translations of the page (keys `page.alimentation-convoyage-stockage.intro`,
  `.intro2`, `.outro`), so the page and the brochures say exactly the same thing; they are mine, not proofread by a
  professional translator. The three entries of the old sentences were removed from `tools/brochures/translations/*.json`
  (`localize.py`: 0 missing, 0 unused). In Spanish, the last three words of the second paragraph (*precisión y eficacia*) are
  joined by non-breaking spaces, in the page string too (invisible there), so that the paragraph does not end on a line of two
  words.
- **Checked**: the builder reports 0 problem for the 14 files; the PDF checks (texts, links, QR code, number of pages) report
  0 problem; every text of the brochures is found on the site; the words that differ from the previous PDFs are those of the
  paragraphs above and nothing else; the 14 files were looked at page by page in the 7 languages.
- **Git history**: these 14 PDFs weigh about 9 MB; the 98 others are byte for byte the ones of 24 November.

## Alimentations, convoyage, stockage: contact strip on the page with the tiles

- The black band *Un projet lié à cette solution ?* with the yellow *Nous contacter →* button (a `mailto:robotplus@robotplus.fr`
  link) is now on the page with the 7 tiles (`solutions/alimentation-convoyage-stockage.html`), the only page of `solutions/`
  that did not have it. It is the last element of the page, **under the tiles**, with the same markup, the same two
  translation keys (`common.project_question`, `common.contact_button`) and the same look as on the 14 other pages: nothing
  new had to be translated or styled, so the band is in the 7 languages.
- **Checked**: in a browser, the page in the 7 languages at 7 window widths (320 to 1440 px, 49 views): one band, after the
  tiles and aligned with them, right link, right text in each language, button and question inside the band and not
  overlapping, nothing cut off, no sideways scroll; `tools/check_layout.py`: 1,568 page views, 0 problems. This change does
  not touch the PDFs.
- README: the *Contact strip* paragraph now says that the band is on the 15 pages of `solutions/`.

## Alimentations, convoyage, stockage: Documents box on the page with the tiles

- The **Documents** box with the two brochures (*Brochure A4 "Alimentations, convoyage, stockage" (PDF)* and *Brochure
  pliable "Alimentations, convoyage, stockage" (PDF)*) is now also on the page with the 7 tiles
  (`solutions/alimentation-convoyage-stockage.html`). It is the box of the 7 sub-pages of the family, byte for byte: same
  markup, same keys (`common.documents`, `brochure.alimentation-convoyage-stockage.a4` and `.fold`), so nothing new had to be
  translated and the links follow the language of the visitor (`site.js`, 14 PDFs). The checks of `update_site.py` on the
  brochure links apply to this page too.
- **Place**: the intro text and the box are in a new block `<div class="hub-top">` (`assets/css/site.css`, next to
  `.hub-intro`). On a computer the box is in the `<aside>` to the right of the text, at the height of its first line and
  ending where the tiles end; it is 30 % of the width of the page, between 270 and 330 px. Up to 900 px wide (same
  breakpoint as the other pages) the block is one column: text, box, tiles. The text column is a little narrower than before
  (805 px instead of 850 px at most), so a few lines of the list of the seven families may now go on two lines in some
  languages.
- **Checked**: in a browser, the page in the 7 languages at 10 window widths (320 to 1440 px, 70 views): one box, in the
  right place and aligned with the text and the tiles, right title, right label and right link in each language, the 14 PDFs
  are served, nothing cut off; `tools/check_layout.py`: 1,568 page views, 0 problems.
- Noticed, **not changed**: in German, between 901 and 905 px of window width, the footer tagline (*Sondermaschinen.*) is
  5 px wider than the window, so the page scrolls sideways by 5 px. It is on every page (the home page too) and was already
  so before this change.
- README: the *Page with the tiles* paragraph describes `hub-top` and the Documents box.

## Alimentations, convoyage, stockage: the cover photo of the brochures is moved

- The photo of the cover (page 1 of the A4, outside of the tri-fold) was cut on the left: the electrical cabinet, the rod and
  the left of the bowl were hidden. It was moved in two steps, both in
  `tools/brochures/content/alimentation-convoyage-stockage.json`:
  1. `cover.focus` went from `[0.5, 0.5]` to `[0.41, 0.5]` (picture moved to the right in its frame, the right of the photo
     being cut instead), for both formats;
  2. then each format got its own position. **Tri-fold**: `cover.focus` is now `[0.43, 0.5]`, i.e. the picture is moved back
     slightly to the left: the visible part of the photo runs from 5.6 % to 80.4 % of its width (12.6 % to 87.4 % at the
     start, 3.6 % to 78.4 % after step 1), so a little more of the hopper is seen and the electrical cabinet stays whole,
     about 2 mm from the edge. **A4**: the photo is slid slightly further to the right, see the next point.
- **A4**: the photo is almost as wide as its frame (only 10 % of its width is cropped), so after step 1 it was already
  against the left edge of the frame, the furthest to the right it could go, and the cable loop beside the rod and the left
  of the bowl were still hidden by the yellow diagonal or touching it. To go further, page 1 of the A4 has its own `hero`
  entry (`a4.pages[0].hero`, with `"crop": [-0.035, 0, 1, 1]` and `"focus": [0, 0.5]`): the photo is extended on its left by
  3.5 % of its width (about 3.7 mm) and the picture is therefore 3.7 mm further to the right. The strip that is added
  mirrors the edge of the photo (plain wall, baseboard, floor); it lies under the yellow diagonal and shows only as a
  sliver, at most 1.3 mm wide, in the bottom-left corner, where it continues the floor tiles. Measured on the PDF: the cable
  loop is about 1 mm from the diagonal, the cabinet's top-left corner and the bowl about 2 to 2.5 mm; the hopper's table is
  now 1.3 mm from the right edge of the page (it was 4.9 mm), its tip still whole.
- `tools/brochures/make_brochures.py`: a `crop` that goes beyond the photo (negative `x0`, or `x1`, `y0`, `y1` outside 0–1)
  now extends the photo by mirroring its edge (new `Photos.mirror_pad`); until now it would have added black. No other
  brochure uses this.
- The 14 PDFs were rebuilt (the website and its photo are unchanged). Compared with the previous PDFs, the texts, the links,
  the page sizes and the fonts are the same and only the area of the cover photo differs (page 1 of the A4, page 1 of the
  tri-fold), checked pixel by pixel in the 7 languages; the builder reports 0 problem. About 9 MB more in the Git history.
- To change the position again, edit `cover.focus` (tri-fold) or `a4.pages[0].hero` (A4) in that file (`x` between 0 = left
  edge of the photo and 1 = right edge) and run `make_brochures.py` for `alimentation-convoyage-stockage` (see
  `tools/brochures/README.md`).

# Update — 24 November 2026 (brochures in 7 languages, design review)

The brochures now exist in the 7 languages of the site, carry the title of their card on the home page, show
`www.robotplus.fr` and the new e-mail address. The Documents box of every sub-page has only the two brochures.
The design of the brochures and of the site was then reviewed for overlaps (yellow slash against text, cut-off text):
see **Design review** below. Last, the *Nous contacter* button of the contact strip opens an e-mail and the strip is on all
the sub-pages: see **Contact strip** below.

## Brochures

- **112 PDFs** in `assets/brochures/`: 8 brochures x 2 formats (A4, tri-fold) x 7 languages, named
  `brochure-<name>-<format>-<language>.pdf`, for instance `brochure-robotique-industrielle-pliable-de.pdf`
  (`<name>` is the name of the page, `<format>` is `a4` or `pliable`, `<language>` is `fr en it de es pt ro`).
  The 14 French-only PDFs of 23 November are replaced.
- **Language**: the two links of the Documents box open the brochure in the language chosen in the menu of the site,
  and follow the visitor who changes language (`assets/js/site.js`). The links are written in French in the pages
  (`...-fr.pdf`, `data-brochure="..."`); `tools/update_site.py` checks that the 7 files exist for every link.
- **Titles**: the title of each brochure, of each page and of the "Nos solutions" list is the title of the card on the
  home page, in every language: *Robotique*, *Machines de contrôle*, *Contrôle laser*, *Machines spéciales*,
  *Alimentations, convoyage, stockage*, *Rétrofit machines*, *Lavage, dewatering, dégraissage*, *Postes de travail*.
  On the site this changes the browser title, the H1 and the H2 of *Robotique industrielle* (now *Robotique*, in the 7
  languages) and of *Lavage, dewatering, dégraissage* (the French "&" became a comma, as on the card), and the
  translated titles that differed from their card: Italian *Retrofit macchine*, German *Maschinenretrofit*, Spanish
  *Retrofit de máquinas*, Romanian *Retrofit utilaje* (Rétrofit); German *Waschen, Dewatering und Entfetten*, Spanish
  *Lavado, dewatering y desengrase*, Portuguese *Lavagem, dewatering e desengorduramento*, Romanian *Spălare, dewatering
  și degresare* (Lavage); English *Feeding, conveying & storage*, Italian *Alimentazione, convogliamento e stoccaggio*,
  Romanian *Alimentare, transport și stocare* (Alimentations). Checked in a browser on the 8 category pages in the 7
  languages: the H1, the H2 and the browser title of every page equal its card.
- **Control brochures split**: *Machines de contrôle* and *Contrôle laser* each have their own pair (the shared
  `controle-vision` brochure is gone). That is why there are 8 brochures, not 7.
- **Web address and QR codes**: `www.robotplus.fr` is printed on every brochure (no more `github.io` in the text) and is a
  link to `https://www.robotplus.fr` in the PDF. Since `www.robotplus.fr` will only redirect to the home page of the site,
  the **QR code points to the page itself on GitHub Pages**: `https://robotplus-automatisme.github.io/<page>#<language>`,
  for instance `https://robotplus-automatisme.github.io/solutions/robotique-industrielle.html#de`. All 112 QR codes were
  decoded, and each address was opened in a browser (right page, right language). If the site ever gets a domain of its
  own that keeps the path, change `SITE_URL` in `tools/brochures/make_brochures.py` and rebuild.
- **E-mail**: `robotplus@robotplus.fr` replaces `robotplus@orange.fr` on the brochures and on the site (footer of
  every page, home page, legal notice, privacy policy).
- **Texts and translations**: the French texts are those of the 23 November brochures, now in
  `tools/brochures/content/<page name>.json`. The six translations (`tools/brochures/translations/*.json`, 116
  sentences each) are mine, not proofread by a professional translator: they reuse the words of the site when the
  sentence is the same, European Portuguese, formal "you" in every language (Romanian *dvs.*). A brochure whose texts
  are not all translated is not built, so French cannot remain in the middle of a translation. A reading by someone
  who knows the trade is worthwhile, as for the pages.
- **Layout**: translated texts are not as long as the French everywhere; each panel shrinks its text by up to 20 %
  when needed (it happened on 6 of the 112 files, by 2 to 6 %), long words are hyphenated, and the titles of the covers
  and panels shrink to fit (*Sondermaschinen*, *Maschinenretrofit* and the Portuguese *Lavagem, dewatering e
  desengorduramento* are at 80-82 %). The A4 of *Machines de contrôle* has no photo in its right column, because the
  list of 8 solutions takes the room; the last panel of the *Contrôle laser* tri-fold has a photo instead of an empty
  band.
- **Checks**: every PDF was checked by script (page count and size, fonts embedded and only Barlow Condensed and
  Inter, no `github.io` or `orange` in the text, new e-mail present, `www.robotplus.fr` as the only link, QR code
  decoded and equal to the expected address, no French word left in the translated ones, no photo with a filigrane)
  and looked at page by page in the 7 languages.
- **Size**: the PDFs weigh 71 MB (28 MB before, with the data sheets). Photos are 220 dpi. Git keeps every version of a
  binary file, so **each rebuild of the 112 PDFs adds about 70 MB to the repository history**: rebuild only when a
  brochure changes.

## Design review (brochures and site)

**Bug reported**: in the English tri-fold *Robotics*, the title touched the yellow diagonal line on its left.

- **Cause**: the slash was a fixed 7 mm from the edge of the cover, but a slash 36-46 mm high slants by 0.1625 x its height
  on each side (6-7 mm), so its upper tip reached the first letters of the title. It was the same on the A4 headers, on
  the flap, the back cover and the titles of the inside panels, in every language and on all 8 brochures.
- **Fix**: the position of every slash is now *computed from the text*: the text starts after the slash by its width + its
  slant + 2.2 mm (`slash_fit()` in `tools/brochures/make_brochures.py`), and a slash that would leave its block is made
  shorter. Titles on covers now start 12 mm from the edge (A4 headers: 9.5 mm).
- **Automatic checks added to the builder** (`GEOMETRY ...` lines, counted as problems): distance between each slash and
  the text lines next to it (at least 1.5 mm), margin of every text, slash tips against the edge of the page, text
  against the photos and the yellow stripe of the A4 header (at least 3 mm), text that overlaps something else, and
  paragraphs ending in a very short line. The last build measured 9,580 lines of text and 287 slashes: smallest gap
  between a slash and a text 2.2 mm, smallest margin 9 mm, photos at least 220 dpi, **0 problems**.
- **Other defects found and fixed while looking at all 112 PDFs**: the lead sentence was printed twice on the A4 of
  *Machines spéciales*; the A4 header subtitles were 2-3 mm from the diagonal of the photo (the text block is now
  97 mm wide); lone words on the last line of paragraphs (175 before, 32 after, mostly the legal line) thanks to
  `text-wrap: pretty/balance` and non-breaking spaces inside bold groups; two cover slashes that were too tall
  (*Alimentations, convoyage, stockage* and *Lavage, dewatering, dégraissage*: 46 mm -> 37 mm).
- **Titles that shrink to fit** (unchanged in principle, slightly more with the new indent): Portuguese *Lavagem,
  dewatering e desengorduramento* 75 %, German *Sondermaschinen* 76 % and *Maschinenretrofit* 77 %, English
  *Special-purpose machines* 83 %.

**Site**, same kind of problems found with the new script `tools/check_layout.py` (see *For maintenance*):

- **Home page, "Une solution sur mesure pour chaque projet"**: the *Nous contacter* button is now a `mailto:
  robotplus@robotplus.fr` link, and the diagonal between the text and the photo is a real 18° yellow band that follows the
  cut of the photo (before: a short vertical piece). On phones the small yellow marker no longer overlaps the title.
- **Category and sub pages** (header with the title): the yellow slash overlapped or touched the line *MARNAZ · HAUTE-SAVOIE
  · FRANCE* in every window narrower than about 1100 px. The slash is now placed from the text (width + slant + 10 px,
  8 px on phones) and the line is aligned with the title. Home page header: the slash is 8 px from that line (3 px, and 0
  on phones, before).
- **Long words on phones** (German *Sondermaschinen*, *Vibrationswendelförderer*, Portuguese *desengorduramento*...): titles
  were cut off at the right edge and the German home page scrolled sideways. Titles are now a little smaller on narrow
  screens, hyphenated on phones (`hyphens: auto`, as soon as the browser has the dictionary of the language) and, as a last
  resort, broken; single-column grids no longer grow with their longest word (`minmax(0,1fr)`).
- **Checked**: 15 pages x 7 languages x 14 widths from 320 to 1920 px: no slash within 6 px of a text (2 px for the small
  markers of the home page, which are 2.5 px by design), no cut-off text, no sideways scroll.

**Legal notice**: the *Dernière mise à jour* date of `mentions-legales.html` is now 24 novembre 2026, and
`python3 tools/update_site.py --legal-date` sets it to today (or `--legal-date=YYYY-MM-DD`). Run it **every time a new
version of the site is delivered**; `update_site.py --check` reports a date older than the latest entry of this file.
The date of `politique-confidentialite.html` (changed because its e-mail address changed) was set by hand.

## Brochure links name their brochure

- In the **Documents** box of the 14 pages, the two links now say which brochure they open, with the title of its card on
  the home page in quotes: `Brochure A4 "Robotique" (PDF)` and `Brochure pliable "Robotique" (PDF)`. The 7 sub-pages of
  *Alimentations, convoyage, stockage* offer that family's brochure, so their links carry that title. The file names do not change.
- **Translations**: the same pattern in each language, with the title of the card in that language, for example
  `A4 brochure "Robotics" (PDF)`, `Tri-fold brochure "Robotics" (PDF)`, `Broschüre A4 "Robotik" (PDF)`, `Faltbroschüre "Robotik"
  (PDF)`, `Tríptico "Robótica" (PDF)`. The keys `common.brochure_a4` and `common.brochure_fold` are replaced by 16 keys,
  `brochure.<name>.a4` and `brochure.<name>.fold` (8 brochures), in `assets/js/i18n.js`.
- `python3 tools/update_site.py --check` now also reports a link without the right key, and a label that does not quote
  the title of its card in one of the 7 languages (so a title changed on the home page cannot be forgotten here).
- The PDFs are unchanged.

## Data sheets removed

- The *Fiche technique (PDF)* link is gone from the 14 sub-pages, the translation key `common.datasheet` is deleted, and
  the 7 `fiche-technique-*.pdf` are removed from `assets/brochures/`. They stay in the git history (commit `dbec2a9`).
  The *To decide* point of 23 November (the data sheet of *Rétrofit machines* was a robot cell) no longer applies.

## Contact strip

- **The *Nous contacter →* button of the black band *Un projet lié à cette solution ?* now opens an e-mail**
  (`mailto:robotplus@robotplus.fr`), like the *Nous contacter* button of the home page. On the 7 category pages (*Robotique*,
  *Machines de contrôle*, *Contrôle laser*, *Machines spéciales*, *Rétrofit machines*, *Lavage, dewatering, dégraissage*,
  *Postes de travail*) it used to scroll down to the footer.
- **The band was missing on the 7 sub-pages of *Alimentations, convoyage, stockage*** (`bols-vibrants`, `tremies`,
  `convoyeurs`, `elevateurs-a-lames`, `tremies-pour-axes`, `stockage-de-pieces`, `tables-rotatives-stockage`): it is now
  there, under the photo gallery, identical to the other pages. The page with the tiles
  (`alimentation-convoyage-stockage.html`) has no band, as before.
- The same markup and the same translation keys (`common.project_question`, `common.contact_button`) are used on the 14
  pages, so nothing new had to be translated: the band is in the 7 languages.
- **Checked**: in a browser, the 14 pages in the 7 languages (98 views) each have one band, after the gallery, with the right
  link and the right text in the right language; seen on a desktop and on a phone window; `tools/check_layout.py`: 1,568
  page views, 0 problems. The PDFs are unchanged.

## For maintenance

- Change a French text of a brochure: edit `tools/brochures/content/<name>.json`, change the same sentence in the six
  `tools/brochures/translations/*.json`, run `python3 -I tools/brochures/localize.py` (it lists what is missing), then
  rebuild (`tools/brochures/README.md`). Titles are never typed there: they come from the site.
- `python3 tools/update_site.py --check`: also reports a linked brochure that is missing in one of the languages, and
  a PDF in `assets/brochures/` that no page links to.
- `python3 tools/check_layout.py .` (needs Playwright, like the brochures): opens the home page and the 14 category pages
  in the 7 languages at 14 window widths and reports a yellow slash that touches a text, text cut off by the edge of the
  window or of its box, and a page that scrolls sideways. Run it after changing `assets/css/site.css` or the texts of
  `assets/js/i18n.js` (`--quick` is faster: 4 widths; `--widths 390,1100`, `--pages index,bols`, `--langs de`).

---

# Update — 23 November 2026 (brochures)

The brochures that were drafts made with ChatGPT are replaced by new ones, built from the texts and the photos of the
site. Every category page now offers two brochures in its **Documents** box: *Brochure A4* and *Brochure pliable*.

## Brochures

- **14 PDFs** in `assets/brochures/`: 7 brochures, each in two formats, named `brochure-<name>-a4.pdf` and
  `brochure-<name>-pliable.pdf`.
  - **Pliable** (tri-fold): A4 landscape, 2 pages, folded in 3 panels. Page 1 is the outside (flap | back cover | front
    cover), page 2 the inside (three panels).
  - **A4**: portrait, 1 page. *Contrôle* and *Alimentations, convoyage, stockage* have 2 pages, because they carry
    more content (the 7 families, the two control pages).
  - Same texts, same photos and same style in both formats; the look is that of the site (yellow and dark, Barlow
    Condensed titles, Inter texts, the white lines with a yellow edge, the dark Applications box, the yellow contact
    band). Contact details, a QR code to the page of the site and the legal line are on every brochure.
- **Which brochure on which page**: *Robotique industrielle*, *Machines spéciales*, *Rétrofit machines*, *Lavage
  dewatering dégraissage* and *Postes de travail* have their own; *Machines de contrôle* and *Contrôle laser* share
  one; the 7 pages of the family *Alimentations, convoyage, stockage* share one (seven families, one card each).
- **Texts**: condensed from the French texts of the pages (the ones of the document of 22 November): headlines,
  paragraphs, lists, Applications, the closing sentences. They are shortened and merged to fit a panel, so they are
  not word for word the text of the pages; I checked by script that they use the vocabulary of the site and that every
  figure (30 years, 1996, ± 0,07 µm) and the legal line come from it. French only; the other languages get the same
  French brochures, as for the data sheets.
- **Photos**: taken from your full-resolution originals (`Photos site/…`), **without filigrane**, cropped for each place
  and placed at 220 dpi (checked in the PDFs: at least 219 ppi). They are photos of the site, listed in
  `tools/photo-sources.csv`. The *Rétrofit* originals are two photos side by side: each half is used on its own,
  without the red separator.
- **Printing the tri-fold**: A4 landscape, double-sided, flip on the short edge. The right-hand panel of the inside
  (97 mm) folds in first. There is no bleed: the dark and yellow areas go to the edge of the sheet, so a desktop
  printer leaves a white border; ask the printer for a version with bleed if it is printed in quantity.
- **Removed**: the 7 old `brochure-*.pdf` files, including `brochure-robotisation-machine-transfert.pdf` (the robot
  cell): none of them matched the new texts. They stay in git history. A brochure for the robot cell can be made
  the same way if you want to keep it.
- **Data sheets**: the 7 `fiche-technique-*.pdf` are untouched.

## Pages

- **Documents box** of the 14 sub-pages: three links, *Fiche technique (PDF)*, *Brochure A4 (PDF)* and *Brochure
  pliable (PDF)*. The labels are translated into the 7 languages (keys `common.datasheet`, `common.brochure_a4`,
  `common.brochure_fold`; the old `common.brochure` is gone). The PDFs themselves are in French. The translations of
  these three labels are mine.
- ***Alimentations, convoyage, stockage*** (the page with the 7 tiles): the Documents box is removed, since the documents
  are in each of the 7 sub-pages. The CSS rule `.sub-main .source-box`, no longer used, is removed too.
- **To decide**: the *Fiche technique* of *Rétrofit machines* is still `fiche-technique-robotisation-machine-transfert.pdf`,
  the data sheet of a robot cell, which is not about retrofit. I left it as it was; tell me if it should be removed or
  replaced.

## Tablet footer

- At 768 px the footer pushed the page sideways (the longest German word, "Sondermaschinen."). Up to 900 px wide
  the footer now has 2 columns. Checked at 768, 820, 900, 1024 and 1280 px in the 7 languages: no sideways scroll.
- **Not changed**: on phones, the big title of a few pages is wider than the screen in German, Spanish and
  Portuguese (12 page/language combinations at 320 px, 3 at 360 px, 2 at 390 px). The worst are the German
  *Vibrationswendelförderer* (143 px too wide at 320 px, 73 px at 390 px) and the Portuguese *Lavagem, desidratação e
  desengorduramento* (92 px at 320 px, 22 px at 390 px); the others are within 55 px. It was already like this before
  this update. A smaller title on phones, or letting long words break, would fix it: tell me if you want it.

## For maintenance

- `tools/brochures/` holds the generator (`make_brochures.py`), one content file per brochure (`content/*.json`), the
  fonts and the logos, and a `README.md` (rebuild, edit, print). The brochures are **not** updated automatically when a
  page text changes: change the content file of the brochure, then rebuild. The originals of the photos stay on your
  computer (`--originals`).
- `python3 tools/update_site.py --check`: no missing translation, no duplicate or unused key, no missing link.

---

# Update — 23 November 2026 (texts of the categories)

The 14 category pages of `solutions/` now carry the texts of the document `Textes_des_catégories_2026_11_22.docx`: in
French as written in the document, and translated into the six other languages. The layout of these pages changed too.

## Texts

- **Pages updated**: Robotique industrielle, Machines de contrôle, Contrôle laser, Machines spéciales, Bols vibrants,
  Convoyeurs, Élévateurs à lames, Stockage de pièces, Tables rotatives de stockage, Trémies, Trémies pour axes,
  Rétrofit machines, Lavage dewatering dégraissage, Postes de travail. Each page shows the text of the document in its
  order: bold headlines, paragraphs (bold words kept), sub-headings, lists with their bold lead-ins, then the
  Applications box. The French of every page was compared with the document by a script: same words, same bold.
- **Replaced**: everything these pages said that is not in the document (old paragraphs, the "Contrôles réalisés" card
  of *Contrôle laser*, the robot texts and the "Positionnement" card of *Rétrofit machines*, …). The texts you typed
  yourself on github.com in *Robotique industrielle* and *Machines de contrôle* were already close to the document;
  both pages now follow the document exactly (for instance "courants de Foucault", paragraphs split as in the
  document), with `<strong>` instead of `<B>`, their own keys and the translations. The previous texts are in the
  git history.
- **Not changed**: the titles of the pages and of the menu (the headings of the document are names of pages, not new
  titles), the pictures and galleries, the PDF documents, and the page *Alimentations, convoyage, stockage* (its
  introduction already contains the sentence of the document).
- **Translations**: English, Italian, German, Spanish, Portuguese and Romanian, 212 texts, written for this update and
  not proofread by a professional translator. They reuse the words already on the site (*Blade elevators*,
  *Hoppers*, *Vibrationswendelförderer*, *Lamellenförderer*, …). A reading by someone who knows the trade in each
  language is worthwhile, in particular for German and Romanian.
- **Obvious typos of the document corrected**: "Machines en contrôle en ligne avec la production" → "Machines de
  contrôle en ligne avec la production"; "Convoyage de pièce en entrée machine" → "Convoyage de pièces en entrée de
  machine"; "Convoyage de panier" → "Convoyage de paniers"; "Remplacement d'automate programmables" → "Remplacement
  d'automates programmables"; "Déshuilage et déwatering" → "Déshuilage et dewatering" (the spelling used elsewhere in
  the document); "Lavage inter opération en ligne" → "Lavage inter-opération en ligne". Apostrophes are typographic
  (’), as everywhere on the site, and the eight Applications of *Stockage de pièces* have no final full stop, like
  the other lists.
- **Robotique industrielle, Applications box**: the five items already on the page keep their translations;
  "Robotique collaborative", the sixth item of the document, has its own key and translations. The duplicate keys that
  *Robotique industrielle* and *Machines de contrôle* had are gone.

## Layout

- **Wide screen**: the text is in the left column, the **Documents** box and, below it, the **Applications** box are in
  the right column. **Phone**: text, then Applications, then Documents (the Applications box used to sit inside the
  text column).
- **The 7 pages of the family *Alimentations, convoyage, stockage*** (bols vibrants, convoyeurs, élévateurs à lames,
  stockage de pièces, tables rotatives, trémies, trémies pour axes) had a bare layout: one sentence, then the photos.
  They now use the layout of the other pages: "← Retour aux sous-catégories" above the text, the Documents box (the
  data sheet and the brochure of the family; there is no document per sub-category, so the 7 pages show the same two
  PDFs), the Applications box, then the gallery.
- **Sub-headings** of a page (for example "Performances et fonctionnalités") are `<h3>` titles inside the text column;
  lists are the white cards with the yellow edge already used on the site.
- `assets/css/site.css`: `.detail-grid aside` (the two boxes one under the other), `.detail-section > h3`,
  `.detail-section > .back-link`, and the order of the boxes below 900 px.

## For maintenance

- New keys in `assets/js/i18n.js`: `page.<name>.lead1…` (paragraphs), `.head1…` (sub-headings), `.item1…` (list items),
  `.card1.item1…` (Applications). The 82 old keys of these pages and the unused `common.checks` were removed.
  `python3 tools/update_site.py --check`: no missing translation, no duplicate key, no unused key.
- Bold in a text is `<strong>…</strong>`, in the page and in every language (see README, "Layout of a category page").

---

# Update — 21 November 2026 (filigrane)

The ROBOTPLUS logo is now printed as a filigrane (watermark) in the centre of the 134 photos of the galleries of the
14 subpages.

- **Size**: the visible logo is 50 % of the width of the picture for a horizontal photo (83 photos) and 70 % for a
  portrait photo (51 photos). It is exactly centred.
- **Opacity**: 10 % for light photos, like the example you sent, 13 % for darker ones where the filigrane is harder to
  see. A photo counts as dark when the average brightness of the part under the logo is below 120 (scale 0–255):
  73 photos at 13 %, 61 at 10 %. Orientation, size, brightness and opacity of each photo:
  `tools/watermark-2026-11-21.csv`.
- **Not touched**: the title pictures (`assets/photos/categories/`), the homepage pictures (`assets/photos/home/`),
  and the building, logo and map (`assets/images/`).
- File names, order and dimensions in pixels are unchanged, so no page needed a change. The photos were saved again as
  JPEG with the same settings as before (quality 80); the files are 2 % heavier on average, the heaviest is 483 KB.
- The filigrane is part of the picture. The photos without it are in the git history (last commit before this update:
  `714c8bb`). A photo added with `tools/resize_photos.py` does not get the filigrane automatically.

---

# Update — 18 November 2026 (picture names)

All pictures renamed and the galleries reordered from the sheet `robotplus-pictures-to-rename.xlsx` you filled in.

- **169 files renamed**: the 135 gallery photos (minus one, see below), the 15 category pictures with their
  `-thumb` twins, the 2 homepage covers with their `-mobile` twins, and the building. Old and new names:
  `tools/picture-renames-2026-11-18.csv`. Pages, `site.css`, `tools/pages.json` (header picture, `og:image`, preload),
  `tools/photo-sources.csv` and the galleries were updated; no page mentions an old name any more.
- **Gallery files** are `NN-name.jpg`: `NN` is the position, so the order on the page is the one you chose. New order
  for *Machines de contrôle* (the old 14th photo is now first) and *Lavage, dewatering* (see below).
- **Deleted**: `assets/photos/lavage-dewatering-degraissage/09-ts7.jpg` ("A SUPPRIMER"). The gallery now has 8 photos.
- **Adjusted while applying the sheet**: in *Lavage, dewatering* two photos had position 8; they were placed 7 and 8, as
  their names say. The category picture "Robotplus.fr Alimentatoions" became `robotplus.fr-alimentations` (typo).
  Names are lowercase, accents and spaces become `-`, the dot of "robotplus.fr" is kept.
- `tools/resize_photos.py --category <page>` now uses the file name written in `tools/pages.json` (before, it would have
  created a file with the old name). README: new paragraph "Names of the pictures".

---

# Update — 18 November 2026

Follow-up to the rebuild, after two problems reported on the Robotique page. The edits made on github.com to
`solutions/robotique-industrielle.html` (new subtitle, "Cellules standards de robotique collaborative." and the
extra paragraph) are kept.

## What was wrong

1. **A text edited in an HTML page showed for a moment, then went back to the old one.** The texts of every language,
   French included, were stored in `assets/js/i18n.js` and written into the page when it loaded, so the French in
   the HTML was never what the visitor saw. The README sent you to `i18n.js` for any text change, but editing the
   page itself is the natural thing to do, and it has to work.
2. **The picture next to the title first showed a text.** The photo carried an alt text (the page title) that some
   browsers write in the empty frame until the file has downloaded.

## What changed

- **French is now the text written in the page**, and nothing overwrites it. `assets/js/i18n.js` only provides the
  six other languages; a text with no translation yet (a paragraph you have just added, for instance) is shown in
  French in those languages. `assets/js/site.js` and `tools/update_site.py` were reworked for this: the script no
  longer writes French into the pages. It keeps the reference `"fr"` copy of `i18n.js` up to date, adds an empty
  line for each new key, lists the texts whose French changed (their translations are to review) and warns when one
  key is used with two different French texts. See "Texts and translations" in `README.md`.
- The legal line of the footer (SARL, SIREN…) used to exist only in `i18n.js`; it is now in `tools/partials/footer.html`.
- **New subtitle** "ROBOTPLUS — Robotique, contrôle, machines spéciales." on the 7 pages that carried the old one
  (Robotique industrielle, Machines de contrôle, Contrôle laser, Machines spéciales, Rétrofit machines, Postes de
  travail, Lavage-dewatering-dégraissage), translated into the 6 other languages with the wording of the footer
  slogan. The Alimentation pages have their own subtitle and are unchanged.
- **Robotique page**: "Cellules standards de robotique collaborative." is translated into the 6 languages;
  "Réalisation de cellules sur mesure." keeps its translations under its new key `page.robotique-industrielle.lead4`.
- **Photo next to the title** (15 pages): no alt text (it is decorative, the title is right beside it), the 800 px
  file for ordinary screens (118 KB instead of 283 KB on Robotique; it is the file the homepage card uses, so it is
  often already in the browser cache), the 1400 px file for sharp screens and phones, no asynchronous decoding.
  The grey frame stays empty until the photo arrives. Every other photo of a page also hides its alt text while
  loading (`main img{color:transparent}` in `site.css`).

## How to install (26 files)

    cd ~/mygit/robotplus-automatisme.github.io
    git pull        # first: it fetches the edits made on github.com, which the update contains
    unzip -o ~/Downloads/robotplus-update-2026-11-18.zip -d .
    git status      # 26 modified files
    git add -A
    git commit -m "French text is written in the pages; new subtitle; header photo without flash"
    git push

Do not edit `solutions/robotique-industrielle.html` on github.com between the download and the push: the update
replaces that file with the version of commit `792c30b` (14:31 on 18 November) plus the changes above.

## To check

- The translations of the new subtitle and of the collaborative-robotics sentence are mine: worth a look by native speakers.

---

# Rebuild — 14 November 2026 (already installed)

Rebuild of the site from commit `16967a6` ("updating cover pic"). Same design and content,
with the bugs, weight, structure, SEO and readability problems found in the code review fixed.
Every page was tested in a headless Chrome in the 7 languages, on desktop, tablet and phone widths.

## How to install it

1. **Save your original photos first**: copy the folder `Photos site` from your repository to somewhere
   outside it (for example `~/Pictures/robotplus-originals`). The new site only contains web-size copies.
2. Unzip, then replace the content of the repository with the new version (keeps `.git`):

       rsync -a --delete --exclude .git ~/Downloads/robotplus-automatisme.github.io/ ~/mygit/robotplus-automatisme.github.io/

3. Look at it: open `index.html` in a browser, and run `git status` in the repository.
4. Publish:

       git add -A
       git commit -m "Rebuild: bug fixes, web-size photos, shared CSS/JS and translations"
       git push

## Bugs fixed

- **Translations of 18 solution pages**: the script had a syntax error (a doubled `{`) and never ran; texts,
  titles and footers stayed in French. All pages now translate fully (the legal pages stay in French and say so).
- **Homepage forgot the language**: after a click on a menu link (`#solutions`…), a reload or a shared link went
  back to French and overwrote the saved choice. The language is now kept.
- **Homepage card descriptions** were French in every language: now translated.
- **Gallery jumped back to photo 1** on the washing / dewatering page (it listed 3 photos that don't exist).
  Galleries are now generated from the photos actually present, and a photo that fails to load is skipped forward.
- **Every photo with an accent in its path was requested twice** (paths written in macOS-style Unicode): all photo
  paths are now plain ASCII (`assets/photos/convoyeurs/05-img-0071.jpg`).
- **Broken CSS quote** on 7 sub-category pages (requests to `image-01.jpg)`): gone.
- **Gallery heading did not change language** after switching: fixed.
- **Headings fell back to Times** when Google Fonts could not load: fallback fonts added everywhere.
- Found while rebuilding:
  - between 721 and 1050 px wide (tablets), the language button was hidden;
  - on phones, the Robotique and Machines de contrôle pages squeezed their text into a narrow column;
  - on the legal pages, the "L'entreprise" and "Solutions" menu links did nothing;
  - in English the legal pages' tab title was the homepage slogan.

## Speed

- Photos resized (max. 1600 px for galleries, 1400/800 px for category pictures) and re-encoded:
  225 MB of camera files → 34 MB. Homepage: about 22 MB → 1.3 MB; solution pages: 0.5–1.1 MB.
- The old hidden slideshows (whose images were downloaded and never shown) are removed.
- Images below the screen load only when needed; the next gallery photo is loaded in advance.
- Phones get smaller versions of the two big homepage photos.

## Structure (so a fix only has to be made once)

- One stylesheet `assets/css/site.css` (the 5 stacked "correction" blocks merged), one script `assets/js/site.js`,
  and **one translation file** `assets/js/i18n.js` instead of three diverging 44 KB copies in each page.
  The 24 old pages weighed 1.5 MB of HTML; the 19 new ones weigh 0.23 MB, plus the shared 70 KB translation file.
- Shared head, header and footer live in `tools/partials/`; `python3 tools/update_site.py` writes them into every
  page, rebuilds the galleries from the photo folders and checks translations and links. See `README.md`.
- `tools/resize_photos.py` prepares new photos (size, orientation, no camera/GPS data).

## Content, SEO and legal pages

- Placeholder sentences removed from 8 pages ("Cette page sera complétée…", "…enrichis ultérieurement").
- Legal pages: the two internal notes removed ("L'inventaire des visuels tiers… avant publication définitive";
  "Les durées précises de conservation… doivent être définies…"); date updated to 14 November 2026.
- The two Alimentation brochures are now linked from the Alimentation, convoyage, stockage page.
- Every page has its own title and meta description, Open Graph tags (preview image when shared) and a favicon.
- `sitemap.xml` and `robots.txt` are generated by GitHub Pages (`jekyll-sitemap`; the unused `jekyll-seo-tag` removed).
- The homepage HTML now carries the current slogan (it showed the old one until the script replaced it).
- A `404.html` page for unknown addresses.
- Small fixes: Romanian "concepeam" → "concepem"; German region name unified ("Hochsavoyen").

## Readability and accessibility

- No more 7–9 px text: footer 11–13 px, card descriptions 12 px, body copy 14 px. Text under 12 px went from
  59 % of the homepage to 10 % (only the 11 px capitals above the title and the legal line in the footer).
- Footer text contrast raised above the WCAG AA level (7.2:1 and 6.1:1).
- Menus: `aria-expanded` kept up to date, Escape and outside click close the language menu, all images
  have size and text alternatives, one `<h1>` per page.

## Repository

- Removed: `preview.html` (old homepage) and 5 unlinked solution pages, the unused folders
  `assets/pdf-photos`, `assets/pdf-extracted`, `assets/pdf-pages`, old images, `style.css`, `main.js`,
  the camera originals in `Photos site`, and the 8 `.DS_Store` files. `.gitignore` added.

## To check or decide

- **Translations I wrote**: card descriptions, the 404 page, the "French only" notice and a few button labels.
  Worth a look by native speakers. Existing translations were kept as they were.
- **Retention periods** in the privacy policy: the to-do sentence is gone and the policy states the criteria.
  If it matches your practice, you could add for example: « Les échanges avec des prospects sont conservés au
  maximum trois ans après le dernier contact ; les données d'une relation commerciale sont conservées pendant
  la relation puis archivées pendant les durées légales (dix ans pour les pièces comptables). » These are the
  CNIL's usual reference values, not a statement of what ROBOTPLUS does — confirm before adding.
- **Laser marking**: `marquage-laser.html` (removed, it was not linked) was the only removed page whose text
  existed nowhere else (marking units, Datamatrix). It and its two brochures are still in git history
  (`git show 16967a6:solutions/marquage-laser.html`). If you still offer it, it can come back as a linked page.
- **Domain**: the repository has no `CNAME`, so the site is not served at robotplus.fr yet (see `README.md`).
- Not changed: fonts are still loaded from Google Fonts (declared in the privacy policy); search engines still
  see the French version only (other languages are switched in the browser); the git history still contains
  the old photos; `fiche-technique-robotique-industrielle.pdf` weighs 8 MB.
