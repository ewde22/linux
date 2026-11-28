import os
import uuid
import pymysql
import requests
from flask import Flask, jsonify, render_template_string, request, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Viikko 5 - Paikallinen LLM Chat</title>
    <style>
        body {
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            font-family: 'Courier New', Courier, monospace;
            line-height: 1.6;
            background: #f3ebff;
            color: #2b1347;
        }
        .card {
            background: #faf5ff;
            border: 2px solid #b89ce0;
            border-radius: 8px;
            padding: 22px;
            margin-bottom: 24px;
        }
        h1, h2 {
            margin-top: 0;
            color: #2b1347;
        }
        #chat-box {
            height: 360px;
            overflow-y: auto;
            border: 1px solid #cbb4eb;
            background: #ffffff;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .msg {
            padding: 10px 14px;
            border-radius: 8px;
            max-width: 80%;
            line-height: 1.5;
            white-space: pre-wrap;
        }
        .user {
            background-color: #4a237a;
            color: #ffffff;
            align-self: flex-end;
        }
        .assistant {
            background-color: #e6d6fa;
            color: #2b1347;
            align-self: flex-start;
        }
        .input-row {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 10px 12px;
            font-family: inherit;
            font-size: 14px;
            background: #ffffff;
            color: #2b1347;
            border: 2px solid #9d78d1;
            border-radius: 6px;
        }
        button {
            padding: 10px 20px;
            font-family: inherit;
            font-weight: bold;
            background-color: #4a237a;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }
        button:hover {
            background-color: #36175c;
        }
        button:disabled {
            background-color: #a992c7;
        }
        .meta {
            font-size: 12px;
            color: #4a237a;
            margin-top: 12px;
        }
        .meta a {
            color: #36175c;
            font-weight: bold;
        }
        code, pre {
            background: #e6d6fa;
            color: #2b1347;
            padding: 2px 6px;
            border-radius: 4px;
        }
        pre {
            padding: 14px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Paikallinen LLM Chat (Viikko 5)</h1>
        <p>Keskustele suoraan cPouta-palvelimella pyörivän <strong>{{ model }}</strong> -kielimallin kanssa.</p>

        <div id="chat-box">
            {% for m in messages %}
                <div class="msg {{ m.role }}">{{ m.content }}</div>
            {% endfor %}
        </div>

        <form id="chat-form" class="input-row">
            <input type="text" id="prompt-input" placeholder="Kirjoita viesti mallille..." required autocomplete="off">
            <button type="submit" id="send-btn">Lähetä</button>
        </form>

        <div class="meta">
            Käynnissä oleva versio (Commit SHA): <code>{{ commit_sha }}</code> |
            <a href="/viikko5/health">Health JSON</a> |
            <a href="https://github.com" target="_blank">GitHub-repositorio</a>
        </div>
    </div>

    <div class="card" id="docs">
        <h2>Dokumentaatio (Viikko 5)</h2>

        <h3>1. Linkit</h3>
        <ul>
            <li><strong>Chat-sovellus:</strong> <a href="http://195.148.20">http://195.148.20</a></li>
            <li><strong>Health-rajapinta:</strong> <a href="http://195.148.20health">http://195.148.20health</a></li>
            <li><strong>GitHub-repositorio:</strong> <a href="https://github.com" target="_blank">https://github.com</a></li>
            <li><strong>Epäonnistunut CI-työnkulku (todiste):</strong> <a href="https://github.com" target="_blank">Run #46153803763 (commit b2d9881)</a></li>
        </ul>

        <h3>2. Arkkitehtuuri ja pyyntöpolku</h3>
        <pre>Selain (HTTP :80)
  └──&gt; Nginx (/viikko5/ location snippet)
         └──&gt; Gunicorn + Flask (127.0.0.1:5005, käyttäjä: viikko5user)
                ├──&gt; MariaDB (localhost:3306, viikko5_db.messages - istuntohistoria)
                └──&gt; Ollama (127.0.0.1:11434, qwen2.5:0.5b - paikallinen kielimalli)</pre>

        <h3>3. CI/CD-putki (GitHub Actions)</h3>
        <ul>
            <li><strong>Pull Request &amp; Push:</strong> Jokainen push ja pull request suorittaa <code>ruff</code>-linterin ja <code>pytest</code>-yksikkötestit, joissa tietokanta ja Ollama-rajapinta on mockattu. Epäonnistunut testi estää julkaisun.</li>
            <li><strong>Automaattinen julkaisu (main):</strong> Kun <code>main</code>-haaran muutos läpäisee testit, työnkulku ottaa SSH-yhteyden erillisellä avainparilla palvelimelle, hakee koodin, asentaa riippuvuudet, testaa Nginx-asetukset (<code>nginx -t</code>), käynnistää uudelleen vain <code>viikko5.service</code>-palvelun ja varmistaa <code>/viikko5/health</code>-osoitteesta, että käynnissä oleva <code>COMMIT_SHA</code> vastaa julkaistua committia.</li>
        </ul>

        <h3>4. Käyttäjät, oikeudet, salaisuudet ja palomuuri</h3>
        <ul>
            <li><strong>Linux-käyttäjä:</strong> Erillinen kirjautumaton järjestelmäkäyttäjä <code>viikko5user</code> (<code>/usr/sbin/nologin</code>), joka omistaa kansion <code>/opt/viikko5</code>.</li>
            <li><strong>Tietokantakäyttäjä:</strong> <code>'viikko5_dbuser'@'localhost'</code>, jolla on rajatut <code>SELECT, INSERT</code> -oikeudet vain tauluun <code>viikko5_db.messages</code>.</li>
            <li><strong>Salaisuudet:</strong> Tietokannan salasana ja istuntoavain on tallennettu palvelimelle tiedostoon <code>/etc/viikko5.env</code> (oikeudet <code>640</code>, omistaja <code>root:viikko5user</code>). SSH-avain ja isäntäavain ovat GitHub Actions Secrets -asetuksissa.</li>
            <li><strong>cPouta Security Group (SSH):</strong> Koska GitHub Actions -runnerit yhdistävät vaihtuvista IP-osoitteista, SSH-portti 22 on avoinna ulkoverkkoon. Tietoturvariski on minimoitu käyttämällä pelkkää avainpohjaista tunnistautumista (salasanakirjautuminen estetty), erillistä SSH-avainparia sekä tiukasti rajattua <code>sudoers</code>-sääntöä.</li>
        </ul>

        <h3>5. Nginx-integraatio ja Viikon 4 replikointi</h3>
        <ul>
            <li><strong>Nginx:</strong> Lisätty erillinen <code>include /etc/nginx/snippets/viikko5.conf;</code> -rivi olemassa olevaan sivustoon koskematta aiempien viikkojen reitteihin.</li>
            <li><strong>Viikon 4 tietokantareplikointi:</strong> Sovellus ajetaan Palvelimella A (pääpalvelin), koska Palvelin B on vain luku -tilassa (read-only replica). Uusi <code>viikko5_db</code>-tietokanta rajattiin replikoinnin ulkopuolelle, sillä se on itsenäinen sovellustietokanta eikä kuulu viikon 4 replikoituun kantaan.</li>
        </ul>

        <h3>6. Kielimallin valinta ja palvelimen resurssit</h3>
        <p>Palvelimella on 7,6 GiB RAM-muistia ja 77 Gt levytilaa (74 Gt vapaana). Valitsin malliksi kevyen <strong><code>qwen2.5:0.5b</code></strong> (397 MB), joka vastaa nopeasti pelkällä CPU:lla ja kuluttaa vain vähän muistia (1,1 GiB käytössä, 6,4 GiB vapaana malli ladattuna), joten swap-muistia ei tarvittu.</p>

        <h3>7. Testitulokset</h3>
        <ul>
            <li><strong>Julkinen chat &amp; istunnot:</strong> <code>/viikko5/</code> on julkisesti saavutettavissa, malli vastaa viesteihin, historia säilyy sivun päivityksen (F5) yli ja uusi Incognito-istunto alkaa tyhjänä.</li>
            <li><strong>Verkkoeristys:</strong> <code>ss -ltnp</code> vahvistaa, että Gunicorn (<code>127.0.0.1:5005</code>) ja Ollama (<code>127.0.0.1:11434</code>) kuuntelevat vain localhostia.</li>
            <li><strong>Automaattinen julkaisu &amp; SHA:</strong> Useat pushit <code>main</code>-haaraan päivittivät palvelun automaattisesti ja <code>/viikko5/health</code> päivitti vastaavan commit SHA -tunnisteen.</li>
            <li><strong>Virheellisen testin esto:</strong> Tahallinen epäonnistuva testi (commit <code>b2d9881</code>) pysähtyi CI-vaiheeseen (<a href="https://github.com" target="_blank">Actions-ajo</a>) eikä käynnistänyt julkaisua.</li>
            <li><strong>Uudelleenkäynnistys (reboot):</strong> Palvelimen uudelleenkäynnistyksen jälkeen sekä <code>viikko5.service</code> että <code>ollama.service</code> käynnistyivät automaattisesti ilman käsin tehtäviä toimia.</li>
            <li><strong>Aiempien viikkojen sivut:</strong> Viikkojen 1–4 sivut toimivat edelleen alkuperäisissä osoitteissaan.</li>
        </ul>

        <h3>8. Ratkaistu ongelma ja opitut asiat</h3>
        <p>Kehityksen aikana Nginx palautti aluksi 500 Internal Server Error -virheen, koska <code>proxy_pass</code>-osoitteesta puuttui porttinumero <code>:5005</code>, jolloin Nginx ohjasi pyynnöt silmukassa takaisin omaan porttiinsa 80. Virhelokin (<code>/var/log/nginx/error.log</code>) avulla silmukka paikannettiin nopeasti ja korjattiin Gitin kautta CI/CD-putken läpi.</p>

        <h3>9. Palvelimen todistetulosteet (salaisuudet poistettu)</h3>
        <pre>=== systemctl status viikko5 &amp; User/Group ===
● viikko5.service - Viikko 5 Local LLM Chat Flask App
     Loaded: loaded (/etc/systemd/system/viikko5.service; enabled; preset: enabled)
     Active: active (running) since Sat 2026-11-28 14:21:20 UTC
   Main PID: 1309 (gunicorn)
User=viikko5user
Group=viikko5user

=== ls -la /opt/viikko5 &amp; /etc/viikko5.env ===
drwxrwxr-x 8 viikko5user viikko5user 4096 Nov 26 16:30 .
-rw-r----- 1 viikko5user viikko5user   52 Nov 26 18:01 .commit_env
drwxrwxr-x 3 viikko5user viikko5user 4096 Nov 26 16:30 app
drwxrwxr-x 2 viikko5user viikko5user 4096 Nov 26 17:43 deploy
-rw-rw-r-- 1 viikko5user viikko5user   88 Nov 26 16:23 requirements.txt
drwxrwxr-x 2 viikko5user viikko5user 4096 Nov 26 16:30 tests
drwxrwxr-x 5 viikko5user viikko5user 4096 Nov 26 17:40 venv
-rw-r----- 1 root        viikko5user  217 Nov 26 16:07 /etc/viikko5.env

=== SHOW GRANTS FOR 'viikko5_dbuser'@'localhost' ===
GRANT USAGE ON *.* TO `viikko5_dbuser`@`localhost` IDENTIFIED BY PASSWORD '&lt;REDACTED&gt;'
GRANT SELECT, INSERT ON `viikko5_db`.`messages` TO `viikko5_dbuser`@`localhost`

=== ollama list &amp; free -h ===
NAME            ID              SIZE      MODIFIED
qwen2.5:0.5b    a8b0c5157701    397 MB    47 hours ago

               total        used        free      shared  buff/cache   available
Mem:           7.6Gi       1.1Gi       5.7Gi       4.1Mi       973Mi       6.4Gi
Swap:             0B          0B          0B

=== sudo ss -ltnp (localhost-palvelut) ===
LISTEN 0 2048 127.0.0.1:5005  0.0.0.0:* users:(("gunicorn",pid=1326,fd=5),("gunicorn",pid=1325,fd=5),("gunicorn",pid=1309,fd=5))
LISTEN 0 512  127.0.0.1:39841 0.0.0.0:* users:(("llama-server",pid=1395,fd=3))
LISTEN 0 4096 127.0.0.1:11434 0.0.0.0:* users:(("ollama",pid=920,fd=4))
LISTEN 0 511  0.0.0.0:80      0.0.0.0:* users:(("nginx",pid=1054,fd=5),...)
LISTEN 0 2048 127.0.0.1:8000  0.0.0.0:* users:(("gunicorn",pid=1151,fd=3),...)</pre>
    </div>

    <script>
        const chatBox = document.getElementById('chat-box');
        chatBox.scrollTop = chatBox.scrollHeight;

        const form = document.getElementById('chat-form');
        const input = document.getElementById('prompt-input');
        const btn = document.getElementById('send-btn');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = input.value.trim();
            if (!text) return;

            appendMessage('user', text);
            input.value = '';
            input.disabled = true;
            btn.disabled = true;

            const loadingDiv = appendMessage('assistant', 'Malli miettii vastausta...');

            try {
                const res = await fetch('/viikko5/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                if (res.ok) {
                    loadingDiv.textContent = data.reply;
                } else {
                    loadingDiv.textContent = 'Virhe: ' + (data.error || 'Tuntematon virhe');
                }
            } catch (err) {
                loadingDiv.textContent = 'Yhteysvirhe palvelimeen.';
            } finally {
                input.disabled = false;
                btn.disabled = false;
                input.focus();
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        });

        function appendMessage(role, text) {
            const div = document.createElement('div');
            div.className = 'msg ' + role;
            div.textContent = text;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
            return div;
        }
    </script>
</body>
</html>
"""


def get_db_connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "viikko5_dbuser"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "viikko5_db"),
        cursorclass=pymysql.cursors.DictCursor,
    )


def get_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return session["session_id"]


def fetch_history(session_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT role, content FROM messages WHERE session_id = %s ORDER BY id ASC",
                (session_id,),
            )
            return cursor.fetchall()
    finally:
        conn.close()


def save_message(session_id, role, content):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)",
                (session_id, role, content),
            )
        conn.commit()
    finally:
        conn.close()


def query_ollama(messages):
    base_url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    model = os.environ.get("OLLAMA_MODEL", "qwen2.5:0.5b")
    payload = {
        "model": model,
        "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
        "stream": False,
    }
    response = requests.post(f"{base_url}/api/chat", json=payload, timeout=90)
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]


@app.route("/viikko5/")
def index():
    sid = get_session_id()
    try:
        history = fetch_history(sid)
    except Exception:
        history = []
    return render_template_string(
        HTML_TEMPLATE,
        messages=history,
        model=os.environ.get("OLLAMA_MODEL", "qwen2.5:0.5b"),
        commit_sha=os.environ.get("COMMIT_SHA", "local-dev"),
    )


@app.route("/viikko5/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    if not user_message:
        return jsonify({"error": "Viesti ei voi olla tyhjä."}), 400

    sid = get_session_id()
    save_message(sid, "user", user_message)
    history = fetch_history(sid)

    try:
        reply = query_ollama(history)
    except Exception as exc:
        return jsonify({"error": f"Kielimallivirhe: {exc}"}), 502

    save_message(sid, "assistant", reply)
    return jsonify({"reply": reply})


@app.route("/viikko5/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "commit_sha": os.environ.get("COMMIT_SHA", "unknown"),
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5005)
