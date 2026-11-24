"""ROBOTPLUS brochures: builds, from one content file per brochure (content/*.json) and one language, two PDFs in the
style of the site:

  brochure-<base>-pliable-<lang>.pdf   A4 landscape, 2 pages (outside / inside), folded in 3 panels
  brochure-<base>-a4-<lang>.pdf        A4 portrait, 1 or 2 pages

<base> is the name of the page of the website (solutions/<base>.html), <lang> one of fr en it de es pt ro.
The French texts are in content/*.json, the other languages in translations/<lang>.json (see localize.py).

Usage (see README.md in this folder):
    python3 -I tools/brochures/make_brochures.py --originals "/path/to/the/folder/that/contains/Photos site"
    python3 -I tools/brochures/make_brochures.py --originals ... robotique-industrielle --formats a4 --lang fr,de

The PDFs are written to assets/brochures/ (change it with --out). The photos are taken at full resolution, without
watermark, from the folder given by --originals: the "Photos site/..." files listed in tools/photo-sources.csv.
Needs: Python 3, Pillow, segno (QR codes) and Playwright with Chromium. pyphen is optional: it hyphenates the long
words of the translations (German...).
"""
import argparse, csv, hashlib, html, io, json, math, os, re, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)                      # python3 -I does not add it

from PIL import Image, ImageCms, ImageOps
import segno
import localize
try:
    import pyphen
except ImportError:                           # optional
    pyphen = None

DPI = 220            # resolution of the photos placed in the brochures
JPEG_Q = 82
# The yellow slash is a parallelogram skewed by 18 degrees. Skewed around its centre, a slash of height h leans out by
# tan(18)*h/2 on each side: its top end moves to the right and its bottom end to the left. The text next to a slash must
# therefore start after (width of the slash + that overhang + a gap), not just after its width.
TAN18 = math.tan(math.radians(18))
COVER_TEXT_LEFT = 12              # mm: the title of a cover starts there, whatever the height of its slash
A4_TEXT_LEFT = 9.5
SLASH_GAP = 2.2                  # mm between the top end of a slash and the text that follows it (checked: at least 1.5)


def slash_fit(text_left, width, height, room):
    """A slash `width` x `height` mm in front of a text that starts `text_left` mm after the left edge of its block.
    The height is reduced if its lower end would go more than `room` mm to the left of the block.
    Returns (height, left of the slash box), in mm."""
    hmax = (text_left - SLASH_GAP - width + room) / TAN18
    height = min(height, hmax)
    over = TAN18 * height / 2
    return round(height, 2), round(text_left - SLASH_GAP - width - over, 2)


# The QR codes point to the page itself on GitHub Pages: <SITE_URL><page>#<language>. www.robotplus.fr is only printed (and
# linked) as the address of the company, because it redirects to the home page of the site, not to the page of the brochure.
SITE_URL = 'https://robotplus-automatisme.github.io/'

COMPANY = {
    'address': ['ZI des Lèchères', '369 rue des Abeilles', '74460 Marnaz'],     # + the country, in the language of the brochure
    'phone': '+33 4 50 96 38 28',
    'phone_href': 'tel:+33450963828',
    'email': 'robotplus@robotplus.fr',
    'web': 'www.robotplus.fr',                 # printed on the brochures
    'web_href': 'https://www.robotplus.fr',    # where it leads when it is clicked in the PDF
}
# The legal line, the country and the names of the solutions come from the website, per language (localize.py).

BUILTIN = {'solutions': {'t': 'solutions'}, 'grow': {'t': 'grow'}, 'gap': {'t': 'gap'}}

# ----------------------------------------------------------------------------- text helpers
NBSP, NNBSP = ' ', ' '


def fr_typo(s):
    """French typography: no line break before : ; ! ? » or after «."""
    s = re.sub(r' ([:;!?»])', NNBSP + r'\1', s)
    s = s.replace(NNBSP + ':', NBSP + ':')
    s = re.sub(r'(«) ', r'\1' + NBSP, s)
    s = re.sub(r'(\d) (\d{3})\b', r'\1' + NNBSP + r'\2', s)       # 15 000
    s = re.sub(r'(\d) (µm|mm|kg|€|%)', r'\1' + NNBSP + r'\2', s)
    s = s.replace('± ', '±' + NNBSP)
    return s


HYPH_LANG = {'en': 'en_US', 'it': 'it_IT', 'de': 'de_DE', 'es': 'es', 'pt': 'pt_PT', 'ro': 'ro_RO'}
_hyph = {}


def typo(s, lang):
    """Typography of a language: the French rules for French; for the others only the non-breaking spaces inside
    numbers and before units."""
    if lang == 'fr':
        return fr_typo(s)
    s = re.sub(r'(\d) (\d{3})\b', r'\1' + NNBSP + r'\2', s)
    s = re.sub(r'(\d) (µm|mm|kg|€|%)', r'\1' + NNBSP + r'\2', s)
    return s.replace('± ', '±' + NNBSP)


def hyphenate(s, lang):
    """Soft hyphens in the long words: the browser that prints the PDF does not hyphenate by itself."""
    if lang == 'fr' or pyphen is None:
        return s
    d = _hyph.get(lang)
    if d is None:
        d = _hyph[lang] = pyphen.Pyphen(lang=HYPH_LANG[lang], left=3, right=3)
    return re.sub(r'[^\W\d_]{11,}', lambda m: m.group(0) if m.group(0).isupper() else d.inserted(m.group(0), '\u00ad'), s)


