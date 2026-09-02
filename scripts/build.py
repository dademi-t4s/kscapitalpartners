#!/usr/bin/env python3
"""Genera le pagine statiche di KS Capital Partners in italiano e inglese.

    python3 scripts/build.py

Legge scripts/copy.json (una voce per chiave, con testo 'it' ed 'en') e scrive
index.html, en/index.html e le pagine legali. Le pagine prodotte sono HTML
statico puro: nessun runtime, nessuna dipendenza.
"""
import json, os, pathlib, re, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
COPY = json.load(open(ROOT / "scripts" / "copy.json", encoding="utf-8"))
SITE = "https://www.kscapitalpartners.it"

# Gli indirizzi assoluti servono solo a canonical, hreflang, og:url e ai dati
# strutturati: sono l'indirizzo definitivo del sito. Tutto ciò che il browser
# deve scaricare o seguire usa invece percorsi relativi, così le pagine
# funzionano alla radice di un dominio, dentro una sottocartella e anche
# aperte direttamente dal disco.
# Il sito è in inglese. I testi italiani restano in copy.json: per riattivare
# la versione italiana basta rimettere la voce "it" qui sotto e in write().
LANGS = {
    "en": {"dir": "", "abs": "/", "up": ""},
}

LINKS = {
    "en": {"home_en": "index.html", "legal_en": "legal.html"},
}


def asset(lang, path):
    """Percorso di una risorsa, relativo alla profondità della pagina."""
    return LANGS[lang]["up"] + path.lstrip("/")


def home(lang, of=None):
    return LINKS[lang]["home_" + (of or lang)]


def legal(lang, of=None):
    return LINKS[lang]["legal_" + (of or lang)]


EMAIL = "d.kapo@kscapitalpartners.it"
PHONE = "+39 328 702 3109"
PHONE_HREF = "+393287023109"

# Dati d'iscrizione, obbligatori sul sito di una S.r.l. per l'art. 2250 c.c.
COMPANY = {
    "legal_name": "KS Capital Partners S.r.l.",
    "street":     "Via Tommaso Grossi 2",
    "postcode":   "20121",
    "city":       "Milano",
    "province":   "MI",
    "country":    "IT",
    "vat":        "14697790963",
    "rea":        "MI - 2801568",
    "pec":        "kscapitalpartners@pec.it",
}

NAV = [
    ("home",     {"it": "Home",             "en": "Home"}),
    ("about",    {"it": "Chi siamo",        "en": "About"}),
    ("focus",    {"it": "Aree di attività", "en": "Focus Areas"}),
    ("approach", {"it": "Metodo",           "en": "Approach"}),
    ("network",  {"it": "Rete",             "en": "Network"}),
    ("contact",  {"it": "Contatti",         "en": "Contact"}),
]

UI = {
    "menu":        {"it": "Menu",                      "en": "Menu"},
    "close":       {"it": "Chiudi",                    "en": "Close"},
    "skip":        {"it": "Vai al contenuto",          "en": "Skip to content"},
    "lang_label":  {"it": "Lingua",                    "en": "Language"},
    "to_it":       {"it": "Italiano",                  "en": "Italian"},
    "to_en":       {"it": "Inglese",                   "en": "English"},
    "copy":        {"it": "Copia",                     "en": "Copy"},
    "copied":      {"it": "Copiato",                   "en": "Copied"},
    "regions":     {"it": "Aree geografiche",          "en": "Regions"},
    "counterp":    {"it": "Controparti",               "en": "Counterparties"},
    "close_panel": {"it": "Chiudi scheda",             "en": "Close panel"},
    "sector":      {"it": "Settore",                   "en": "Sector"},
    "back_home":   {"it": "Torna alla home",           "en": "Back to home"},
    "legal_title": {"it": "Note legali",               "en": "Legal"},
    "rail":        {"it": "Indice delle sezioni",      "en": "Section index"},
}



def t(key, lang, default=""):
    v = COPY.get(key)
    if not v:
        return default
    return v.get(lang) or v.get("en") or default


def e(s):
    return html.escape(s, quote=True)


def parts(key, lang):
    return [p.strip() for p in t(key, lang).split("|") if p.strip()]


