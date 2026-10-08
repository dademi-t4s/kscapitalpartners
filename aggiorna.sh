#!/usr/bin/env bash
# Rigenera le pagine e pubblica. Un comando solo: ./aggiorna.sh "cosa ho cambiato"
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/build.py
git add -A
git commit -q -m "${1:-aggiornamento}" || { echo "Niente da pubblicare."; exit 0; }

# Il repository appartiene all'account GitHub dademi-t4s. Sul Mac la GitHub
# CLI può avere attivo un altro account (che riceve un 403): il token giusto
# si passa solo a questo push, senza cambiare l'account attivo.
if TOKEN=$(gh auth token --user dademi-t4s 2>/dev/null); then
  GH_TOKEN="$TOKEN" git push -q
else
  git push -q
fi

echo
echo "  Pubblicato. Online fra circa un minuto:"
echo "  https://kscapitalpartners.it/"
