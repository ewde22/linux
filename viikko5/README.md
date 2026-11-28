# Viikko 5: CI/CD-putki ja paikallinen LLM-chat

Verkkosovellus, jossa käyttäjä voi keskustella suoraan cPouta-palvelimella (Ollama + `qwen2.5:0.5b`) pyörivän kielimallin kanssa. Keskusteluhistoria tallentuu selainistuntokohtaisesti MariaDB-tietokantaan, ja jokainen `main`-haaraan tuleva muutos testataan ja julkaistaan automaattisesti GitHub Actions -putkella.

- **Sovellus ja dokumentaatio:** http://195.148.20
- **Terveysrajapinta (Commit SHA):** http://195.148.20health
- **Epäonnistuneen testiajon todiste:** https://github.com

## Hakemistorakenne
- `app/main.py` — Flask-sovellus, chat-käyttöliittymä, istuntokohtainen MariaDB-tallennus ja `/viikko5/health`-rajapinta.
- `tests/test_app.py` — Pytest-yksikkötestit mockatulla tietokannalla ja kielimallilla.
- `deploy/nginx_viikko5.conf` — Nginx-sijaintilohko (`/viikko5/`).
- `deploy/viikko5.service` — Systemd-palvelutiedosto (`viikko5user`).
- `deploy/schema.sql` — MariaDB-tietokantakaavio.
- `deploy/deploy.sh` — Palvelimen automaattinen julkaisu- ja varmistusskripti.
- `../.github/workflows/viikko5.yml` — GitHub Actions CI/CD -työnkulku.

## Paikallinen testaus ja julkaisu
1. Asenna riippuvuudet: `pip install -r requirements.txt`
2. Aja tyylitarkistus ja yksikkötestit: `ruff check . && pytest`

3. Luo palvelimelle käyttäjä viikko5user, tietokanta deploy/schema.sql-tiedostosta ja suojattu ympäristötiedosto /etc/viikko5.env (chmod 640).
4. Push main-haaraan käynnistää automaattisesti testit ja julkaisun palvelimelle.
