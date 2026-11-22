# Viikko 4: Varmuuskopiointi ja tietokannan replikointi

## Linkit
- **Palvelin A (Primary – laskuri):** http://195.148.20.157
- **Palvelin B (Replica – vain luku & dokumentaatio):** http://86.50.231.159

## Kansion sisältö
- `varmuuskopio.sh`: Tunnin välein päivittyvä `rsync`-varmuuskopioskripti palvelimelta A palvelimelle B.
- `crontab_a.txt`: Ajastetun varmuuskopioinnin `cron`-määritys.
- `mariadb_primary_sanitised.cnf`: Siivottu MariaDB Primary -palvelimen konfiguraatio (ilman salasanoja).
- `mariadb_replica_sanitised.cnf`: Siivottu MariaDB Replica -palvelimen konfiguraatio (ilman salasanoja).
- `replica_b.py`: Palvelimen B Flask-sovellus, joka lukee replikoitua tietokantaa kasvattamatta laskuria (salasana poistettu).
