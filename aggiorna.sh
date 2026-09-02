#!/usr/bin/env bash
# Rigenera le pagine e pubblica. Un comando solo: ./aggiorna.sh "cosa ho cambiato"
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/build.py
git add -A
git commit -q -m "${1:-aggiornamento}" || { echo "Niente da pubblicare."; exit 0; }
git push -q
echo
echo "  Pubblicato. Online fra circa un minuto:"
echo "  https://dademi-t4s.github.io/kscapitalpartners/"