def md(s, lang='fr', hy=True):
    """Escape, then **bold** -> <strong>; apply the typography of the language."""
    s = typo(s, lang)
    s = html.escape(hyphenate(s, lang) if hy else s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    if lang != 'fr':
        return s
    return re.sub(r'\b([A-Za-zÀ-ÿ]+-(?:nous|vous|en|y|moi|lui)\b)', r'<span style="white-space:nowrap">\1</span>', s)


def plain(s, lang='fr', hy=False):
    s = typo(s, lang)
    return html.escape(hyphenate(s, lang) if hy else s, quote=False)


# ----------------------------------------------------------------------------- photos
class Photos:
    def __init__(self, originals, sources_csv, cache):
        self.originals, self.cache = originals, cache
        os.makedirs(cache, exist_ok=True)
        self.map = {}
        with open(sources_csv, newline='', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                self.map[r['web_file'].replace('assets/photos/', '', 1)] = r['original_file_in_old_repo']
        self._loaded = {}

    def _load(self, key):
        if key in self._loaded:
            return self._loaded[key]
        if key not in self.map:
            sys.exit(f'photo "{key}" is not listed in photo-sources.csv')
        path = os.path.join(self.originals, self.map[key])
        if not os.path.exists(path):
            sys.exit(f'original photo missing: {path}')
        im = Image.open(path)
        icc = im.info.get('icc_profile')
        im = ImageOps.exif_transpose(im)
        if icc:
            try:
                src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
                if 'srgb' not in ImageCms.getProfileDescription(src).lower():
                    im = ImageCms.profileToProfile(im.convert('RGB'), src, ImageCms.createProfile('sRGB'), outputMode='RGB')
            except Exception:
                pass
        im = im.convert('RGB')
        self._loaded = {key: im}      # keep a single image in memory
        return im

    def get(self, key, w_mm, h_mm=None, focus=(0.5, 0.5), zoom=1.0, crop=None):
        """Crop to the box ratio around `focus`, resize for DPI, save, return the file path.
        h_mm=None keeps the ratio of the photo. `zoom` > 1 crops closer."""
        tag = json.dumps([key, w_mm, h_mm, list(focus), zoom, DPI, JPEG_Q, crop])
        out = os.path.join(self.cache, hashlib.md5(tag.encode()).hexdigest()[:16] + '.jpg')
        if not os.path.exists(out):
            im = self._load(key)
            if crop:
                W0, H0 = im.size
                im = im.crop((round(crop[0] * W0), round(crop[1] * H0), round(crop[2] * W0), round(crop[3] * H0)))
            W, H = im.size
            ratio = (w_mm / h_mm) if h_mm else W / H
            cw, ch = (W, W / ratio) if W / H < ratio else (H * ratio, H)
            cw, ch = cw / zoom, ch / zoom
            cx = min(max(focus[0] * W, cw / 2), W - cw / 2)
            cy = min(max(focus[1] * H, ch / 2), H - ch / 2)
            box = (round(cx - cw / 2), round(cy - ch / 2), round(cx + cw / 2), round(cy + ch / 2))
            im = im.crop(box)
            tw = round(w_mm / 25.4 * DPI)
            if im.width > tw:
                im = im.resize((tw, round(tw * im.height / im.width)), Image.LANCZOS)
            im.save(out + '.tmp', 'JPEG', quality=JPEG_Q, optimize=True)
            os.replace(out + '.tmp', out)
        return out


# ----------------------------------------------------------------------------- css
CSS = r'''
:root{--yellow:#ffea00;--dark:#172127;--dark2:#111a1f;--ink:#111820;--text:#2b353b;--paper:#f4f5f4;--muted:#586166;--line:#dfe3e5;
  --head:'Barlow Condensed','Arial Narrow',Arial,sans-serif;--body:Inter,Arial,sans-serif}
*{box-sizing:border-box}
a{color:inherit;text-decoration:none}
html,body{margin:0;padding:0;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-family:var(--body);color:var(--ink);font-size:8.5pt;line-height:1.5;font-kerning:normal;text-rendering:geometricPrecision;overflow-wrap:break-word}
.page{position:relative;overflow:hidden;break-after:page;page-break-after:always}
.page:last-child{break-after:auto;page-break-after:auto}
.land{width:297mm;height:210mm}.port{width:210mm;height:297mm}
.panel{position:absolute;top:0;height:210mm;overflow:hidden;display:flex;flex-direction:column;padding:11mm 9mm 9mm}
.panel>*{flex:none}
.dark{background:var(--dark);color:#fff}
.paper{background:var(--paper)}
img{display:block}
p{margin:0;color:var(--text);font-size:var(--fs,8.5pt);line-height:1.5}
/* no line that is only one short word: paragraphs avoid it, headings are balanced */
p,li,.lead,.quote,.cta .c,.legal{text-wrap:pretty}
.statement,.cta .t,h3,h4,h5,h6,.steps div{text-wrap:balance}
strong{font-weight:700;color:var(--ink)}
.dark p,.dark strong{color:#e6eaec}.dark strong{color:#fff}
.slash{display:inline-block;width:2.3mm;height:6.4mm;background:var(--yellow);transform:skew(-18deg);flex:none}

/* headings */
.title{font-family:var(--head);font-weight:800;font-size:var(--ts,30pt);line-height:.95;margin:0;color:var(--ink);letter-spacing:-.005em;white-space:nowrap}
.titlerow{display:flex;gap:calc(var(--sh,15mm)*.1625 + 2.2mm);align-items:flex-start}   /* .1625 = tan(18deg)/2: overhang of the slash */
.titlerow .slash{width:2.6mm;height:var(--sh,15mm);margin-top:1mm}
.lead{font-weight:700;font-size:var(--lfs,10pt);line-height:1.38;color:var(--ink)}
.dark .lead{color:#fff}
h3{font-family:var(--head);font-weight:700;font-size:15pt;line-height:1.05;margin:0;color:var(--ink);display:flex;align-items:center;gap:2.4mm}
h3:before{content:"";width:1.8mm;height:4.2mm;background:var(--yellow);transform:skew(-18deg);flex:none}
h4{font-family:var(--head);font-weight:700;font-size:12pt;letter-spacing:.02em;text-transform:uppercase;margin:0;color:var(--muted)}

/* rows: white lines with a yellow bar, like the lists of the website */
ul.rows{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:1.5mm}
ul.rows li{background:#fff;border-left:1.1mm solid var(--yellow);padding:1.5mm 2.5mm 1.6mm;font-size:var(--rfs,8pt);line-height:1.36;color:var(--text)}
ul.rows li strong{color:var(--ink)}
ul.rows.plain li{background:transparent;border-left:0;padding:0 0 0 3.6mm;position:relative}
ul.rows.plain li:before{content:"";position:absolute;left:0;top:1.3mm;width:1.5mm;height:1.5mm;background:var(--yellow);transform:skew(-18deg)}

/* applications: dark box like the website */
.apps{background:var(--dark);color:#fff;padding:4.6mm 4.8mm 4.2mm}
.apps h5{font-family:var(--head);font-weight:700;font-size:15pt;margin:0;line-height:1;color:#fff}
.apps h5:after{content:"";display:block;width:8mm;height:.9mm;background:var(--yellow);margin-top:1.8mm}
.apps ul{list-style:none;margin:3mm 0 0;padding:0}
.apps li{position:relative;padding-left:4mm;font-size:var(--afs,8pt);line-height:1.36;margin:0 0 1.35mm;color:#e6eaec}
.apps li:before{content:"";position:absolute;left:0;top:1.25mm;width:1.4mm;height:1.4mm;background:var(--yellow);transform:skew(-18deg)}
.apps li:last-child{margin-bottom:0}

/* closing statement */
.quote{border-left:1.2mm solid var(--yellow);padding:.3mm 0 .3mm 3.2mm;font-weight:700;font-size:var(--qfs,9pt);line-height:1.4;color:var(--ink)}
.dark .quote{color:#fff}
.cta{background:var(--yellow);color:var(--ink);padding:4mm 4.6mm}
.cta .t{font-family:var(--head);font-weight:800;font-size:15pt;line-height:1.05;color:var(--ink)}
.cta .c{font-size:8pt;line-height:1.5;margin-top:1.6mm;color:var(--ink);font-weight:600}
.cta .c b{font-weight:800}

/* photos */
figure{margin:0;overflow:hidden;background:#cfd5d8;position:relative}
figure img{width:100%;height:100%;object-fit:cover}
.grid{display:grid;gap:1.8mm}
.grid.c2{grid-template-columns:1fr 1fr}.grid.c3{grid-template-columns:1fr 1fr 1fr}.grid.c4{grid-template-columns:1fr 1fr 1fr 1fr}

/* product cards (family brochure) */
.cards{display:flex;flex-direction:column;gap:2.6mm}
.card{display:flex;gap:3mm;background:#fff;border-top:.9mm solid var(--yellow);padding:0}
.card figure{width:var(--cw,34mm);flex:none;align-self:stretch}
.card .tx{padding:2.2mm 2.6mm 2.4mm 0;display:flex;flex-direction:column;gap:1mm}
.card .tx h6{font-family:var(--head);font-weight:800;font-size:13.5pt;line-height:1;margin:0;color:var(--ink)}
.card .tx p{font-size:var(--cfs,7.9pt);line-height:1.38}

.fill{flex:1 1 0 !important;min-height:26mm}
.cards.fill{flex:1 1 auto !important;min-height:0}
.cards.fill .card{flex:1 1 auto}
.grid.fill{grid-auto-rows:1fr;min-height:40mm}
.grid.fill figure{height:100%}
.sol.light li{color:#6a767c;border-bottom:.25mm solid var(--line);font-size:10.5pt;padding:1.2mm 0 1.2mm 5.2mm}
.sol.light li:before{background:#b9c3c8}
.sol.light li.on{color:var(--ink)}.sol.light li.on:before{background:var(--yellow)}
.port .sol.light li{font-size:10pt;padding:.8mm 0 .8mm 5.2mm}
.port .fill{min-height:22mm}
/* steps (machines spéciales) */
.steps{display:flex;gap:1mm}
.steps div{flex:1;background:var(--dark);color:#fff;font-family:var(--head);font-weight:700;font-size:10.5pt;line-height:1.05;padding:2.4mm 1.6mm 2.4mm 3.4mm;position:relative;clip-path:polygon(0 0,calc(100% - 2.4mm) 0,100% 50%,calc(100% - 2.4mm) 100%,0 100%)}
.steps div b{display:block;color:var(--yellow);font-size:7.5pt;font-family:var(--body);font-weight:800;letter-spacing:.08em;margin-bottom:.6mm}

/* ------------------------------------------------ cover / flap / back (dark panels) */
.logo{width:var(--lw,56mm);height:auto}
.eyebrow{font-size:6.6pt;letter-spacing:.2em;font-weight:700;color:#9fabb1;text-transform:uppercase}
.cover .tb{position:relative;margin-top:var(--tbm,17mm);padding-left:var(--tl)}
.cover .tb .slash{position:absolute;left:var(--sx);top:9mm;width:3.2mm;height:var(--sh)}
.cover h1{font-family:var(--head);font-weight:800;font-size:var(--cts,40pt);line-height:.92;margin:3mm 0 0;color:#fff;white-space:nowrap;letter-spacing:-.01em;display:inline-block}
.fit{display:inline-block}
.cover .sub{font-size:9pt;line-height:1.4;color:#dfe3e5;margin-top:4mm;max-width:76mm}
.cover .hero{position:absolute;left:0;right:0;bottom:0;height:var(--hh,100mm);border-top:1.4mm solid var(--yellow)}
.statement{font-family:var(--head);font-weight:800;font-size:27pt;line-height:.96;color:#fff;margin:0;letter-spacing:-.005em}
.statement em{font-style:normal;color:var(--yellow)}
.sol{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:0}
.sol li{font-family:var(--head);font-weight:600;font-size:13pt;line-height:1;padding:2.5mm 0 2.5mm 5.2mm;border-bottom:.25mm solid #2e3b42;color:#b9c3c8;position:relative}
.sol li:before{content:"";position:absolute;left:.4mm;top:50%;margin-top:-1.5mm;width:1.2mm;height:3mm;background:#55646c;transform:skew(-18deg)}
.sol li.on{color:#fff}.sol li.on:before{background:var(--yellow)}
.contact{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:3.2mm}
.contact li{display:flex;gap:3.2mm;align-items:flex-start;font-size:9pt;line-height:1.4;color:#fff}
.contact svg{width:5mm;height:5mm;flex:none;margin-top:.2mm;fill:none;stroke:var(--yellow);stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.contact b{font-weight:700}
.qr{background:#fff;padding:1.8mm;width:25mm;height:25mm;flex:none}.qr svg{width:100%;height:100%;display:block}
.fmap{position:relative;width:27mm;height:21mm;flex:none}.fmap img{width:100%;opacity:.28}
.fmap .pin{position:absolute;width:3.6mm;height:5mm;left:calc(83.5% - 1.8mm);top:calc(72% - 4.6mm);fill:var(--yellow)}
.legal{font-size:5.9pt;line-height:1.45;color:#7e8b92}
.dark .legal{color:#7e8b92}
'''

# ----------------------------------------------------------------------------- icons
ICON = {
    'pin': '<svg viewBox="0 0 24 24"><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    'phone': '<svg viewBox="0 0 24 24"><path d="M7 4h3l2 5-2 2c1 2 2 3 4 4l2-2 4 2v3c0 1-1 2-2 2C10 20 4 14 4 6c0-1 1-2 3-2Z"/></svg>',
    'mail': '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/></svg>',
    'web': '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/></svg>',
}
PIN_SVG = '<svg class="pin" viewBox="0 0 24 24"><path d="M12 21s7-7.1 7-12A7 7 0 1 0 5 9c0 4.9 7 12 7 12Z"/></svg>'


def qr_svg(url):
    q = segno.make(url, error='m', micro=False)
    buf = io.BytesIO()
    q.save(buf, kind='svg', xmldecl=False, svgns=True, nl=False, border=0, dark='#111820', light=None, scale=1, omitsize=True)
    return buf.getvalue().decode()


# ----------------------------------------------------------------------------- builder
class Builder:
    def __init__(self, photos, assets, lang='fr', ui=None, solutions=None):
        self.photos, self.assets = photos, assets
        self.lang, self.ui, self.solutions = lang, ui or {}, solutions or []
        self.fills = {}      # measured heights (mm) of the photos that fill the free space, from the previous pass
        self.ctx = ''        # name of the panel being rendered

    # --- texts
    def md(self, s, hy=True):
        return md(s, self.lang, hy)

    def plain(self, s, hy=False):
        return plain(s, self.lang, hy)

    def em(self, s):
        """**x** -> <em>x</em> (the yellow words of the statements)."""
        return re.sub(r'\*\*(.+?)\*\*', lambda m: '<em>' + m.group(1).replace(' ', '\u00a0') + '</em>', html.escape(typo(s, self.lang), quote=False))

    def address(self):
        return COMPANY['address'] + [self.ui['country']]

    def url(self, c):
        return SITE_URL + c['page'] + '#' + self.lang

    # --- elementary pieces
    def img(self, key, w, h=None, focus=(0.5, 0.5), zoom=1.0, alt='', crop=None):
        return f'<img src="file://{self.photos.get(key, w, h, tuple(focus), zoom, tuple(crop) if crop else None)}" alt="{html.escape(alt)}">'

    def fig(self, spec, w, h, fmt, fid=None):
        p = dict(spec); p.update(spec.get(fmt, {}))
        hh = p.get('h', h)
        extra = ''
        if fid:                      # a photo that takes all the free space of its panel
            hh = self.fills.get(fid, hh)
            extra = f' class="fill" data-fid="{fid}"'
        return f'<figure{extra} style="width:{w}mm;height:{hh}mm">{self.img(p["img"], w, hh, p.get("focus", (.5, .5)), p.get("zoom", 1.0), crop=p.get("crop"))}</figure>'

    def block(self, b, width, fmt):
        """Render one content block for a column of `width` mm."""
        t = b['t']
        o = dict(b); o.update(b.get(fmt, {}))
        style = ''
        if 'fs' in o: style = f' style="--fs:{o["fs"]}pt"'
        if t == 'title':
            lines = '<br>'.join(self.plain(x) for x in o['lines'])
            st = f' style="--ts:{o["pt"]}pt;--sh:{o.get("sh", 15)}mm"' if 'pt' in o else ''
            return f'<div class="titlerow"{st}><span class="slash"></span><h2 class="title">{lines}</h2></div>'
        if t == 'lead':
            return f'<p class="lead"{style}>{self.md(o["text"])}</p>'
        if t == 'p':
            return f'<p{style}>{self.md(o["text"])}</p>'
        if t == 'h3':
            return f'<h3>{self.plain(o["text"])}</h3>'
        if t == 'rows':
            cls = ' plain' if o.get('plain') else ''
            st = f' style="--rfs:{o["fs"]}pt"' if 'fs' in o else ''
            return f'<ul class="rows{cls}"{st}>' + ''.join(f'<li>{self.md(i)}</li>' for i in o['items']) + '</ul>'
        if t == 'apps':
            st = f' style="--afs:{o["fs"]}pt"' if 'fs' in o else ''
            return f'<div class="apps"{st}><h5>{self.plain(o["title"])}</h5><ul>' + ''.join(f'<li>{self.md(i)}</li>' for i in o['items']) + '</ul></div>'
        if t == 'quote':
            st = f' style="--qfs:{o["fs"]}pt"' if 'fs' in o else ''
            return f'<div class="quote"{st}>{self.md(o["text"])}</div>'
        if t == 'photo':
            return self.fig(o, width, o.get('h', 50), fmt, fid=(f'{self.ctx}:{b.get("id", "photo")}' if o.get('fill') else None))
        if t == 'photos':
            cols = o.get('cols', 2); n = len(o['imgs'])
            cw = round((width - 1.8 * (cols - 1)) / cols, 2)
            fid = f'{self.ctx}:{b.get("id", "photos")}' if o.get('fill') else None
            rows = -(-n // cols)
            hh = o.get('h', 30)
            if fid:                  # the grid fills the free space; every row gets the same height
                hh = round((self.fills.get(fid, hh * rows + 1.8 * (rows - 1)) - 1.8 * (rows - 1)) / rows, 2)
            figs = ''.join(self.fig({'img': i['img'], 'focus': i.get('focus', (.5, .5)), 'zoom': i.get('zoom', 1), 'crop': i.get('crop')}, cw, hh, fmt) for i in o['imgs'])
            extra = f' fill" data-fid="{fid}' if fid else ''
            return f'<div class="grid c{cols}{extra}">{figs}</div>'
        if t == 'solutions':
            return f'<div><h4 style="margin-bottom:1.6mm">{self.plain(self.ui["solutions"])}</h4>' + self.solutions_list(self.on, light=True) + '</div>'
        if t == 'cards':
            cw = o.get('cw', 34)
            out = []
            for ci, c in enumerate(o['items']):
                ph = c.get('h', o.get('h', 30))
                fid = f'{self.ctx}:{b.get("id", "cards")}:{ci}'      # always measured: the figure stretches to the card height
                ph = self.fills.get(fid, ph)
                attr = f' data-fid="{fid}"'
                fig = f'<figure{attr} style="width:{cw}mm">{self.img(c["img"], cw, ph, c.get("focus", (.5, .5)), c.get("zoom", 1.0), crop=c.get("crop"))}</figure>'
                out.append(f'<div class="card" style="--cw:{cw}mm">{fig}<div class="tx"><h6>{self.plain(c["title"], hy=True)}</h6><p>{self.md(c["text"])}</p></div></div>')
            st = f' style="--cfs:{o["fs"]}pt"' if 'fs' in o else ''
            return f'<div class="cards{" fill" if o.get("fill") else ""}"{st}>' + ''.join(out) + '</div>'
        if t == 'steps':
            return '<div class="steps">' + ''.join(f'<div><b>{i + 1:02d}</b>{self.plain(s, hy=True)}</div>' for i, s in enumerate(o['items'])) + '</div>'
        if t == 'cta':
            return (f'<div class="cta"><div class="t">{self.md(o["text"])}</div><div class="c">{self.plain(COMPANY["phone"])} · {self.plain(COMPANY["email"])}</div></div>')
        if t == 'gap':
            return f'<div style="height:{o.get("h", 3)}mm"></div>'
        if t == 'grow':
            return '<div style="flex:1 1 auto"></div>'
        raise ValueError('unknown block type ' + t)

    def flow(self, ids, blocks, width, fmt, ctx=''):
        out = []
        self.ctx = ctx
        for i in ids:
            b = dict(i if isinstance(i, dict) else (blocks[i] if i in blocks else BUILTIN[i]))
            if not isinstance(i, dict):
                b['id'] = i
            out.append(self.block(b, width, fmt))
        return ''.join(out)

    # --- dark panels
    def logo(self, w):
        return f'<img class="logo" style="--lw:{w}mm" src="file://{self.assets}/logo-dark.png" alt="ROBOT+ Automatisme">'

    def contact_list(self):
        c = COMPANY
        return ('<ul class="contact">'
                f'<li>{ICON["pin"]}<span>{"<br>".join(self.plain(x) for x in self.address())}</span></li>'
                f'<li>{ICON["phone"]}<span><b>{c["phone"]}</b></span></li>'
                f'<li>{ICON["mail"]}<span>{c["email"]}</span></li>'
                f'<li>{ICON["web"]}<span><a href="{c["web_href"]}">{c["web"]}</a></span></li>'
                '</ul>')

    def solutions_list(self, on, light=False):
        return f'<ul class="sol{" light" if light else ""}">' + ''.join(f'<li class="{"on" if s in on else ""}">{self.plain(s)}</li>' for s in self.solutions) + '</ul>'

    def map_block(self):
        return (f'<div class="fmap"><img src="file://{self.assets}/france.png" alt="">{PIN_SVG}</div>')

    def cover_panel(self, c, left, width):
        title = '<br>'.join(self.plain(x) for x in c['title'])
        hero = c['cover']
        hh = c.get('tri_hero_h', 100)
        sh, sx = slash_fit(COVER_TEXT_LEFT, 3.2, c.get('slash_h', 36), room=5.5)
        return (f'<section class="panel cover dark" data-check="cover" style="left:{left}mm;width:{width}mm;--hh:{hh}mm;--cts:{c.get("cover_pt", 40)}pt;--sh:{sh}mm;--sx:{sx}mm;--tl:{COVER_TEXT_LEFT}mm">'
                f'{self.logo(56)}'
                f'<div class="tb"><span class="slash"></span><div class="eyebrow">{self.plain(self.ui["eyebrow"])}</div>'
                f'<h1 class="fit">{title}</h1><p class="sub">{self.md(c["subtitle"])}</p></div>'
                f'<figure class="hero">{self.img(hero["img"], width, hh, hero.get("focus", (.5, .5)), hero.get("zoom", 1.0), crop=hero.get("crop"))}</figure>'
                '</section>')

    def flap_panel(self, c, left, width):
        on = c.get('highlight', [])
        u = self.ui
        return (f'<section class="panel flap dark" data-check="flap" style="left:{left}mm;width:{width}mm;padding-top:14mm;gap:6.5mm">'
                '<div class="titlerow" style="--sh:23mm"><span class="slash"></span>'
                f'<h2 class="statement">{self.em(u["flap.statement"])}</h2></div>'
                f'<p style="font-size:9pt;line-height:1.5;color:#dfe3e5">{self.md(u["flap.text"])}</p>'
                f'<div style="margin-top:1mm"><h4 style="color:#9fabb1;margin-bottom:2mm">{self.plain(u["solutions"])}</h4>' + self.solutions_list(on) + '</div>'
                '<div style="flex:1 1 auto"></div>'
                f'<p style="font-size:8.6pt;line-height:1.5;color:#c9d1d5">{self.md(u["flap.since"])}</p>'
                '</section>')

    def back_panel(self, c, left, width):
        u = self.ui
        title = '<br>'.join(self.plain(x) for x in u['back.title'].split('|'))
        return (f'<section class="panel back dark" data-check="back" style="left:{left}mm;width:{width}mm;padding-top:11mm;gap:0">'
                f'{self.logo(46)}'
                f'<div class="titlerow" style="margin-top:17mm;--sh:15mm"><span class="slash"></span><h2 class="statement" style="font-size:29pt">{title}</h2></div>'
                f'<p style="margin-top:4.5mm;font-size:9pt;line-height:1.5;color:#dfe3e5">{self.md(u["back.text"])}</p>'
                f'<div style="margin-top:7mm;position:relative">{self.contact_list()}<div style="position:absolute;right:0;top:-1mm">{self.map_block()}</div></div>'
                '<div style="flex:1 1 auto"></div>'
                f'<div style="display:flex;gap:4mm;align-items:center"><div class="qr">{qr_svg(self.url(c))}</div>'
                f'<p style="font-size:7.6pt;line-height:1.45;color:#c9d1d5">{self.md(u["back.qr"])}</p></div>'
                f'<p class="legal" style="margin-top:5mm">{self.plain(u["legal"])}</p>'
                '</section>')

    # --- tri-fold
    def trifold(self, c):
        blocks = c['blocks']
        self.on = c.get('highlight', [])
        W_A, W_B, W_C = 100, 100, 97
        outside = (self.flap_panel(c, 0, 97) + self.back_panel(c, 97, 100) + self.cover_panel(c, 197, 100))
        def panel(name, left, width, ids, extra=''):
            return (f'<section class="panel paper" data-check="{name}" style="left:{left}mm;width:{width}mm;gap:{c.get("tri_gap", 3.6)}mm;{extra}">'
                    + self.flow(ids, blocks, width - 18, 'tri', ctx='tri-' + name) + '</section>')
        inside = (panel('A', 0, W_A, c['tri']['A']) + panel('B', 100, W_B, c['tri']['B']) + panel('C', 200, W_C, c['tri']['C']))
        return (f'<div class="page land">{outside}</div><div class="page land">{inside}</div>')

    # --- A4 portrait (1 page, or several when the content needs it)
    def a4(self, c):
        a = c['a4']
        self.on = c.get('highlight', [])
        pages = a.get('pages') or [{}]
        css = """
        .a4h{position:absolute;left:0;top:0;width:210mm;height:var(--hh);background:var(--dark);color:#fff;overflow:hidden}
        .a4h .logo{position:absolute;left:12mm;top:11mm;width:52mm}
        .a4h .tb{position:absolute;left:12mm;top:var(--tbt);width:97mm;padding-left:var(--tl)}
        .a4h .tb .slash{position:absolute;left:var(--sx);top:7.4mm;width:3mm;height:var(--slh)}
        .a4h h1{font-family:var(--head);font-weight:800;font-size:var(--tpt);line-height:.92;margin:2.4mm 0 0;color:#fff;white-space:nowrap;letter-spacing:-.01em}
        .a4h .sub{font-size:8.6pt;line-height:1.4;color:#dfe3e5;margin-top:3.2mm;max-width:92mm}
        .a4h .hero{position:absolute;right:0;top:0;width:var(--hw);height:var(--hh);clip-path:polygon(15mm 0,100% 0,100% 100%,0 100%)}
        .a4h .stripe{position:absolute;top:0;left:calc(210mm - var(--hw) - 1.4mm);height:var(--hh);width:17mm;background:var(--yellow);clip-path:polygon(15mm 0,17.4mm 0,2.4mm 100%,0 100%)}
        .a4h .logo{top:9mm;width:46mm}
        .a4h.slim .logo{top:8.5mm;width:42mm}
        .a4h.slim .tb{left:78mm;top:9.5mm;width:120mm}
        .a4h.slim .tb .slash{top:6.6mm;width:2.6mm}
        .a4b{position:absolute;left:12mm;right:12mm;top:var(--bt);display:grid;grid-template-columns:var(--lw) var(--rw);gap:var(--cg);--fs:var(--bfs)}
        .a4b .col{display:flex;flex-direction:column;gap:var(--gap);min-height:0;overflow:hidden;height:var(--ch)}
        .a4b .col>*{flex:none}
        .a4s{position:absolute;left:12mm;right:12mm;bottom:33mm}
        .a4f{position:absolute;left:0;right:0;bottom:0;height:27mm;background:var(--yellow);color:var(--ink)}
        .a4f .ct{position:absolute;left:12mm;top:5mm;display:flex;gap:9mm;font-size:8pt;line-height:1.42;color:var(--ink);font-weight:600}
        .a4f .ct>div{display:flex;flex-direction:column;gap:.9mm}
        .a4f .ct span{display:flex;gap:1.8mm;align-items:flex-start}
        .a4f .ct .ic{width:3.5mm;height:3.5mm;flex:none;margin-top:.45mm;fill:none;stroke:#111820;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
        .a4f .ct b{font-weight:800}
        .a4f .qr{position:absolute;right:12mm;top:2.6mm;width:21.8mm;height:21.8mm;padding:1.2mm;background:#fff}
        .a4f .q2{position:absolute;right:37mm;top:5mm;width:38mm;font-size:6.8pt;line-height:1.4;text-align:right;color:var(--ink);font-weight:600}
        .a4f .lg{position:absolute;left:12mm;bottom:2.6mm;font-size:5.4pt;color:#4a5200;line-height:1.2;font-weight:500}
        """
        out = [f'<style>{css}</style>']
        n = len(pages)
        for idx, pg in enumerate(pages):
            sp = dict(a); sp.update(pg)
            out.append(self.a4_page(c, sp, idx, n))
        return ''.join(out)

    def a4_page(self, c, a, idx, n):
        blocks = c['blocks']
        slim = a.get('head') == 'slim'
        hero = a.get('hero', c['cover'])
        title_lines = a.get('slim_title', c['title']) if slim else c['title']
        title = '<br>'.join(self.plain(x) for x in title_lines)
        url = self.url(c)
        head_h = a.get('head_h', 40 if slim else 74)
        hero_w = a.get('hero_w', 96)
        lw, rw = a.get('lw', 112), a.get('rw', 66)
        strip_h = a.get('strip_h', 28)
        has_strip = bool(a.get('strip'))
        body_top = a.get('body_top', head_h + (10 if slim else 11))
        col_h = a.get('col_h') or round(297 - 27 - 6 - ((strip_h + 6) if has_strip else 0) - 6 - body_top, 1)
        fs = a.get('fs', 9)
        left = self.flow(a['left'], blocks, lw, 'a4', ctx=f'a4{idx}-left')
        right = self.flow(a['right'], blocks, rw, 'a4', ctx=f'a4{idx}-right')
        strip = ''
        if has_strip:
            k = len(a['strip']); sw = round((186 - 2 * (k - 1)) / k, 2)
            strip = (f'<div style="display:grid;grid-template-columns:repeat({k},1fr);gap:2mm">' +
                     ''.join(f'<figure style="height:{strip_h}mm">{self.img(s_["img"], sw, strip_h, s_.get("focus", (.5, .5)), s_.get("zoom", 1), crop=s_.get("crop"))}</figure>' for s_ in a['strip']) + '</div>')
        ic = lambda k_: ICON[k_].replace('<svg', '<svg class="ic"')
        slh, slx = slash_fit(A4_TEXT_LEFT, 3, a.get('slash_h', 24), room=7)
        vars_ = (f'--hh:{head_h}mm;--hw:{hero_w}mm;--bt:{body_top}mm;--ch:{col_h}mm;--lw:{lw}mm;--rw:{rw}mm;--cg:{210 - 24 - lw - rw}mm;'
                 f'--gap:{a.get("gap", 3.2)}mm;--tbt:{a.get("tb_top", 29)}mm;--slh:{slh}mm;--sx:{slx}mm;--tl:{A4_TEXT_LEFT}mm;--tpt:{a.get("title_pt", 34)}pt;'
                 f'--bfs:{fs}pt;--rfs:{fs - .5}pt;--afs:{fs - .5}pt;--qfs:{fs + .5}pt;--lfs:{fs + 1.5}pt;--cfs:{fs - 1.1}pt')
        adr = self.address()
        addr = f'{self.plain(adr[0])}, {self.plain(adr[1])}<br>{self.plain(adr[2])} · {self.plain(adr[3])}'
        if slim:
            sl_h, sl_x = slash_fit(7, 2.6, round(len(title_lines) * a.get('slim_pt', 28) * .92 * .3528 + 3), room=4)    # as tall as the title
            head = (f'<div class="a4h slim"><img class="logo" src="file://{self.assets}/logo-dark.png" alt="ROBOT+ Automatisme">'
                    f'<div class="tb" style="--tpt:{a.get("slim_pt", 28)}pt;--tl:7mm;--slh:{sl_h}mm;--sx:{sl_x}mm"><span class="slash"></span><div class="eyebrow">{self.plain(self.ui["eyebrow"])}</div><h1 class="fit">{title}</h1></div></div>')
        else:
            head = (f'<div class="a4h"><img class="logo" src="file://{self.assets}/logo-dark.png" alt="ROBOT+ Automatisme">'
                    f'<div class="tb"><span class="slash"></span><div class="eyebrow">{self.plain(self.ui["eyebrow"])}</div><h1 class="fit">{title}</h1><p class="sub">{self.md(c["subtitle"])}</p></div>'
                    f'<figure class="hero">{self.img(hero["img"], hero_w, head_h, hero.get("focus", (.5, .5)), hero.get("zoom", 1.0), crop=hero.get("crop"))}</figure><div class="stripe"></div></div>')
        return (f'<div class="page port paper" style="{vars_}" data-check="a4page{idx}">{head}'
                f'<div class="a4b"><div class="col" data-check="a4{idx}-left" style="width:{lw}mm">{left}</div>'
                f'<div class="col" data-check="a4{idx}-right" style="width:{rw}mm">{right}</div></div>'
                f'<div class="a4s">{strip}</div>'
                f'<div class="a4f"><div class="ct"><div><span>{ic("pin")}<i style="font-style:normal">{addr}</i></span></div>'
                f'<div><span>{ic("phone")}<b>{COMPANY["phone"]}</b></span><span>{ic("mail")}{COMPANY["email"]}</span><span>{ic("web")}<a href="{COMPANY["web_href"]}">{COMPANY["web"]}</a></span></div></div>'
                f'<div class="q2">{self.md(self.ui["a4.qr"])}</div><div class="qr">{qr_svg(url)}</div>'
                f'<div class="lg">{self.plain(self.ui["legal"])}</div></div></div>')

    # --- document
    def document(self, c, fmt):
        body = self.trifold(c) if fmt == 'pliable' else self.a4(c)
        size = '297mm 210mm' if fmt == 'pliable' else '210mm 297mm'
        label = self.ui['doc.pliable' if fmt == 'pliable' else 'doc.a4']
        return (f'<!doctype html><html lang="{self.lang}"><head><meta charset="utf-8"><title>ROBOTPLUS — {self.plain(c["title_plain"])} — {label}</title>'
                f'<link rel="stylesheet" href="file://{HERE}/fonts/fonts.css"><style>@page{{size:{size};margin:0}}{CSS}</style></head><body>{body}</body></html>')


JS_FIT = '''() => {
  const rep = [];
  document.querySelectorAll('.fit, .title').forEach(el => {
    const row = el.parentElement;
    let avail;
    if (el.classList.contains('title')) {            // title of a panel: next to the yellow slash
      const sl = row.querySelector('.slash');
      avail = row.clientWidth - (sl ? sl.getBoundingClientRect().width : 0) - (parseFloat(getComputedStyle(row).columnGap) || 0);
    } else {
      const cs = getComputedStyle(row);
      avail = row.clientWidth - parseFloat(cs.paddingLeft || 0) - parseFloat(cs.paddingRight || 0) - 1;
    }
    const fs0 = parseFloat(getComputedStyle(el).fontSize);
    let fs = fs0;
    while (el.getBoundingClientRect().width > avail && fs > 22) { fs -= 0.5; el.style.fontSize = fs + 'px'; }
    rep.push({t: el.textContent.trim().replace(/\\s+/g, ' '), k: Math.round(fs / fs0 * 100) / 100, over: Math.round((el.getBoundingClientRect().width - avail) * 10) / 10});
  });
  return rep;
}'''

# A panel whose text does not fit (translations are not as long as the French everywhere): its text is reduced by steps of 2%,
# down to 80%. Returns the factor of each panel that was reduced.
JS_SHRINK = '''() => {
  const sel = 'p, li, .lead, .quote, .cta .c, h6, .steps div, .statement';
  const rep = {};
  document.querySelectorAll('[data-check]').forEach(c => {
    const over = () => (c.scrollHeight - c.clientHeight > 0.5) || (c.scrollWidth - c.clientWidth > 0.5);
    if (!over()) return;
    const els = Array.from(c.querySelectorAll(sel));
    const base = els.map(e => parseFloat(getComputedStyle(e).fontSize));
    let k = 1;
    while (over() && k > 0.8) {
      k = Math.round((k - 0.02) * 100) / 100;
      els.forEach((e, i) => { e.style.fontSize = (base[i] * k) + 'px'; });
    }
    rep[c.dataset.check] = k;
  });
  return rep;
}'''

# The soft hyphens are put in the long words so that the browser can break them; once the lines are laid out, those that are not
# at the end of a line are removed (this does not change the layout), so that the text of the PDF stays clean to copy and search.
JS_SHY = '''() => {
  const SHY = '\\u00ad';
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const todo = [];
  while (w.nextNode()) { const n = w.currentNode; if (n.nodeValue.includes(SHY)) todo.push(n); }
  const rng = document.createRange();
  // the letter after a hyphen that ends a line has two rectangles (the hyphen, then itself on the next line): take the last one
  const top = (n, a, last) => { rng.setStart(n, a); rng.setEnd(n, a + 1); const r = rng.getClientRects(); return r.length ? r[last ? r.length - 1 : 0].top : null; };
  const plan = todo.map(n => {
    const s = n.nodeValue, keep = [];
    for (let i = 0; i < s.length; i++) {
      if (s[i] !== SHY) { keep.push(true); continue; }
      const a = i > 0 ? top(n, i - 1, false) : null, b = i + 1 < s.length ? top(n, i + 1, true) : null;
      keep.push(a !== null && b !== null && b - a > 4);        // the next letter is on another line: the hyphen is used
    }
    return keep;
  });
  let kept = 0, removed = 0;
  todo.forEach((n, k) => {
    const s = n.nodeValue; let out = '';
    for (let i = 0; i < s.length; i++) { if (s[i] !== SHY) out += s[i]; else if (plan[k][i]) { out += s[i]; kept++; } else removed++; }
    n.nodeValue = out;
  });
  return {kept, removed};
}'''


JS_CHECK = '''() => {
  const out = [];
  document.querySelectorAll('[data-check]').forEach(el => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    const pb = parseFloat(cs.paddingBottom) || 0;
    let bottom = 0;
    el.querySelectorAll(':scope > *').forEach(ch => { bottom = Math.max(bottom, ch.getBoundingClientRect().bottom); });
    const inner = r.bottom - pb;
    out.push({id: el.dataset.check, over: Math.round((el.scrollHeight - el.clientHeight) * 10) / 10,
              free_mm: Math.round((inner - bottom) / 3.7795 * 10) / 10, wover: Math.round((el.scrollWidth - el.clientWidth) * 10) / 10});
  });
  return out;
}'''


# Geometry of the laid-out pages, measured in the browser before the PDF is written (all the distances are in mm):
#   slash   : a text line closer than `gap` mm to a yellow slash (the slashes are skewed: their top end leans out)
#   edge    : text closer than `margin` mm to the edge of its panel / page, or the tip of a slash too close to a fold or an edge
#   collide : two lines of text of different blocks that overlap, or a line of text over a photo, a QR code or the map
#   dpi     : the lowest resolution of the photos, as placed on the page
JS_GEOM = r"""(o) => {
  const MM = 96 / 25.4, TAN = Math.tan(18 * Math.PI / 180);
  const f1 = v => Math.round(v * 10) / 10, fmm = v => f1(v / MM);
  const res = {slash: [], edge: [], collide: [], orphans: [], dpi: null, n: {lines: 0, slashes: 0}, min: {gap: 99, side: 99, tip: 99, photo: 99, stripe: 99}};
  const box = el => { const c = el.closest('[data-check]'); return c ? c.dataset.check : 'page'; };
  const lines = [], rng = document.createRange();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const n = walker.currentNode, el = n.parentElement;
    const txt = n.nodeValue.replace(/­/g, '').trim();
    if (!txt || el.closest('style, script, title, svg')) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    let blk = el;
    while (blk.parentElement && /^inline/.test(getComputedStyle(blk).display)) blk = blk.parentElement;
    rng.selectNodeContents(n);
    for (const r of rng.getClientRects()) if (r.width > 1 && r.height > 1) lines.push({r, el, blk, txt});
  }
  const short = t => t.length > 26 ? t.slice(0, 25) + '…' : t;
  res.n.lines = lines.length;
  // 1. text close to a slash
  document.querySelectorAll('.slash').forEach(sl => {
    res.n.slashes++;
    const b = sl.getBoundingClientRect(), H = b.height, w = b.width - TAN * H, cx = (b.left + b.right) / 2;
    const R = y => cx + w / 2 + TAN * (H / 2 - (y - b.top)), L = y => cx - w / 2 + TAN * (H / 2 - (y - b.top));
    for (const t of lines) {
      const y0 = Math.max(b.top, t.r.top), y1 = Math.min(b.bottom, t.r.bottom);
      if (y1 - y0 < 1) continue;
      const sep = Math.max(Math.min(t.r.left - R(y0), t.r.left - R(y1)), Math.min(L(y0) - t.r.right, L(y1) - t.r.right)) / MM;
      if (sep < res.min.gap) res.min.gap = f1(sep);
      if (sep < o.gap) res.slash.push(`${box(sl)}: "${short(t.txt)}" is ${f1(sep)} mm from the slash (min ${o.gap})`);
    }
  });
  // 2. edges
  const room = el => el.closest('.panel') || el.closest('.page');
  lines.forEach(t => {
    const c = room(t.el), cr = c.getBoundingClientRect(), tri = c.classList.contains('panel');
    const m = tri ? o.panelMargin : o.pageMargin;
    const l = (t.r.left - cr.left) / MM, r = (cr.right - t.r.right) / MM, tp = (t.r.top - cr.top) / MM, bt = (cr.bottom - t.r.bottom) / MM;
    res.min.side = Math.min(res.min.side, f1(Math.min(l, r)));
    if (l < m || r < m || tp < o.topMargin || bt < o.bottomMargin)
      res.edge.push(`${box(t.el)}: "${short(t.txt)}" is ${f1(Math.min(l, r))} mm from the side (min ${m}) / ${f1(Math.min(tp, bt))} mm from top or bottom`);
  });
  document.querySelectorAll('.slash').forEach(sl => {
    const c = room(sl), cr = c.getBoundingClientRect(), b = sl.getBoundingClientRect();
    const l = (b.left - cr.left) / MM;
    res.min.tip = Math.min(res.min.tip, f1(l));
    if (l < o.tipMargin) res.edge.push(`${box(sl)}: the tip of a slash is ${f1(l)} mm from the edge (min ${o.tipMargin})`);
  });
  // 3. collisions
  const shrink = r => ({l: r.left, r: r.right, t: r.top + r.height * .18, b: r.bottom - r.height * .18});
  for (let i = 0; i < lines.length; i++) for (let j = i + 1; j < lines.length; j++) {
    const a = lines[i], b = lines[j];
    if (a.blk === b.blk || a.blk.contains(b.blk) || b.blk.contains(a.blk)) continue;
    const A = shrink(a.r), B = shrink(b.r);
    const w = Math.min(A.r, B.r) - Math.max(A.l, B.l), h = Math.min(A.b, B.b) - Math.max(A.t, B.t);
    if (w > 1 && h > 1) res.collide.push(`${box(a.el)}: "${short(a.txt)}" overlaps "${short(b.txt)}" (${fmm(w)} x ${fmm(h)} mm)`);
  }
  const solids = Array.from(document.querySelectorAll('figure, .qr, .fmap'));
  lines.forEach(t => solids.forEach(f => {
    if (f.contains(t.el)) return;
    const q = f.getBoundingClientRect(), A = shrink(t.r);
    const w = Math.min(A.r, q.right) - Math.max(A.l, q.left), h = Math.min(A.b, q.bottom) - Math.max(A.t, q.top);
    if (w > 1 && h > 1) res.collide.push(`${box(t.el)}: "${short(t.txt)}" is over a ${f.tagName === 'FIGURE' ? 'photo' : f.className} (${fmm(w)} x ${fmm(h)} mm)`);
  }));
  // 3b. clearance between a text and a photo of the same panel / page (they must not touch), and between the text of an
  //      A4 header and the yellow diagonal stripe next to its photo
  lines.forEach(t => solids.forEach(f => {
    if (f.contains(t.el) || room(f) !== room(t.el)) return;
    const q = f.getBoundingClientRect();
    const dx = Math.max(q.left - t.r.right, t.r.left - q.right, 0), dy = Math.max(q.top - t.r.bottom, t.r.top - q.bottom, 0);
    const d = Math.hypot(dx, dy) / MM;
    if (d > 0 || (dx === 0 && dy === 0)) {
      if (d < res.min.photo) res.min.photo = f1(d);
      if (d < o.photoGap && !(dx === 0 && dy === 0)) res.collide.push(`${box(t.el)}: "${short(t.txt)}" is ${f1(d)} mm from a photo (min ${o.photoGap})`);
    }
  }));
  document.querySelectorAll('.a4h .stripe').forEach(st => {
    const q = st.getBoundingClientRect(), hd = st.parentElement.getBoundingClientRect();
    const X = y => q.left + 15 * MM * (1 - (y - q.top) / q.height);      // left edge of the stripe at height y (polygon 15mm 0 ... 0 100%)
    lines.forEach(t => {
      if (t.el.closest('.a4h') !== st.parentElement) return;
      const sep = (X(t.r.bottom) - t.r.right) / MM;
      if (sep < res.min.stripe) res.min.stripe = f1(sep);
      if (sep < o.stripeGap) res.collide.push(`${box(t.el)}: "${short(t.txt)}" is ${f1(sep)} mm from the yellow stripe (min ${o.stripeGap})`);
    });
  });
  // 4. a paragraph or a heading whose last line is only a few letters (a "widow"): reported, not an error
  document.querySelectorAll('p, li, .lead, .quote, .t, .statement, h1, h2, h6, .sub').forEach(e => {
    if (e.closest('style, script, svg') || e.querySelector('p, li')) return;
    const rs = Array.from((() => { const r = document.createRange(); r.selectNodeContents(e); return r.getClientRects(); })()).filter(r => r.width > 1 && r.height > 1);
    if (!rs.length) return;
    const rows = {}; rs.forEach(r => { const k = Math.round(r.top / 4); (rows[k] = rows[k] || []).push(r); });
    const keys = Object.keys(rows).map(Number).sort((a, b) => a - b);
    if (keys.length < 2) return;
    const last = rows[keys[keys.length - 1]];
    const w = Math.max(...last.map(r => r.right)) - Math.min(...last.map(r => r.left));
    const full = Math.max(...rs.map(r => r.right)) - Math.min(...rs.map(r => r.left));
    if (w / full < o.widow) res.orphans.push(`${box(e)}: "${short(e.textContent.trim().replace(/\s+/g, ' '))}" ends with a line of ${fmm(w)} mm`);
  });
  // 5. resolution of the photos
  let dpi = null;
  document.querySelectorAll('figure img').forEach(im => {
    const w = im.getBoundingClientRect().width / 96;
    if (w > 0.2 && im.naturalWidth) { const d = im.naturalWidth / w; dpi = dpi === null ? d : Math.min(dpi, d); }
  });
  res.dpi = dpi === null ? null : Math.round(dpi);
  return res;
}"""


JS_FILLS = """() => { const o = {}; document.querySelectorAll('[data-fid]').forEach(e => { o[e.dataset.fid] = Math.round(e.getBoundingClientRect().height / 3.7795 * 100) / 100; }); return o; }"""


GEOM_LIMITS = {'photoGap': 2.5, 'stripeGap': 3, 'widow': 0.16, 'gap': 1.5, 'panelMargin': 7, 'pageMargin': 10, 'topMargin': 5, 'bottomMargin': 2, 'tipMargin': 3}


def render_pdf(page, bld, c, fmt, workdir, name, out_pdf):
    """Two passes: the first measures the room left for the photos that fill their panel, the second is the final one.
    Returns the overflow report and the panels whose text had to be reduced."""
    bld.fills = {}
    for final in (False, True):
        path = os.path.join(workdir, name + '.html')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(bld.document(c, fmt))
        page.goto('file://' + path, wait_until='load')
        page.evaluate('document.fonts.ready')
        page.wait_for_function('Array.from(document.images).every(i => i.complete)')
        fits = page.evaluate(JS_FIT)
        shrunk = page.evaluate(JS_SHRINK)
        page.evaluate(JS_SHY)
        if not final:
            bld.fills = page.evaluate(JS_FILLS)
    report = page.evaluate(JS_CHECK)
    geom = page.evaluate(JS_GEOM, GEOM_LIMITS)
    geom['fills'] = page.evaluate(JS_FILLS)
    w, h = ('297mm', '210mm') if fmt == 'pliable' else ('210mm', '297mm')
    page.pdf(path=out_pdf, width=w, height=h, print_background=True, prefer_css_page_size=True,
             margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}, tagged=True)
    return report, shrunk, [f for f in fits if f['k'] < 0.85 or f['over'] > 0.5], geom


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('names', nargs='*', help='brochures to build (default: all the files of content/)')
    ap.add_argument('--formats', default='pliable,a4')
    ap.add_argument('--lang', default='all', help='languages: all, or a list such as fr,en,de')
    ap.add_argument('--originals', required=True, help='folder that contains "Photos site" (the full-resolution photos)')
    ap.add_argument('--sources', default=os.path.join(HERE, '..', 'photo-sources.csv'), help='table web photo -> original photo')
    ap.add_argument('--out', default=os.path.join(HERE, '..', '..', 'assets', 'brochures'), help='folder of the PDFs')
    ap.add_argument('--work', default=os.path.join(tempfile.gettempdir(), 'robotplus-brochures'), help='temporary files')
    a = ap.parse_args()
    langs = localize.LANGS if a.lang == 'all' else a.lang.split(',')
    for lang in langs:
        if lang not in localize.LANGS:
            sys.exit(f'unknown language "{lang}" (fr en it de es pt ro)')
    os.makedirs(a.out, exist_ok=True); os.makedirs(a.work, exist_ok=True)
    names = a.names or sorted(f[:-5] for f in os.listdir(os.path.join(HERE, 'content')) if f.endswith('.json'))
    photos = Photos(a.originals, a.sources, os.path.join(a.work, 'img'))
    texts = localize.Texts()
    from playwright.sync_api import sync_playwright
    problems = 0
    allfills = []
    stats = {'lines': 0, 'slashes': 0, 'gap': 99, 'side': 99, 'tip': 99, 'photo': 99, 'stripe': 99, 'dpi': 9999}
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        page = br.new_page()
        for n in names:
            c0 = json.load(open(os.path.join(HERE, 'content', n + '.json'), encoding='utf-8'))
            for lang in langs:
                try:
                    c = texts.localize(c0, lang)
                    ui = texts.ui(lang)
                except (localize.Missing, KeyError) as e:
                    print(f'{n} [{lang}] NOT BUILT: ' + (f'{len(e.texts)} text(s) without translation, e.g. {e.texts[:2]} {e.problems}' if isinstance(e, localize.Missing) else f'missing UI text {e}'))
                    problems += 1
                    continue
                bld = Builder(photos, os.path.join(HERE, 'assets'), lang, ui, texts.site.solutions(lang))
                for fmt in a.formats.split(','):
                    out_pdf = os.path.join(a.out, f'brochure-{c["base"]}-{fmt}-{lang}.pdf')
                    rep, shrunk, tfit, geom = render_pdf(page, bld, c, fmt, a.work, f'{c["base"]}-{fmt}-{lang}', out_pdf)
                    flags = [r for r in rep if r['over'] > 0.5 or r['wover'] > 0.5]
                    problems += len(flags)
                    stats['lines'] += geom['n']['lines']; stats['slashes'] += geom['n']['slashes']
                    for k_ in ('gap', 'side', 'tip', 'photo', 'stripe'):
                        stats[k_] = min(stats[k_], geom['min'][k_])
                    if geom['dpi'] is not None:
                        stats['dpi'] = min(stats['dpi'], geom['dpi'])
                    bad = geom['slash'] + geom['edge'] + geom['collide']
                    problems += len(bad)
                    for msg in bad:
                        print(f'    GEOMETRY {os.path.basename(out_pdf)}: {msg}')
                    stats['widows'] = stats.get('widows', 0) + len(geom['orphans'])
                    for fid_, mm_ in geom['fills'].items():
                        if mm_ < stats.get('fill', (999,))[0]:
                            stats['fill'] = (mm_, f'{c["base"]}-{fmt}-{lang} {fid_}')
                        allfills.append((mm_, f'{c["base"]}-{fmt}-{lang} {fid_}'))
                    if os.environ.get('SHOW_WIDOWS'):
                        for msg in geom['orphans']:
                            print(f'    widow {os.path.basename(out_pdf)}: {msg}')
                    if geom['dpi'] is not None and geom['dpi'] < 150:
                        print(f'    note: the lowest photo resolution is {geom["dpi"]} dpi')
                    print(f'{os.path.basename(out_pdf):62s} {os.path.getsize(out_pdf) / 1024:7.0f} KB  ' +
                          ' '.join(f'{r["id"]}:{"OVER " + str(r["over"]) + "/" + str(r["wover"]) if r["over"] > 0.5 or r["wover"] > 0.5 else "free " + str(r["free_mm"])}' for r in rep) +
                          ('  SHRUNK ' + ' '.join(f'{k}x{v}' for k, v in shrunk.items()) if shrunk else '') +
                          ('  TITLE ' + ' '.join(f'[{f["t"]} x{f["k"]}{" WIDE " + str(f["over"]) if f["over"] > 0.5 else ""}]' for f in tfit) if tfit else ''))
                    problems += sum(1 for f in tfit if f['over'] > 0.5)
        br.close()
    print(f'geometry: {stats["lines"]} lines of text and {stats["slashes"]} slashes measured; smallest gap between a slash and a text '
          f'{stats["gap"]} mm, smallest margin of a text {stats["side"]} mm, closest tip of a slash to an edge {stats["tip"]} mm, '
          f'closest text to a photo {stats["photo"]} mm and to the stripe of an A4 header {stats["stripe"]} mm, lowest photo resolution {stats["dpi"]} dpi; '
          f'{stats.get("widows", 0)} paragraphs end with a very short line')
    if os.environ.get('SHOW_FILLS'):
        for mm_, who in sorted(allfills)[:25]:
            print(f'    photo that fills its panel: {mm_} mm  {who}')
    print('problems:', problems)
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
