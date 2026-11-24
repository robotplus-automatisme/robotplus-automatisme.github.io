#!/usr/bin/env python3
"""Keep the ROBOT+ pages in sync. Run from anywhere:  python3 tools/update_site.py

The French text of the site is written in the HTML pages: editing a page is enough, nothing overwrites it.
This script is only needed for the parts that are shared between pages. For every page listed in tools/pages.json it:
  * rewrites the shared blocks between the <!-- shared:... --> markers (head, header, footer, scripts) from the
    templates in tools/partials/ (edit those templates, not the blocks inside a page: they are overwritten here);
  * rebuilds the photo gallery between <!-- gallery:start --> and <!-- gallery:end --> from the photos in the
    page's folder (assets/photos/<page>/, shown in file-name order: 01-..., 02-...);
  * keeps the "fr" values of assets/js/i18n.js equal to the French written in the pages (a reference for whoever
    translates), adds an empty entry to i18n.js for every new data-i18n="key", and lists the texts whose French has
    changed so that their translations can be reviewed;
  * reports missing translations, a key used with two different French texts, and links to missing files;
  * checks the brochure links: the 7 PDFs exist, and the label of each link names its brochure, Brochure A4 "<title of its card
    on the home page>" (PDF), in every language (keys brochure.<name>.a4 and brochure.<name>.fold);
  * with --legal-date (or --legal-date=YYYY-MM-DD) writes today's date (or that date) in the "Dernière mise à jour" line of
    the legal notice (mentions-legales.html). Do it every time a new version of the site is published; without the option,
    the script reports an error when that date is older than the latest entry of CHANGES.md.
Only the Python standard library is needed. Use --check to report without writing any file.
"""
import datetime, hashlib, html, json, os, re, struct, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
I18N = os.path.join(ROOT, 'assets/js/i18n.js')
LANGS = ['fr', 'en', 'it', 'de', 'es', 'pt', 'ro']
CHECK_ONLY = '--check' in sys.argv
problems = []

# parts of a page that this script regenerates from the templates: their French text lives in tools/partials/
GENERATED = re.compile(r'<!-- shared:(\w+) -->.*?<!-- /shared:\1 -->|<!-- gallery:start -->.*?<!-- gallery:end -->', re.S)
TEXT = re.compile(r'<(?P<tag>[a-zA-Z][a-zA-Z0-9]*)\b[^>]*?\sdata-i18n="(?P<key>[^"]+)"[^>]*>(?P<body>.*?)</(?P=tag)>', re.S)
ATTR_TAG = re.compile(r'<[a-zA-Z][^>]*\sdata-i18n-(?:alt|aria)="[^"]+"[^>]*>')
I18N_DICT = re.compile(r'window\.RP_I18N\s*=\s*(\{.*\})\s*;?\s*$', re.S)


def read(path):
    with open(path, encoding='utf-8') as fh:
        return fh.read()


def load_i18n():
    """(file text, dict) of assets/js/i18n.js."""
    text = read(I18N)
    m = I18N_DICT.search(text)
    if not m:
        sys.exit('assets/js/i18n.js: cannot find "window.RP_I18N = { ... };"')
    try:
        return text, json.loads(m.group(1))
    except json.JSONDecodeError as e:
        line = text[:m.start(1)].count('\n') + e.lineno
        sys.exit(f'assets/js/i18n.js line {line}: {e.msg} (the file must stay valid JSON: double quotes, no trailing comma)')


def render_i18n(text, data):
    """The text of i18n.js with its dictionary replaced by `data` (one entry per line, same layout as before)."""
    rows = [f'{json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}' for k, v in data.items()]
    m = I18N_DICT.search(text)
    return text[:m.start(1)] + '{\n' + ',\n'.join(rows) + '\n}' + text[m.end(1):]


def md5(data):
    return hashlib.md5(data).hexdigest()[:8]


def version(rel):
    with open(os.path.join(ROOT, rel), 'rb') as fh:
        return md5(fh.read())


def image_size(path):
    """(width, height) of a JPEG or PNG, read from the file header."""
    with open(path, 'rb') as fh:
        data = fh.read()
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return struct.unpack('>II', data[16:24])
    if data[:2] == b'\xff\xd8':
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack('>HH', data[i + 5:i + 9])
                return w, h
            if marker in (0xD8, 0x01, 0xFF) or 0xD0 <= marker <= 0xD7:
                i += 1 if marker == 0xFF else 2
                continue
            i += 2 + struct.unpack('>H', data[i + 2:i + 4])[0]
    return None


