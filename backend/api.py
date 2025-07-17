import requests
from auth import get_valid_token

def get_headers():
    token = get_valid_token()
    return {"Authorization": f"Bearer {token}"}

def get_current_user():
    headers = get_headers()
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return response.json()

def get_recently_played(limit=1):
    headers = get_headers()
    url = f"https://api.spotify.com/v1/me/player/recently-played?limit={limit}"
    response = requests.get(url, headers=headers)
    return response.json()


def get_currently_playing():
    headers = get_headers()
    url = "https://api.spotify.com/v1/me/player"
    response = requests.get(url, headers=headers)

    if response.status_code == 204 or response.status_code == 202:
        return None

    data = response.json()
    track = data.get("item")
    if not track:
        return None

    track_name = track["name"]
    artists = track.get("artists", [])
    
    artist_name_all = ", ".join([artist["name"] for artist in artists])
    artist_name_main = artists[0]["name"] if artists else "Nieznany artysta"
    artist_id = artists[0]["id"] if artists else None
    
    artist_image = None
    if artist_id:
        artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
        artist_response = requests.get(artist_url, headers=headers)
        if artist_response.status_code == 200:
            artist_data = artist_response.json()
            if artist_data.get("images"):
                artist_image = artist_data["images"][0]["url"]

    album_image = track["album"]["images"][0]["url"] if track["album"]["images"] else None
    progress_ms = data.get("progress_ms", 0)
    is_playing = data.get("is_playing", False)
    duration_ms = track.get("duration_ms", 0)

    return {
        "track": track_name,
        "track_id": track.get("id"),
        "artist": artist_name_all,
        "artist_main": artist_name_main,
        "artist_id": artist_id,
        "artist_image": artist_image,
        "image": album_image,
        "progress_ms": progress_ms,
        "is_playing": is_playing,
        "duration_ms": duration_ms
    }

def skip_to_next():
    headers = get_headers()
    response = requests.post("https://api.spotify.com/v1/me/player/next", headers=headers)
    if response.status_code in (200, 204):
        print("⏭️ Przewinięto do następnego utworu.")
    elif response.status_code == 403:
        print("🚫 Nie można przewinąć – brak uprawnień (np. reklamowy Spotify).")
    else:
        print(f"⚠️ Błąd: {response.status_code} – {response.text}")

def skip_to_previous():
    headers = get_headers()
    response = requests.post("https://api.spotify.com/v1/me/player/previous", headers=headers)
    if response.status_code in (200, 204):
        print("⏭️ Przewinięto do poprzedniego utworu.")
    elif response.status_code == 403:
        print("🚫 Nie można przewinąć – brak uprawnień (np. reklamowy Spotify).")
    else:
        print(f"⚠️ Błąd: {response.status_code} – {response.text}")

def pause_or_resume():
    headers = get_headers()
    headers["Content-Type"] = "application/json"

    # Najpierw pobierz stan odtwarzania
    state_resp = requests.get("https://api.spotify.com/v1/me/player", headers=headers)
    if state_resp.status_code != 200:
        print("⚠️ Nie udało się pobrać stanu odtwarzania.")
        return

    data = state_resp.json()
    if not data.get("is_playing"):
        # Jeśli nie gra – wznowienie
        play_resp = requests.put("https://api.spotify.com/v1/me/player/play", headers=headers, json={})
        if play_resp.status_code in (200, 204):
            print("▶️ Wznowiono odtwarzanie.")
        else:
            print(f"⚠️ Błąd przy wznawianiu: {play_resp.status_code}")
    else:
        # Jeśli gra – pauza
        pause_resp = requests.put("https://api.spotify.com/v1/me/player/pause", headers=headers, json={})
        if pause_resp.status_code in (200, 204):
            print("⏸️ Wstrzymano odtwarzanie.")
        else:
            print(f"⚠️ Błąd przy pauzie: {pause_resp.status_code}")

def set_shuffle(state):
    headers = get_headers()
    url = f"https://api.spotify.com/v1/me/player/shuffle?state={'true' if state else 'false'}"
    response = requests.put(url, headers=headers)
    return response.status_code, response.text

