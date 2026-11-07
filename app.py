import sqlite3
from flask import Flask
app = Flask(__name__)

DATABASE = "laskuri.db"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kaynnit (
                id INTEGER PRIMARY KEY,
                maara INTEGER
            )
        """)
        cursor.execute("SELECT COUNT(*) FROM kaynnit")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO kaynnit (id, maara) VALUES (1, 0)")
        conn.commit()

init_db()

@app.route("/")
def hello():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE kaynnit SET maara = maara + 1 WHERE id = 1")
        conn.commit()
        
        cursor.execute("SELECT maara FROM kaynnit WHERE id = 1")
        tulos = cursor.fetchone()
        
        
        kayntimaara = tulos[0] if tulos else 1

    return f"""
    <!DOCTYPE html>
    <html lang="fi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CSC Viikko 2</title>
        <style>
            body {{
                font-family: 'Courier New', Courier, monospace;
                background-color: #ffd1dc;
                color: #800020;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                box-sizing: border-box;
            }}
            .container {{
                background: #fff0f5;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(128, 0, 32, 0.1);
                text-align: center;
                max-width: 550px;
                width: 100%;
            }}
            h1 {{
                color: #800020;
                font-size: 24px;
                margin-bottom: 10px;
                font-weight: bold;
            }}
            p {{
                color: #800020;
                font-size: 15px;
                line-height: 1.6;
                margin-bottom: 20px;
            }}
            .counter {{
                font-size: 32px;
                font-weight: bold;
                background-color: #800020;
                color: #ffd1dc;
                padding: 10px 20px;
                border-radius: 6px;
                display: inline-block;
                margin: 15px 0 25px 0;
            }}
            .btn {{
                display: inline-block;
                font-family: 'Courier New', Courier, monospace;
                background-color: #800020;
                color: #ffd1dc;
                text-decoration: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                transition: background-color 0.2s;
            }}
            .btn:hover {{
                background-color: #600018;
            }}
            .info-box {{
                text-align: left;
                background: rgba(128, 0, 32, 0.04);
                padding: 15px;
                border-radius: 6px;
                font-size: 12px;
                line-height: 1.6;
                margin-top: 30px;
                border-left: 4px solid #800020;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Python-verkkosovellus</h1>
            <p>Tämä sovellus pyörii Gunicorn- ja Nginx-palveluiden takana CSC cPoudassa.</p>
            
            <p>Sivun latauskerrat (tietokannassa):</p>
            <div class="counter">{kayntimaara}</div>
            
            <br>
            <a href="https://github.com/ewde22/linux" target="_blank" class="btn">Avaa GitHub</a>
		<br><br>

	<div class="info box">
		<strong>Kävijälaskuri ja sen toiminta:</strong><br>
     		<strong>Käytetty tietokanta:</strong> SQLite3 (Pythonin sisäänrakennettu tiedostopohjainen relaatiotietokanta).<br>
     		<strong>Tallennustapa:</strong> Jokaisella sivun latauksella suoritetaan SQL UPDATE -lause,
 		joka kasvattaa tietokantataulun lukemaa yhdellä.<br>
     		<strong>Uudelleenkäynnistystesti:</strong> Testattu käynnistämällä virtuaalikone uudelleen. Laskuri jatkoi
		siitä mihin se jäi ennen uudelleenkäynnistystä.           
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run()