def plain(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', value))).strip()


def attr(value):
    return html.escape(plain(value), quote=True)


def fill(template, values):
    return re.sub(r'\{\{(\w+)\}\}', lambda m: values[m.group(1)], template)


def replace_block(page_html, name, content, file):
    pattern = re.compile(r'(<!-- shared:%s -->)(.*?)(<!-- /shared:%s -->)' % (name, name), re.S)
    if not pattern.search(page_html):
        problems.append(f'{file}: marker <!-- shared:{name} --> not found')
        return page_html
    return pattern.sub(lambda m: m.group(1) + '\n' + content.strip('\n') + '\n' + m.group(3), page_html, count=1)


def gallery_html(page, prefix, title_fr):
    folder = os.path.join(ROOT, page['gallery'])
    photos = sorted(f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')))
    if not photos:
        problems.append(f'{page["file"]}: no photos in {page["gallery"]}')
        return ''
    slides = []
    for i, name in enumerate(photos):
        path = os.path.join(folder, name)
        if os.path.getsize(path) > 900_000:
            problems.append(f'{page["gallery"]}/{name} is {os.path.getsize(path) // 1024} KB: resize it with tools/resize_photos.py')
        if not re.fullmatch(r'[a-z0-9._-]+', name):
            problems.append(f'{page["gallery"]}/{name}: use only lowercase letters, digits and "-" in photo names')
        size = image_size(path)
        dims = f' width="{size[0]}" height="{size[1]}"' if size else ''
        hidden = '' if i == 0 else ' hidden'
        slides.append(f'      <figure class="rp-slide"{hidden}><img src="{prefix}{page["gallery"]}/{name}"{dims} '
                      f'alt="{attr(title_fr)} — photo {i + 1}" loading="lazy" decoding="async"></figure>')
    tpl = read(os.path.join(TOOLS, 'partials/gallery.html'))
    return fill(tpl, {'slides': '\n'.join(slides), 'count': str(len(photos))})


def french_in(fragment, label, found):
    """Record the French written in a piece of HTML, as found[key] = [(text, label), ...]:
    the content of the data-i18n="key" elements (HTML kept as written), and the alt / aria-label of the
    data-i18n-alt / data-i18n-aria elements (plain text, only used for keys that have no element of their own)."""
    for m in TEXT.finditer(fragment):
        found['text'].setdefault(m.group('key'), []).append((' '.join(m.group('body').split()), label))
    for m in ATTR_TAG.finditer(fragment):
        tag = m.group(0)
        for kind, target in (('alt', 'alt'), ('aria', 'aria-label')):
            key = re.search(r'\sdata-i18n-%s="([^"]+)"' % kind, tag)
            value = re.search(r'\s%s="([^"]*)"' % target, tag)
            if key and value:
                found['attr'].setdefault(key.group(1), []).append((plain(value.group(1)), label))


def french_texts(sources):
    """{key: (French text, 'text' or 'attr')} for every data-i18n* key found in `sources` = [(label, html), ...]."""
    found = {'text': {}, 'attr': {}}
    for label, fragment in sources:
        french_in(fragment, label, found)
    result = {}
    for kind in ('text', 'attr'):
        for key, occurrences in found[kind].items():
            if key in result:
                continue
            first, where = occurrences[0]
            result[key] = (first, kind)
            for text, label in occurrences[1:]:
                if text != first:
                    problems.append(f'data-i18n="{key}" is written differently in {where} ("{first}") and in {label} ("{text}"): '
                                    f'all its occurrences share one translation, so give the second text its own key')
    return result


def same_french(current, written, kind):
    if kind == 'attr':
        return plain(current) == written
    return ' '.join(current.split()) == written


def sibling_of(i18n, key):
    """The existing key after which a new `key` is best placed: the numbered neighbour (lead3 for lead4), else the
    last key of the same page / group, else None (the entry is then added at the end)."""
    stem = re.sub(r'\d+$', '', key)
    numbered = [k for k in i18n if k.startswith(stem) and k[len(stem):].isdigit()] if stem != key else []
    if numbered:
        return numbered[-1]
    parts = key.split('.')
    for n in range(len(parts) - 1, 1, -1):
        group = [k for k in i18n if k.startswith('.'.join(parts[:n]) + '.')]
        if group:
            return group[-1]
    return None


def refresh_french(i18n, french):
    """Copy the French written in the pages into i18n (reference copy) and create entries for new keys.
    Returns (changed keys, added keys). Keys that are not written in any page (browser-tab titles of pages without
    a matching title element, photo counter) keep the French that is in i18n.js."""
    changed, added = [], []
    for key, (written, kind) in french.items():
        entry = i18n.get(key)
        if entry is None:
            new = {'fr': written}
            new.update({lang: '' for lang in LANGS if lang != 'fr'})
            anchor = sibling_of(i18n, key)
            if anchor:   # keep the file tidy: the new entry goes right after its neighbours (lead3 -> lead4)
                items = []
                for k, v in i18n.items():
                    items.append((k, v))
                    if k == anchor:
                        items.append((key, new))
                i18n.clear()
                i18n.update(items)
            else:
                i18n[key] = new
            added.append(key)
        elif not same_french(entry.get('fr', ''), written, kind):
            entry['fr'] = written
            changed.append(key)
    return changed, added


def check_links(page_html, file):
    base = os.path.dirname(os.path.join(ROOT, file))
    for ref in re.findall(r'\s(?:href|src)="([^"#?]+)', page_html):
        if re.match(r'^(https?:|mailto:|tel:|data:)', ref):
            continue
        target = os.path.join(ROOT, ref.lstrip('/')) if ref.startswith('/') else os.path.normpath(os.path.join(base, ref))
        if not os.path.exists(target):
            problems.append(f'{file}: link to a missing file: {ref}')


brochures_used = set()
brochure_keys = set()        # the i18n keys of the labels of the brochure links


def check_brochures(page_html, file):
    """A link with data-brochure="<name>-<format>" leads to assets/brochures/brochure-<name>-<format>-<language>.pdf (French in the
    href, the other languages are put in by assets/js/site.js): the 7 files must exist."""
    for tag in re.findall(r'<a\b[^>]*\sdata-brochure="[^"]*"[^>]*>', page_html):
        name = re.search(r'data-brochure="([^"]*)"', tag).group(1)
        href = re.search(r'\shref="([^"]*)"', tag)
        if not href or not href.group(1).endswith(f'/brochure-{name}-fr.pdf'):
            problems.append(f'{file}: the link data-brochure="{name}" must have href="../assets/brochures/brochure-{name}-fr.pdf"')
        base, _, fmt = name.rpartition('-')
        expected = f'brochure.{base}.{"a4" if fmt == "a4" else "fold"}'
        key = re.search(r'\sdata-i18n="([^"]*)"', tag)
        if not key or key.group(1) != expected:
            problems.append(f'{file}: the link data-brochure="{name}" must have data-i18n="{expected}"')
        brochure_keys.add(expected)
        for lang in LANGS:
            brochures_used.add(f'brochure-{name}-{lang}.pdf')
            if not os.path.exists(os.path.join(ROOT, 'assets', 'brochures', f'brochure-{name}-{lang}.pdf')):
                problems.append(f'{file}: assets/brochures/brochure-{name}-{lang}.pdf does not exist (python3 tools/brochures/make_brochures.py)')


def shorten(text, n=90):
    text = plain(text)
    return text if len(text) <= n else text[:n - 1] + '…'


# ---- last update date of the legal notice (mentions légales): it is the date of the latest version of the site
LEGAL_PAGE = 'mentions-legales.html'
LEGAL_DATE = re.compile(r'(<p class="legal-updated"><strong>Dernière mise à jour : )([^<]*)(</strong></p>)')
MONTHS_FR = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


def french_date(d):
    return f'{"1er" if d.day == 1 else d.day} {MONTHS_FR[d.month - 1]} {d.year}'


def date_from(day, month, months, year):
    try:
        return datetime.date(int(year), months.index(month.lower() if months is MONTHS_FR else month) + 1, int(day))
    except ValueError:
        return None


def legal_date():
    """Write (--legal-date) and check the "Dernière mise à jour" date of the legal notice."""
    path = os.path.join(ROOT, LEGAL_PAGE)
    if not os.path.exists(path):
        return
    text = read(path)
    m = LEGAL_DATE.search(text)
    if not m:
        problems.append(f'{LEGAL_PAGE}: the line <p class="legal-updated"><strong>Dernière mise à jour : …</strong></p> is missing')
        return
    wanted = None
    for arg in sys.argv[1:]:
        if arg == '--legal-date':
            wanted = datetime.date.today()
        elif arg.startswith('--legal-date='):
            try:
                wanted = datetime.date.fromisoformat(arg.split('=', 1)[1])
            except ValueError:
                sys.exit('--legal-date=YYYY-MM-DD expects a date such as 2026-11-24')
    if wanted and not CHECK_ONLY:
        new = LEGAL_DATE.sub(lambda g: g.group(1) + french_date(wanted) + g.group(3), text, count=1)
        if new != text:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(new)
            print(f'{LEGAL_PAGE}: "Dernière mise à jour" is now {french_date(wanted)}.')
        text = new
        m = LEGAL_DATE.search(text)
    dm = re.match(r'\s*(\d{1,2})(?:er)?\s+(\S+)\s+(\d{4})\s*$', m.group(2))
    current = date_from(dm.group(1), dm.group(2), MONTHS_FR, dm.group(3)) if dm and dm.group(2).lower() in MONTHS_FR else None
    if current is None:
        problems.append(f'{LEGAL_PAGE}: cannot read the date "{m.group(2)}" (write it like "24 novembre 2026")')
        return
    log = os.path.join(ROOT, 'CHANGES.md')
    if os.path.exists(log):
        h = re.search(r'^#[^\n]*?\b(\d{1,2}) (' + '|'.join(MONTHS_EN) + r') (\d{4})', read(log), re.M)
        latest = date_from(h.group(1), h.group(2), MONTHS_EN, h.group(3)) if h else None
        if latest and current < latest:
            problems.append(f'{LEGAL_PAGE}: "Dernière mise à jour" is {french_date(current)} but the latest version of the site is '
                            f'dated {latest.day} {MONTHS_EN[latest.month - 1]} {latest.year} in CHANGES.md: '
                            'run  python3 tools/update_site.py --legal-date  (the date of the legal notice follows every new version of the site)')


def main():
    legal_date()
    config = json.loads(read(os.path.join(TOOLS, 'pages.json')))
    i18n_text, i18n = load_i18n()
    partials = {n: read(os.path.join(TOOLS, 'partials', n + '.html')) for n in ('head', 'header', 'footer', 'scripts', 'gallery')}

    # 1. read every page, then collect the French that is written in the templates and in the pages
    originals = {}
    sources = [(f'tools/partials/{name}.html', tpl) for name, tpl in partials.items()]
    for page in config['pages']:
        path = os.path.join(ROOT, page['file'])
        if not os.path.exists(path):
            problems.append(f'{page["file"]}: listed in tools/pages.json but the file does not exist')
            continue
        originals[page['file']] = read(path)
        sources.append((page['file'], GENERATED.sub('', originals[page['file']])))
    french = french_texts(sources)

    # 2. i18n.js: refresh the French reference, add the new keys (written first: the pages link to it with a version number)
    changed_fr, added = refresh_french(i18n, french)
    new_i18n_text = render_i18n(i18n_text, i18n)
    if new_i18n_text != i18n_text and not CHECK_ONLY:
        with open(I18N, 'w', encoding='utf-8') as fh:
            fh.write(new_i18n_text)
    v_i18n = md5(new_i18n_text.encode('utf-8')) if CHECK_ONLY else version('assets/js/i18n.js')

    # 3. pages
    versions = {'v_css': version('assets/css/site.css'), 'v_site': version('assets/js/site.js'), 'v_i18n': v_i18n}
    logo = image_size(os.path.join(ROOT, 'assets/images/robotplus-logo.png'))
    francemap = image_size(os.path.join(ROOT, 'assets/images/france-contour.png'))
    all_used = set(french)
    changed = 0
    for page in config['pages']:
        file = page['file']
        if file not in originals:
            continue
        prefix = page.get('root', '../' * file.count('/'))
        home = prefix + 'index.html' if page['id'] != 'home' else ''
        title_key = f'page.{page["id"]}.title'
        if title_key in french:
            title_fr = plain(french[title_key][0])
        elif title_key in i18n:
            title_fr = plain(i18n[title_key]['fr'])
        else:
            problems.append(f'{file}: no "{title_key}" entry in assets/js/i18n.js (page title)')
            title_fr = 'ROBOT+ Automatisme'
        all_used.add(title_key)
        preload = ''.join(f'\n<link rel="preload" as="image" href="{prefix}{href}" media="{media}" fetchpriority="high">'
                          for href, media in page.get('preload', []))
        values = dict(versions)
        values.update({
            'root': prefix, 'home': home, 'title': html.escape(title_fr), 'description': html.escape(page['description']),
            'og_image': config['site_url'].rstrip('/') + '/' + page['image'],
            'robots': '\n<meta name="robots" content="noindex">' if page.get('noindex') else '',
            'preload': preload,
            'active_home': ' class="active"' if page.get('nav') == 'home' else '',
            'active_solutions': ' class="active"' if page.get('nav') == 'solutions' else '',
            'logo_w': str(logo[0]), 'logo_h': str(logo[1]), 'map_w': str(francemap[0]), 'map_h': str(francemap[1]),
        })
        original = originals[file]
        out = original
        for name in ('head', 'header', 'footer', 'scripts'):
            out = replace_block(out, name, fill(partials[name], values), file)
        out = re.sub(r'(<body\b[^>]*\sdata-root=")[^"]*(")', lambda m: m.group(1) + prefix + m.group(2), out, count=1)
        if page.get('gallery'):
            g = re.compile(r'(<!-- gallery:start -->)(.*?)(<!-- gallery:end -->)', re.S)
            if g.search(out):
                out = g.sub(lambda m: m.group(1) + '\n' + gallery_html(page, prefix, title_fr).strip('\n') + '\n' + m.group(3), out, count=1)
            else:
                problems.append(f'{file}: has a gallery folder but no <!-- gallery:start --> marker')
        check_links(out, file)
        check_brochures(out, file)
        if out != original:
            changed += 1
            if not CHECK_ONLY:
                with open(os.path.join(ROOT, file), 'w', encoding='utf-8') as fh:
                    fh.write(out)

    # 4. report
    folder = os.path.join(ROOT, 'assets', 'brochures')
    if os.path.isdir(folder):
        for name in sorted(os.listdir(folder)):
            if name.endswith('.pdf') and name not in brochures_used:
                problems.append(f'assets/brochures/{name}: no page links to this file (delete it, or add the link)')
    all_used |= {k for k in i18n if k.startswith('gallery.')}
    # the label of a brochure link names the brochure: Brochure A4 "<title of its card on the home page>" (PDF), in every language
    for key in sorted(brochure_keys):
        titles = i18n.get('card.' + key.split('.')[1] + '.title') or {}
        for lang in LANGS:
            label = (i18n.get(key) or {}).get(lang) or ''
            title = titles.get(lang)
            if label and title and f'"{title}"' not in label:
                problems.append(f'"{key}" ({lang}): the label must contain "{title}" (the title of its card on the home page, in quotes): {label}')
    for key in sorted(all_used):
        entry = i18n.get(key)
        if not entry:
            continue
        missing = [lang for lang in LANGS if lang != 'fr' and not entry.get(lang)]
        if missing and entry.get('fr'):
            problems.append(f'translation missing for "{key}" ({", ".join(missing)}): until it is added, that language shows the French text')
    unused = sorted(k for k in i18n if k not in all_used)
    print(f'{len(config["pages"])} pages checked, {changed} {"would change" if CHECK_ONLY else "updated"}.')
    if changed_fr:
        print(f'French text changed since the last run, check the translations of these texts in assets/js/i18n.js ({len(changed_fr)}):')
        for key in changed_fr:
            print(f'  {key}: {shorten(i18n[key]["fr"])}')
    if added:
        print(f'New texts {"to add" if CHECK_ONLY else "added"} to assets/js/i18n.js, translations still empty ({len(added)}):')
        for key in added:
            print(f'  {key}: {shorten(i18n[key]["fr"])}')
    if unused:
        print('Keys in i18n.js not used by any page (can be deleted):', ', '.join(unused))
    for p in problems:
        print('  !', p)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
