# ROBOT+ Automatisme — website

Website of ROBOTPLUS (Marnaz, Haute-Savoie), published by GitHub Pages at
https://robotplus-automatisme.github.io/. The pages are plain HTML files: there is no build step,
GitHub publishes them as they are. Opening `index.html` from the disk also works for a quick preview.

## Where things are

| What | Where |
|---|---|
| Pages | `index.html`, `solutions/*.html`, `mentions-legales.html`, `politique-confidentialite.html`, `404.html` |
| Texts in French | written in the pages themselves (`index.html`, `solutions/*.html`, …) |
| Texts in English, Italian, German, Spanish, Portuguese and Romanian | `assets/js/i18n.js` |
| Styles of all pages | `assets/css/site.css` |
| Menu, language switch, photo galleries | `assets/js/site.js` |
| Photos (web size) | `assets/photos/<page>/` (galleries), `assets/photos/categories/` (page headers and cards), `assets/photos/home/` |
| PDF brochures | `assets/brochures/` |
| Shared head / header / footer, list of pages, maintenance scripts | `tools/` (kept in the repository, not published) |

## Making changes

Texts and photos can be changed directly on github.com (pencil icon on a file) or on your computer: no tool is
needed. The commands below are run from this folder (Python 3 is enough; `resize_photos.py` also needs
`python3 -m pip install Pillow`).

**Texts and translations**

- **French**: edit the text in the page (`index.html`, `solutions/….html`, …). What is written in the page is what
  is displayed in French; nothing else has to be done and nothing overwrites it.
- **Other languages**: edit `assets/js/i18n.js`. One line is one text, found with the key written in the page next to
  it (`<p data-i18n="page.convoyeurs.lead1">` is the line starting with `"page.convoyeurs.lead1"`). Change the value of
  the language you want. A language whose value is empty shows the French text. The `"fr"` value of each line is only
  a reference copy: changing it changes nothing.
- **A text that appears on several pages** (for instance the subtitle under the page titles, key `common.tagline`)
  must be changed on each of those pages, with the same wording: all elements with the same key share one translation.
- **New paragraph or list item**: copy an existing one in the page and change its text. Then either delete its
  `data-i18n="…"` attribute (the text stays in French in every language), or give it a new key of its own
  (`page.convoyeurs.lead9`) and add that key with its translations to `assets/js/i18n.js` (until then the other
  languages show the French text). Never reuse the key of another text.
- **`python3 tools/update_site.py`** is not needed for a text change. If you run it, it lists the French texts that
  changed (their translations may need an update), adds an empty line to `i18n.js` for each new key and updates the
  `<title>` of a page from its `<h1>`. It never rewrites the text of a page.

**Parts shared by all pages**

- **Header, footer, `<head>`**: edit `tools/partials/*.html`, then run `python3 tools/update_site.py`, which copies
  them into every page. A change made by hand inside a page, between the `<!-- shared:... -->` markers, is
  overwritten the next time the script runs. The same goes for the photo gallery between `<!-- gallery:start -->`
  and `<!-- gallery:end -->`.
- **Add photos to a gallery**: `python3 tools/resize_photos.py ~/Desktop/new/*.jpg --to assets/photos/convoyeurs`,
  then run the script. Photos are shown in file-name order (`01-…`, `02-…`); new ones are added at the end.
  The tool resizes them, turns them upright and removes the camera data (including GPS position).
  Keep your full-resolution originals outside this folder.
- **Filigrane**: the photos of the galleries carry the ROBOTPLUS logo, centred, at 10 % or 13 % opacity (50 % of the
  width of the picture, 70 % for a portrait one). It is part of the JPEG file, so it cannot be switched off. A photo
  added with `resize_photos.py` does not get it automatically, and the unmarked photos are in the git history.
  Details of each photo: `tools/watermark-2026-11-21.csv`. The title pictures and the homepage pictures have none.
- **Names of the pictures**: a gallery photo is called `NN-name.jpg`, e.g. `03-robotplus.fr-robotique-3.jpg`. The two
  digits give the order on the page; the rest is free (lowercase letters, digits, `-` and `.`, no accents or spaces).
  To rename or reorder a photo, rename the file (keep the `NN-` prefix, numbers without gaps are not required) and run
  the script. Category and homepage pictures have no prefix (`robotplus.fr-robotique.jpg`) and come with a small
  twin: `-thumb` (categories) or `-mobile` (homepage covers). The name of a category picture is the one written in
  `tools/pages.json`; if you rename it, rename its twin too and change `pages.json` and the `<img>` of its page.
- **Replace the picture of a category** (page header + homepage card or tile):
  `python3 tools/resize_photos.py photo.jpg --category convoyeurs` (the page name, e.g. `convoyeurs`), then run the
  script. The new picture takes the file name written in `tools/pages.json`.
- **Add a page**: copy a similar page, change its content and its `data-page="…"`, give its title the key
  `page.<name>.title` (`<h1 data-i18n="page.<name>.title">`), add the page to `tools/pages.json` (with its description
  and photo), then run the script: it creates the lines to translate in `assets/js/i18n.js`.
- **Check everything without changing files**: `python3 tools/update_site.py --check`
  (reports missing translations, missing files and photos that are too heavy).
- **Preview**: open `index.html` in a browser, or run `python3 -m http.server` here and open http://localhost:8000.

`tools/photo-sources.csv` lists which original photo each web photo comes from.
`tools/picture-renames-2026-11-18.csv` lists the old and new file name of each picture renamed on 18 November 2026.

## Publishing

Commit and push only what changed:

    git add -A
    git commit -m "Describe the change"
    git push

Please avoid deleting every file and adding them back in two commits: git can then no longer show what changed,
and it removes the `CNAME` file that GitHub adds when a custom domain is configured.

## Custom domain (robotplus.fr)

The site currently answers at robotplus-automatisme.github.io only. To serve it at robotplus.fr:
1. In the repository on GitHub: Settings → Pages → Custom domain → `www.robotplus.fr` (or `robotplus.fr`) → Save.
   GitHub adds a `CNAME` file to the repository: run `git pull` before your next push so you keep it.
2. At OVHcloud, point the domain to GitHub Pages (the DNS records are listed in GitHub's documentation
   "Managing a custom domain for your GitHub Pages site").
3. Tick "Enforce HTTPS" once GitHub offers it, and change `site_url` in `tools/pages.json`, then run the script.
