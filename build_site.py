import os
import re
import urllib.request
import json

# === KONFIGURACJA GITHUBA ===
USER = "mich111discord"
REPO = "Kanon-DiscoAdamusa"
TAG = "latest"

# === MAPOWANIE: nazwa pliku .mp4 (dokładnie tak jak w Release) -> link YouTube ===
# Dopisuj tu kolejne pozycje w miarę dodawania nowych filmów.
# Klucz MUSI być identyczny z nazwą pliku widoczną w assets Release'a.
MOVIE_THUMBNAILS = {
    # "nazwa_pliku.mp4": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
}

THUMBNAILS_DIR = "thumbnails"
OUTPUT_JSON = "tracks.json"

# Obsługa tokenu z GitHub Actions
github_token = os.getenv("GITHUB_TOKEN")
headers = {'User-Agent': 'Mozilla/5.0'}
if github_token:
    headers['Authorization'] = f'token {github_token}'

if TAG == "latest":
    url = f"https://api.github.com/repos/{USER}/{REPO}/releases/latest"
else:
    url = f"https://api.github.com/repos/{USER}/{REPO}/releases/tags/{TAG}"

req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
except Exception as e:
    print(f"Błąd podczas pobierania release'a: {e}")
    url = f"https://api.github.com/repos/{USER}/{REPO}/releases/latest"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())

assets = data.get('assets', [])
tracks_js = []

os.makedirs(THUMBNAILS_DIR, exist_ok=True)


def extract_youtube_id(link):
    """Wyciąga ID filmu z różnych formatów linków YouTube."""
    if not link:
        return None
    patterns = [
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"youtube\.com/watch\?v=([A-Za-z0-9_-]{11})",
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
        r"youtube\.com/shorts/([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)
    return None


def download_thumbnail(video_id, dest_path):
    """Próbuje pobrać najlepszą dostępną jakość miniatury z YouTube."""
    if os.path.exists(dest_path):
        return True  # już pobrana wcześniej, nie ściągamy ponownie

    candidates = ["maxresdefault", "hqdefault", "mqdefault", "default"]
    for quality in candidates:
        thumb_url = f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"
        try:
            req_thumb = urllib.request.Request(thumb_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_thumb) as resp:
                content = resp.read()
                # YouTube zwraca małą "szarą" grafikę-placeholder gdy dana jakość nie istnieje
                if len(content) < 1000:
                    continue
                with open(dest_path, "wb") as f:
                    f.write(content)
                return True
        except Exception:
            continue
    return False


for idx, asset in enumerate(assets, start=1):
    download_url = asset['browser_download_url']
    raw_name = asset['name']

    if not raw_name.lower().endswith('.mp4'):
        continue

    title = raw_name.replace('.mp4', '').replace('.', ' ').replace('_', ' ')

    thumbnail_path = None
    youtube_link = MOVIE_THUMBNAILS.get(raw_name)
    video_id = extract_youtube_id(youtube_link)

    if video_id:
        local_thumb_path = os.path.join(THUMBNAILS_DIR, f"{video_id}.jpg")
        if download_thumbnail(video_id, local_thumb_path):
            thumbnail_path = f"{THUMBNAILS_DIR}/{video_id}.jpg"
        else:
            print(f"⚠️  Nie udało się pobrać miniatury dla: {raw_name}")
    else:
        print(f"ℹ️  Brak wpisu w MOVIE_THUMBNAILS dla: {raw_name}")

    tracks_js.append({
        'id': idx,
        'title': title,
        'url': download_url,
        'size': f"{round(asset['size'] / (1024 * 1024), 1)} MB",
        'thumbnail': thumbnail_path,
    })

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(tracks_js, f, ensure_ascii=False, indent=4)

print(f"Pomyślnie wygenerowano {OUTPUT_JSON} dla {len(tracks_js)} plików MP4!")
