#!/usr/bin/env bash
set -euo pipefail

COMMIT_SHA="${1:-unknown}"
SRC_DIR="/home/ubuntu/linux/viikko5"
APP_DIR="/opt/viikko5"

echo "Deploying commit: $COMMIT_SHA"

# Siirretään omistajuus väliaikaisesti ubuntu-käyttäjälle päivityksen ajaksi
sudo /usr/bin/chown -R ubuntu:ubuntu "$APP_DIR"

# Kopioidaan sovelluskoodi ja riippuvuudet
/usr/bin/rsync -av --delete --exclude 'venv' --exclude '.commit_env' --exclude '__pycache__' "$SRC_DIR/" "$APP_DIR/"

# Luodaan virtuaaliympäristö tarvittaessa ja asennetaan paketit
if [ ! -d "$APP_DIR/venv" ]; then
    python3 -m venv "$APP_DIR/venv"
fi
"$APP_DIR/venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"

# Kirjoitetaan käynnissä oleva Git commit SHA ympäristötiedostoon
echo "COMMIT_SHA=$COMMIT_SHA" > "$APP_DIR/.commit_env"

# Palautetaan tiukat käyttöoikeudet palvelukäyttäjälle
sudo /usr/bin/chown -R viikko5user:viikko5user "$APP_DIR"
sudo /usr/bin/chmod 640 "$APP_DIR/.commit_env"

# Päivitetään Nginx-sijaintilohko ja testataan konfiguraatio ennen latausta
sudo /usr/bin/cp "$SRC_DIR/deploy/nginx_viikko5.conf" /etc/nginx/snippets/viikko5.conf
sudo /usr/sbin/nginx -t
sudo /usr/bin/systemctl reload nginx

# Päivitetään systemd-palvelu ja käynnistetään vain viikko5 uudelleen
sudo /usr/bin/cp "$SRC_DIR/deploy/viikko5.service" /etc/systemd/system/viikko5.service
sudo /usr/bin/systemctl daemon-reload
sudo /usr/bin/systemctl enable viikko5
sudo /usr/bin/systemctl restart viikko5

# Varmistetaan, että uusi versio vastaa ja palauttaa oikean commit SHA:n
sleep 2
HEALTH_JSON=$(curl -fsS http://127.0.0.1:5005/viikko5/health)
echo "Health response: $HEALTH_JSON"

if [[ "$HEALTH_JSON" != *"$COMMIT_SHA"* ]]; then
    echo "ERROR: Deployed commit SHA does not match expected $COMMIT_SHA!"
    exit 1
fi

echo "Deployment verified successfully!"
