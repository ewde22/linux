from flask import Flask
import pymysql

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="eevalinux2_user",
        password="SALASANA_POISTETTU", 
        database="eevalinux2_db",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/viikko4/')
def lue_laskuri():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT maara FROM laskuri WHERE id = 1;")
    rivi = cursor.fetchone()
    conn.close()
    
    maara = rivi['maara'] if rivi else 0
    
    return f"""
    <!DOCTYPE html>
    <html lang="fi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CSC Viikko 4 - Read-Only Replica & Dokumentaatio</title>
        <style>
            body {{
                font-family: 'Courier New', Courier, monospace;
                background-color: #FBCEB1; /* Apricot */
                color: #8A3300;
                margin: 0;
                padding: 40px 20px;
                box-sizing: border-box;
                display: flex;
                justify-content: center;
            }}
            .container {{
                background: #FFD8B1; /* Cantaloupe */
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 6px 20px rgba(204, 85, 0, 0.18);
                border: 2px solid #FF7F50; /* Coral */
                max-width: 800px;
                width: 100%;
                text-align: center;
            }}
            h1 {{
                color: #CC5500; /* Burnt Orange */
                font-size: 26px;
                margin-bottom: 10px;
            }}
            h2 {{
                color: #CC5500;
                font-size: 18px;
                border-bottom: 2px solid #FF7F50;
                padding-bottom: 6px;
                margin-top: 28px;
                text-align: left;
            }}
            .badge {{
                display: inline-block;
                background-color: #FF7F50;
                color: #FFFFFF;
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                margin-bottom: 15px;
            }}
            .counter {{
                font-size: 38px;
                font-weight: bold;
                background-color: #FF7F50;
                color: #FFFFFF;
                border: 2px solid #CC5500;
                padding: 12px 30px;
                border-radius: 8px;
                display: inline-block;
                margin: 10px 0 20px 0;
            }}
            .btn-group {{
                margin: 15px 0 25px 0;
            }}
            .btn {{
                display: inline-block;
                font-family: 'Courier New', Courier, monospace;
                background-color: #CC5500;
                color: #FFF5EE;
                text-decoration: none;
                padding: 10px 18px;
                border-radius: 6px;
                font-weight: bold;
                margin: 5px;
                font-size: 13px;
                transition: background-color 0.2s;
            }}
            .btn:hover {{
                background-color: #FF7F50;
                color: #FFFFFF;
            }}
            .doc-section {{
                text-align: left;
                background: rgba(255, 255, 255, 0.45);
                padding: 25px;
                border-radius: 8px;
                font-size: 13px;
                line-height: 1.65;
                margin-top: 20px;
                border-left: 5px solid #CC5500;
            }}
            ul {{
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 8px;
            }}
            code {{
                background: rgba(204, 85, 0, 0.12);
                padding: 2px 5px;
                border-radius: 4px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="badge">STATUS: READ-ONLY REPLICA</div>
            <h1>Palvelin B: tilanseuranta ja viikko 4 dokumentaatio</h1>
            <p>Tämä sivu lukee kävijämäärän paikallisesta MariaDB- tietokannasta, mutta ei kasvata tällä sivulla olevaa lukua.</p>

            <div class="counter">{maara}</div>

            <div class="btn-group">
                <a href="http://195.148.20.157/viikko2/" target="_blank" class="btn">Palvelin A: Laskuri (/viikko2/)</a>
                <a href="http://86.50.231.159/viikko4/" target="_blank" class="btn">Palvelin B: Replica (/viikko4/)</a>
                <a href="https://github.com/ewde22/linux/tree/main/viikko4" target="_blank" class="btn">GitHub-repositorio</a>
            </div>

            <div class="doc-section">

                <h2>Palvelimen B luominen</h2>
                <p>Palvelin B (<code>eevalinux2</code>, IP: <code>86.50.231.159</code>): Loin uuden palvelimen cPouta -pilviympäristössä ottamalla ensin snapshotin olemassa
		 olevasta palvelimesta A (<code>eevalinux</code>) ja käynnistämällä uuden virtuaalikoneen omalla julkisella kelluvalla IP-osoitteella (samat vaiheet kuin 
		palvelin A pystytyksessä).
 		Tämän jälkeen muutin palvelimen B tietokantapalvelimen <code>server-id:n</code> yksilölliseksi (<code>2</code>, 
		palvelin A on <code>1</code>) ja avasin tietoturvaryhmän palomuurisäännöt HTTP/HTTPS- ja tietokantaliikenteelle.</p>

                <h2>Tallennusrakenne ja varmuuskopioiden sijainnit</h2>
                <ul>
                    <li><strong>Palvelin A (Primary):</strong> Verkkosivuston juurihakemisto sijaitsee polussa <code>/var/www/html/</code> ja 
		Python/Flask-sovellukset polussa <code>/home/ubuntu/python_sovellus/</code>. MariaDB tallentaa tiedot <code>eevalinux2_db</code>-tietokantaan.</li>
                    <li><strong>Palvelin B (Replica):</strong> Vastaanottaa varmuuskopiot hakemistoon <code>/home/ubuntu/nettisivu_varmuuskopiot/</code>
		 aikaleimattuihin alikansioihin (esim. <code>html_YYYY-MM-DD_HH-MM</code>). Paikallinen MariaDB-replica säilyttää kopiota tietokannasta
		 sekä relay-lokeja polussa <code>/var/lib/mysql/</code>.</li>
                </ul>

                <h2>Käyttäjät ja käyttöoikeudet</h2>
                <ul>
                    <li><strong>Linux-käyttäjät:</strong> Molemmilla palvelimilla käytetään <code>ubuntu</code>-käyttäjää sovellusten ja skriptien ajamiseen
		 sekä <code>www-data</code>-ryhmää Nginx- ja Gunicorn-palveluille. Palvelinten välinen varmuuskopiointi toimii ilman salasanaa SSH-avainparilla
		 (<code>~/.ssh/authorized_keys</code>. Oikeudet <code>600</code>, eli vain tiedoston omistaja (ubuntu) voi lukea ja muokata sitä.</li>
                    <li><strong>Tietokantakäyttäjät:</strong> Palvelimella A sovellus käyttää <code>eevalinux2_user</code>-tunnusta
		 (<code>ALL PRIVILEGES</code> vain <code>eevalinux2_db</code>-kantaan). Replikointia varten loin rajatun käyttäjän <code>replica_user</code>,
		 jolla on ainoastaan <code>REPLICATION SLAVE</code> -oikeudet. Palvelimella B lukusovellus käyttää paikallista <code>laskuri_user</code>-tunnusta
		 ja suorittaa vain <code>SELECT</code>-kyselyitä.</li>
                </ul>

                <h2>Varmuuskopiointi ja jatkuva replikointi</h2>
                <ul>
                    <li><strong>Varmuuskopiointiaikataulu:</strong> Palvelimen A <code>cron</code> ajaa tasatunnein (<code>0 * * * *</code>) skriptin
		 <code>/home/ubuntu/varmuuskopio.sh</code>, joka siirtää tiedostot <code>rsync</code>-komennolla SSH:n yli palvelimen B varmuuskopiokansioon.</li>
                    <li><strong>Jatkuva replikointi:</strong> MariaDB on konfiguroitu Primary–Replica-tilaan. Palvelin A kirjaa muutokset binäärilokiin
		 (<code>log-bin</code>), josta palvelimen B IO- ja SQL-säikeet hakevat ja suorittavat päivitykset reaaliajassa.</li>
                </ul>

                <h2>Testitulokset</h2>
                <ul>
                    <li><strong>Julkinen saavutettavuus ja laskurin toiminta:</strong> Molemmat sivut ovat julkisesti saavutettavia. Palvelimen A
		 <code>/viikko2/</code>-sivun lataaminen kasvattaa lukua, ja muutos päivittyy välittömästi palvelimen B <code>/viikko4/</code>-sivulle.
		 B-sivun päivittäminen ei kasvata laskuria.</li>
                    <li><strong>Replikoinnin tila:</strong> Tarkistettu komennolla <code>SHOW SLAVE STATUS\\G</code>: sekä <code>Slave_IO_Running</code>
		 että <code>Slave_SQL_Running</code> ovat tilassa <code>Yes</code>.</li>
                    <li><strong>Ajastetut varmuuskopiot ja palautustesti:</strong> Varmuuskopiokansiossa on useita onnistuneita tuntikopioita.
		 Vertasin varmuuskopioista palautettua <code>index.html</code>-tiedostoa alkuperäiseen komennolla <code>diff -s</code>,
		 joka vahvisti tiedostojen olevan identtiset (<code>Files ... are identical</code>).</li>
                    <li><strong>Uudelleenkäynnistystesti:</strong> Käynnistin palvelimen B uudelleen komennolla <code>sudo reboot</code>. Käynnistyksen jälkeen Nginx,
		 Gunicorn ja MariaDB-replikointi käynnistyivät uudelleen ja synkronointi jatkui normaalisti.</li>
                </ul>

                <h2>Ongelmat ja opitut asiat</h2>

                <p><strong>Ongelma ja ratkaisu:</strong> Replikointia ja lukusivua pystytettäessä ilmeni muutamia ongelmia.
		 Ensin tietokantayhteys palautti virheen <code>Table 'eevalinux2_db.laskuri' doesn't exist</code>, koska en ollut alustanut tietokantaa
		ja taulua Primary-palvelimelle replikoinnin kytkemisen jälkeen. Lisäksi Nginxin <code>proxy_pass</code>-asetuksen loppuvino-viiva (<code>/</code>)
		 aiheutti reititysristiriidan Flaskin <code>@app.route('/viikko4/')</code> -polun kanssa. Tämän kanssa ihmetellessä meni ehkä eniten aikaa. 
		Ongelmat ratkesivat alustamalla taulu palvelimella A, jolloin se replikoitui välittömästi B:lle, ja yhdenmukaistamalla Nginxin ja Flaskin URL-polut.</p>

                <p><strong>Opitut asiat:</strong> Opin jotain Primary–Replica-tietokantareplikoinnin toiminnasta ja kuinka palvelinten välinen
		 salasanaton SSH-varmuuskopiointi automatisoidaan.</p>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

