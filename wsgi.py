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
        <title>CSC Viikko 2</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f7f6;
                color: #333;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                text-align: center;
                max-width: 500px;
                width: 100%;
            }
            h1 {
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 10px;
            }
            p {
                color: #7f8c8d;
                font-size: 16px;
                line-height: 1.6;
                margin-bottom: 30px;
            }
            .btn {
                display: inline-block;
                background-color: #3498db;
                color: white;
                text-decoration: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                transition: background-color 0.2s;
            }
            .btn:hover {
                background-color: #2980b9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Python-verkkosovellus</h1>
            <p>Tämä sovellus pyörii onnistuneesti Gunicorn- ja Nginx-palveluiden takana CSC cPoudassa.</p>
            <a href="https://github.com" target="_blank" class="btn">Avaa GitHub Repositorio</a>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run()


