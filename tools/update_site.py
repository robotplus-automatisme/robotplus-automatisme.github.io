#!/usr/bin/env python3
"""Keep the ROBOT+ pages in sync. Run from anywhere:  python3 tools/update_site.py

What it does, for every page listed in tools/pages.json:
  * rewrites the shared blocks between the <!-- shared:... --> markers (head, header, footer, scripts)
    from the templates in tools/partials/;
  * rebuilds the photo gallery between <!-- gallery:start --> and <!-- gallery:end --> from the
    photos in the page's folder (assets/photos/<page>/, shown in file-name order: 01-..., 02-...);
  * copies the French texts of assets/js/i18n.js into the elements marked data-i18n="key"
    (so the HTML matches the translation file, also for search engines);
  * reports missing translations and broken links to local files.
Only the Python standard library is needed. Use --check to report problems without writing files.
"""
import hashlib, html, json, os, re, struct, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
LANGS = ['fr', 'en', 'it', 'de', 'es', 'pt', 'ro']
CHECK_ONLY = '--check' in sys.argv
problems = []


def read(path):
    with open(path, encoding='utf-8') as fh:
        return fh.read()


def load_i18n():
    text = read(os.path.join(ROOT, 'assets/js/i18n.js'))
    m = re.search(r'window\.RP_I18N\s*=\s*(\{.*\})\s*;?\s*$', text, re.S)
    if not m:
        sys.exit('assets/js/i18n.js: cannot find "window.RP_I18N = { ... };"')
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as e:
        line = text[:m.start(1)].count('\n') + e.lineno
        sys.exit(f'assets/js/i18n.js line {line}: {e.msg} (the file must stay valid JSON: double quotes, no trailing comma)')


def version(rel):
    with open(os.path.join(ROOT, rel), 'rb') as fh:
        return hashlib.md5(fh.read()).hexdigest()[:8]


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


def sync_texts(page_html, i18n, file):
    """Copy French values from i18n.js into data-i18n elements and data-i18n-alt / -aria attributes."""
    used = set()

    def body(m):
        key = m.group('key')
        used.add(key)
        if key not in i18n:
            problems.append(f'{file}: data-i18n="{key}" has no entry in assets/js/i18n.js')
            return m.group(0)
        return m.group(1) + i18n[key]['fr'] + m.group(5)
    page_html = re.sub(r'(<(?P<tag>[a-zA-Z][a-zA-Z0-9]*)\b[^>]*?\sdata-i18n="(?P<key>[^"]+)"[^>]*>)(.*?)(</(?P=tag)>)',
                       body, page_html, flags=re.S)

    def tag(m):
        t = m.group(0)
        for kind, target in (('alt', 'alt'), ('aria', 'aria-label')):
            km = re.search(r'\sdata-i18n-%s="([^"]+)"' % kind, t)
            if not km:
                continue
            key = km.group(1)
            used.add(key)
            if key not in i18n:
                problems.append(f'{file}: data-i18n-{kind}="{key}" has no entry in assets/js/i18n.js')
                continue
            value = attr(i18n[key]['fr'])
            if re.search(r'\s%s="[^"]*"' % target, t):
                t = re.sub(r'(\s%s=")[^"]*(")' % target, lambda mm: mm.group(1) + value + mm.group(2), t, count=1)
            else:
                t = t[:km.start()] + f' {target}="{value}"' + t[km.start():]
        return t
    page_html = re.sub(r'<[a-zA-Z][^>]*\sdata-i18n-(?:alt|aria)="[^"]+"[^>]*>', tag, page_html)
    return page_html, used


def check_links(page_html, file):
    base = os.path.dirname(os.path.join(ROOT, file))
    for ref in re.findall(r'\s(?:href|src)="([^"#?]+)', page_html):
        if re.match(r'^(https?:|mailto:|tel:|data:)', ref):
            continue
        target = os.path.join(ROOT, ref.lstrip('/')) if ref.startswith('/') else os.path.normpath(os.path.join(base, ref))
        if not os.path.exists(target):
            problems.append(f'{file}: link to a missing file: {ref}')


def main():
    config = json.loads(read(os.path.join(TOOLS, 'pages.json')))
    i18n = load_i18n()
    partials = {n: read(os.path.join(TOOLS, 'partials', n + '.html')) for n in ('head', 'header', 'footer', 'scripts')}
    versions = {'v_css': version('assets/css/site.css'), 'v_site': version('assets/js/site.js'), 'v_i18n': version('assets/js/i18n.js')}
    logo = image_size(os.path.join(ROOT, 'assets/images/robotplus-logo.png'))
    francemap = image_size(os.path.join(ROOT, 'assets/images/france-contour.png'))
    all_used = set()
    changed = 0
    for page in config['pages']:
        file = page['file']
        path = os.path.join(ROOT, file)
        if not os.path.exists(path):
            problems.append(f'{file}: listed in tools/pages.json but the file does not exist')
            continue
        prefix = page.get('root', '../' * file.count('/'))
        home = prefix + 'index.html' if page['id'] != 'home' else ''
        title_key = f'page.{page["id"]}.title'
        if title_key not in i18n:
            problems.append(f'{file}: no "{title_key}" entry in assets/js/i18n.js (page title)')
            title_fr = 'ROBOT+ Automatisme'
        else:
            title_fr = plain(i18n[title_key]['fr'])
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
        original = read(path)
        out = original
        for name, tpl in partials.items():
            out = replace_block(out, name, fill(tpl, values), file)
        out = re.sub(r'(<body\b[^>]*\sdata-root=")[^"]*(")', lambda m: m.group(1) + prefix + m.group(2), out, count=1)
        if page.get('gallery'):
            g = re.compile(r'(<!-- gallery:start -->)(.*?)(<!-- gallery:end -->)', re.S)
            if g.search(out):
                out = g.sub(lambda m: m.group(1) + '\n' + gallery_html(page, prefix, title_fr).strip('\n') + '\n' + m.group(3), out, count=1)
            else:
                problems.append(f'{file}: has a gallery folder but no <!-- gallery:start --> marker')
        out, used = sync_texts(out, i18n, file)
        all_used |= used
        check_links(out, file)
        if out != original:
            changed += 1
            if not CHECK_ONLY:
                with open(path, 'w', encoding='utf-8') as fh:
                    fh.write(out)
    all_used |= {k for k in i18n if k.startswith('gallery.')}
    for key in sorted(all_used):
        entry = i18n.get(key)
        if not entry:
            continue
        missing = [l for l in LANGS if l != 'fr' and not entry.get(l)]
        if missing and entry.get('fr'):
            problems.append(f'translation missing for "{key}": {", ".join(missing)}')
    unused = sorted(k for k in i18n if k not in all_used)
    print(f'{len(config["pages"])} pages checked, {changed} {"would change" if CHECK_ONLY else "updated"}.')
    if unused:
        print('Keys in i18n.js not used by any page (can be deleted):', ', '.join(unused))
    for p in problems:
        print('  !', p)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
