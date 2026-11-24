#!/usr/bin/env python3
"""Texts of the brochures in the 7 languages of the site (fr en it de es pt ro).

The French texts are written in content/*.json (one file per brochure). Every other language is a translation of
those texts, found in this order:

  1. translations/<lang>.json   {"<French text, exactly as in content/*.json>": "<translation>"}
     (the texts that are specific to the brochures; a line break in a title is written "|")
  2. the translation the website already has for the very same French text (assets/js/i18n.js), so that the
     brochures and the pages use the same words
  3. nothing found: the build stops and lists what is missing.

Never written in a translation file, always read from the website (assets/js/i18n.js):
  - the title of each brochure and the list of solutions: the titles of "Nos solutions" on the home page,
  - the eyebrow, the country and the legal line.

Run it alone to get a report of what is missing / not used any more, per language:

    python3 -I tools/brochures/localize.py
    python3 -I tools/brochures/localize.py de ro
"""
import copy, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
LANGS = ['fr', 'en', 'it', 'de', 'es', 'pt', 'ro']

I18N_DICT = re.compile(r'window\.RP_I18N\s*=\s*(\{.*\})\s*;?\s*$', re.S)

# Fixed texts of the brochures (flap, back cover, footer of the A4, labels). Translated like the content texts.
UI_FR = {
    'flap.statement': 'Une solution **sur mesure** pour chaque projet',
    'flap.text': 'Des machines standards aux systèmes les plus complexes, nous concevons des solutions adaptées à vos contraintes.',
    'solutions': 'Nos solutions',
    'flap.since': '**Depuis 1996**, ROBOTPLUS conçoit et intègre des solutions d’automatisation adaptées à vos besoins.',
    'back.title': 'Parlons de|votre projet',
    'back.text': 'Notre expertise en robotique, en vision et en machines spéciales nous permet d’accompagner vos projets, de l’étude à la mise en service, sur les secteurs les plus exigeants.',
    'back.qr': 'Scannez ce code pour retrouver cette page, nos réalisations et nos documents sur notre site.',
    'a4.qr': 'Scannez pour retrouver cette page sur notre site.',
    'doc.a4': 'Brochure A4',
    'doc.pliable': 'Brochure pliable',
}


class Missing(Exception):
    def __init__(self, lang, texts, problems=()):
        self.lang, self.texts, self.problems = lang, list(texts), list(problems)
        super().__init__(f'{lang}: {len(self.texts)} text(s) without translation, {len(self.problems)} problem(s)')


def _from_html(s):
    """Text of an i18n.js value as the brochures write it: <strong> -> **, <br> -> space, no other tag."""
    s = re.sub(r'<br\s*/?>', ' ', s)
    s = re.sub(r'</?(?:strong|b)>', '**', s)
    s = re.sub(r'<[^>]+>', '', s)
    return html.unescape(s)


def _key(s):
    """Key used to compare two French texts."""
    s = s.replace(' ', ' ').replace(' ', ' ').replace("'", '’')
    return re.sub(r'\s+', ' ', s).strip()


class Site:
    """What the brochures read from the website."""

    def __init__(self, root=ROOT):
        text = open(os.path.join(root, 'assets', 'js', 'i18n.js'), encoding='utf-8').read()
        self.D = json.loads(I18N_DICT.search(text).group(1))
        home = open(os.path.join(root, 'index.html'), encoding='utf-8').read()
        self.slugs = []                     # the solutions of the home page, in the order of the page
        for m in re.finditer(r'data-i18n="card\.([a-z0-9-]+)\.title"', home):
            if m.group(1) not in self.slugs:
                self.slugs.append(m.group(1))
        self.by_fr = {}
        for k, v in self.D.items():
            self.by_fr.setdefault(_key(_from_html(v['fr'])), []).append(k)

    def text(self, key, lang):
        return _from_html(self.D[key][lang])

    def title(self, slug, lang):
        return _key(self.text(f'card.{slug}.title', lang))

    def solutions(self, lang):
        return [self.title(s, lang) for s in self.slugs]

    def ui(self, lang):
        keep = [x for x in self.text('footer.company', lang).split(' · ') if x.startswith(('ROBOTPLUS', 'SIREN', 'RCS', 'NAF'))]
        return {'eyebrow': self.text('common.eyebrow', lang),
                'country': self.text('footer.map_alt', lang).split(' — ')[0],
                'legal': ' · '.join(keep)}


