from flask import Flask, jsonify, request
from flask_cors import CORS
from api import get_current_user, get_currently_playing, skip_to_next, skip_to_previous, pause_or_resume

app = Flask(__name__)
CORS(app)

@app.route("/current-track", methods=["GET"])
def current_track():
    track = get_currently_playing()
    if not track:
        return jsonify({"error": "Brak aktywnego utworu"}), 204
    return jsonify(track)

@app.route("/play", methods=["POST"])
def play():
    # Jeśli gra, to pauza, jeśli nie gra – wznowienie
    pause_or_resume()
    return '', 204

@app.route("/next", methods=["POST"])
def next_track():
    skip_to_next()
    return '', 204

@app.route("/previous", methods=["POST"])
def previous_track():
    skip_to_previous()
    return '', 204

@app.route("/user", methods=["GET"])
def user():
    user = get_current_user()
    return jsonify({"display_name": user.get("display_name", "Nieznany")})

if __name__ == "__main__":
    app.run(port=5000)
