#!/usr/bin/env python3
"""Layout check of the website in a real browser (Playwright, Chromium).

For every page (the home page and the 14 pages of solutions/), every language and every window width it checks:
  - the yellow slashes (header of the home page, header of the category and sub pages, small markers of the home page,
    diagonal band of "Une solution sur mesure pour chaque projet") against the text lines next to them: the distance
    must not be smaller than MIN_GAP (6 px, 2 px for the small markers). The polygon of a slash is computed from the CSS,
    skew included, so the slant of 18 degrees is taken into account;
  - text cut off by the edge of the window or by a box with overflow hidden (a long German word in a title, for example);
  - a page wider than the window (sideways scroll).

usage, from the root of the repository (about 10 minutes for everything, 14 widths from 320 to 1920 px):
  python3 tools/check_layout.py .
  python3 tools/check_layout.py . --quick                              4 widths only
  python3 tools/check_layout.py . --pages index,bols --widths 390,1100 --langs de,fr --all
Without --all only the first 60 problems are printed. Exit status 1 when there is a problem.
Run it after changing assets/css/site.css or the texts of assets/js/i18n.js (see CHANGES.md, 24 November 2026).
"""
import sys, os, json, glob, argparse
from playwright.sync_api import sync_playwright

LANGS = ['fr', 'en', 'it', 'de', 'es', 'pt', 'ro']
WIDTHS = [320, 360, 390, 430, 480, 600, 720, 768, 900, 1024, 1100, 1280, 1440, 1920]
MIN_GAP = {'home-hero': 6.0, 'page-hero': 6.0, 'marker': 2.0, 'project-cut': 6.0}   # px between a slash and any text line (fails below)
TAN18 = 0.3249197

