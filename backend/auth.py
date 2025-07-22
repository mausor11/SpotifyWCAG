import os
import json
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SCOPES = "user-read-private playlist-read-private user-library-read user-read-email user-read-playback-state user-modify-playback-state user-read-recently-played"
TOKEN_FILE = "spotify_tokens.json"
TOKEN_URL = "https://accounts.spotify.com/api/token"

def save_tokens(refresh_token):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"refresh_token": refresh_token}, f)

def load_refresh_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return json.load(f).get("refresh_token")
    return None

def request_access_token_from_refresh(refresh_token):
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(TOKEN_URL, data=data)
    response_data = response.json()
    if "access_token" in response_data:
        new_refresh = response_data.get("refresh_token")
        if new_refresh:
            save_tokens(new_refresh)
        return response_data["access_token"]
    return None

def request_tokens_via_auth():
    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
    }
    auth_request_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    print("🔐 Kliknij w link i zaloguj się:")
    print(auth_request_url)
    redirect_response = input("📥 Wklej pełny URL przekierowania po logowaniu: ")
    code = urllib.parse.parse_qs(urllib.parse.urlparse(redirect_response).query)["code"][0]
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(TOKEN_URL, data=data)
    response_data = response.json()
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    save_tokens(refresh_token)
    return access_token

def get_valid_token():
    refresh_token = load_refresh_token()
    if refresh_token:
        token = request_access_token_from_refresh(refresh_token)
        if token:
            return token
    return request_tokens_via_auth()

def request_tokens_via_code(code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(TOKEN_URL, data=data)
    response_data = response.json()
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    save_tokens(refresh_token)
    return access_token