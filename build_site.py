import urllib.request
import json
import re

# === KONFIGURACJA GITHUBA ===
USER = "mich111discord"       
REPO = "Kanon-DiscoAdamusa"         
TAG = "latest"                        


url = f"https://api.github.com/repos/{USER}/{REPO}/releases/tags/{TAG}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
except Exception as e:
    print(f"Błąd podczas pobierania release'a: {e}")
   
    url = f"https://api.github.com/repos/{USER}/{REPO}/releases/latest"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())

assets = data.get('assets', [])

tracks_js = []

for idx, asset in enumerate(assets, start=1):
    download_url = asset['browser_download_url']
    raw_name = asset['name']
    
    
    title = raw_name.replace('.mp4', '')
    title = title.replace('.', ' ')
    title = title.replace('_', ' ')
    
    tracks_js.append({
        'id': idx,
        'title': title,
        'url': download_url,
        'size': f"{round(asset['size'] / (1024 * 1024), 1)} MB"
    })


tracks_json_str = json.dumps(tracks_js, ensure_ascii=False, indent=4)


html_content = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kanon DiscoAdamusa 2026</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #0b0e14;
            color: #e6edf3;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        header {{
            text-align: center;
            margin-bottom: 25px;
        }}
        h1 {{
            color: #f1c40f;
            margin: 0 0 5px 0;
            font-size: 2.2rem;
            letter-spacing: 1px;
            text-shadow: 0 2px 10px rgba(241, 196, 15, 0.2);
        }}
        .subtitle {{
            color: #8b949e;
            font-size: 0.95rem;
        }}
        .container {{
            width: 100%;
            max-width: 900px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        #player-box {{
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }}
        video {{
            width: 100%;
            max-height: 500px;
            border-radius: 8px;
            background-color: #000;
            outline: none;
        }}
        #now-playing {{
            margin-top: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            color: #f1c40f;
            text-align: center;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        #playlist-box {{
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 15px;
            max-height: 450px;
            overflow-y: auto;
        }}
        .track-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 15px;
            border-bottom: 1px solid #21262d;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s, color 0.2s;
        }}
        .track-item:last-child {{
            border-bottom: none;
        }}
        .track-item:hover {{
            background-color: #21262d;
        }}
        .track-item.active {{
            background-color: #272e3b;
            border-left: 4px solid #f1c40f;
            color: #f1c40f;
        }}
        .track-title {{
            font-size: 0.95rem;
            word-break: break-word;
            padding-right: 10px;
        }}
        .track-size {{
            font-size: 0.8rem;
            color: #8b949e;
            white-space: nowrap;
        }}
        /* Custom Scrollbar */
        #playlist-box::-webkit-scrollbar {{
            width: 8px;
        }}
        #playlist-box::-webkit-scrollbar-track {{
            background: #161b22;
        }}
        #playlist-box::-webkit-scrollbar-thumb {{
            background: #30363d;
            border-radius: 4px;
        }}
    </style>
</head>
<body>

    <header>
        <h1>👑 Kanon DiscoAdamusa 2026 👑</h1>
        <div class="subtitle">Oficjalne Archiwum Wideo 1080p</div>
    </header>

    <div class="container">
        <div id="player-box">
            <video id="player" controls autoplay preload="metadata">
                <source src="" type="video/mp4">
            </video>
            <div id="now-playing">Wybierz utwór z listy...</div>
        </div>

        <div id="playlist-box" id="playlist">
            <!-- Utwory ładowane z JS -->
        </div>
    </div>

    <script>
        const tracks = {tracks_json_str};

        const player = document.getElementById('player');
        const nowPlaying = document.getElementById('now-playing');
        const playlistBox = document.getElementById('playlist-box');

        function renderPlaylist() {{
            playlistBox.innerHTML = '';
            tracks.forEach((track, index) => {{
                const item = document.createElement('div');
                item.className = 'track-item' + (index === 0 ? ' active' : '');
                item.dataset.index = index;
                item.innerHTML = `
                    <span class="track-title">${{track.id}}. ${{track.title}}</span>
                    <span class="track-size">${{track.size}}</span>
                `;
                item.addEventListener('click', () => playTrack(index));
                playlistBox.appendChild(item);
            }});
        }}

        function playTrack(index) {{
            const items = document.querySelectorAll('.track-item');
            items.forEach(el => el.classList.remove('active'));
            
            if(items[index]) {{
                items[index].classList.add('active');
                items[index].scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }}

            const track = tracks[index];
            player.src = track.url;
            nowPlaying.innerText = `${{track.id}}. ${{track.title}}`;
            player.play();
        }}

        player.addEventListener('ended', () => {{
            const currentActive = document.querySelector('.track-item.active');
            let nextIndex = 0;
            if (currentActive) {{
                nextIndex = parseInt(currentActive.dataset.index) + 1;
            }}
            if (nextIndex < tracks.length) {{
                playTrack(nextIndex);
            }} else {{
                playTrack(0); // Zapętlenie od pierwszego
            }}
        }});

        // Inicjalizacja
        renderPlaylist();
        if(tracks.length > 0) {{
            player.src = tracks[0].url;
            nowPlaying.innerText = `${{tracks[0].id}}. ${{tracks[0].title}}`;
        }}
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Pomyślnie wygenerowano index.html dla {len(tracks_js)} plików MP4!")
