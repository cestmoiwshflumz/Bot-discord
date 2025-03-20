import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
ARTIST_ID = "2bU3YsbwUEM8P8G6sHYgVE"  # L'ID de l'artiste à surveiller
LATEST_RELEASE_FILE = "latest_release.json"


# Obtenir un token d'accès à l'API Spotify
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")


# Récupérer la dernière sortie de l’artiste
def get_latest_release():
    token = get_spotify_token()
    if not token:
        print("❌ Erreur : Impossible de récupérer le token Spotify.")
        return None

    url = f"https://api.spotify.com/v1/artists/{ARTIST_ID}/albums?include_groups=single,album&limit=1"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data["items"]:
            latest_album = data["items"][0]

            # Récupération des informations importantes
            album_id = latest_album["id"]
            cover_url = latest_album["images"][0]["url"] if latest_album["images"] else None

            # Conversion de la date (Format Spotify: YYYY-MM-DD → Jour Numéro Mois Année)
            release_date = latest_album["release_date"]
            formatted_date = datetime.strptime(release_date, "%Y-%m-%d").strftime("%d %b %Y")

            # Récupérer les morceaux de l'album pour obtenir un preview
            track_url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
            track_response = requests.get(track_url, headers=headers)
            preview_url = None
            if track_response.status_code == 200:
                track_data = track_response.json()
                if track_data["items"]:
                    preview_url = track_data["items"][0].get("preview_url")

            return {
                "name": latest_album["name"],
                "url": latest_album["external_urls"]["spotify"],
                "release_date": formatted_date,  # Formaté en "07 Mar 2024"
                "cover": cover_url,
                "preview": preview_url
            }
    return None



# Vérifier si une nouvelle sortie est disponible
def check_for_new_release():
    latest_release = get_latest_release()
    if not latest_release:
        return None

    try:
        with open(LATEST_RELEASE_FILE, "r") as file:
            saved_release = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        saved_release = {"name": "", "url": "", "release_date": "", "cover": "", "preview": ""}

    if latest_release["name"] != saved_release["name"]:
        # Mise à jour du fichier
        with open(LATEST_RELEASE_FILE, "w") as file:
            json.dump(latest_release, file, indent=4)
        return latest_release

    return None