def set_repeat(state):
    headers = get_headers()
    url = f"https://api.spotify.com/v1/me/player/repeat?state={state}"
    response = requests.put(url, headers=headers)
    return response.status_code, response.text

def get_player_state():
    headers = get_headers()
    url = "https://api.spotify.com/v1/me/player"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    data = response.json()
    return {
        'shuffle_state': data.get('shuffle_state', False),
        'repeat_state': data.get('repeat_state', 'off'),
        'device': data.get('device', {}),
        'is_playing': data.get('is_playing', False),
        'track': data.get('item', {}).get('name', ''),
        'artist': data.get('item', {}).get('artists', [{}])[0].get('name', ''),
        'image': (data.get('item', {}).get('album', {}).get('images', [{}])[0].get('url', '') if data.get('item', {}).get('album', {}).get('images') else ''),
    }

def get_queue():
    headers = get_headers()
    url = 'https://api.spotify.com/v1/me/player/queue'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"⚠️  Błąd API Spotify przy pobieraniu kolejki: Status {response.status_code}")
        print(f"   Odpowiedź: {response.text}")
        return None
    return response.json()

def play_specific_track(track_uris):
    headers = get_headers()
    url = "https://api.spotify.com/v1/me/player/play"
    data = {
        "uris": track_uris
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code not in range(200, 299):
        print(f"⚠️ Błąd przy odtwarzaniu utworu: {response.status_code} - {response.text}")
    return response.status_code, response.text

def get_artist_albums(artist_id):
    headers = get_headers()
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    params = {
        'include_groups': 'album,single',
        'limit': 3
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print(f"⚠️ Błąd API Spotify przy pobieraniu albumów artysty: Status {response.status_code}")
        print(f"   Odpowiedź: {response.text}")
        return None

def get_album_tracks(album_id):
    headers = get_headers()
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    params = {
        'limit': 50  # Maksymalna liczba utworów z albumu
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        tracks = response.json().get('items', [])
        # Konwertuj na URI format wymagany przez Spotify API
        track_uris = [f"spotify:track:{track['id']}" for track in tracks]
        return track_uris
    else:
        print(f"⚠️ Błąd API Spotify przy pobieraniu utworów z albumu: Status {response.status_code}")
        print(f"   Odpowiedź: {response.text}")
        return None

def get_user_saved_albums():
    headers = get_headers()
    url = "https://api.spotify.com/v1/me/albums"
    params = {
        'limit': 10,
        'offset': 0
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        albums = response.json().get('items', [])
    else:
        print(f"⚠️ Błąd API Spotify przy pobieraniu zapisanych albumów: Status {response.status_code}")
        print(f"   Odpowiedź: {response.text}")
        return None
    
    albums_list = []
    for album in albums:
        album_data = album['album']
        album_id = album_data['id']
        album_name = album_data['name']
        album_image = album_data['images'][0]['url'] if album_data['images'] else None
        author = album_data['artists'][0]['name'] if album_data['artists'] else ''
        albums_list.append({
            'id': album_id,
            'name': album_name,
            'image': album_image,
            'author': author
        })
    return albums_list

def get_new_releases():
    headers = get_headers()
    url = "https://api.spotify.com/v1/browse/new-releases"
    params = {
        'limit': 9,
        'offset': 0
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        albums = response.json().get('albums', {}).get('items', [])
    else:
        print(f"⚠️ Błąd API Spotify przy pobieraniu zapisanych albumów: Status {response.status_code}")
        print(f"   Odpowiedź: {response.text}")
        return None
    
    albums_list = []
    for album in albums:
        album_id = album['id']
        album_name = album['name']
        album_image = album['images'][0]['url'] if album['images'] else None
        author = album['artists'][0]['name'] if album['artists'] else ''
        albums_list.append({
            'id': album_id,
            'name': album_name,
            'image': album_image,
            'author': author
        })
    return albums_list

print(get_new_releases())