#!/usr/bin/env python3
"""ROBOTPLUS brochures: builds, from one content file per brochure (content/*.json), two PDFs in the style of the site:

  brochure-<base>-pliable.pdf   A4 landscape, 2 pages (outside / inside), folded in 3 panels
  brochure-<base>-a4.pdf        A4 portrait, 1 or 2 pages

Usage (see README.md in this folder):
    python3 -I tools/brochures/make_brochures.py --originals "/path/to/the/folder/that/contains/Photos site"
    python3 -I tools/brochures/make_brochures.py --originals ... robotique-industrielle --formats a4

The PDFs are written to assets/brochures/ (change it with --out). The photos are taken at full resolution, without
watermark, from the folder given by --originals: the "Photos site/..." files listed in tools/photo-sources.csv.
Needs: Python 3, Pillow, segno (QR codes) and Playwright with Chromium.
"""
import argparse, csv, hashlib, html, io, json, os, re, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

from PIL import Image, ImageCms, ImageOps
import segno

DPI = 220            # resolution of the photos placed in the brochures
JPEG_Q = 82
SITE_URL = 'https://robotplus-automatisme.github.io/'

COMPANY = {
    'address': ['ZI des Lèchères', '369 rue des Abeilles', '74460 Marnaz', 'France'],
    'phone': '+33 4 50 96 38 28',
    'phone_href': 'tel:+33450963828',
    'email': 'robotplus@orange.fr',
    'web': 'robotplus-automatisme.github.io',
    'legal': 'ROBOTPLUS — SARL au capital de 15 000 € · SIREN 407 664 119 · RCS Annecy · NAF 46.69B',
}
# The solutions of the home page, in the same order and with the same names.
SOLUTIONS = ['Robotique', 'Machines de contrôle', 'Contrôle laser', 'Machines spéciales',
             'Alimentations, convoyage, stockage', 'Rétrofit machines', 'Lavage, dewatering, dégraissage',
             'Postes de travail']

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


