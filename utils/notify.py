import os, requests

def send_slack(text: str) -> bool:
    url = os.getenv("SLACK_WEBHOOK_URL", "").strip()
    if not url:
        return False
    try:
        r = requests.post(url, json={"text": text}, timeout=10)
        return r.status_code in (200, 204)
    except Exception:
        return False

def send_telegram(text: str) -> bool:
    bot = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not bot or not chat:
        return False
    try:
        api = f"https://api.telegram.org/bot{bot}/sendMessage"
        r = requests.post(api, data={"chat_id": chat, "text": text, "parse_mode": "Markdown"}, timeout=10)
        return r.status_code == 200
    except Exception:
        return False

