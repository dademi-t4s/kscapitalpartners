/* ==========================================================================
   KS Capital Partners — comportamenti di pagina
   Vanilla JS, nessuna dipendenza. Ogni funzione è progressiva: senza questo
   file la pagina resta interamente leggibile e navigabile.
   ========================================================================== */
(function () {
  'use strict';

  var root = document.documentElement;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)');

  function on(el, ev, fn, opt) { if (el) el.addEventListener(ev, fn, opt); }
  function all(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  /* --- Rivelazione allo scroll ------------------------------------------ */
  function initReveal() {
    var items = all('[data-reveal]');
    if (!('IntersectionObserver' in window) || reduced.matches) {
      items.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });

    // Rete di sicurezza: quanto è già nella finestra si mostra subito, senza
    // attendere il primo giro dell'osservatore. E se per qualsiasi motivo
    // qualcosa restasse nascosto pur essendo visibile, un controllo allo
    // scroll lo recupera: nessun contenuto può restare intrappolato a opacità 0.
    function sweep() {
      var h = window.innerHeight || document.documentElement.clientHeight;
      for (var i = items.length - 1; i >= 0; i--) {
        var el = items[i];
        if (el.classList.contains('is-in')) { items.splice(i, 1); continue; }
        var r = el.getBoundingClientRect();
        if (r.top < h * 0.94 && r.bottom > 0) {
          el.classList.add('is-in');
          io.unobserve(el);
          items.splice(i, 1);
        }
      }
      if (!items.length) window.removeEventListener('scroll', onScroll);
    }
    var pending = false;
    function onScroll() {
      if (pending) return;
      pending = true;
      requestAnimationFrame(function () { pending = false; sweep(); });
    }
    on(window, 'scroll', onScroll, { passive: true });
    on(window, 'resize', onScroll, { passive: true });
    sweep();
  }

  /* --- Titolo dell'hero, rivelato riga per riga ------------------------- */
  function initHeroTitle() {
    var title = document.querySelector('.hero .mask-lines');
    if (!title) return;
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { title.classList.add('is-in'); });
    });
  }

  /* --- Testata: compatta allo scroll, si ritira scendendo --------------- */
  function initHeader() {
    var header = document.getElementById('header');
    if (!header) return;
    var last = window.scrollY;
    var ticking = false;

    function update() {
      var y = window.scrollY;
      header.classList.toggle('is-stuck', y > 24);
      var goingDown = y > last && y > 320;
      if (!document.body.classList.contains('is-locked')) {
        header.classList.toggle('is-hidden', goingDown);
      }
      last = y;
      ticking = false;
    }
    on(window, 'scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    update();
  }

  /* --- Barra di avanzamento della lettura -------------------------------- */
  function initProgress() {
    var bar = document.querySelector('.progress__bar');
    if (!bar) return;
    var ticking = false;
    function update() {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.transform = 'scaleX(' + (h > 0 ? Math.min(window.scrollY / h, 1) : 0) + ')';
      ticking = false;
    }
    on(window, 'scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    on(window, 'resize', update, { passive: true });
    update();
  }

  /* --- Menu a scomparsa -------------------------------------------------- */
  function initDrawer() {
    var burger = document.querySelector('.burger');
    var drawer = document.getElementById('drawer');
    if (!burger || !drawer) return;
    var links = all('.drawer__link', drawer);

    function setOpen(open) {
      burger.setAttribute('aria-expanded', String(open));
      drawer.classList.toggle('is-open', open);
      document.body.classList.toggle('is-locked', open);
      if (open) { drawer.removeAttribute('inert'); } else { drawer.setAttribute('inert', ''); }
      links.forEach(function (l, i) {
        l.style.transitionDelay = open ? (140 + i * 55) + 'ms' : '0ms';
      });
      if (open) {
        var first = drawer.querySelector('a');
        if (first) first.focus({ preventScroll: true });
      } else {
        burger.focus({ preventScroll: true });
      }
    }

    on(burger, 'click', function () {
      setOpen(burger.getAttribute('aria-expanded') !== 'true');
    });
    links.forEach(function (l) { on(l, 'click', function () { setOpen(false); }); });
    on(document, 'keydown', function (ev) {
      if (ev.key === 'Escape' && burger.getAttribute('aria-expanded') === 'true') setOpen(false);
    });
    // Trattiene il fuoco dentro al menu aperto
    on(drawer, 'keydown', function (ev) {
      if (ev.key !== 'Tab') return;
      var f = all('a[href], button:not([disabled])', drawer);
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (ev.shiftKey && document.activeElement === first) { ev.preventDefault(); last.focus(); }
      else if (!ev.shiftKey && document.activeElement === last) { ev.preventDefault(); first.focus(); }
    });
    var mq = window.matchMedia('(min-width: 961px)');
    (mq.addEventListener ? mq.addEventListener.bind(mq, 'change') : mq.addListener.bind(mq))(
      function (m) { if (m.matches) setOpen(false); });
  }

  /* --- Schede delle aree di attività ------------------------------------ */
  function initSectors() {
    all('.sector__toggle').forEach(function (btn) {
      var panel = document.getElementById(btn.getAttribute('aria-controls'));
      if (!panel) return;
      on(btn, 'click', function () {
        var open = btn.getAttribute('aria-expanded') === 'true';
        // una scheda alla volta
        all('.sector__toggle').forEach(function (other) {
          if (other === btn) return;
          other.setAttribute('aria-expanded', 'false');
          other.closest('.sector').classList.remove('is-open');
          var p = document.getElementById(other.getAttribute('aria-controls'));
          if (p) { p.style.height = '0px'; p.hidden = true; }
        });
        btn.setAttribute('aria-expanded', String(!open));
        btn.closest('.sector').classList.toggle('is-open', !open);
        if (open) {
          panel.style.height = panel.scrollHeight + 'px';
          requestAnimationFrame(function () { panel.style.height = '0px'; });
          window.setTimeout(function () {
            if (btn.getAttribute('aria-expanded') === 'false') panel.hidden = true;
          }, reduced.matches ? 0 : 420);
        } else {
          panel.hidden = false;
          panel.style.height = '0px';
          requestAnimationFrame(function () { panel.style.height = panel.scrollHeight + 'px'; });
        }
      });
      on(panel, 'transitionend', function (ev) {
        if (ev.propertyName === 'height' && btn.getAttribute('aria-expanded') === 'true') {
          panel.style.height = 'auto';
        }
      });
    });
  }

  /* --- Voce di menu attiva in base alla sezione visibile ----------------- */
  function initScrollSpy() {
    var links = all('.nav__link[data-nav]').concat(all('.rail__item[data-rail]'));
    if (!links.length || !('IntersectionObserver' in window)) return;
    var key = function (l) { return l.getAttribute('data-nav') || l.getAttribute('data-rail'); };
    var map = {};
    links.forEach(function (l) { map[key(l)] = l; });
    var sections = Object.keys(map)
      .map(function (id) { return document.getElementById(id); })
      .filter(Boolean);
    if (!sections.length) return;

    var visible = {};
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { visible[en.target.id] = en.isIntersecting ? en.intersectionRatio : 0; });
      var best = null, bestRatio = 0;
      Object.keys(visible).forEach(function (id) {
        if (visible[id] > bestRatio) { bestRatio = visible[id]; best = id; }
      });
      links.forEach(function (l) {
        if (key(l) === best && bestRatio > 0) l.setAttribute('aria-current', 'true');
        else l.removeAttribute('aria-current');
      });
    }, { threshold: [0.12, 0.4, 0.75], rootMargin: '-20% 0px -45% 0px' });
    sections.forEach(function (s) { io.observe(s); });
  }

  /* --- Bagliore che segue il puntatore ----------------------------------- */
  function initSpotlight() {
    if (!fine.matches || reduced.matches) return;
    root.classList.add('has-pointer');
    var x = 0, y = 0, pending = false;
    on(window, 'pointermove', function (ev) {
      x = ev.clientX; y = ev.clientY;
      if (pending) return;
      pending = true;
      requestAnimationFrame(function () {
        root.style.setProperty('--mx', x + 'px');
        root.style.setProperty('--my', y + 'px');
        pending = false;
      });
    }, { passive: true });
  }

  /* --- Copia negli appunti ----------------------------------------------- */
  function initCopy() {
    all('.copy').forEach(function (btn) {
      var label = btn.querySelector('.copy__text');
      var done = btn.getAttribute('data-done');
      var idle = btn.getAttribute('data-label');
      on(btn, 'click', function () {
        var value = btn.getAttribute('data-copy');
        var finish = function () {
          btn.classList.add('is-done');
          if (label) label.textContent = done;
          window.setTimeout(function () {
            btn.classList.remove('is-done');
            if (label) label.textContent = idle;
          }, 2200);
        };
        if (navigator.clipboard && window.isSecureContext) {
          navigator.clipboard.writeText(value).then(finish, function () {});
        } else {
          var ta = document.createElement('textarea');
          ta.value = value; ta.setAttribute('readonly', '');
          ta.style.cssText = 'position:absolute;left:-9999px';
          document.body.appendChild(ta); ta.select();
          try { document.execCommand('copy'); finish(); } catch (err) {}
          document.body.removeChild(ta);
        }
      });
    });
  }

  /* --- Parallasse leggera sui fondali ------------------------------------ */
  function initParallax() {
    if (reduced.matches) return;
    var layers = all('[data-parallax]');
    if (!layers.length) return;
    var ticking = false;
    function update() {
      var vh = window.innerHeight;
      layers.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) return;
        var progress = (r.top + r.height / 2 - vh / 2) / vh;
        var depth = parseFloat(el.getAttribute('data-parallax')) || 0.12;
        el.style.setProperty('--py', (-progress * depth * 100).toFixed(2) + 'px');
      });
      ticking = false;
    }
    on(window, 'scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    on(window, 'resize', update, { passive: true });
    update();
  }

  /* --- Luce radente sul titolo dell'hero ---------------------------------
     Parte quando le righe hanno finito di salire, e al termine il titolo
     torna a colore pieno: nessun testo trasparente residuo. */
  function initRake() {
    var title = document.querySelector('.hero__title.rake');
    if (!title) return;
    // @property è ciò che rende interpolabile la percentuale: senza, la lama
    // non si muoverebbe e il titolo resterebbe spento. registerProperty è il
    // segnale affidabile del supporto (CSS.supports su una custom property
    // risponde sempre di sì e non serve a nulla).
    var supported = window.CSS && CSS.supports && ('registerProperty' in CSS) &&
      (CSS.supports('background-clip', 'text') || CSS.supports('-webkit-background-clip', 'text'));
    if (!supported || reduced.matches) { title.classList.add('rake-done'); return; }
    window.setTimeout(function () { title.classList.add('is-lit'); }, 1350);
    window.setTimeout(function () { title.classList.add('rake-done'); }, 3000);
  }

  /* --- Indice laterale: compare una volta lasciata l'apertura ------------ */
  function initRail() {
    var rail = document.querySelector('.rail');
    if (!rail) return;
    var ticking = false;
    function update() {
      rail.classList.toggle('is-visible', window.scrollY > window.innerHeight * 0.6);
      ticking = false;
    }
    on(window, 'scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    update();
  }

  function init() {
    initReveal(); initHeroTitle(); initRake(); initRail(); initHeader(); initProgress();
    initDrawer(); initSectors(); initScrollSpy(); initSpotlight();
    initCopy(); initParallax();
  }

  window.__ksReady = true;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