# --- Icone lineari per i quattro pilastri --------------------------------
ICONS = {
    "reach": '<circle cx="16" cy="16" r="12.5"/><ellipse cx="16" cy="16" rx="5.6" ry="12.5"/>'
             '<path d="M3.9 12.2h24.2M3.9 19.8h24.2"/>',
    "discretion": '<rect x="6.5" y="14" width="19" height="14" rx="1.6"/>'
                  '<path d="M10.4 14V9.8a5.6 5.6 0 0 1 11.2 0V14"/><circle cx="16" cy="20.4" r="1.5"/>'
                  '<path d="M16 21.9v2.6"/>',
    "trust": '<path d="M2.5 17.4l5-5.2 4.6 4.1 3.9-3.6 3.9 3.6 4.6-4.1 5 5.2"/>'
             '<path d="M12.1 16.3l-3 3a2 2 0 0 0 2.9 2.8l.6-.6.9.9a2 2 0 0 0 2.9-2.8"/>'
             '<path d="M16.5 19.6l2.3 2.3a2 2 0 0 0 2.9-2.8l-2.3-2.3"/>',
    "results": '<circle cx="16" cy="16" r="12.5"/><circle cx="16" cy="16" r="7.4"/>'
               '<circle cx="16" cy="16" r="2.2"/><path d="M16 3.5v3.4M16 25.1v3.4M3.5 16h3.4M25.1 16h3.4"/>',
}


