# KS Capital Partners — sito vetrina

Sito statico per **https://kscapitalpartners.it**, in inglese.
HTML, CSS e JavaScript puri: nessun framework, nessun passaggio di compilazione
lato server, nessuna richiesta a server di terze parti.

- **`PUBBLICAZIONE.md`** — dove e come è pubblicato, come aggiornarlo.
- **`INFO-CLIENTE.md`** — cosa è stato chiesto al cliente e cosa resta aperto.

---

## Regole sui testi (dal cliente, ottobre 2026)

- **KS può operare su mandato.** Mai scrivere o far intendere "nessun mandato".
  Indipendenza significa *nessuna posizione propria nell'operazione*: KS non
  diventa proprietaria dei beni, né principal, salvo diverso accordo espresso.
- **"Advisory" è consulenza commerciale** e supporto alle operazioni, mai
  consulenza finanziaria regolamentata. KS non riceve né detiene fondi dei
  clienti e non presta servizi finanziari regolamentati.
- Le verifiche specialistiche (bancarie, legali, regolamentari) restano a banche
  e professionisti: il sito non deve far pensare che le faccia KS.
- Niente numeri, loghi di clienti, testimonianze, operazioni o relazioni
  istituzionali non autorizzate. Niente CTA generiche ("Get started", "Book a call").

I testi legali (privacy, cookie, condizioni d'uso) vanno comunque fatti
validare da un legale.

---

## Struttura

```
index.html  legal.html  404.html     generati da scripts/build.py
robots.txt  sitemap.xml  site.webmanifest  favicon.svg
CNAME                                dominio per GitHub Pages
_config.yml                          cosa GitHub Pages NON pubblica

assets/
  css/style.css         foglio unico: token, movimento, componenti, sezioni
  css/fonts.css         @font-face dei caratteri ospitati in locale
  js/main.js            comportamenti (rivelazioni, menu, indice, schede)
  fonts/                Cormorant Garamond + Jost, font variabili, subset latin
  img/                  marchio, icone, scene SVG, fotografie, anteprima social
  img/_raw/             originali a piena risoluzione (esclusi da git)

scripts/
  build.py              genera le pagine da copy.json
  copy.json             tutti i testi (inglese pubblicato, italiano tenuto pronto)
  dev-server.py         anteprima locale con ricarica automatica
  generate-images.sh    genera le fotografie con OpenAI (gpt-image-2)
  optimize-images.sh    prepara le versioni web (JPEG, WebP, AVIF)
  image-prompts.json    i prompt delle fotografie, con stile e negativi
  make-og.py            ricompone l'anteprima social
```

## Anteprima locale

```bash
python3 scripts/dev-server.py
```
→ http://localhost:8747/ — la pagina si ricarica da sola a ogni salvataggio.

Parametri utili solo in locale, che **non finiscono nei file pubblicati**:
`?review=1` disattiva le animazioni per esaminare il layout, `?audit=1` controlla
overflow orizzontale e contrasto e ne stampa l'esito in pagina, `?spy=1` collauda
l'evidenziazione del menu allo scroll.

## Modificare i testi

Tutti i contenuti stanno in `scripts/copy.json`, una chiave per stringa con la
versione `en` (pubblicata) e quella `it`. Email, telefono e dati societari stanno
in cima a `scripts/build.py`. Si modifica e si rilancia `python3 scripts/build.py`:
l'HTML non si tocca a mano, altrimenti la modifica si perde alla generazione
successiva. Per riattivare l'italiano basta rimettere la voce `it` in `LANGS`.

## Fotografie

Sette fotografie, tutte generate con lo stesso stile: luce calda, neri profondi,
architettura e materia, nessun volto riconoscibile, nessuna scritta. Sotto ogni
fotografia resta una scena SVG/CSS: se il file manca, il riquadro non è mai vuoto.

```bash
./scripts/generate-images.sh --force about   # rigenera uno slot (richiama l'API)
./scripts/optimize-images.sh                  # rifà le versioni web, senza API
python3 scripts/build.py                      # aggiorna srcset e <picture>
```

`generate-images.sh` salva l'originale in `assets/img/_raw/` e sposta quello
precedente in `_raw/_precedenti/`, con data e ora. `optimize-images.sh` produce
per ogni slot JPEG, WebP e AVIF in due larghezze (serve `brew install webp libavif`);
la sala riunioni di "Who we are" ha due ritagli dallo stesso originale, 4:5 per
il desktop e 16:10 per i telefoni.

## Peso della pagina

Misurato con Chrome (desktop 1440 px) e WebKit (iPhone 14), ottobre 2026:

| | desktop | iPhone |
|---|---|---|
| Al caricamento | ~500 KB | ~500 KB |
| Pagina intera, dopo lo scroll | ~685 KB | ~1,05 MB |
| Caratteri tipografici | 101 KB | 101 KB |
| Richieste a terze parti | **0** | **0** |

## Scelte tecniche degne di nota

- **Caratteri ospitati in locale.** Google Fonts via CDN trasmette l'indirizzo IP
  del visitatore a Google: su un dominio europeo è un problema di conformità già
  sanzionato. Qui i file `.woff2` stanno sul sito. Sono font variabili: un solo
  file per alfabeto copre tutti i pesi.
- **Immagini stabili sul telefono.** Sotto i 960 px nessuna immagine cambia
  misura, taglio o scala mentre si scorre; la testata ha altezza costante.
  Attenzione al riquadro `.about__media`: deve restare `position: relative`.
  Con `static` la foto, a rivelazione finita, si allargava a tutta la sezione.
- **Il contenuto non dipende dal JavaScript.** Le rivelazioni allo scroll si
  attivano solo se lo script parte; se non parte, dopo quattro secondi la pagina
  torna interamente visibile da sola.
- **`prefers-reduced-motion` gestito a monte**, non effetto per effetto.
- **HTTPS obbligatorio**: il pulsante "copia indirizzo" usa l'API degli appunti,
  disponibile solo su connessione sicura (esiste comunque un ripiego).
