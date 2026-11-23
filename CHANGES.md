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
