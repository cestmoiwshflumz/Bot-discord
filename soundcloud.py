import json
from dotenv import load_dotenv
import requests
import xml.etree.ElementTree as ET
import os
from datetime import datetime

load_dotenv()
# ID SoundCloud de ton ami
SOUNDCLOUD_RSS = os.getenv("SOUNDCLOUD_RSS")
SOUNDCLOUD_FEED_URL = f"https://feeds.soundcloud.com/users/soundcloud:users:{SOUNDCLOUD_RSS}/sounds.rss"
LATEST_RELEASE_FILE = "latest_soundcloud.json"


def get_latest_sound():
    response = requests.get(SOUNDCLOUD_FEED_URL)
    if response.status_code != 200:
        print("❌ Erreur lors de la récupération du flux SoundCloud")
        return None

    root = ET.fromstring(response.text)
    latest_entry = root.find(".//item")  # Trouve le dernier son

    if latest_entry is not None:
        title = latest_entry.find("title").text
        url = latest_entry.find("link").text
        pub_date = latest_entry.find("pubDate").text
        cover_url = None

        pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z").strftime("%d %b %Y")

        # Extraire l'image de la cover
        for element in latest_entry.iter():
            if "image" in element.tag and "href" in element.attrib:
                cover_url = element.attrib["href"]
                break  # Prend la première image trouvée

        return {
            "title": title,
            "url": url,
            "published": pub_date,
            "image": cover_url
        }

    return None
def check_for_new_sound():
    latest_sound = get_latest_sound()
    if not latest_sound:
        return None

    try:
        with open("latest_sound.json", "r") as file:
            saved_sound = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        saved_sound = {"title": "", "url": "", "published": ""}

    if latest_sound["title"] != saved_sound["title"]:
        with open("latest_sound.json", "w") as file:
            json.dump(latest_sound, file, indent=4)
        return latest_sound

    return None