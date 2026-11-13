"""SkyFetch: protótipo de interface Flask para o projeto PRJ.9."""

from flask import Flask, render_template

app = Flask(__name__)


@app.get("/")
def index():
    """Serve a interface demonstrativa de busca de voos."""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
