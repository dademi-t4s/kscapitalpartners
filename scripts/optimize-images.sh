#!/usr/bin/env bash
# ---------------------------------------------------------------------------
#  Prepara le fotografie per il web, partendo dagli originali in
#  assets/img/_raw/. Si può rilanciare quante volte si vuole: non chiama l'API.
#
#  Per ogni slot produce, in due larghezze, JPEG (per tutti), WebP e AVIF (per
#  i browser che li leggono, cioè quasi tutti): <slot>.<ext> è la versione
#  grande, <slot>-<larghezza>.<ext> quella ridotta. build.py le trova da sé e
#  scrive srcset e <picture>.
#
#  Richiede cwebp e avifenc:  brew install webp libavif
#  Senza, produce solo i JPEG, che restano perfettamente validi.
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")/.."

# uscita : originale : larghezze : qualità JPEG : ritaglio (AxL+y+x, oppure -)
#
# La qualità segue quanto l'immagine è davvero visibile: la hero è a piena
# vista, la texture dell'invito è coperta da un velo quasi opaco.
# La sala riunioni dà due ritagli dallo stesso originale 1024x1536: 4:5 per
# la colonna del desktop, 16:10 per i telefoni, entrambi con le due figure
# accanto alla finestra.
TARGETS=(
  "hero:hero:1536,768:78:-"
  "focus-oil:focus-oil:1024,512:70:-"
  "focus-art:focus-art:1024,512:72:-"
  "focus-stone:focus-stone:1024,512:68:-"
  "about:about:1024,640:76:1280x1024+64+0"
  "about-m:about:1024,640:76:640x1024+300+0"
  "network:network:1536,768:70:-"
  "cta-texture:cta-texture:1200,800:58:-"
)

have_webp=0; command -v cwebp   >/dev/null 2>&1 && have_webp=1
have_avif=0; command -v avifenc >/dev/null 2>&1 && have_avif=1
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

for entry in "${TARGETS[@]}"; do
  IFS=':' read -r out raw widths quality crop <<< "$entry"
  src="assets/img/_raw/${raw}.png"
  [[ -f "$src" ]] || { echo "  ·  ${out}: manca ${src}, salto"; continue; }

  base="$tmp/${out}.png"
  if [[ "$crop" != "-" ]]; then
    [[ "$crop" =~ ^([0-9]+)x([0-9]+)\+([0-9]+)\+([0-9]+)$ ]]
    sips -c "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}" \
         --cropOffset "${BASH_REMATCH[3]}" "${BASH_REMATCH[4]}" "$src" --out "$base" >/dev/null
  else
    cp "$src" "$base"
  fi
  native=$(sips -g pixelWidth "$base" | awk '/pixelWidth/{print $2}')

  # Vecchie versioni dello slot: le larghezze possono essere cambiate.
  rm -f "assets/img/${out}".{jpg,webp,avif} assets/img/"${out}"-[0-9]*.{jpg,webp,avif}

  line="  ✓ ${out}"
  first=1
  for w in ${widths//,/ }; do
    # Mai ingrandire: un'immagine generata allargata non guadagna dettaglio.
    (( w > native )) && w=$native
    name="assets/img/${out}"; (( first )) || name+="-${w}"
    img="$tmp/${out}-${w}.png"
    if (( w < native )); then
      # --resampleWidth agisce sulla larghezza: -Z guarderebbe il lato maggiore
      # e schiaccerebbe le immagini verticali.
      sips --resampleWidth "$w" "$base" --out "$img" >/dev/null
    else
      cp "$base" "$img"
    fi
    sips -s format jpeg -s formatOptions "$quality" "$img" --out "${name}.jpg" >/dev/null
    (( have_webp )) && cwebp -quiet -q $(( quality + 8 )) -m 6 -af -sharp_yuv "$img" -o "${name}.webp"
    (( have_avif )) && avifenc -q $(( quality - 4 )) -s 6 -y 420 "$img" "${name}.avif" >/dev/null
    kb() { [[ -f "$1" ]] && echo "$(( $(stat -f%z "$1") / 1024 ))" || echo "-"; }
    line+="  ${w}px $(kb "${name}.jpg")/$(kb "${name}.webp")/$(kb "${name}.avif") KB"
    first=0
  done
  echo "$line   (jpg/webp/avif)"
done

if (( ! have_webp || ! have_avif )); then
  echo
  echo "  ℹ  cwebp o avifenc mancanti: generati solo i formati disponibili."
  echo "     brew install webp libavif && ./scripts/optimize-images.sh"
fi
