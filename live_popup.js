(function() {
    const style = document.createElement('style');
    style.innerHTML = `
        .live-popup-container {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background-color: #181818;
            border: 1px solid #222222;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.7);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 320px;
            width: 100%;
            animation: slideUp 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }

        @keyframes slideUp {
            from { transform: translateY(100px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .live-popup-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .live-popup-tag {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 0, 0, 0.15);
            color: #ff0000;
            border: 1px solid #ff0000;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.7rem;
            font-weight: 700;
        }

        .live-popup-dot {
            width: 6px;
            height: 6px;
            background-color: #ff0000;
            border-radius: 50%;
            box-shadow: 0 0 6px #ff0000;
            animation: pulse 1.5s infinite;
        }

        .live-popup-close {
            background: none;
            border: none;
            color: #aaa;
            cursor: pointer;
            font-size: 1.1rem;
            line-height: 1;
        }

        .live-popup-close:hover { color: #fff; }

        .live-popup-title {
            font-size: 0.9rem;
            font-weight: 700;
            color: #f1f1f1;
            line-height: 1.3;
        }

        .live-popup-btn {
            display: block;
            text-align: center;
            background-color: #ff0000;
            color: #ffffff;
            text-decoration: none;
            padding: 8px 12px;
            border-radius: 18px;
            font-size: 0.85rem;
            font-weight: 500;
            transition: opacity 0.2s;
        }

        .live-popup-btn:hover { opacity: 0.9; }
    `;
    document.head.appendChild(style);

    async function checkLiveStatus() {
        try {
            const res = await fetch('live.json?t=' + Date.now());
            if (!res.ok) return;
            const data = await res.json();

            if (data.isLive) {
                showPopup(data);
            }
        } catch (e) {
            console.warn("Nie udało się sprawdzić stanu transmisji dla popupu:", e);
        }
    }

    function showPopup(data) {
        if (document.getElementById('live-popup')) return;

        const popup = document.createElement('div');
        popup.id = 'live-popup';
        popup.className = 'live-popup-container';

        const platformName = data.platform === 'tiktok' ? 'TikTok' : 'YouTube';

        popup.innerHTML = `
            <div class="live-popup-header">
                <div class="live-popup-tag">
                    <div class="live-popup-dot"></div>
                    <span>LIVE na ${platformName}</span>
                </div>
                <button class="live-popup-close" id="close-live-popup">✕</button>
            </div>
            <div class="live-popup-title">${data.title || 'Trwa transmisja na żywo!'}</div>
            <a href="live.html" class="live-popup-btn">Oglądaj transmisję</a>
        `;

        document.body.appendChild(popup);

        document.getElementById('close-live-popup').addEventListener('click', () => {
            popup.remove();
        });
    }

    checkLiveStatus();
})();
