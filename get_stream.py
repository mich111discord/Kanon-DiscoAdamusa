import json
import yt_dlp

CHANNELS = [
    {"name": "YouTube", "url": "https://www.youtube.com/channel/UC7wqel4udl9FaiyH5v78zQg/live"},
    {"name": "TikTok", "url": "https://www.tiktok.com/@discoadamus/live"}
]

OUTPUT_FILE = "stream.json"

def get_m3u8(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'best',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info.get('is_live') or info.get('live_status') == 'is_live':
                return info.get('url')
    except Exception:
        return None
    return None

def main():
    result = {"is_live": False, "platform": None, "m3u8_url": ""}

    for channel in CHANNELS:
        m3u8_url = get_m3u8(channel["url"])
        if m3u8_url:
            result = {
                "is_live": True,
                "platform": channel["name"],
                "m3u8_url": m3u8_url
            }
            break

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
