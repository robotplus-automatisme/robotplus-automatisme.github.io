# ROBOT+ Automatisme — website

Website of ROBOTPLUS (Marnaz, Haute-Savoie), published by GitHub Pages at
https://robotplus-automatisme.github.io/. The pages are plain HTML files: there is no build step,
GitHub publishes them as they are. Opening `index.html` from the disk also works for a quick preview.

## Where things are

| What | Where |
|---|---|
| Pages | `index.html`, `solutions/*.html`, `mentions-legales.html`, `politique-confidentialite.html`, `404.html` |
| Every text, in French, English, Italian, German, Spanish, Portuguese and Romanian | `assets/js/i18n.js` |
| Styles of all pages | `assets/css/site.css` |
| Menu, language switch, photo galleries | `assets/js/site.js` |
| Photos (web size) | `assets/photos/<page>/` (galleries), `assets/photos/categories/` (page headers and cards), `assets/photos/home/` |
| PDF brochures | `assets/brochures/` |
| Shared head / header / footer, list of pages, maintenance scripts | `tools/` (kept in the repository, not published) |

## Making changes

Run the commands from this folder (Python 3 is enough; `resize_photos.py` also needs `python3 -m pip install Pillow`).

- **Change a text**: edit its line in `assets/js/i18n.js` (all languages are side by side), then run
  `python3 tools/update_site.py`. The script copies the French text into the pages, so search engines see it too.
- **Change the header, the footer or the `<head>`**: edit `tools/partials/*.html`, then run the script.
  Do not edit these parts inside a page: everything between `<!-- shared:... -->` markers is rewritten by the script.
- **Add photos to a gallery**: `python3 tools/resize_photos.py ~/Desktop/new/*.jpg --to assets/photos/convoyeurs`,
  then run the script. Photos are shown in file-name order (`01-…`, `02-…`); new ones are added at the end.
  The tool resizes them, turns them upright and removes the camera data (including GPS position).
  Keep your full-resolution originals outside this folder.
- **Replace the picture of a category** (page header + homepage card or tile):
  `python3 tools/resize_photos.py photo.jpg --category convoyeurs`, then run the script.
- **Add a page**: copy a similar page, change its content and its `data-page="…"`, add it to `tools/pages.json`
  (with its description and photo), add its texts to `assets/js/i18n.js` (a `page.<name>.title` entry is required),
  then run the script.
- **Check everything without changing files**: `python3 tools/update_site.py --check`
  (reports missing translations, missing files and photos that are too heavy).
- **Preview**: open `index.html` in a browser, or run `python3 -m http.server` here and open http://localhost:8000.

`tools/photo-sources.csv` lists which original photo each web photo comes from.

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
