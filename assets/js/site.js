/* ROBOT+ Automatisme — shared behaviour for every page:
   mobile menu, language menu, translations (texts live in assets/js/i18n.js) and photo galleries. */
(function () {
  'use strict';

  var LANGS = ['fr', 'en', 'it', 'de', 'es', 'pt', 'ro'];
  var NAMES = { fr: 'Français', en: 'English', it: 'Italiano', de: 'Deutsch', es: 'Español', pt: 'Português', ro: 'Română' };
  var STORAGE_KEY = 'robotplus-lang';
  var DICT = window.RP_I18N || {};
  var html = document.documentElement;
  var body = document.body;
  var root = body.getAttribute('data-root') || '';
  var page = body.getAttribute('data-page') || '';
  var current = 'fr';
  var galleries = [];

  function validLang(value) {
    value = String(value || '').toLowerCase();
    return LANGS.indexOf(value) >= 0 ? value : null;
  }
  function readStored() {
    try { return validLang(window.localStorage.getItem(STORAGE_KEY)); } catch (e) { return null; }
  }
  function store(lang) {
    try { window.localStorage.setItem(STORAGE_KEY, lang); } catch (e) { /* private mode: ignore */ }
  }
  function t(key, lang) {
    var entry = DICT[key];
    if (!entry) return null;
    lang = lang || current;
    return entry[lang] != null && entry[lang] !== '' ? entry[lang] : (entry.fr != null ? entry.fr : null);
  }
  function plain(text) {
    var div = document.createElement('div');
    div.innerHTML = text;
    return (div.textContent || '').replace(/\s+/g, ' ').trim();
  }

  /* ---------- mobile navigation ---------- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---------- language menu ---------- */
  var langButton = document.querySelector('.lang-button');
  var langMenu = document.querySelector('.lang-menu');
  function setMenu(open) {
    if (!langMenu || !langButton) return;
    langMenu.classList.toggle('open', open);
    langButton.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  if (langButton && langMenu) {
    langButton.addEventListener('click', function (e) {
      e.stopPropagation();
      setMenu(!langMenu.classList.contains('open'));
    });
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.header-contact')) setMenu(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && langMenu.classList.contains('open')) { setMenu(false); langButton.focus(); }
    });
    langMenu.querySelectorAll('a[data-lang]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        choose(a.getAttribute('data-lang'));
        setMenu(false);
      });
    });
  }

  /* ---------- translations ---------- */
  function applyLanguage(lang) {
    current = lang;
    html.lang = lang;
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var value = t(el.getAttribute('data-i18n'), lang);
      if (value != null) el.innerHTML = value;
    });
    document.querySelectorAll('[data-i18n-alt]').forEach(function (el) {
      var value = t(el.getAttribute('data-i18n-alt'), lang);
      if (value != null) el.setAttribute('alt', plain(value));
    });
    document.querySelectorAll('[data-i18n-aria]').forEach(function (el) {
      var value = t(el.getAttribute('data-i18n-aria'), lang);
      if (value != null) el.setAttribute('aria-label', plain(value));
    });
    var title = t('page.' + page + '.title', lang);
    if (title != null) document.title = plain(title) + ' | ROBOT+ Automatisme';
    var flag = document.getElementById('lang-flag');
    if (flag) { flag.src = root + 'assets/icons/flags/' + lang + '.svg'; flag.alt = NAMES[lang]; }
    var code = document.getElementById('lang-code');
    if (code) code.textContent = lang.toUpperCase();
    galleries.forEach(function (g) { g.refresh(); });
  }
  function choose(lang) {
    lang = validLang(lang) || 'fr';
    applyLanguage(lang);
    store(lang);
    // keep the choice in the address so a copied link opens in the same language
    if (window.history && window.history.replaceState) {
      try { window.history.replaceState(null, '', '#' + lang); } catch (e) { /* file:// in some browsers */ }
    }
  }
  window.addEventListener('hashchange', function () {
    var lang = validLang(location.hash.slice(1));
    if (lang && lang !== current) { applyLanguage(lang); store(lang); }
  });

  /* ---------- photo galleries ---------- */
  function Gallery(section) {
    var slides = Array.prototype.slice.call(section.querySelectorAll('.rp-slide'));
    var prev = section.querySelector('.rp-slide-arrow.prev');
    var next = section.querySelector('.rp-slide-arrow.next');
    var dotsBox = section.querySelector('.rp-slide-dots');
    var counter = section.querySelector('.rp-slide-counter');
    var index = 0;
    var dots = slides.map(function (slide, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'rp-slide-dot';
      b.addEventListener('click', function () { show(i); });
      dotsBox.appendChild(b);
      return b;
    });
    function active() {
      return slides.map(function (s, i) { return s.getAttribute('data-failed') ? -1 : i; }).filter(function (i) { return i >= 0; });
    }
    function show(i) { index = i; refresh(); }
    function step(delta) {
      var list = active();
      if (!list.length) return;
      var pos = list.indexOf(index);
      if (pos < 0) pos = 0;
      index = list[(pos + delta + list.length) % list.length];
      refresh();
    }
    function refresh() {
      var list = active();
      if (list.indexOf(index) < 0) index = list.length ? list[0] : 0;
      var photo = t('gallery.photo') || 'Photo';
      var title = plain(t('page.' + page + '.title') || '');
      slides.forEach(function (s, i) {
        s.hidden = i !== index;
        var img = s.querySelector('img');
        if (img) img.alt = (title ? title + ' — ' : '') + photo.toLowerCase() + ' ' + (i + 1);
      });
      dots.forEach(function (d, i) {
        d.hidden = list.indexOf(i) < 0;
        d.setAttribute('aria-current', i === index ? 'true' : 'false');
        d.setAttribute('aria-label', photo + ' ' + (i + 1));
      });
      if (counter) counter.textContent = list.length ? photo + ' ' + (list.indexOf(index) + 1) + ' ' + (t('gallery.of') || '/') + ' ' + list.length : '';
      if (prev) prev.disabled = list.length < 2;
      if (next) next.disabled = list.length < 2;
      // fetch the next photo in advance so "next" feels instant
      var pos = list.indexOf(index);
      if (list.length > 1 && pos >= 0) {
        var upcoming = slides[list[(pos + 1) % list.length]].querySelector('img');
        if (upcoming && upcoming.loading === 'lazy') upcoming.loading = 'eager';
      }
    }
    slides.forEach(function (s, i) {
      var img = s.querySelector('img');
      if (!img) return;
      img.addEventListener('error', function () {
        s.setAttribute('data-failed', '1');
        if (i === index) {
          // a photo that cannot load is skipped: move forward, never back to the first photo
          var list = active(), after = list.filter(function (j) { return j > i; });
          index = after.length ? after[0] : (list.length ? list[list.length - 1] : 0);
        }
        refresh();
      });
    });
    if (prev) prev.addEventListener('click', function () { step(-1); });
    if (next) next.addEventListener('click', function () { step(1); });
    section.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') step(-1);
      if (e.key === 'ArrowRight') step(1);
    });
    this.refresh = refresh;
  }
  document.querySelectorAll('.rp-photo-gallery').forEach(function (section) {
    galleries.push(new Gallery(section));
  });

  /* ---------- start: language from the address (#en), else the saved choice, else French ---------- */
  var fromHash = validLang(location.hash.slice(1));
  if (fromHash) store(fromHash);
  applyLanguage(fromHash || readStored() || 'fr');
})();
