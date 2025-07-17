from flask import Flask, jsonify, request
from flask_cors import CORS
from api import get_valid_token, get_current_user, get_currently_playing, skip_to_next, skip_to_previous, pause_or_resume, set_shuffle, set_repeat, get_player_state, get_queue, play_specific_track, get_artist_albums, get_album_tracks, get_user_saved_albums, get_new_releases
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

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

@app.route('/set-volume', methods=['PUT'])
def set_volume():
    volume = request.args.get('volume_percent')
    if not volume:
        return {'error': 'Missing volume_percent'}, 400

    token = get_valid_token()
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.put(
        f'https://api.spotify.com/v1/me/player/volume?volume_percent={volume}',
        headers=headers
    )

    if response.status_code == 204:
        return '', 204
    else:
        return {'error': 'Spotify volume update failed', 'details': response.json()}, response.status_code

@app.route('/set-shuffle', methods=['PUT'])
def set_shuffle_route():
    state = request.args.get('state', 'false').lower() == 'true'
    status, text = set_shuffle(state)
    return ('', 204) if status == 204 else (text, status)

@app.route('/set-repeat', methods=['PUT'])
def set_repeat_route():
    state = request.args.get('state', 'off')
    status, text = set_repeat(state)
    return ('', 204) if status == 204 else (text, status)

@app.route('/player-state', methods=['GET'])
def player_state():
    data = get_player_state()
    if not data:
        return {'error': 'No player state'}, 204
    return data

@app.route('/queue', methods=['GET'])
def queue():
    data = get_queue()
    if not data:
        return {'error': 'No queue'}, 204
    
    print("--- KOLEJKA ---")
    if 'queue' in data and data['queue']:
        for i, track in enumerate(data['queue']):
            track_name = track.get('name', 'Brak nazwy')
            artist_name = track.get('artists', [{}])[0].get('name', 'Brak artysty')
            print(f"{i+1}. {track_name} - {artist_name}")
    else:
        print("Kolejka jest pusta.")
    print("---------------")

    return data

@app.route("/play-track", methods=["POST"])
def play_track():
    data = request.get_json()
    track_uris = data.get('uris')
    if not track_uris:
        return jsonify({"error": "Missing track URIs"}), 400
    
    status, text = play_specific_track(track_uris)
    if status not in range(200, 299):
        return jsonify(text), status
    return '', 204

@app.route('/artist-albums/<artist_id>', methods=['GET'])
def artist_albums(artist_id):
    albums = get_artist_albums(artist_id)
    if albums is None:
        return jsonify({"error": "Could not fetch artist albums"}), 500
    return jsonify(albums)

@app.route("/play-album", methods=["POST"])
def play_album():
    data = request.get_json()
    album_id = data.get('album_id')
    if not album_id:
        return jsonify({"error": "Missing album_id"}), 400
    
    # Pobierz utwory z albumu
    track_uris = get_album_tracks(album_id)
    if not track_uris:
        return jsonify({"error": "Could not fetch album tracks"}), 500
    
    # Odtwórz album
    status, text = play_specific_track(track_uris)
    if status not in range(200, 299):
        return jsonify(text), status
    return '', 204

@app.route("/user-albums", methods=["GET"])
def user_albums():
    albums = get_user_saved_albums()
    if albums is None:
        return jsonify({"error": "Could not fetch user albums"}), 500
    return jsonify(albums)

@app.route("/new-releases", methods=["GET"])
def new_releases():
    albums = get_new_releases()
    if albums is None:
        return jsonify({"error": "Could not fetch new releases"}), 500
    return jsonify(albums)

if __name__ == "__main__":
    app.run(port=5000)

