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
        return None  # Brak aktywnego odtwarzania

    data = response.json()
    track = data.get("item")
    if not track:
        return None

    track_name = track["name"]
    artist_name = track["artists"][0]["name"]
    album_image = track["album"]["images"][0]["url"] if track["album"]["images"] else None
    progress_ms = data.get("progress_ms", 0)
    is_playing = data.get("is_playing", False)
    duration_ms = data.get("duration_ms", 0)

    return {
        "track": track_name,
        "artist": artist_name,
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