def icon(name):
    return (f'<svg class="pillar__icon" viewBox="0 0 32 32" fill="none" stroke="currentColor" '
            f'stroke-width="1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            f'{ICONS[name]}</svg>')


PHOTO_SLOTS = ("hero", "focus-oil", "focus-art", "focus-stone",
               "about", "network", "cta-texture")


def image_size(path):
    """Larghezza e altezza lette dall'intestazione del file.

    Gli attributi width/height fissano il rapporto d'aspetto e impediscono
    lo scatto del layout mentre la fotografia carica: vanno letti dal file,
    non ipotizzati, altrimenti si sfasano a ogni ricompressione."""
    with open(path, "rb") as fh:
        head = fh.read(2)
        if head == b"\xff\xd8":                       # JPEG
            while True:
                b = fh.read(1)
                while b and b != b"\xff":
                    b = fh.read(1)
                marker = fh.read(1)
                while marker == b"\xff":
                    marker = fh.read(1)
                if not marker:
                    return None
                if marker[0] in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6,
                                 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    fh.read(3)
                    h = int.from_bytes(fh.read(2), "big")
                    w = int.from_bytes(fh.read(2), "big")
                    return w, h
                seg = int.from_bytes(fh.read(2), "big")
                fh.seek(seg - 2, 1)
        fh.seek(0)
        if fh.read(8) == b"\x89PNG\r\n\x1a\n":       # PNG
            fh.seek(16)
            return (int.from_bytes(fh.read(4), "big"),
                    int.from_bytes(fh.read(4), "big"))
    return None


def photo(lang, slot, priority=False, css_class=""):
    """Restituisce il tag <img> solo se il file esiste: finché manca, resta
    visibile il fondale procedurale e il layout non cambia di una riga."""
    for ext in ("webp", "jpg", "png"):
        rel = f"assets/img/{slot}.{ext}"
        if (ROOT / rel).exists():
            size = image_size(ROOT / rel)
            if not size:
                return ""
            w, h = size
            cls = f' class="{css_class}"' if css_class else ""
            attrs = (f'src="{asset(lang, rel)}" width="{w}" height="{h}" '
                     f'alt="" decoding="async"{cls}') 
            if priority:
                attrs += ' fetchpriority="high"'
            else:
                attrs += ' loading="lazy"'
            return f"<img {attrs}>"
    return ""


ARROW = ('<svg class="btn__arrow" width="22" height="8" viewBox="0 0 22 8" fill="none" '
         'aria-hidden="true"><path d="M0 4h20M17 1l3.4 3-3.4 3" stroke="currentColor" '
         'stroke-width="1"/></svg>')

LOGO_MARK = open(ROOT / "assets" / "img" / "logo-mark.svg", encoding="utf-8").read()
LOGO_MARK = re.sub(r'\s*role="img"[^>]*?aria-label="[^"]*"', '', LOGO_MARK)
LOGO_MARK = LOGO_MARK.replace("<svg ", '<svg class="logo__mark" aria-hidden="true" ', 1).strip()


def logo(lang, tag="a", href="#top"):
    label = "KS Capital Partners"
    attrs = f' href="{href}"' if tag == "a" else ""
    return f'''<{tag} class="logo"{attrs} aria-label="{label}">
        {LOGO_MARK}
        <span class="logo__type">
          <span class="logo__name">KS Capital</span>
          <span class="logo__sub">Partners</span>
        </span>
      </{tag}>'''


# --- Testa del documento --------------------------------------------------
def head(lang, title, desc, path):
    o = LANGS[lang]
    return f'''<!doctype html>
<html lang="{lang}" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta name="theme-color" content="#0b0b0d">
<meta name="robots" content="index, follow, max-image-preview:large">

<meta property="og:type" content="website">
<meta property="og:site_name" content="KS Capital Partners">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/assets/img/og-image-{lang}.jpg">
<meta property="og:image:alt" content="{e(title)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">

<link rel="icon" href="{asset(lang, "favicon.svg")}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{asset(lang, "assets/img/apple-touch-icon.png")}">
<link rel="manifest" href="{asset(lang, "site.webmanifest")}">

<link rel="preload" as="font" type="font/woff2" href="{asset(lang, "assets/fonts/cormorant-garamond-300-latin.woff2")}" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="{asset(lang, "assets/fonts/jost-300-latin.woff2")}" crossorigin>
<link rel="stylesheet" href="{asset(lang, "assets/css/fonts.css")}">
<link rel="stylesheet" href="{asset(lang, "assets/css/style.css")}">
<script>
document.documentElement.className='js';
/* Qualsiasi copia che non stia sul dominio ufficiale — un'anteprima su
   github.io, netlify.app, o un file aperto dal disco — si esclude da sola
   dai motori di ricerca. Sul dominio vero questa riga non fa nulla. */
(function(h){{if(h&&h!=='www.kscapitalpartners.it'&&h!=='kscapitalpartners.it'){{
 var m=document.createElement('meta');m.name='robots';m.content='noindex,nofollow';
 document.head.appendChild(m);}}}})(location.hostname);
setTimeout(function(){{if(!window.__ksReady){{document.documentElement.className='';}}}},4000);
</script>
</head>
<body id="top">
<a class="skip-link" href="#main">{e(UI["skip"][lang])}</a>
<div class="grain" aria-hidden="true"></div>
<div class="spotlight" aria-hidden="true"></div>
<div class="progress" aria-hidden="true"><span class="progress__bar"></span></div>
'''


# --- Testata e menu -------------------------------------------------------
def header(lang, active="home"):
    o = LANGS[lang]
    links = "".join(
        f'<a class="nav__link" href="{"#" + k if k != "home" else home(lang)}"'
        f'{" aria-current=\"true\"" if k == active else ""} data-nav="{k}">{e(lbl[lang])}</a>'
        for k, lbl in NAV)
    drawer_links = "".join(
        f'<a class="drawer__link" href="{"#" + k if k != "home" else home(lang)}">'
        f'<span class="drawer__num">{i:02d}</span>{e(lbl[lang])}</a>'
        for i, (k, lbl) in enumerate(NAV, 1))
    rail_items = "".join(
        f'<a class="rail__item" href="{"#" + k if k != "home" else home(lang)}" '
        f'data-rail="{k}"><span class="rail__label">{e(lbl[lang])}</span>'
        f'<span class="rail__tick"></span></a>'
        for k, lbl in NAV)
    lang_switch = ""
    return f'''<header class="header" id="header">
  <div class="header__inner">
    {logo(lang, "a", home(lang))}
    <nav class="nav nav--desktop" aria-label="{e(UI["menu"][lang])}">
      {links}
      {lang_switch}
    </nav>
    <button class="burger" type="button" aria-expanded="false" aria-controls="drawer"
            aria-label="{e(UI["menu"][lang])}">
      <span class="burger__bar"></span><span class="burger__bar"></span><span class="burger__bar"></span>
    </button>
  </div>
</header>

<nav class="rail" aria-label="{e(UI["rail"][lang])}">
  {rail_items}
</nav>

<div class="drawer" id="drawer" inert>
  <nav class="drawer__nav" aria-label="{e(UI["menu"][lang])}">{drawer_links}</nav>
  <div class="drawer__foot">
    <a href="mailto:{EMAIL}">{EMAIL}</a>
    {lang_switch}
  </div>
</div>
'''


# --- Hero -----------------------------------------------------------------
def hero(lang):
    lines = parts("hero.title", lang)
    rendered = "".join(
        f'<span class="mask-lines__line"><span style="--line-delay:{i * 130}ms">{e(l)}</span></span>'
        for i, l in enumerate(lines))
    return f'''<section class="hero" id="home">
  <div class="hero__media figure art--hero" aria-hidden="true">
    <div class="hero__kb kenburns">{photo(lang, "hero", priority=True)}</div>
    <div class="hero__scrim"></div>
  </div>
  <div class="wrap hero__inner">
    <p class="eyebrow hero__eyebrow" data-reveal="fade">{e(t("hero.eyebrow", lang))}</p>
    <h1 class="hero__title mask-lines rake">{rendered}</h1>
    <hr class="rule hero__rule" data-reveal="rule" style="--reveal-delay:520ms">
    <p class="hero__body" data-reveal style="--reveal-delay:640ms">{e(t("hero.body", lang))}</p>
    <div class="hero__actions" data-reveal style="--reveal-delay:760ms">
      <a class="btn" href="#contact">{e(t("hero.cta_primary", lang))}{ARROW}</a>
      <a class="btn btn--ghost" href="#focus">{e(t("hero.cta_secondary", lang))}</a>
    </div>
  </div>
  <a class="hero__scroll" href="#focus" data-reveal style="--reveal-delay:900ms">
    <span>{e(t("hero.scroll_hint", lang))}</span>
    <span class="hero__scroll-line" aria-hidden="true"></span>
  </a>
</section>
'''


# --- Aree di attività -----------------------------------------------------
SECTORS = [("oil", "art--oil"), ("art", "art--art"), ("stone", "art--stone")]


def focus(lang):
    cards = []
    for i, (key, art) in enumerate(SECTORS):
        pts = "".join(f"<li>{e(p)}</li>" for p in parts(f"focus.{key}.points", lang))
        cards.append(f'''
    <article class="sector" data-reveal style="--reveal-delay:{i * 120}ms">
      <button class="sector__toggle" type="button" aria-expanded="false" aria-controls="panel-{key}">
        <span class="figure sector__media {art}" aria-hidden="true">{photo(lang, "focus-" + key)}</span>
        <span class="sector__body">
          <span class="sector__name">{e(t(f"focus.{key}.name", lang))}</span>
          <span class="sector__hr" aria-hidden="true"></span>
          <span class="sector__sub">{e(t(f"focus.{key}.sublabel", lang))}</span>
          <span class="sector__text">{e(t(f"focus.{key}.body", lang))}</span>
          <span class="link-arrow sector__cta">{e(t(f"focus.{key}.cta", lang))}{ARROW}</span>
        </span>
      </button>
      <div class="sector__panel" id="panel-{key}" hidden>
        <p class="sector__detail">{e(t(f"focus.{key}.detail", lang))}</p>
        <ul class="sector__points">{pts}</ul>
      </div>
    </article>''')
    return f'''<section class="section focus" id="focus">
  <div class="wrap">
    <div class="section__head focus__head">
      <div>
        <p class="eyebrow" data-reveal="fade">{e(t("focus.eyebrow", lang))}</p>
        <h2 class="focus__title" data-reveal>{e(t("focus.title", lang))}</h2>
      </div>
      <p class="focus__intro muted" data-reveal style="--reveal-delay:160ms">{e(t("focus.intro", lang))}</p>
    </div>
    <div class="sectors">{"".join(cards)}</div>
  </div>
</section>
'''


# --- Pilastri -------------------------------------------------------------
PILLARS = ["reach", "discretion", "trust", "results"]


def pillars(lang):
    items = "".join(f'''
    <li class="pillar" data-reveal style="--reveal-delay:{i * 110}ms">
      {icon(k)}
      <h3 class="pillar__name">{e(t(f"values.{k}.name", lang))}</h3>
      <span class="pillar__hr" aria-hidden="true"></span>
      <p class="pillar__text">{e(t(f"values.{k}.body", lang))}</p>
    </li>''' for i, k in enumerate(PILLARS))
    return f'''<section class="section section--tint pillars-section" aria-label="{e(t("about.eyebrow", lang))}">
  <div class="wrap"><ul class="pillars">{items}</ul></div>
</section>
'''


# --- Chi siamo ------------------------------------------------------------
def about(lang):
    stats = "".join(f'''
        <div class="stat" data-reveal style="--reveal-delay:{i * 110}ms">
          <span class="stat__value">{e(t(f"about.stat_{i}_value", lang))}</span>
          <span class="stat__label">{e(t(f"about.stat_{i}_label", lang))}</span>
        </div>''' for i in (1, 2, 3))
    return f'''<section class="section about" id="about">
  <div class="wrap about__grid">
    <div class="about__media figure art--about" data-reveal="scale" aria-hidden="true">{photo(lang, "about")}</div>
    <div class="about__col">
      <p class="eyebrow" data-reveal="fade">{e(t("about.eyebrow", lang))}</p>
      <h2 class="about__title" data-reveal>{e(t("about.title", lang))}</h2>
      <hr class="rule" data-reveal="rule" style="--reveal-delay:200ms">
      <p class="lead about__lead" data-reveal style="--reveal-delay:120ms">{e(t("about.lead", lang))}</p>
      <p class="prose" data-reveal style="--reveal-delay:200ms">{e(t("about.body_1", lang))}</p>
      <p class="prose" data-reveal style="--reveal-delay:260ms">{e(t("about.body_2", lang))}</p>
      <blockquote class="quote" data-reveal style="--reveal-delay:320ms">{e(t("about.quote", lang))}</blockquote>
      <div class="stats">{stats}</div>
    </div>
  </div>
</section>
'''


# --- Metodo ---------------------------------------------------------------
def approach(lang):
    steps = "".join(f'''
      <li class="step" data-reveal style="--reveal-delay:{i * 100}ms">
        <span class="step__num">{e(t(f"approach.step{i}.num", lang))}</span>
        <div class="step__body">
          <h3 class="step__name">{e(t(f"approach.step{i}.name", lang))}</h3>
          <p class="step__text muted">{e(t(f"approach.step{i}.body", lang))}</p>
        </div>
      </li>''' for i in (1, 2, 3, 4))
    return f'''<section class="section section--tint approach" id="approach">
  <div class="wrap">
    <div class="section__head approach__head">
      <div>
        <p class="eyebrow" data-reveal="fade">{e(t("approach.eyebrow", lang))}</p>
        <h2 data-reveal>{e(t("approach.title", lang))}</h2>
      </div>
      <p class="approach__intro muted" data-reveal style="--reveal-delay:140ms">{e(t("approach.intro", lang))}</p>
    </div>
    <ol class="steps">{steps}</ol>
    <p class="approach__note dim" data-reveal>{e(t("approach.note", lang))}</p>
  </div>
</section>
'''


# --- Rete -----------------------------------------------------------------
def network(lang):
    regions = "".join(f'<li data-reveal="left" style="--reveal-delay:{i * 70}ms">{e(r)}</li>'
                      for i, r in enumerate(parts("network.regions", lang)))
    sectors = "".join(f'<li data-reveal="left" style="--reveal-delay:{i * 70}ms">{e(s)}</li>'
                      for i, s in enumerate(parts("network.sectors", lang)))
    return f'''<section class="section network" id="network">
  <div class="network__bg figure art--network" aria-hidden="true">{photo(lang, "network")}</div>
  <div class="wrap network__grid">
    <div class="network__col">
      <p class="eyebrow" data-reveal="fade">{e(t("network.eyebrow", lang))}</p>
      <h2 data-reveal>{e(t("network.title", lang))}</h2>
      <hr class="rule" data-reveal="rule" style="--reveal-delay:200ms">
      <p class="prose" data-reveal style="--reveal-delay:140ms">{e(t("network.body", lang))}</p>
      <p class="network__note dim" data-reveal style="--reveal-delay:200ms">{e(t("network.disclaimer", lang))}</p>
    </div>
    <div class="network__lists">
      <div class="netlist">
        <h3 class="netlist__head">{e(UI["regions"][lang])}</h3>
        <ul class="netlist__items">{regions}</ul>
      </div>
      <div class="netlist">
        <h3 class="netlist__head">{e(UI["counterp"][lang])}</h3>
        <ul class="netlist__items">{sectors}</ul>
      </div>
    </div>
  </div>
</section>
'''


# --- Invito ---------------------------------------------------------------
def cta(lang):
    lines = parts("cta.title", lang)
    return f'''<section class="section cta" aria-label="{e(t("cta.button", lang))}">
  <div class="wrap">
    <div class="cta__band figure art--texture" data-reveal>{photo(lang, "cta-texture")}
      <div class="cta__inner">
        <h2 class="cta__title">{"<br>".join(e(l) for l in lines)}</h2>
        <p class="cta__body muted">{e(t("cta.body", lang))}</p>
        <a class="btn btn--solid cta__btn" href="#contact">{e(t("cta.button", lang))}{ARROW}</a>
      </div>
    </div>
  </div>
</section>
'''


# --- Contatti -------------------------------------------------------------
def contact(lang):
    rows = [
        (t("contact.email_label", lang),
         f'<a class="contact__email" href="mailto:{EMAIL}">{EMAIL}</a>'
         f'<button class="copy" type="button" data-copy="{EMAIL}" '
         f'data-label="{e(UI["copy"][lang])}" data-done="{e(UI["copied"][lang])}">'
         f'<span class="copy__text">{e(UI["copy"][lang])}</span></button>'),
        (t("contact.phone_label", lang),
         f'<a class="contact__phone" href="tel:{PHONE_HREF}">{e(PHONE)}</a>'),
        (t("contact.location_label", lang), e(t("contact.location_value", lang))),
    ]
    items = "".join(f'''
        <div class="cinfo" data-reveal style="--reveal-delay:{i * 110}ms">
          <dt class="cinfo__key">{e(k)}</dt>
          <dd class="cinfo__val">{v}</dd>
        </div>''' for i, (k, v) in enumerate(rows))
    return f'''<section class="section section--tint contact" id="contact">
  <div class="wrap contact__grid">
    <div class="contact__col">
      <p class="eyebrow" data-reveal="fade">{e(t("contact.eyebrow", lang))}</p>
      <h2 data-reveal>{e(t("contact.title", lang))}</h2>
      <hr class="rule" data-reveal="rule" style="--reveal-delay:200ms">
      <p class="prose" data-reveal style="--reveal-delay:140ms">{e(t("contact.body", lang))}</p>
      <p class="contact__note dim" data-reveal style="--reveal-delay:200ms">{e(t("contact.response_note", lang))}</p>
    </div>
    <dl class="contact__info">{items}
      <div class="contact__cta" data-reveal style="--reveal-delay:340ms">
        <a class="btn btn--solid" href="mailto:{EMAIL}">{e(t("cta.button", lang))}{ARROW}</a>
      </div>
    </dl>
  </div>
</section>
'''


# --- Piede ----------------------------------------------------------------
def footer(lang):
    o = LANGS[lang]
    legal_href = legal(lang)
    nav_links = "".join(
        f'<li><a href="{"#" + k if k != "home" else home(lang)}">{e(lbl[lang])}</a></li>'
        for k, lbl in NAV)
    legal_links = "".join(f'<li><a href="{legal_href}#{anchor}">{e(t(key, lang))}</a></li>'
                          for anchor, key in [("privacy", "footer.privacy_link"),
                                              ("cookie", "footer.cookie_link"),
                                              ("terms", "footer.terms_link")])
    return f'''<footer class="footer">
  <div class="wrap footer__grid">
    <div class="footer__brand">
      {logo(lang, "a", home(lang))}
      <p class="footer__tagline dim">{e(t("footer.tagline", lang))}</p>
    </div>
    <nav class="footer__col" aria-label="{e(t("footer.nav_heading", lang))}">
      <h2 class="footer__head">{e(t("footer.nav_heading", lang))}</h2>
      <ul>{nav_links}</ul>
    </nav>
    <nav class="footer__col" aria-label="{e(t("footer.legal_heading", lang))}">
      <h2 class="footer__head">{e(t("footer.legal_heading", lang))}</h2>
      <ul>{legal_links}</ul>
    </nav>
    <div class="footer__col">
      <h2 class="footer__head">{e(t("contact.email_label", lang))}</h2>
      <ul><li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li class="dim">{e(t("contact.location_value", lang))}</li></ul>
    </div>
  </div>
  <div class="wrap footer__legalinfo">
    <h2 class="footer__head">{e(t("footer.company_heading", lang))}</h2>
    <p>
      <b>{COMPANY["legal_name"]}</b>
      <span>{e(t("company.registered_office", lang))}: {COMPANY["street"]},
        {COMPANY["postcode"]} {COMPANY["city"]} ({COMPANY["province"]}), Italy</span>
      <span>{e(t("company.vat", lang))} {COMPANY["vat"]}</span>
      <span>{e(t("company.rea", lang))} {COMPANY["rea"]} — {e(t("company.registry", lang))}</span>
      <span>{e(t("company.pec", lang))} <a href="mailto:{COMPANY["pec"]}">{COMPANY["pec"]}</a></span>
    </p>
  </div>
  <div class="wrap footer__bar">
    <p class="dim">{e(t("footer.rights", lang))}</p>
    <a class="footer__top" href="#top">{e(UI["back_home"][lang])}
      <svg width="10" height="12" viewBox="0 0 10 12" fill="none" aria-hidden="true">
        <path d="M5 11.5V1M1 4.4 5 .6l4 3.8" stroke="currentColor" stroke-width="1"/></svg>
    </a>
  </div>
</footer>
<script src="{asset(lang, "assets/js/main.js")}" defer></script>
</body>
</html>
'''


# --- Dati strutturati -----------------------------------------------------
def jsonld(lang, desc):
    o = LANGS[lang]
    services = [{
        "@type": "Service",
        "name": t(f"focus.{k}.name", lang),
        "serviceType": t(f"focus.{k}.sublabel", lang),
        "description": t(f"focus.{k}.body", lang),
        "provider": {"@id": f"{SITE}/#organization"},
        "areaServed": parts("network.regions", lang),
    } for k, _ in SECTORS]
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": f"{SITE}/#organization",
                "name": "KS Capital Partners",
                "legalName": COMPANY["legal_name"],
                "url": SITE + "/",
                "description": desc,
                "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/img/icon-512.png",
                         "width": 512, "height": 512},
                "email": EMAIL,
                "telephone": PHONE,
                "vatID": COMPANY["vat"],
                "taxID": COMPANY["vat"],
                "identifier": {"@type": "PropertyValue", "name": "REA",
                               "value": COMPANY["rea"]},
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": COMPANY["street"],
                    "postalCode": COMPANY["postcode"],
                    "addressLocality": COMPANY["city"],
                    "addressRegion": COMPANY["province"],
                    "addressCountry": COMPANY["country"],
                },
                "contactPoint": [{
                    "@type": "ContactPoint",
                    "contactType": "business enquiries",
                    "email": EMAIL,
                    "telephone": PHONE,
                    "availableLanguage": ["it", "en"],
                }],
                "knowsLanguage": ["it", "en"],
            },
            {
                "@type": "WebSite",
                "@id": f"{SITE}/#website",
                "url": SITE + "/",
                "name": "KS Capital Partners",
                "inLanguage": lang,
                "publisher": {"@id": f"{SITE}/#organization"},
            },
            {
                "@type": "WebPage",
                "@id": f"{SITE}{o['abs']}#webpage",
                "url": SITE + o["abs"],
                "name": t("hero.title", lang).replace(" | ", " "),
                "description": desc,
                "inLanguage": lang,
                "isPartOf": {"@id": f"{SITE}/#website"},
                "about": {"@id": f"{SITE}/#organization"},
            },
            *services,
        ],
    }
    return ('<script type="application/ld+json">'
            + json.dumps(graph, ensure_ascii=False, separators=(",", ":"))
            + "</script>\n")


