import os
import urllib.request
import json

# === KONFIGURACJA GITHUBA I DISCORDA ===
USER = "mich111discord"       
REPO = "Kanon-DiscoAdamusa"         
TAG = "latest"                        
DISCORD_INVITE_URL = "https://discord.gg/ErbWv3kKCB"

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

for idx, asset in enumerate(assets, start=1):
    download_url = asset['browser_download_url']
    raw_name = asset['name']
    
    if not raw_name.lower().endswith('.mp4'):
        continue
    
    title = raw_name.replace('.mp4', '').replace('.', ' ').replace('_', ' ')
    
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
            margin-bottom: 20px;
            position: relative;
            width: 100%;
            max-width: 900px;
        }}
        h1 {{
            color: #f1c40f;
            margin: 0 0 5px 0;
            font-size: 2.2rem;
            letter-spacing: 1px;
            text-shadow: 0 2px 10px rgba(241, 196, 15, 0.4);
        }}
        .subtitle {{
            color: #8b949e;
            font-size: 0.95rem;
            margin-bottom: 15px;
        }}
        .discord-btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background-color: #5865F2;
            color: #fff;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.9rem;
            transition: background 0.2s, transform 0.1s;
        }}
        .discord-btn:hover {{
            background-color: #4752C4;
            transform: translateY(-1px);
        }}
        .container {{
            width: 100%;
            max-width: 900px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        /* --- ZŁOTY PLAYER VIDEO --- */
        #player-box {{
            background: linear-gradient(145deg, #1c180a, #161b22);
            border: 2px solid #f1c40f;
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 0 15px rgba(241, 196, 15, 0.25), 0 8px 24px rgba(0,0,0,0.6);
            position: relative;
        }}
        video {{
            width: 100%;
            max-height: 500px;
            border-radius: 8px;
            background-color: #000;
            outline: none;
            border: 1px solid rgba(241, 196, 15, 0.3);
        }}
        .cdn-status {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            margin-top: 10px;
            font-size: 0.82rem;
            color: #2ecc71;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        .cdn-dot {{
            width: 8px;
            height: 8px;
            background-color: #2ecc71;
            border-radius: 50%;
            box-shadow: 0 0 8px #2ecc71;
            animation: pulse 1.5s infinite;
        }}
        @keyframes pulse {{
            0% {{ opacity: 0.4; }}
            50% {{ opacity: 1; }}
            100% {{ opacity: 0.4; }}
        }}
        #now-playing {{
            margin-top: 10px;
            font-size: 1.15rem;
            font-weight: 700;
            color: #f1c40f;
            text-align: center;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            text-shadow: 0 1px 3px rgba(0,0,0,0.8);
        }}
        #search-box {{
            width: 100%;
            padding: 12px 16px;
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            color: #e6edf3;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.2s;
        }}
        #search-box:focus {{
            border-color: #f1c40f;
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
        <a href="{DISCORD_INVITE_URL}" target="_blank" class="discord-btn">
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                <path d="M13.545 2.907a13.227 13.227 0 0 0-3.257-1.011.05.05 0 0 0-.052.025c-.141.25-.297.577-.406.833a12.19 12.19 0 0 0-3.658 0 8.258 8.258 0 0 0-.412-.833.051.051 0 0 0-.052-.025c-1.125.194-2.22.534-3.257 1.011a.041.041 0 0 0-.021.018C.356 6.024-.213 9.047.066 12.032c.001.014.01.028.021.037a13.276 13.276 0 0 0 3.995 2.02.05.05 0 0 0 .056-.019c.308-.42.582-.863.818-1.329a.05.05 0 0 0-.01-.059.051.051 0 0 0-.018-.011 8.875 8.875 0 0 1-1.248-.595.05.05 0 0 1-.02-.066.051.051 0 0 1 .015-.019c.084-.063.168-.129.248-.195a.05.05 0 0 1 .051-.007c2.619 1.196 5.454 1.196 8.041 0a.052.052 0 0 1 .053.007c.08.066.164.132.248.195a.051.051 0 0 1-.004.085 8.254 8.254 0 0 1-1.249.594.05.05 0 0 0-.03.07.05.05 0 0 0 .02.018c.24.464.512.907.817 1.329a.05.05 0 0 0 .056.019 13.235 13.235 0 0 0 4.001-2.02.049.049 0 0 0 .021-.037c.334-3.451-.559-6.449-2.366-9.106a.034.034 0 0 0-.02-.019zM5.318 10.366c-.786 0-1.432-.72-1.432-1.602 0-.883.633-1.602 1.432-1.602.798 0 1.444.726 1.432 1.602 0 .882-.634 1.602-1.432 1.602zm4.72 0c-.786 0-1.432-.72-1.432-1.602 0-.883.633-1.602 1.432-1.602.798 0 1.444.726 1.432 1.602 0 .882-.634 1.602-1.432 1.602z"/>
            </svg>
            Dołącz do Discorda
        </a>
    </header>

    <div class="container">
        <!-- ZŁOTY PLAYER VIDEO -->
        <div id="player-box">
            <video id="player" controls autoplay preload="metadata">
                <source src="" type="video/mp4">
            </video>
            <div id="now-playing">Wybierz utwór z listy...</div>
            <div class="cdn-status">
                <div class="cdn-dot"></div>
                <span>Łączenie z CDN: GitHub Releases 1080p</span>
            </div>
        </div>

        <input type="text" id="search-box" placeholder="🔍 Szukaj hitu DiscoAdamusa (np. 67, PHONK, BANAN)...">

        <div id="playlist-box">
            <!-- Utwory ładowane dynamicznie -->
        </div>
    </div>

    <script>
        const tracks = {tracks_json_str};

        const player = document.getElementById('player');
        const nowPlaying = document.getElementById('now-playing');
        const playlistBox = document.getElementById('playlist-box');
        const searchBox = document.getElementById('search-box');

        let filteredTracks = [...tracks];

        function renderPlaylist(list = tracks) {{
            playlistBox.innerHTML = '';
            if (list.length === 0) {{
                playlistBox.innerHTML = '<div style="text-align:center; padding: 20px; color: #8b949e;">Brak wyników wyszukiwania 👁️👄👁️</div>';
                return;
            }}

            list.forEach((track) => {{
                const item = document.createElement('div');
                item.className = 'track-item';
                item.dataset.id = track.id;
                
                if (player.src === track.url) {{
                    item.classList.add('active');
                }}

                item.innerHTML = `
                    <span class="track-title">${{track.id}}. ${{track.title}}</span>
                    <span class="track-size">${{track.size}}</span>
                `;
                item.addEventListener('click', () => playTrackById(track.id));
                playlistBox.appendChild(item);
            }});
        }}

        function playTrackById(id) {{
            const trackIndex = tracks.findIndex(t => t.id === id);
            if (trackIndex === -1) return;

            const track = tracks[trackIndex];
            player.src = track.url;
            nowPlaying.innerText = `${{track.id}}. ${{track.title}}`;
            player.play();

            document.querySelectorAll('.track-item').forEach(el => {{
                el.classList.toggle('active', parseInt(el.dataset.id) === id);
            }});
        }}

        searchBox.addEventListener('input', (e) => {{
            const query = e.target.value.toLowerCase().trim();
            filteredTracks = tracks.filter(track => track.title.toLowerCase().includes(query));
            renderPlaylist(filteredTracks);
        }});

        player.addEventListener('ended', () => {{
            const currentUrl = player.src;
            const currentIndex = tracks.findIndex(t => t.url === currentUrl);
            let nextIndex = currentIndex + 1;
            
            if (nextIndex >= tracks.length) {{
                nextIndex = 0;
            }}
            
            if (tracks[nextIndex]) {{
                playTrackById(tracks[nextIndex].id);
            }}
        }});

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
