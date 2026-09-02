#!/usr/bin/env python3
"""Compone le immagini di anteprima social (1200x630) per le due lingue.

    python3 scripts/make-og.py

Usa il titolo reale della home e il marchio del sito, e le renderizza con
Chrome in headless. Nessun servizio esterno.
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
COPY = json.load(open(ROOT / "scripts" / "copy.json", encoding="utf-8"))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
MARK = (ROOT / "assets" / "img" / "logo-mark.svg").read_text(encoding="utf-8")
MARK = MARK.replace("<svg ", '<svg style="width:74px;height:auto;color:#d8b476" ', 1)

SECTORS = {"it": "Materie prime · Arte · Pietra naturale",
           "en": "Commodities · Fine Art · Natural Stone"}

TPL = """<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="{root}/assets/css/fonts.css">
<style>
  *{{box-sizing:border-box;margin:0}}
  body{{width:1200px;height:630px;overflow:hidden;position:relative;background:#0b0b0d;
       font-family:'Jost',sans-serif;--logo-knockout:#0b0b0d}}
  .bg{{position:absolute;inset:0;background:url('{root}/{bg}') center/cover}}
  .veil{{position:absolute;inset:0;background:
      linear-gradient(100deg,#0b0b0d 0%,rgba(11,11,13,.96) 34%,rgba(11,11,13,.58) 56%,rgba(11,11,13,.18) 100%)}}
  .grain{{position:absolute;inset:0;opacity:.05;mix-blend-mode:overlay;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.82' numOctaves='3'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)'/%3E%3C/svg%3E")}}
  .in{{position:absolute;inset:0;padding:64px 78px;display:flex;flex-direction:column;justify-content:space-between;gap:28px}}
  .top{{display:flex;align-items:center;gap:18px}}
  .name{{font-family:'Cormorant Garamond',serif;font-size:30px;font-weight:400;
        letter-spacing:.14em;text-transform:uppercase;color:#f2efe9;line-height:1}}
  .sub{{font-size:11px;letter-spacing:.42em;text-transform:uppercase;color:#8a857f;margin-top:9px}}
  h1{{font-family:'Cormorant Garamond',serif;font-weight:300;font-size:54px;line-height:1.1;
      letter-spacing:-.016em;color:#f2efe9;max-width:17ch}}
  .rule{{width:76px;height:1px;background:#d8b476;margin:30px 0 24px}}
  .tag{{font-size:15px;letter-spacing:.24em;text-transform:uppercase;color:#d8b476}}
</style>
<div class="bg"></div><div class="veil"></div><div class="grain"></div>
<div class="in">
  <div class="top">{mark}<div><div class="name">KS Capital</div><div class="sub">Partners</div></div></div>
  <div><h1>{title}</h1><div class="rule"></div><div class="tag">{tag}</div></div>
</div>"""

# La fotografia della hero se esiste, altrimenti la scena SVG: in entrambi i
# casi l'anteprima social è compiuta.
BG = next((f"assets/img/hero.{x}" for x in ("jpg", "webp", "png")
           if (ROOT / f"assets/img/hero.{x}").exists()), "assets/img/art-hero.svg")
print(f"  fondale: {BG}")

for lang in ("it", "en"):
    title = COPY["hero.title"][lang].replace(" | ", " ")
    html = TPL.format(root=ROOT.as_uri(), mark=MARK, title=title, tag=SECTORS[lang], bg=BG)
    src = ROOT / f".og-{lang}.html"
    src.write_text(html, encoding="utf-8")
    out = ROOT / "assets" / "img" / f"og-image-{lang}.png"  # convertito poi in .jpg
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--virtual-time-budget=8000", f"--screenshot={out}",
                    "--window-size=1200,630", src.as_uri()],
                   check=True, capture_output=True)
    src.unlink()
    print(f"  ✓ og-image-{lang}.png  {out.stat().st_size // 1024} KB")

# Le anteprime social viaggiano meglio in JPEG: stessa resa, un quinto del peso.
for lang in ("it", "en"):
    png = ROOT / "assets" / "img" / f"og-image-{lang}.png"
    jpg = png.with_suffix(".jpg")
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "86",
                    str(png), "--out", str(jpg)], check=True, capture_output=True)
    png.unlink()
    print(f"  ✓ og-image-{lang}.jpg  {jpg.stat().st_size // 1024} KB")
