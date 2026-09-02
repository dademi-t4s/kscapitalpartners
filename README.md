# KS Capital Partners — sito vetrina

Sito statico bilingue (italiano/inglese) per **www.kscapitalpartners.it**.
HTML, CSS e JavaScript puri: nessun framework, nessun passaggio di compilazione,
nessuna richiesta a server di terze parti.

---

## Da sistemare prima di pubblicare

| Dove | Cosa | Perché |
|---|---|---|
| `scripts/build.py`, variabile `EMAIL` | `info@kscapitalpartners.it` | **Indirizzo inventato da me.** Va sostituito con quello vero prima di andare online. |
| `scripts/copy.json`, chiavi `legal.*` | `[CONTROLLER]` e `[EMAIL]` | Denominazione dell'entità titolare del trattamento e indirizzo per l'esercizio dei diritti GDPR. |
| Testi legali | Privacy, cookie, condizioni d'uso | Sono **bozze di lavoro**, scritte per il sito così com'è (nessun modulo, nessun tracciamento). Vanno fatte validare da un legale prima della pubblicazione. |

Dopo ogni modifica: `python3 scripts/build.py`.

Due documenti a parte:
- **`INFO-CLIENTE.md`** — tutto ciò che va chiesto al cliente, diviso per urgenza.
- **`PUBBLICAZIONE.md`** — come mettere il sito online gratis, con dominio e HTTPS.

---

## Struttura

```
index.html              home in italiano
en/index.html           home in inglese
note-legali.html        privacy, cookie e condizioni (IT)
en/legal.html           idem (EN)
robots.txt  sitemap.xml  site.webmanifest  favicon.svg

assets/
  css/style.css         foglio unico: token, movimento, componenti, sezioni
  css/fonts.css         @font-face dei caratteri ospitati in locale
  js/main.js            comportamenti (rivelazioni, menu, indice, schede)
  fonts/                Cormorant Garamond + Jost, 6 tagli, subset latin
  img/                  marchio, icone, scene SVG, anteprime social

scripts/
  build.py              genera le quattro pagine da copy.json
  copy.json             tutti i testi, in italiano e inglese
  dev-server.py         anteprima locale con ricarica automatica
  generate-images.sh    genera le fotografie con OpenAI
  optimize-images.sh    ridimensiona e converte per il web
  image-prompts.json    gli otto prompt, con stile e negativi
  make-og.py            ricompone le anteprime social

CNAME  .nojekyll  .gitignore   pronti per GitHub Pages
404.html  en/404.html          pagina non trovata, nelle due lingue
```

## Anteprima locale

```bash
python3 scripts/dev-server.py
```
→ http://localhost:8747/ (IT) e http://localhost:8747/en/ (EN).
La pagina si ricarica da sola a ogni salvataggio.

Due parametri utili solo in locale, che **non finiscono nei file pubblicati**:
`?review=1` disattiva le animazioni per esaminare il layout, `?audit=1` esegue
un controllo di overflow orizzontale e contrasto e ne stampa l'esito in pagina.

## Modificare i testi

Tutti i contenuti stanno in `scripts/copy.json`, una chiave per stringa con la
versione `it` e quella `en`. Si modifica il JSON e si rilancia `build.py`:
non si tocca l'HTML a mano, altrimenti la modifica si perde alla generazione
successiva.

## Fotografie

Le sette fotografie sono **già generate e inserite** (gpt-image-2), coerenti fra
loro: unica sorgente di luce calda, neri profondi, nessun volto, nessuna scritta.
Gli originali a piena risoluzione stanno in `assets/img/_raw/`, esclusi dal
versionamento.

Sotto ogni fotografia resta la scena SVG che avevo costruito prima: se un file
manca o non carica, il riquadro non diventa mai un rettangolo vuoto.

```bash
./scripts/generate-images.sh          # genera solo le mancanti
./scripts/generate-images.sh --force  # rigenera tutto (richiama l'API)
./scripts/optimize-images.sh          # ricomprime dagli originali, senza API
```

La qualità JPEG è tarata per slot in `optimize-images.sh`, in base a quanto
ciascuna immagine è realmente visibile: la hero è a piena vista (q78), il
fondale della rete sta al 45% di opacità sotto una maschera (q62), la texture
dell'invito è coperta da un velo quasi opaco (q58). Così le sette pesano
1,5 MB invece di 2,3.

Installando `cwebp` (`brew install webp`) e rilanciando `optimize-images.sh` si
ottengono anche i WebP, circa un terzo più leggeri.

## Pubblicazione

Sono file statici: si caricano così come sono nella cartella pubblica del
dominio (`public_html`, `htdocs`, oppure Netlify, Vercel, Cloudflare Pages,
GitHub Pages). Nessuna configurazione di server necessaria.

Sul server conviene attivare la compressione (gzip o brotli) e una cache lunga
su `/assets/`. Pesi effettivi della home:

| | peso |
|---|---|
| Sopra la piega (HTML, CSS, JS, caratteri, foto della hero) | ~537 KB |
| Differito allo scroll (sei fotografie, `loading="lazy"`) | ~1,25 MB |
| Richieste a terze parti | **0** |

Dei 537 KB immediati, 190 KB sono i caratteri tipografici, che il browser riusa
su tutte le pagine, e 244 KB la fotografia della hero, che è l'elemento LCP e
viene caricata con `fetchpriority="high"`.

**HTTPS obbligatorio**: il pulsante "copia indirizzo" usa l'API degli appunti,
disponibile solo su connessione sicura (esiste comunque un ripiego funzionante).

## Scelte tecniche degne di nota

- **Caratteri ospitati in locale.** Google Fonts via CDN trasmette l'indirizzo IP
  del visitatore a Google: su un dominio europeo è un problema di conformità già
  sanzionato. Qui i file `.woff2` stanno sul sito, e le richieste esterne sono zero.
- **Due pagine statiche invece di un selettore in JavaScript.** Ogni lingua ha il
  proprio indirizzo, il proprio `lang`, il proprio titolo e la propria descrizione,
  con `hreflang` incrociati: nessun lampeggio al caricamento e indicizzazione corretta.
- **Il contenuto non dipende dal JavaScript.** Le rivelazioni allo scroll si
  attivano solo se lo script parte; se non parte, dopo quattro secondi la pagina
  torna interamente visibile da sola.
- **`prefers-reduced-motion` gestito a monte**, non effetto per effetto.
