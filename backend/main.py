from flask import Flask, jsonify, request
from flask_cors import CORS
from api import get_valid_token, get_current_user, get_currently_playing, skip_to_next, skip_to_previous, pause_or_resume, set_shuffle, set_repeat, get_player_state, get_queue, play_specific_track, get_artist_albums, get_album_tracks, get_user_saved_albums, get_new_releases, get_recently_played, get_user_saved_playlists, play_playlist, get_playlist_tracks, search_and_play_song
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
    # Pobierz parametry z query string
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    albums = get_user_saved_albums(limit=limit, offset=offset)
    if albums is None:
        return jsonify({"error": "Could not fetch user albums"}), 500
    return jsonify(albums)

@app.route("/new-releases", methods=["GET"])
def new_releases():
    albums = get_new_releases()
    if albums is None:
        return jsonify({"error": "Could not fetch new releases"}), 500
    return jsonify(albums)

@app.route("/recently-played-tracks", methods=["GET"])
def recently_played_tracks():
    """Pobiera ostatnio grane utwory (nowy endpoint)"""
    try:
        # Użyj istniejącej funkcji z api.py
        data = get_recently_played(limit=20)
        
        if data and 'items' in data:
            tracks = []
            
            for item in data['items']:
                track = item.get('track', {})
                if track:
                    # Formatuj czas trwania
                    duration_ms = track.get('duration_ms', 0)
                    duration_minutes = duration_ms // 60000
                    duration_seconds = (duration_ms % 60000) // 1000
                    duration = f"{duration_minutes}:{duration_seconds:02d}"
                    
                    tracks.append({
                        'id': track.get('id'),
                        'name': track.get('name'),
                        'artist': track.get('artists', [{}])[0].get('name', 'Unknown Artist'),
                        'album': track.get('album', {}).get('name', 'Unknown Album'),
                        'image': track.get('album', {}).get('images', [{}])[0].get('url', ''),
                        'duration': duration
                    })
            
            return jsonify(tracks)
        else:
            return jsonify([])
            
    except Exception as e:
        print(f"❌ Błąd pobierania ostatnio granych: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/play-single-track", methods=["POST"])
def play_single_track():
    """Odtwarza pojedynczy utwór (nowy endpoint)"""
    try:
        data = request.get_json()
        track_id = data.get('track_id')
        
        if not track_id:
            return jsonify({"error": "No track ID provided"}), 400
        
        # Użyj istniejącej funkcji z api.py
        track_uris = [f'spotify:track:{track_id}']
        status, text = play_specific_track(track_uris)
        
        if status in [200, 204]:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Could not play track"}), status
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/user-playlists", methods=["GET"])
def user_playlists():
    # Pobierz parametry z query string
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    playlists = get_user_saved_playlists(limit=limit)
    if playlists is None:
        return jsonify({"error": "Could not fetch user playlists"}), 500
    
    # Formatuj playlisty podobnie jak albumy
    playlists_list = []
    for playlist in playlists:
        playlist_id = playlist['id']
        playlist_name = playlist['name']
        playlist_image = playlist['images'][0]['url'] if playlist['images'] else None
        owner = playlist['owner']['display_name'] if playlist['owner'] else ''
        playlists_list.append({
            'id': playlist_id,
            'name': playlist_name,
            'image': playlist_image,
            'author': owner
        })
    
    return jsonify(playlists_list)

@app.route("/play-playlist", methods=["POST"])
def play_playlist():
    data = request.get_json()
    playlist_id = data.get('playlist_id')
    if not playlist_id:
        return jsonify({"error": "Missing playlist_id"}), 400
    
    # Pobierz utwory z playlisty
    track_uris = get_playlist_tracks(playlist_id)
    if not track_uris:
        return jsonify({"error": "Could not fetch playlist tracks"}), 500
    print(track_uris)
    # Odtwórz album
    status, text = play_specific_track(track_uris)
    if status not in range(200, 299):
        return jsonify(text), status
    return '', 204

@app.route("/speech-command", methods=["POST"])
def speech_command():
    """Obsługuje komendy głosowe"""
    try:
        data = request.get_json()
        action = data.get('action')
        
        if action == 'next':
            skip_to_next()
            return jsonify({"success": True, "action": "next"})
        elif action == 'previous':
            skip_to_previous()
            return jsonify({"success": True, "action": "previous"})
        elif action == 'play':
            pause_or_resume()
            return jsonify({"success": True, "action": "play"})
        elif action == 'pause':
            pause_or_resume()
            return jsonify({"success": True, "action": "pause"})
        elif action == 'play_song':
            song_title = data.get('song')
            if song_title:
                success, message = search_and_play_song(song_title)
                return jsonify({"success": success, "action": "play_song", "song": song_title, "message": message})
            else:
                return jsonify({"error": "No song title provided"}), 400
        else:
            return jsonify({"error": "Unknown action"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)