JS = r"""
() => {
  const TAN = 0.3249197;
  const res = [];
  function textRects(container) {
    const rects = [];
    const w = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = w.nextNode())) {
      if (!n.nodeValue.trim()) continue;
      const p = n.parentElement;
      if (!p) continue;
      const cs = getComputedStyle(p);
      if (cs.visibility === 'hidden' || cs.display === 'none') continue;
      const r = document.createRange(); r.selectNodeContents(n);
      for (const q of r.getClientRects())
        if (q.width > 0.5 && q.height > 0.5) rects.push([q.left, q.top, q.right, q.bottom, n.nodeValue.trim().slice(0, 20)]);
    }
    return rects;
  }
  // polygon of a box (x, y, w, h in viewport coordinates) after the CSS transform of cs about its transform-origin
  function poly(x, y, w, h, cs) {
    const m = cs.transform === 'none' ? new DOMMatrix() : new DOMMatrix(cs.transform);
    const o = cs.transformOrigin.split(' ').map(parseFloat);
    return [[0, 0], [w, 0], [w, h], [0, h]].map(([px, py]) => {
      const dx = px - o[0], dy = py - o[1];
      return [x + o[0] + m.a * dx + m.c * dy + m.e, y + o[1] + m.b * dx + m.d * dy + m.f];
    });
  }
  function pseudoPoly(el, which) {
    const cs = getComputedStyle(el, which);
    if (cs.display === 'none' || cs.content === 'none') return null;
    const pr = el.getBoundingClientRect();
    const ecs = getComputedStyle(el);
    const x = pr.left + parseFloat(ecs.borderLeftWidth) + parseFloat(cs.left);
    const y = pr.top + parseFloat(ecs.borderTopWidth) + parseFloat(cs.top);
    return poly(x, y, parseFloat(cs.width), parseFloat(cs.height), cs);
  }
  function elPoly(el) {
    const cs = getComputedStyle(el);
    const old = el.style.transform;
    el.style.transform = 'none';
    const r = el.getBoundingClientRect();
    el.style.transform = old;
    return poly(r.left, r.top, r.width, r.height, cs);
  }
  // distance between a convex polygon and an axis-aligned rectangle (0 when they overlap)
  function dist(P, r) {
    const R = [[r[0], r[1]], [r[2], r[1]], [r[2], r[3]], [r[0], r[3]]];
    function axes(A) { return A.map((a, i) => { const b = A[(i + 1) % A.length]; return [-(b[1] - a[1]), b[0] - a[0]]; }); }
    let overlap = true;
    for (const ax of axes(P).concat(axes(R))) {
      const proj = A => A.map(p => p[0] * ax[0] + p[1] * ax[1]);
      const a = proj(P), b = proj(R);
      if (Math.max(...a) < Math.min(...b) || Math.max(...b) < Math.min(...a)) { overlap = false; break; }
    }
    if (overlap) return 0;
    function pd(p, a, b) {
      const dx = b[0] - a[0], dy = b[1] - a[1];
      const t = Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)));
      return Math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy);
    }
    let best = 1e9;
    for (const p of P) for (let i = 0; i < 4; i++) best = Math.min(best, pd(p, R[i], R[(i + 1) % 4]));
    for (const p of R) for (let i = 0; i < P.length; i++) best = Math.min(best, pd(p, P[i], P[(i + 1) % P.length]));
    return best;
  }
  function check(kind, P, container) {
    if (!P || !container) return;
    let best = 1e9, who = '';
    for (const r of textRects(container)) {
      const d = dist(P, r);
      if (d < best) { best = d; who = r[4]; }
    }
    res.push({ kind, gap: best === 1e9 ? null : Math.round(best * 10) / 10, text: who });
  }
  // hero of the home page
  for (const el of document.querySelectorAll('.yellow-slash')) check('home-hero', elPoly(el), el.closest('.hero'));
  // hero of the category pages
  for (const el of document.querySelectorAll('.detail-copy')) check('page-hero', pseudoPoly(el, '::before'), el);
  // small markers before the titles of the home page
  for (const el of document.querySelectorAll('.section-marker')) check('marker', elPoly(el), el.parentElement);
  // diagonal band of the 'solution sur mesure' section: the dark text must stay left of the yellow band
  for (const ph of document.querySelectorAll('.project-photo')) {
    const cs = getComputedStyle(ph, '::after');
    if (cs.display === 'none') continue;
    const r = ph.getBoundingClientRect();
    const dark = ph.parentElement.querySelector('.project-dark');
    if (!dark || r.width < 50) continue;
    check('project-cut', poly(r.left + parseFloat(cs.left), r.top + parseFloat(cs.top), parseFloat(cs.width), parseFloat(cs.height), cs), dark);
  }
  // text cut off by the edge of the window or by an ancestor with overflow hidden (partly visible only)
  const cut = [];
  {
    const W = document.documentElement.clientWidth;
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = w.nextNode())) {
      if (!n.nodeValue.trim()) continue;
      const p = n.parentElement;
      if (!p || ['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEXTAREA'].includes(p.tagName)) continue;
      const cs = getComputedStyle(p);
      if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      let hidden = false;
      for (let a = p; a && a !== document.documentElement; a = a.parentElement) {
        const acs = getComputedStyle(a);
        if (acs.display === 'none' || acs.visibility === 'hidden' || acs.opacity === '0') { hidden = true; break; }
      }
      if (hidden) continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      let clipL = 0, clipR = W;
      for (let a = p; a && a !== document.documentElement; a = a.parentElement) {
        const acs = getComputedStyle(a);
        if (acs.overflowX !== 'visible') { const r = a.getBoundingClientRect(); clipL = Math.max(clipL, r.left); clipR = Math.min(clipR, r.right); }
      }
      for (const q of rg.getClientRects()) {
        if (q.width < 1) continue;
        if (q.right <= clipL + 0.5 || q.left >= clipR - 0.5) continue;      // wholly outside: a hidden slide or a skip link
        const over = Math.max(q.right - clipR, clipL - q.left);
        if (over > 1) cut.push({ text: n.nodeValue.trim().slice(0, 24), by: Math.round(over), tag: p.tagName.toLowerCase() + (p.className ? '.' + String(p.className).split(' ')[0] : '') });
      }
    }
  }
  return { slashes: res, cut, overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth };
}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('site')
    ap.add_argument('--quick', action='store_true')
    ap.add_argument('--pages')
    ap.add_argument('--widths')
    ap.add_argument('--langs')
    ap.add_argument('--all', action='store_true', help='print every problem, not only the first 60')
    a = ap.parse_args()
    root = os.path.abspath(a.site)
    pages = ['index.html'] + sorted(os.path.relpath(p, root) for p in glob.glob(root + '/solutions/*.html'))
    if a.pages:
        pages = [p for p in pages if any(k in p for k in a.pages.split(','))]
    widths = [int(w) for w in a.widths.split(',')] if a.widths else ([390, 768, 1100, 1440] if a.quick else WIDTHS)
    langs = a.langs.split(',') if a.langs else LANGS
    worst = {}       # kind -> (gap, where)
    problems = []
    n = 0
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for w in widths:
            ctx = br.new_context(viewport={'width': w, 'height': 900})
            pg = ctx.new_page()
            for page in pages:
                pg.goto('file://' + os.path.join(root, page))
                pg.wait_for_load_state('load')
                pg.evaluate('document.fonts.ready')
                for lang in langs:
                    pg.evaluate("""(l) => new Promise(r => { if (document.documentElement.lang === l) return r();
                        window.addEventListener('hashchange', () => setTimeout(r, 20), {once: true}); location.hash = '#' + l; setTimeout(r, 400); })""", lang)
                    pg.evaluate('document.fonts.ready')
                    out = pg.evaluate(JS)
                    n += 1
                    where = f'{page} [{lang}] {w}px'
                    if out['overflow'] > 1:
                        problems.append(f'SIDEWAYS SCROLL {where}: page is {out["overflow"]}px wider than the window')
                    seen = set()
                    for c in out['cut']:
                        key = (c['text'], c['tag'])
                        if key in seen:
                            continue
                        seen.add(key)
                        problems.append(f'TEXT CUT OFF {where}: "{c["text"]}" ({c["tag"]}) by {c["by"]}px')
                    for s in out['slashes']:
                        if s['gap'] is None:
                            continue
                        k = s['kind']
                        if k not in worst or s['gap'] < worst[k][0]:
                            worst[k] = (s['gap'], where + ' near "' + s['text'] + '"')
                        if s['gap'] < MIN_GAP[k]:
                            problems.append(f'SLASH {k} {where}: {s["gap"]}px from "{s["text"]}"')
            ctx.close()
        br.close()
    for k, (g, w) in sorted(worst.items()):
        print(f'closest {k:12s}: {g:5.1f}px  {w}')
    print(f'{n} page views checked, {len(problems)} problems')
    limit = len(problems) if a.all else 60
    for p in problems[:limit]:
        print('  ', p)
    if len(problems) > limit:
        print(f'   ... and {len(problems) - limit} more (use --all)')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
