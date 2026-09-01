import json
import yt_dlp

TARGETS = {
    "youtube": {
        "name": "YouTube",
        "url": "https://www.youtube.com/channel/UCSJ4gkVC6NrvII8umztf0Ow/live"
    },
    "tiktok": {
        "name": "TikTok",
        "url": "https://www.tiktok.com/@discoadamus/live"
    }
}

OUTPUT_FILE = "stream.json"

def check_stream(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'best',
        # Bypass blokady bota YouTube na serwerach GitHub:
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'mweb']
            }
        }
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info.get('is_live') or info.get('live_status') == 'is_live':
                return {
                    "is_live": True,
                    "title": info.get('title', 'Live Stream'),
                    "m3u8_url": info.get('url', '')
                }
    except Exception as e:
        print(f"Błąd przy pobieraniu {url}: {e}")
    
    return {"is_live": False, "title": "", "m3u8_url": ""}

def main():
    result = {
        "any_live": False,
        "streams": {}
    }

    for key, data in TARGETS.items():
        print(f"Sprawdzanie {data['name']}...")
        stream_info = check_stream(data["url"])
        
        result["streams"][key] = {
            "name": data["name"],
            "is_live": stream_info["is_live"],
            "title": stream_info["title"],
            "m3u8_url": stream_info["m3u8_url"]
        }
        
        if stream_info["is_live"]:
            result["any_live"] = True

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("Poprawnie zapisano status do stream.json")

if __name__ == "__main__":
    main()