class Texts:
    def __init__(self, site=None, tm_dir=None):
        self.site = site or Site()
        self.tm_dir = tm_dir or os.path.join(HERE, 'translations')
        self._tm = {}
        self.used = {}          # lang -> set of the translation file keys that were used

    def tm(self, lang):
        if lang not in self._tm:
            p = os.path.join(self.tm_dir, lang + '.json')
            self._tm[lang] = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
            self._tm[lang].pop('_comment', None)
        return self._tm[lang]

    def translate(self, s, lang, tm_only=False):
        """Translation of a French text, or KeyError."""
        if lang == 'fr':
            return s
        tm = self.tm(lang)
        if s in tm:
            self.used.setdefault(lang, set()).add(s)
            return tm[s]
        if not tm_only:
            keys = self.site.by_fr.get(_key(s), [])
            found = {self.site.text(k, lang) for k in keys}
            if len(found) == 1:
                return found.pop()
        raise KeyError(s)

    # --- ui
    def ui(self, lang):
        out = dict(self.site.ui(lang))
        for k, fr in UI_FR.items():
            out[k] = self.translate(fr, lang, tm_only=('|' in fr))
        return out

    def ui_missing(self, lang):
        miss = []
        for fr in UI_FR.values():
            try:
                self.translate(fr, lang, tm_only=('|' in fr))
            except KeyError:
                miss.append(fr)
        return miss

    # --- content
    def localize(self, c, lang):
        """Copy of the content of one brochure with all its texts in `lang`. Raises Missing."""
        c = copy.deepcopy(c)
        miss, problems = [], []

        def tr(s):
            try:
                return self.translate(s, lang)
            except KeyError:
                miss.append(s)
                return s

        def tr_lines(lines):
            key = '|'.join(lines)
            try:
                return self.translate(key, lang, tm_only=('|' in key)).split('|')
            except KeyError:
                miss.append(key)
                return lines

        def item(i):
            if isinstance(i, str):
                return tr(i)
            i = dict(i)
            for f in ('title', 'text'):
                if f in i:
                    i[f] = tr(i[f])
            return i

        def block(b):
            if 'text' in b: b['text'] = tr(b['text'])
            if 'lines' in b: b['lines'] = tr_lines(b['lines'])
            if isinstance(b.get('title'), str): b['title'] = tr(b['title'])
            if 'items' in b: b['items'] = [item(i) for i in b['items']]
            for fmt in ('tri', 'a4'):
                if isinstance(b.get(fmt), dict):
                    block(b[fmt])

        c['title'] = tr_lines(c['title'])
        c['subtitle'] = tr(c['subtitle'])
        for b in c['blocks'].values():
            block(b)
        titles = [('title', c['title'])]
        for i, pg in enumerate(c.get('a4', {}).get('pages', [])):
            if pg.get('slim_title'):
                pg['slim_title'] = tr_lines(pg['slim_title'])
                titles.append((f'a4 page {i + 1} slim_title', pg['slim_title']))
        # the title of a brochure is the title of its card on the home page ("Nos solutions"), in every language
        card = self.site.title(c['base'], lang)
        for where, lines in titles:
            if _key(' '.join(lines)) != card:
                problems.append(f'{where} is "{" ".join(lines)}" but the home page says "{card}"')
        for b in c['blocks'].values():
            if b.get('t') == 'title' and _key(' '.join(b['lines'])) != card:
                problems.append(f'title block is "{" ".join(b["lines"])}" but the home page says "{card}"')
        c['title_plain'] = card
        c['highlight'] = [card]
        if miss or problems:
            raise Missing(lang, miss, problems)
        return c


def strings(c):
    """All the French texts of a content file, in reading order (what has to be translated)."""
    out = []

    def add(s):
        if s not in out:
            out.append(s)

    def item(i):
        if isinstance(i, str):
            add(i)
        else:
            for f in ('title', 'text'):
                if f in i:
                    add(i[f])

    def block(b):
        if 'text' in b: add(b['text'])
        if 'lines' in b: add('|'.join(b['lines']))
        if isinstance(b.get('title'), str): add(b['title'])
        for i in b.get('items', []): item(i)
        for fmt in ('tri', 'a4'):
            if isinstance(b.get(fmt), dict):
                block(b[fmt])

    add('|'.join(c['title']))
    add(c['subtitle'])
    for b in c['blocks'].values():
        block(b)
    for pg in c.get('a4', {}).get('pages', []):
        if pg.get('slim_title'):
            add('|'.join(pg['slim_title']))
    return out


def load_contents(content_dir=None):
    d = content_dir or os.path.join(HERE, 'content')
    return {f[:-5]: json.load(open(os.path.join(d, f), encoding='utf-8')) for f in sorted(os.listdir(d)) if f.endswith('.json')}


def report(langs, content_dir=None):
    texts = Texts()
    contents = load_contents(content_dir)
    all_fr = []
    for c in contents.values():
        for s in strings(c):
            if s not in all_fr:
                all_fr.append(s)
    for s in UI_FR.values():
        if s not in all_fr:
            all_fr.append(s)
    ok = True
    for lang in langs:
        if lang == 'fr':
            continue
        miss, from_site, from_tm = [], 0, 0
        for s in all_fr:
            if s in texts.tm(lang):
                from_tm += 1
                continue
            try:
                texts.translate(s, lang, tm_only=('|' in s))
                from_site += 1
            except KeyError:
                miss.append(s)
        unused = [k for k in texts.tm(lang) if k not in all_fr]
        bold = [k for k, v in texts.tm(lang).items() if k.count('**') != v.count('**') or v.count('|') > k.count('|')]
        print(f'{lang}: {len(all_fr)} texts: {from_tm} from translations/{lang}.json, {from_site} from the website, {len(miss)} missing, '
              f'{len(unused)} unused, {len(bold)} with different **bold** / line-break marks')
        for s in miss:
            print('   MISSING', json.dumps(s, ensure_ascii=False))
        for s in unused:
            print('   UNUSED ', json.dumps(s, ensure_ascii=False))
        for s in bold:
            print('   MARKS  ', json.dumps(s, ensure_ascii=False))
        for name, c in contents.items():
            try:
                texts.localize(c, lang)
            except Missing as e:
                for p in e.problems:
                    print(f'   TITLE  {name}: {p}')
                    ok = False
        ok = ok and not miss
    return ok


if __name__ == '__main__':
    langs = sys.argv[1:] or LANGS[1:]
    sys.exit(0 if report(langs) else 1)