def md(s):
    """Escape, then **bold** -> <strong>; apply French typography."""
    s = html.escape(fr_typo(s), quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    return re.sub(r'\b([A-Za-zÀ-ÿ]+-(?:nous|vous|en|y|moi|lui)\b)', r'<span style="white-space:nowrap">\1</span>', s)


def plain(s):
    return html.escape(fr_typo(s), quote=False)


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
            im.save(out, 'JPEG', quality=JPEG_Q, optimize=True)
        return out


# ----------------------------------------------------------------------------- css
CSS = r'''
:root{--yellow:#ffea00;--dark:#172127;--dark2:#111a1f;--ink:#111820;--text:#2b353b;--paper:#f4f5f4;--muted:#586166;--line:#dfe3e5;
  --head:'Barlow Condensed','Arial Narrow',Arial,sans-serif;--body:Inter,Arial,sans-serif}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-family:var(--body);color:var(--ink);font-size:8.5pt;line-height:1.5;font-kerning:normal;text-rendering:geometricPrecision}
.page{position:relative;overflow:hidden;break-after:page;page-break-after:always}
.page:last-child{break-after:auto;page-break-after:auto}
.land{width:297mm;height:210mm}.port{width:210mm;height:297mm}
.panel{position:absolute;top:0;height:210mm;overflow:hidden;display:flex;flex-direction:column;padding:11mm 9mm 9mm}
.panel>*{flex:none}
.dark{background:var(--dark);color:#fff}
.paper{background:var(--paper)}
img{display:block}
p{margin:0;color:var(--text);font-size:var(--fs,8.5pt);line-height:1.5}
strong{font-weight:700;color:var(--ink)}
.dark p,.dark strong{color:#e6eaec}.dark strong{color:#fff}
.slash{display:inline-block;width:2.3mm;height:6.4mm;background:var(--yellow);transform:skew(-18deg);flex:none}

/* headings */
.title{font-family:var(--head);font-weight:800;font-size:var(--ts,30pt);line-height:.95;margin:0;color:var(--ink);letter-spacing:-.005em}
.titlerow{display:flex;gap:4.4mm;align-items:flex-start}
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
/* steps (machines spéciales) */
.steps{display:flex;gap:1mm}
.steps div{flex:1;background:var(--dark);color:#fff;font-family:var(--head);font-weight:700;font-size:10.5pt;line-height:1.05;padding:2.4mm 1.6mm 2.4mm 3.4mm;position:relative;clip-path:polygon(0 0,calc(100% - 2.4mm) 0,100% 50%,calc(100% - 2.4mm) 100%,0 100%)}
.steps div b{display:block;color:var(--yellow);font-size:7.5pt;font-family:var(--body);font-weight:800;letter-spacing:.08em;margin-bottom:.6mm}

/* ------------------------------------------------ cover / flap / back (dark panels) */
.logo{width:var(--lw,56mm);height:auto}
.eyebrow{font-size:6.6pt;letter-spacing:.2em;font-weight:700;color:#9fabb1;text-transform:uppercase}
.cover .tb{position:relative;margin-top:var(--tbm,17mm);padding-left:7mm}
.cover .tb .slash{position:absolute;left:0;top:9mm;width:3.2mm;height:var(--sh,36mm)}
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
    def __init__(self, photos, assets):
        self.photos, self.assets = photos, assets
        self.fills = {}      # measured heights (mm) of the photos that fill the free space, from the previous pass
        self.ctx = ''        # name of the panel being rendered

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
            lines = '<br>'.join(plain(x) for x in o['lines'])
            st = f' style="--ts:{o["pt"]}pt;--sh:{o.get("sh", 15)}mm"' if 'pt' in o else ''
            return f'<div class="titlerow"{st}><span class="slash"></span><h2 class="title">{lines}</h2></div>'
        if t == 'lead':
            return f'<p class="lead"{style}>{md(o["text"])}</p>'
        if t == 'p':
            return f'<p{style}>{md(o["text"])}</p>'
        if t == 'h3':
            return f'<h3>{plain(o["text"])}</h3>'
        if t == 'rows':
            cls = ' plain' if o.get('plain') else ''
            st = f' style="--rfs:{o["fs"]}pt"' if 'fs' in o else ''
            return f'<ul class="rows{cls}"{st}>' + ''.join(f'<li>{md(i)}</li>' for i in o['items']) + '</ul>'
        if t == 'apps':
            st = f' style="--afs:{o["fs"]}pt"' if 'fs' in o else ''
            return f'<div class="apps"{st}><h5>{plain(o.get("title", "Applications"))}</h5><ul>' + ''.join(f'<li>{md(i)}</li>' for i in o['items']) + '</ul></div>'
        if t == 'quote':
            st = f' style="--qfs:{o["fs"]}pt"' if 'fs' in o else ''
            return f'<div class="quote"{st}>{md(o["text"])}</div>'
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
            return '<div><h4 style="margin-bottom:1.6mm">Nos solutions</h4>' + self.solutions_list(self.on, light=True) + '</div>'
        if t == 'cards':
            cw = o.get('cw', 34)
            out = []
            for ci, c in enumerate(o['items']):
                ph = c.get('h', o.get('h', 30))
                fid = f'{self.ctx}:{b.get("id", "cards")}:{ci}'      # always measured: the figure stretches to the card height
                ph = self.fills.get(fid, ph)
                attr = f' data-fid="{fid}"'
                fig = f'<figure{attr} style="width:{cw}mm">{self.img(c["img"], cw, ph, c.get("focus", (.5, .5)), c.get("zoom", 1.0), crop=c.get("crop"))}</figure>'
                out.append(f'<div class="card" style="--cw:{cw}mm">{fig}<div class="tx"><h6>{plain(c["title"])}</h6><p>{md(c["text"])}</p></div></div>')
            st = f' style="--cfs:{o["fs"]}pt"' if 'fs' in o else ''
            return f'<div class="cards{" fill" if o.get("fill") else ""}"{st}>' + ''.join(out) + '</div>'
        if t == 'steps':
            return '<div class="steps">' + ''.join(f'<div><b>{i + 1:02d}</b>{plain(s)}</div>' for i, s in enumerate(o['items'])) + '</div>'
        if t == 'cta':
            return (f'<div class="cta"><div class="t">{md(o["text"])}</div><div class="c">{plain(COMPANY["phone"])} · {plain(COMPANY["email"])}</div></div>')
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
                f'<li>{ICON["pin"]}<span>{"<br>".join(plain(x) for x in c["address"])}</span></li>'
                f'<li>{ICON["phone"]}<span><b>{c["phone"]}</b></span></li>'
                f'<li>{ICON["mail"]}<span>{c["email"]}</span></li>'
                f'<li>{ICON["web"]}<span>{c["web"]}</span></li>'
                '</ul>')

    def solutions_list(self, on, light=False):
        return f'<ul class="sol{" light" if light else ""}">' + ''.join(f'<li class="{"on" if s in on else ""}">{plain(s)}</li>' for s in SOLUTIONS) + '</ul>'

    def map_block(self):
        return (f'<div class="fmap"><img src="file://{self.assets}/france.png" alt="">{PIN_SVG}</div>')

    def cover_panel(self, c, left, width):
        title = '<br>'.join(plain(x) for x in c['title'])
        hero = c['cover']
        hh = c.get('tri_hero_h', 100)
        return (f'<section class="panel cover dark" data-check="cover" style="left:{left}mm;width:{width}mm;--hh:{hh}mm;--cts:{c.get("cover_pt", 40)}pt;--sh:{c.get("slash_h", 36)}mm">'
                f'{self.logo(56)}'
                f'<div class="tb"><span class="slash"></span><div class="eyebrow">Marnaz · Haute-Savoie · France</div>'
                f'<h1 class="fit">{title}</h1><p class="sub">{md(c["subtitle"])}</p></div>'
                f'<figure class="hero">{self.img(hero["img"], width, hh, hero.get("focus", (.5, .5)), hero.get("zoom", 1.0), crop=hero.get("crop"))}</figure>'
                '</section>')

    def flap_panel(self, c, left, width):
        on = c.get('highlight', [])
        return (f'<section class="panel flap dark" data-check="flap" style="left:{left}mm;width:{width}mm;padding-top:14mm;gap:6.5mm">'
                '<div class="titlerow" style="--sh:23mm"><span class="slash"></span>'
                '<h2 class="statement">Une solution <em>sur mesure</em> pour chaque projet</h2></div>'
                '<p style="font-size:9pt;line-height:1.5;color:#dfe3e5">Des machines standards aux systèmes les plus complexes, nous concevons des solutions adaptées à vos contraintes.</p>'
                '<div style="margin-top:1mm"><h4 style="color:#9fabb1;margin-bottom:2mm">Nos solutions</h4>' + self.solutions_list(on) + '</div>'
                '<div style="flex:1 1 auto"></div>'
                '<p style="font-size:8.6pt;line-height:1.5;color:#c9d1d5"><strong style="color:#fff">Depuis 1996</strong>, ROBOTPLUS conçoit et intègre des solutions d’automatisation adaptées à vos besoins.</p>'
                '</section>')

    def back_panel(self, c, left, width):
        url = SITE_URL + c['page']
        return (f'<section class="panel back dark" data-check="back" style="left:{left}mm;width:{width}mm;padding-top:11mm;gap:0">'
                f'{self.logo(46)}'
                '<div class="titlerow" style="margin-top:17mm;--sh:15mm"><span class="slash"></span><h2 class="statement" style="font-size:29pt">Parlons de<br>votre projet</h2></div>'
                '<p style="margin-top:4.5mm;font-size:9pt;line-height:1.5;color:#dfe3e5">Notre expertise en robotique, en vision et en machines spéciales nous permet d’accompagner vos projets, de l’étude à la mise en service, sur les secteurs les plus exigeants.</p>'
                f'<div style="margin-top:7mm;position:relative">{self.contact_list()}<div style="position:absolute;right:0;top:-1mm">{self.map_block()}</div></div>'
                '<div style="flex:1 1 auto"></div>'
                f'<div style="display:flex;gap:4mm;align-items:center"><div class="qr">{qr_svg(url)}</div>'
                '<p style="font-size:7.6pt;line-height:1.45;color:#c9d1d5">Scannez ce code pour retrouver cette page, nos réalisations et nos documents sur notre site.</p></div>'
                f'<p class="legal" style="margin-top:5mm">{plain(COMPANY["legal"])}</p>'
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
        .a4h .tb{position:absolute;left:12mm;top:var(--tbt);width:100mm;padding-left:7mm}
        .a4h .tb .slash{position:absolute;left:0;top:7.4mm;width:3mm;height:var(--slh)}
        .a4h h1{font-family:var(--head);font-weight:800;font-size:var(--tpt);line-height:.92;margin:2.4mm 0 0;color:#fff;white-space:nowrap;letter-spacing:-.01em}
        .a4h .sub{font-size:8.6pt;line-height:1.4;color:#dfe3e5;margin-top:3.2mm;max-width:92mm}
        .a4h .hero{position:absolute;right:0;top:0;width:var(--hw);height:var(--hh);clip-path:polygon(15mm 0,100% 0,100% 100%,0 100%)}
        .a4h .stripe{position:absolute;top:0;left:calc(210mm - var(--hw) - 1.4mm);height:var(--hh);width:17mm;background:var(--yellow);clip-path:polygon(15mm 0,17.4mm 0,2.4mm 100%,0 100%)}
        .a4h .logo{top:9mm;width:46mm}
        .a4h.slim .logo{top:8.5mm;width:42mm}
        .a4h.slim .tb{left:78mm;top:9.5mm;width:120mm;padding-left:7mm}
        .a4h.slim .tb .slash{top:6.6mm;height:13mm;width:2.6mm}
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
        .a4f .q2{position:absolute;right:37mm;top:6mm;width:30mm;font-size:6.8pt;line-height:1.4;text-align:right;color:var(--ink);font-weight:600}
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
        title = '<br>'.join(plain(x) for x in title_lines)
        url = SITE_URL + c['page']
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
        vars_ = (f'--hh:{head_h}mm;--hw:{hero_w}mm;--bt:{body_top}mm;--ch:{col_h}mm;--lw:{lw}mm;--rw:{rw}mm;--cg:{210 - 24 - lw - rw}mm;'
                 f'--gap:{a.get("gap", 3.2)}mm;--tbt:{a.get("tb_top", 29)}mm;--slh:{a.get("slash_h", 24)}mm;--tpt:{a.get("title_pt", 34)}pt;'
                 f'--bfs:{fs}pt;--rfs:{fs - .5}pt;--afs:{fs - .5}pt;--qfs:{fs + .5}pt;--lfs:{fs + 1.5}pt;--cfs:{fs - 1.1}pt')
        addr = f'{plain(COMPANY["address"][0])}, {plain(COMPANY["address"][1])}<br>{plain(COMPANY["address"][2])} · {plain(COMPANY["address"][3])}'
        if slim:
            head = (f'<div class="a4h slim"><img class="logo" src="file://{self.assets}/logo-dark.png" alt="ROBOT+ Automatisme">'
                    f'<div class="tb" style="--tpt:{a.get("slim_pt", 28)}pt"><span class="slash"></span><div class="eyebrow">Marnaz · Haute-Savoie · France</div><h1 class="fit">{title}</h1></div></div>')
        else:
            head = (f'<div class="a4h"><img class="logo" src="file://{self.assets}/logo-dark.png" alt="ROBOT+ Automatisme">'
                    f'<div class="tb"><span class="slash"></span><div class="eyebrow">Marnaz · Haute-Savoie · France</div><h1 class="fit">{title}</h1><p class="sub">{md(c["subtitle"])}</p></div>'
                    f'<figure class="hero">{self.img(hero["img"], hero_w, head_h, hero.get("focus", (.5, .5)), hero.get("zoom", 1.0), crop=hero.get("crop"))}</figure><div class="stripe"></div></div>')
        return (f'<div class="page port paper" style="{vars_}" data-check="a4page{idx}">{head}'
                f'<div class="a4b"><div class="col" data-check="a4{idx}-left" style="width:{lw}mm">{left}</div>'
                f'<div class="col" data-check="a4{idx}-right" style="width:{rw}mm">{right}</div></div>'
                f'<div class="a4s">{strip}</div>'
                f'<div class="a4f"><div class="ct"><div><span>{ic("pin")}<i style="font-style:normal">{addr}</i></span></div>'
                f'<div><span>{ic("phone")}<b>{COMPANY["phone"]}</b></span><span>{ic("mail")}{COMPANY["email"]}</span><span>{ic("web")}{COMPANY["web"]}</span></div></div>'
                f'<div class="q2">Scannez pour retrouver cette page sur notre site.</div><div class="qr">{qr_svg(url)}</div>'
                f'<div class="lg">{plain(COMPANY["legal"])}</div></div></div>')

    # --- document
    def document(self, c, fmt):
        body = self.trifold(c) if fmt == 'pliable' else self.a4(c)
        size = '297mm 210mm' if fmt == 'pliable' else '210mm 297mm'
        label = 'Brochure pliable' if fmt == 'pliable' else 'Brochure A4'
        return (f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>ROBOTPLUS — {plain(c["title_plain"])} — {label}</title>'
                f'<link rel="stylesheet" href="file://{HERE}/fonts/fonts.css"><style>@page{{size:{size};margin:0}}{CSS}</style></head><body>{body}</body></html>')


JS_FIT = '''() => {
  document.querySelectorAll('.fit').forEach(el => {
    let fs = parseFloat(getComputedStyle(el).fontSize);
    const cs = getComputedStyle(el.parentElement);
    const avail = el.parentElement.clientWidth - parseFloat(cs.paddingLeft || 0) - parseFloat(cs.paddingRight || 0) - 1;
    while (el.getBoundingClientRect().width > avail && fs > 22) { fs -= 0.5; el.style.fontSize = fs + 'px'; }
  });
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


JS_FILLS = """() => { const o = {}; document.querySelectorAll('[data-fid]').forEach(e => { o[e.dataset.fid] = Math.round(e.getBoundingClientRect().height / 3.7795 * 100) / 100; }); return o; }"""


def render_pdf(page, bld, c, fmt, workdir, name, out_pdf):
    """Two passes: the first measures the room left for the photos that fill their panel, the second is the final one."""
    bld.fills = {}
    for final in (False, True):
        path = os.path.join(workdir, name + '.html')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(bld.document(c, fmt))
        page.goto('file://' + path, wait_until='load')
        page.evaluate('document.fonts.ready')
        page.wait_for_function('Array.from(document.images).every(i => i.complete)')
        page.evaluate(JS_FIT)
        if not final:
            bld.fills = page.evaluate(JS_FILLS)
    report = page.evaluate(JS_CHECK)
    w, h = ('297mm', '210mm') if fmt == 'pliable' else ('210mm', '297mm')
    page.pdf(path=out_pdf, width=w, height=h, print_background=True, prefer_css_page_size=True,
             margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}, tagged=True)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('names', nargs='*', help='content files to build (default: all in content/)')
    ap.add_argument('--formats', default='pliable,a4')
    ap.add_argument('--originals', required=True, help='folder that contains "Photos site" (the full-resolution photos)')
    ap.add_argument('--sources', default=os.path.join(HERE, '..', 'photo-sources.csv'), help='table web photo -> original photo')
    ap.add_argument('--out', default=os.path.join(HERE, '..', '..', 'assets', 'brochures'), help='folder of the PDFs')
    ap.add_argument('--work', default=os.path.join(tempfile.gettempdir(), 'robotplus-brochures'), help='temporary files')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); os.makedirs(a.work, exist_ok=True)
    names = a.names or sorted(f[:-5] for f in os.listdir(os.path.join(HERE, 'content')) if f.endswith('.json'))
    photos = Photos(a.originals, a.sources, os.path.join(a.work, 'img'))
    bld = Builder(photos, os.path.join(HERE, 'assets'))
    from playwright.sync_api import sync_playwright
    problems = 0
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        page = br.new_page()
        for n in names:
            c = json.load(open(os.path.join(HERE, 'content', n + '.json'), encoding='utf-8'))
            for fmt in a.formats.split(','):
                out_pdf = os.path.join(a.out, f'brochure-{c["base"]}-{fmt}.pdf')
                rep = render_pdf(page, bld, c, fmt, a.work, f'{c["base"]}-{fmt}', out_pdf)
                flags = [r for r in rep if r['over'] > 0.5 or r['wover'] > 0.5]
                problems += len(flags)
                print(f'{os.path.basename(out_pdf):62s} {os.path.getsize(out_pdf) / 1024:7.0f} KB  ' +
                      ' '.join(f'{r["id"]}:{"OVER " + str(r["over"]) if r["over"] > 0.5 else "free " + str(r["free_mm"])}' for r in rep))
        br.close()
    print('overflow problems:', problems)


if __name__ == '__main__':
    main()
