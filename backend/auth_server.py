from flask import Flask, redirect, request
from auth import request_tokens_via_code, CLIENT_ID, REDIRECT_URI, SCOPES
import urllib.parse

app = Flask(__name__)

@app.route("/login")
def login():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
    }
    url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
    return redirect(url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Błąd: brak kodu", 400

    request_tokens_via_code(code)
    return redirect("http://localhost:3000")  # lub inna strona frontendu

if __name__ == "__main__":
    app.run(port=8888)