META = {
    "it": ("KS Capital Partners — Introduttore d'affari indipendente",
           "Introduttore d'affari indipendente. Presentiamo controparti qualificate nelle "
           "commodities fisiche, nell'arte e nella pietra naturale, con riservatezza assoluta."),
    "en": ("KS Capital Partners — Independent Business Introducer",
           "Independent business introducer. We bring qualified counterparties together in "
           "physical commodities, fine art and natural stone, in absolute confidence."),
}


def build_home(lang):
    title, desc = META[lang]
    o = LANGS[lang]
    return (head(lang, title, desc, o["abs"])
            + jsonld(lang, desc)
            + header(lang)
            + '<main id="main">\n'
            + hero(lang) + focus(lang) + pillars(lang) + about(lang)
            + approach(lang) + network(lang) + cta(lang) + contact(lang)
            + "</main>\n"
            + footer(lang))


# --- Pagina legale --------------------------------------------------------
def build_legal(lang):
    o = LANGS[lang]
    title = f"{UI['legal_title'][lang]} — KS Capital Partners"
    desc = t("legal.privacy_title", lang) or UI["legal_title"][lang]
    sections = [("privacy", "legal.privacy_title", "legal.privacy_body"),
                ("cookie", "legal.cookie_title", "legal.cookie_body"),
                ("terms", "legal.terms_title", "legal.terms_body")]
    nav = "".join(f'<li><a href="#{a}">{e(t(ti, lang))}</a></li>' for a, ti, _ in sections)
    body = ""
    for anchor, ti, bo in sections:
        paras = "".join(f"<p>{e(p.strip())}</p>"
                        for p in re.split(r"\n{2,}|(?<=\.)\n", t(bo, lang)) if p.strip())
        body += (f'<section class="legal__section" id="{anchor}">'
                 f'<h2>{e(t(ti, lang))}</h2><div class="legal__body">{paras}</div></section>')
    notice = t("legal.disclaimer_notice", lang)
    href = LANGS[lang]["abs"] + "legal.html"
    return (head(lang, title, desc, href)
            + header(lang, active=None)
            + f'''<main id="main" class="legal">
  <div class="wrap legal__wrap">
    <header class="legal__head">
      <p class="eyebrow">{e(UI["legal_title"][lang])}</p>
      <h1>{e(UI["legal_title"][lang])}</h1>
      <hr class="rule">
      {f'<p class="legal__notice">{e(notice)}</p>' if notice else ''}
    </header>
    <nav class="legal__toc" aria-label="{e(UI["legal_title"][lang])}"><ul>{nav}</ul></nav>
    {body}
  </div>
</main>
'''
            + footer(lang))


