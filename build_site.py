import os
import re
import json
import urllib.request
import urllib.parse
import urllib.error

# === KONFIGURACJA GITHUBA ===
USER = "mich111discord"
REPO = "Kanon-DiscoAdamusa"
TAG = "latest"                # tag Release'a z filmami .mp4
THUMBNAILS_TAG = "thumbnails"  # tag Release'a, do którego trafiają miniatury

# === MAPOWANIE: nazwa pliku .mp4 (dokładnie tak jak w Release) -> link YouTube ===
# Dopisuj tu kolejne pozycje w miarę dodawania nowych filmów.
# Klucz MUSI być identyczny z nazwą pliku widoczną w assets Release'a.
MOVIE_THUMBNAILS = {
    # "nazwa_pliku.mp4": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
}

OUTPUT_JSON = "tracks.json"

github_token = os.getenv("GITHUB_TOKEN")
api_headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/vnd.github+json'}
if github_token:
    api_headers['Authorization'] = f'token {github_token}'


# ---------- Pomocnicze wywołania GitHub API ----------

def api_get(url):
    req = urllib.request.Request(url, headers=api_headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def api_post_json(url, payload):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={**api_headers, 'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def get_or_create_thumbnails_release():
    """Pobiera Release z tagiem 'thumbnails', a jeśli nie istnieje - tworzy go."""
    url = f"https://api.github.com/repos/{USER}/{REPO}/releases/tags/{THUMBNAILS_TAG}"
    try:
        return api_get(url)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Release '{THUMBNAILS_TAG}' nie istnieje - tworzę nowy.")
            create_url = f"https://api.github.com/repos/{USER}/{REPO}/releases"
            return api_post_json(create_url, {
                "tag_name": THUMBNAILS_TAG,
                "name": "Miniatury (auto)",
                "body": "Automatycznie generowane miniatury YouTube. Nie usuwaj tego Release'a.",
                "draft": False,
                "prerelease": False,
            })
        raise


def upload_thumbnail_asset(release, filename, content_bytes):
    """Wgrywa plik jako nowy asset do podanego Release'a i zwraca jego browser_download_url."""
    upload_url = release['upload_url'].split('{')[0]
    query = urllib.parse.urlencode({'name': filename})
    req = urllib.request.Request(
        f"{upload_url}?{query}",
        data=content_bytes,
        headers={**api_headers, 'Content-Type': 'image/jpeg'},
        method='POST'
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
        return result['browser_download_url']


# ---------- YouTube ----------

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


def fetch_youtube_thumbnail_bytes(video_id):
    """Próbuje pobrać najlepszą dostępną jakość miniatury z YouTube (w pamięci, bez zapisu na dysk)."""
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
                return content
        except Exception:
            continue
    return None


# ---------- Pobranie listy filmów z Release'a 'latest' ----------

if TAG == "latest":
    videos_url = f"https://api.github.com/repos/{USER}/{REPO}/releases/latest"
else:
    videos_url = f"https://api.github.com/repos/{USER}/{REPO}/releases/tags/{TAG}"

try:
    videos_data = api_get(videos_url)
except Exception as e:
    print(f"Błąd podczas pobierania release'a: {e}")
    videos_url = f"https://api.github.com/repos/{USER}/{REPO}/releases/latest"
    videos_data = api_get(videos_url)

assets = videos_data.get('assets', [])

# ---------- Release z miniaturami ----------

thumbnails_release = get_or_create_thumbnails_release()
existing_thumb_assets = {
    a['name']: a['browser_download_url']
    for a in thumbnails_release.get('assets', [])
}

# ---------- Budowanie playlisty ----------

tracks_js = []

for idx, asset in enumerate(assets, start=1):
    download_url = asset['browser_download_url']
    raw_name = asset['name']

    if not raw_name.lower().endswith('.mp4'):
        continue

    title = raw_name.replace('.mp4', '').replace('.', ' ').replace('_', ' ')

    thumbnail_url = None
    youtube_link = MOVIE_THUMBNAILS.get(raw_name)
    video_id = extract_youtube_id(youtube_link)

    if video_id:
        asset_filename = f"{video_id}.jpg"

        if asset_filename in existing_thumb_assets:
            # Miniatura już wgrana wcześniej - nie pobieramy i nie wgrywamy ponownie
            thumbnail_url = existing_thumb_assets[asset_filename]
        else:
            content = fetch_youtube_thumbnail_bytes(video_id)
            if content:
                try:
                    thumbnail_url = upload_thumbnail_asset(thumbnails_release, asset_filename, content)
                    existing_thumb_assets[asset_filename] = thumbnail_url
                    print(f"✅ Wgrano nową miniaturę: {asset_filename}")
                except Exception as e:
                    print(f"⚠️  Nie udało się wgrać miniatury dla {raw_name}: {e}")
            else:
                print(f"⚠️  Nie udało się pobrać miniatury z YouTube dla: {raw_name}")
    else:
        print(f"ℹ️  Brak wpisu w MOVIE_THUMBNAILS dla: {raw_name}")

    tracks_js.append({
        'id': idx,
        'title': title,
        'url': download_url,
        'size': f"{round(asset['size'] / (1024 * 1024), 1)} MB",
        'thumbnail': thumbnail_url,
    })

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(tracks_js, f, ensure_ascii=False, indent=4)

print(f"Pomyślnie wygenerowano {OUTPUT_JSON} dla {len(tracks_js)} plików MP4!")
