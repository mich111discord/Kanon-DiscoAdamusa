import os
import json
import urllib.request
import urllib.error

# === KONFIGURACJA GITHUBA ===
USER = "mich111discord"
REPO = "Kanon-DiscoAdamusa"
TAG = "latest"                  # tag Release'a z filmami .mp4
THUMBNAILS_TAG = "thumbnails"    # tag Release'a, w którym ręcznie umieszczasz miniatury

OUTPUT_JSON = "tracks.json"

github_token = os.getenv("GITHUB_TOKEN")
api_headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/vnd.github+json'}
if github_token:
    api_headers['Authorization'] = f'token {github_token}'

# === MAPA ZAMIANY POLSKICH ZNAKÓW ===
POLISH_CHAR_MAP = {
    'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
    'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
    'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
    'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z',
}


def api_get(url):
    req = urllib.request.Request(url, headers=api_headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def title_to_thumbnail_basename(title):
    """
    Zamienia tytuł utworu na nazwę bazową pliku miniatury (bez rozszerzenia),
    zgodnie z konwencją: spacje -> kropki, polskie znaki -> odpowiedniki bez ogonków.
    Np. "67 Ćma Remix" -> "67.Cma.Remix"
    """
    result = title.replace(' ', '.')
    return ''.join(POLISH_CHAR_MAP.get(ch, ch) for ch in result)


def get_thumbnails_release_assets():
    """
    Pobiera listę assetów z Release'a 'thumbnails' (wgrywanych ręcznie przez użytkownika).
    Jeśli Release jeszcze nie istnieje, zwraca pusty słownik zamiast wywalać błąd.
    """
    url = f"https://api.github.com/repos/{USER}/{REPO}/releases/tags/{THUMBNAILS_TAG}"
    try:
        release = api_get(url)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"ℹ️  Release '{THUMBNAILS_TAG}' jeszcze nie istnieje - brak miniatur.")
            return {}
        raise
    return {asset['name']: asset['browser_download_url'] for asset in release.get('assets', [])}


def find_thumbnail_url(title, thumb_assets):
    """
    Szuka assetu, którego nazwa (bez rozszerzenia) dokładnie pasuje do przetworzonego tytułu.
    Rozszerzenie może być dowolne (.jpg, .png, .jpeg itd.).
    """
    base_name = title_to_thumbnail_basename(title)
    for asset_name, asset_url in thumb_assets.items():
        name_without_ext = os.path.splitext(asset_name)[0]
        if name_without_ext == base_name:
            return asset_url
    return None


# ---------- Pobranie listy filmów z Release'a otagowanego dosłownie jako TAG ----------
#
# WAŻNE: pobieramy zawsze PO DOSŁOWNYM TAGU (/releases/tags/{TAG}), NIGDY przez alias
# /releases/latest. Ten alias zwraca release, który GitHub aktualnie uznaje za
# "najnowszy" (np. wg daty utworzenia albo flagi "make latest"), więc odkąd istnieje
# drugi release (np. 'thumbnails'), alias mógłby zwrócić WŁAŚNIE JEGO zamiast
# release'a z filmami - i wyzerować całą playlistę.

videos_url = f"https://api.github.com/repos/{USER}/{REPO}/releases/tags/{TAG}"
videos_data = api_get(videos_url)

assets = videos_data.get('assets', [])

mp4_count = sum(1 for a in assets if a['name'].lower().endswith('.mp4'))
if mp4_count == 0:
    raise RuntimeError(
        f"Release '{TAG}' zwrócił {len(assets)} assetów, ale ŻADEN nie jest plikiem .mp4. "
        f"Przerywam działanie, żeby NIE nadpisać istniejącego tracks.json pustą listą. "
        f"Sprawdź, czy tag '{TAG}' na pewno wskazuje na release z filmami, a nie np. na 'thumbnails'."
    )

# ---------- Miniatury wgrane ręcznie do Release'a 'thumbnails' ----------

thumb_assets = get_thumbnails_release_assets()

# ---------- Budowanie playlisty ----------

tracks_js = []

for idx, asset in enumerate(assets, start=1):
    download_url = asset['browser_download_url']
    raw_name = asset['name']

    if not raw_name.lower().endswith('.mp4'):
        continue

    title = raw_name.replace('.mp4', '').replace('.', ' ').replace('_', ' ')

    thumbnail_url = find_thumbnail_url(title, thumb_assets)
    if thumbnail_url is None:
        expected = title_to_thumbnail_basename(title)
        print(f"ℹ️  Brak miniatury dla: {raw_name} (oczekiwana nazwa bazowa: {expected}.*)")

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