# --- Pagina 404 -----------------------------------------------------------
NOT_FOUND = {
    "it": ("Pagina non trovata", "404",
           "L'indirizzo richiesto non esiste, o non esiste più. "
           "Dalla home si raggiunge ogni sezione del sito.",
           "Torna alla home"),
    "en": ("Page not found", "404",
           "The address requested does not exist, or no longer does. "
           "Every section of the site is reachable from the home page.",
           "Back to home"),
}


def build_404(lang):
    title, code, body, cta = NOT_FOUND[lang]
    o = LANGS[lang]
    return (head(lang, f"{title} — KS Capital Partners", body, o["abs"])
            .replace('<meta name="robots" content="index, follow, max-image-preview:large">',
                     '<meta name="robots" content="noindex, follow">')
            + header(lang, active=None)
            + f'''<main id="main" class="notfound">
  <div class="notfound__media figure art--hero" aria-hidden="true"></div>
  <div class="wrap notfound__inner">
    <p class="eyebrow">{code}</p>
    <h1 class="notfound__title">{e(title)}</h1>
    <hr class="rule">
    <p class="lead">{e(body)}</p>
    <p class="notfound__actions">
      <a class="btn" href="{home(lang)}">{e(cta)}{ARROW}</a>
    </p>
  </div>
</main>
'''
            + footer(lang))


# --- Scrittura ------------------------------------------------------------
def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"  {rel:<26} {len(content) / 1024:5.1f} KB"


out = [
    write("index.html", build_home("en")),
    write("legal.html", build_legal("en")),
    write("404.html", build_404("en")),
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n"),
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
          'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
          + "".join(
              f'  <url><loc>{SITE}{u}</loc>'
              f'<changefreq>monthly</changefreq><priority>{pr}</priority></url>\n'
              for u, pr in [("/", "1.0"), ("/legal.html", "0.3")])
          + "</urlset>\n"),
    write("site.webmanifest", json.dumps({
        "name": "KS Capital Partners", "short_name": "KS Capital",
        "start_url": ".", "display": "standalone",
        "background_color": "#0b0b0d", "theme_color": "#0b0b0d",
        "icons": [{"src": "assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}],
    }, indent=2)),
]
print("\n".join(out))
print(f"\n  {len(COPY)} stringhe · 2 lingue")
