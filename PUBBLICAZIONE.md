# Pubblicare il sito — gratis, con dominio e HTTPS

Il sito è fatto di soli file statici: si pubblica ovunque, senza server né
database. Tre strade gratuite, in ordine di semplicità.

---

## ⚠️ Un solo vincolo, che vale per tutte

Le pagine usano percorsi assoluti (`/assets/css/style.css`). Quindi il sito
**deve stare alla radice di un dominio**, non in una sottocartella.

- ✅ `https://www.kscapitalpartners.it/` — funziona
- ✅ `https://nomeutente.github.io/` (sito utente GitHub) — funziona
- ❌ `https://nomeutente.github.io/sito-denis/` — **si rompe**: CSS e immagini
  non caricano

Siccome il dominio c'è già, il vincolo si risolve da sé: si collega
`kscapitalpartners.it` e tutto funziona. Non serve cambiare una riga.

---

## Strada A · GitHub Pages

Gratis, HTTPS automatico, dominio personalizzato incluso.
Unica condizione: con l'account gratuito il repository deve essere **pubblico**
(il codice sarebbe visibile; i testi sono comunque già pubblici sul sito).

### 1. Creare il repository e caricarlo

```bash
cd /Users/deivademi/Documents/sito-denis
git init -b main
git add .
git commit -m "Sito KS Capital Partners"

# poi, con la GitHub CLI (gh auth login la prima volta):
gh repo create kscapitalpartners --public --source=. --push
```

Senza la CLI: si crea il repository su github.com e si esegue
`git remote add origin https://github.com/UTENTE/kscapitalpartners.git`
seguito da `git push -u origin main`.

### 2. Attivare Pages

Sul repository → **Settings** → **Pages** →
*Source:* **Deploy from a branch** → *Branch:* `main`, cartella `/ (root)` → **Save**.

**Il dominio si collega dopo**, quando si è pronti: Settings → Pages →
*Custom domain* → `www.kscapitalpartners.it` → Save. GitHub crea da sé il file
`CNAME` nel repository. Finché non lo si fa, il sito resta raggiungibile
all'indirizzo `github.io`, che è esattamente quello che serve per farlo vedere
al cliente.

### 3. Puntare il dominio (pannello del registrar)

Nella zona DNS di `kscapitalpartners.it`:

| Tipo | Nome | Valore |
|---|---|---|
| CNAME | `www` | `UTENTE.github.io.` |
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| AAAA | `@` | `2606:50c0:8000::153` |
| AAAA | `@` | `2606:50c0:8001::153` |
| AAAA | `@` | `2606:50c0:8002::153` |
| AAAA | `@` | `2606:50c0:8003::153` |

I record `A`/`AAAA` sul dominio nudo servono a far reindirizzare
`kscapitalpartners.it` verso `www`, cosa che GitHub fa da solo.
Sostituire `UTENTE` con il proprio nome utente GitHub.

### 4. Attendere e forzare HTTPS

La propagazione DNS richiede da pochi minuti a qualche ora. Poi, in
**Settings → Pages**, si spunta **Enforce HTTPS** (compare quando il
certificato è pronto). Fine.

### Aggiornare il sito, dopo

```bash
python3 scripts/build.py      # se hai toccato i testi
git add . && git commit -m "aggiornamento" && git push
```
Online in circa un minuto.

---

## Strada B · Cloudflare Pages — la più comoda

Gratis, HTTPS, **repository privato ammesso**, dominio personalizzato incluso,
e la rete più veloce delle tre.

1. `dash.cloudflare.com` → **Workers & Pages** → **Create** → **Pages**
2. Collegare il repository GitHub *oppure* usare **Direct Upload**
   trascinando la cartella del progetto (senza nemmeno usare git)
3. Build command: **lasciare vuoto** · Output directory: `/`
4. **Custom domains** → aggiungere `www.kscapitalpartners.it`

Se il dominio è già gestito da Cloudflare, i DNS si configurano da soli.

---

## Strada C · Netlify — trascina e vai

1. `app.netlify.com/drop`
2. Trascinare la cartella `sito-denis` nel riquadro
3. Il sito è online in dieci secondi su un indirizzo provvisorio
4. **Domain settings** → **Add custom domain** → seguire le istruzioni DNS

È il modo più rapido per far vedere il risultato al cliente prima di toccare
il dominio vero.

---

## Quale scegliere

| | GitHub Pages | Cloudflare Pages | Netlify |
|---|---|---|---|
| Costo | gratis | gratis | gratis |
| Repository privato | a pagamento | **sì** | sì |
| Serve git | sì | no (upload diretto) | no |
| Velocità | buona | **ottima** | buona |
| Redirect da dominio nudo | automatico | automatico | automatico |

**Il mio consiglio:** Netlify o Cloudflare Pages per far vedere subito il sito al
cliente; GitHub Pages quando il progetto è approvato e si vuole tenere il codice
versionato in un posto solo. Passare dall'uno all'altro costa cinque minuti,
perché sono gli stessi file.

---

## Note

- `CNAME`, `.nojekyll` e `.gitignore` sono già pronti nel progetto.
  `.nojekyll` impedisce a GitHub di ignorare le cartelle che iniziano con `_`.
- Il file `sitemap.xml` va segnalato in
  [Google Search Console](https://search.google.com/search-console) dopo la
  pubblicazione: `https://www.kscapitalpartners.it/sitemap.xml`.
- La cartella `scripts/` finisce online ma non è raggiungibile in modo utile e
  non contiene segreti. Volendola escludere, basta aggiungerla al `.gitignore`
  (ma allora non si potranno più rigenerare le pagine da un altro computer).
- **Nessuna chiave API è presente nel progetto**: lo script delle immagini legge
  la chiave dall'ambiente o da un file `.env` locale, mai versionato.
