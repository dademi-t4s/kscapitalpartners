# Pubblicazione — come è online e come si aggiorna

## Com'è configurato

| | |
|---|---|
| Hosting | **GitHub Pages**, repository pubblico `dademi-t4s/kscapitalpartners`, branch `main`, cartella radice |
| Dominio | **kscapitalpartners.it** (file `CNAME`). `www.`, `http://` e il vecchio indirizzo `dademi-t4s.github.io/kscapitalpartners/` rimandano lì con un 301 |
| HTTPS | forzato; certificato Let's Encrypt rinnovato in automatico da GitHub |
| DNS | su GoDaddy (`ns81/ns82.domaincontrol.com`) |
| Posta | Microsoft 365 attivato tramite GoDaddy: **non toccare** i record MX e TXT |

Record DNS del sito, già impostati:

| Tipo | Nome | Valore |
|---|---|---|
| A | `@` | `185.199.108.153` · `185.199.109.153` · `185.199.110.153` · `185.199.111.153` |
| CNAME | `www` | `dademi-t4s.github.io.` |

## Aggiornare il sito

```bash
./aggiorna.sh "cosa ho cambiato"
```

Rigenera le pagine, fa il commit e il push. Online in circa un minuto.

Il repository appartiene all'account GitHub **dademi-t4s**. Sul Mac la GitHub CLI
può avere attivo un altro account (`protiviti-deiv-ademi`), che riceve un 403:
`aggiorna.sh` passa da solo il token di dademi-t4s al solo push, senza cambiare
l'account attivo. Per un push a mano:

```bash
GH_TOKEN="$(gh auth token --user dademi-t4s)" git push
```

## Cosa finisce online

GitHub Pages costruisce il sito con Jekyll. `_config.yml` esclude i documenti
interni e gli strumenti (`README.md`, `PUBBLICAZIONE.md`, `INFO-CLIENTE.md`,
`aggiorna.sh`, `scripts/`): restano nel repository, che è pubblico, ma non
sono raggiungibili dal dominio. Le pagine HTML non hanno front matter, quindi
Jekyll le copia così come sono. Se si aggiunge un file interno, va aggiunto
anche all'elenco `exclude`.

## Note

- Il sito usa percorsi relativi: funziona alla radice del dominio, in una
  sottocartella e aperto dal disco.
- Qualunque copia che non stia su kscapitalpartners.it (anteprime, file locali)
  si esclude da sola dai motori di ricerca con un `noindex`.
- `sitemap.xml` va segnalata in Google Search Console:
  `https://kscapitalpartners.it/sitemap.xml`.
- **Nessuna chiave API è nel progetto**: lo script delle immagini legge la
  chiave dall'ambiente o da un file `.env` locale, mai versionato.
