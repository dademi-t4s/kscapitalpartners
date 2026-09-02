#!/usr/bin/env bash
# ---------------------------------------------------------------------------
#  Ottimizza i PNG generati in assets/img/ per il web.
#  Ridimensiona alla larghezza di visualizzazione ×2 e produce JPEG di qualità,
#  più WebP se sul sistema è disponibile cwebp. Gli originali restano in
#  assets/img/_raw/ così puoi rigenerare senza richiamare l'API.
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p assets/img/_raw

# slot:larghezza_massima_px
# Larghezza massima servita. Mai superiore alla nativa: ingrandire un'immagine
# generata non aggiunge dettaglio, aggiunge solo peso.
# slot : larghezza massima : qualità JPEG
# La qualità segue quanto l'immagine è davvero visibile: la hero è a piena
# vista, il fondale della rete sta al 45% di opacità sotto una maschera e la
# texture dell'invito è coperta da un velo quasi opaco. Spendere byte lì è
# spreco puro.
TARGETS=(
  "hero:1536:78"
  "focus-oil:1024:70" "focus-art:1024:70" "focus-stone:1024:68"
  "about:1400:74" "network:1200:62" "cta-texture:1200:58"
)

have_webp=0; command -v cwebp >/dev/null 2>&1 && have_webp=1

for entry in "${TARGETS[@]}"; do
  IFS=':' read -r slot width quality <<< "$entry"
  src="assets/img/${slot}.png"
  raw="assets/img/_raw/${slot}.png"

  # Il PNG appena generato, se c'è, viene archiviato in _raw. Se non c'è si
  # riparte dall'originale già archiviato: così si può ricomprimere quante
  # volte si vuole senza richiamare l'API.
  if [[ -f "$src" ]]; then
    cp -n "$src" "$raw" 2>/dev/null || true
  fi
  [[ -f "$raw" ]] || continue

    # -Z ingrandirebbe se l'originale fosse più piccolo: si ridimensiona solo al ribasso
  native=$(sips -g pixelWidth "$raw" | awk '/pixelWidth/{print $2}')
  if [[ "$native" -gt "$width" ]]; then
    # --resampleWidth agisce sulla larghezza: -Z guarderebbe il lato maggiore
    # e schiaccerebbe le immagini verticali.
    sips --resampleWidth "$width" "$raw" --out "/tmp/ks-${slot}.png" >/dev/null 2>&1
  else
    cp "$raw" "/tmp/ks-${slot}.png"
  fi
  sips -s format jpeg -s formatOptions "$quality" "/tmp/ks-${slot}.png" \
       --out "assets/img/${slot}.jpg" >/dev/null 2>&1
  size=$(du -k "assets/img/${slot}.jpg" | cut -f1)
  line="  ✓ ${slot}.jpg  ${width}px  q${quality}  ${size}KB"

  if [[ $have_webp -eq 1 ]]; then
    cwebp -quiet -q "$quality" "/tmp/ks-${slot}.png" -o "assets/img/${slot}.webp"
    line+="  ·  $(du -k "assets/img/${slot}.webp" | cut -f1)KB webp"
  fi
  rm -f "/tmp/ks-${slot}.png" "$src"
  echo "$line"
done

if [[ $have_webp -eq 0 ]]; then
  echo
  echo "  ℹ  cwebp non installato: generati solo JPEG (perfettamente validi)."
  echo "     Per avere anche i WebP, più leggeri: brew install webp && ./scripts/optimize-images.sh"
fi
