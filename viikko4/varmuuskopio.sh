#!/usr/bin/env bash

#aikaleiman luonti (YYYY-MM-DD_hh-mm)
AIKALEIMA=$(date +%Y-%m-%d_%H-%M)

#kohdekansio B palvelimella
KOHDE="ubuntu@86.50.231.159:/home/ubuntu/nettisivu_varmuuskopiot/html_$AIKALEIMA"

#lokitiedosto
LOKI="/home/ubuntu/varmuuskopio_loki.txt"

#kopiointi rsyncillä
if rsync -avz /var/www/html/ "$KOHDE" >> "$LOKI" 2>&1; then
    echo "[$AIKALEIMA] Varmuuskopiointi onnistui." >> "$LOKI"
else
    echo "[$AIKALEIMA] VIRHE: Varmuuskopiointi epäonnistui." >> "$LOKI"
fi
