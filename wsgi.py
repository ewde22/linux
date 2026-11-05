from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return """
    <!DOCTYPE html>
    <html lang="fi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Week 2 - Python</title>
        <style>
            body {
                font-family: 'Courier New', Courier, monospace;
                background-color: #ffd1dc;
                color: #800020;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                background: #fff0f5;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(128, 0, 32, 0.1);
                text-align: center;
                max-width: 500px;
                width: 100%;
            }
            h1 {
                color: #800020;
                font-size: 24px;
                margin-bottom: 10px;
                font-weight: bold;
            }
            p {
                color: #800020;
                font-size: 15px;
                line-height: 1.6;
                margin-bottom: 30px;
            }
            .btn {
                display: inline-block;
                font-family: 'Courier New', Courier, monospace;
                background-color: #800020;
                color: #ffd1dc;
                text-decoration: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                transition: background-color 0.2s, color 0.2s;
            }
            .btn:hover {
                background-color: #600018;
                color: #ffe4e1;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Python-verkkosovellus</h1>
            <p>Tämä sovellus pyörii onnistuneesti Gunicorn- ja Nginx-palveluiden takana CSC cPoudassa.</p>
            <a href="https://github.com/ewde22/linux" target="_blank" class="btn">Avaa GitHub Repositorio</a>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run()
