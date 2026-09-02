#!/usr/bin/env bash
# ---------------------------------------------------------------------------
#  KS Capital Partners — generatore immagini (OpenAI gpt-image-2)
#
#  Uso:
#     ./scripts/generate-images.sh            # genera solo le immagini mancanti
#     ./scripts/generate-images.sh --force    # rigenera tutto
#     ./scripts/generate-images.sh hero oil   # genera solo gli slot indicati
#
#  Richiede OPENAI_API_KEY nell'ambiente, oppure in un file .env accanto allo
#  script. Le immagini finiscono in assets/img/ con il nome dello slot.
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")/.."

ENV_CANDIDATES=("./.env" "$HOME/Documents/obs/backend/.env")
if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  for f in "${ENV_CANDIDATES[@]}"; do
    if [[ -f "$f" ]]; then set -a; . "$f"; set +a; fi
    [[ -n "${OPENAI_API_KEY:-}" ]] && break
  done
fi
if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "✗ OPENAI_API_KEY non trovata. Esportala o mettila in ./.env" >&2; exit 1
fi

FORCE=0; SLOTS=()
for a in "$@"; do
  case "$a" in
    --force) FORCE=1 ;;
    *) SLOTS+=("$a") ;;
  esac
done

MODEL="${IMAGE_MODEL:-gpt-image-2}"
QUALITY="${IMAGE_QUALITY:-high}"
mkdir -p assets/img

python3 - "$MODEL" "$QUALITY" "$FORCE" "${SLOTS[@]:-}" <<'PY'
import base64, json, os, sys, time, urllib.request, urllib.error

model, quality, force = sys.argv[1], sys.argv[2], sys.argv[3] == "1"
only = {s for s in sys.argv[4:] if s}
key = os.environ["OPENAI_API_KEY"]

with open("scripts/image-prompts.json") as fh:
    prompts = json.load(fh)

def generate(slot, spec):
    body = json.dumps({
        "model": model,
        "prompt": spec["prompt"],
        "size": spec["size"],
        "quality": quality,
        "n": 1,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        data = json.load(r)
    item = data["data"][0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    with urllib.request.urlopen(item["url"], timeout=300) as r:
        return r.read()

ok = skipped = failed = 0
for slot, spec in prompts.items():
    if slot.startswith("_"):          # blocchi di documentazione, non slot
        continue
    if only and slot not in only:
        continue
    out = f"assets/img/{slot}.png"
    # optimize-images.sh cancella il PNG dopo la conversione: senza questo
    # controllo ogni run rigenererebbe tutto, bruciando credito inutilmente.
    done = any(os.path.exists(f"assets/img/{slot}.{e}") for e in ("png", "jpg", "webp"))
    if done and not force:
        print(f"  ·  {slot:<14} già presente, salto")
        skipped += 1
        continue
    print(f"  →  {slot:<14} {spec['size']}  generazione…", flush=True)
    for attempt in range(1, 4):
        try:
            open(out, "wb").write(generate(slot, spec))
            print(f"  ✓  {slot:<14} {os.path.getsize(out)//1024} KB → {out}")
            ok += 1
            break
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code == 429 and "credit" in msg.lower():
                print(f"  ✗  credito OpenAI esaurito — ricarica e rilancia lo script.")
                sys.exit(2)
            print(f"  !  {slot}: HTTP {e.code} (tentativo {attempt}/3) {msg[:160]}")
            time.sleep(4 * attempt)
        except Exception as e:
            print(f"  !  {slot}: {type(e).__name__} {e} (tentativo {attempt}/3)")
            time.sleep(4 * attempt)
    else:
        failed += 1

print(f"\n  Fatte {ok} · saltate {skipped} · fallite {failed}")
PY

echo
echo "  Ora converto in WebP/AVIF per il web…"
./scripts/optimize-images.sh
