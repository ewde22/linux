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
            font-family: 'Courier New', Courier, monospace;
            background-color: #f4f1ea;
            color: #2c2c2c;
            max-width: 820px;
            margin: 30px auto;
            padding: 20px;
        }
        .card {
            background: #ffffff;
            border: 2px solid #2c2c2c;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 4px 4px 0px #2c2c2c;
            margin-bottom: 25px;
        }
        h1, h2 {
            margin-top: 0;
            color: #1a1a1a;
        }
        #chat-box {
            height: 360px;
            overflow-y: auto;
            border: 1px solid #ccc;
            background: #fafafa;
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
            background-color: #2c2c2c;
            color: #ffffff;
            align-self: flex-end;
        }
        .assistant {
            background-color: #e2e8f0;
            color: #1a1a1a;
            align-self: flex-start;
        }
        .input-row {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px;
            font-family: inherit;
            font-size: 14px;
            border: 2px solid #2c2c2c;
            border-radius: 6px;
        }
        button {
            padding: 12px 20px;
            font-family: inherit;
            font-weight: bold;
            background-color: #2c2c2c;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }
        button:disabled {
            background-color: #888;
        }
        .meta {
            font-size: 12px;
            color: #555;
            margin-top: 10px;
        }
        code {
            background: #eee;
            padding: 2px 5px;
            border-radius: 4px;
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
        <p><em>Tähän osioon täydennetään lopullinen dokumentaatio, arkkitehtuurikuvaus ja testitodisteet vaiheessa 8.</em></p>
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
