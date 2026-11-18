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
