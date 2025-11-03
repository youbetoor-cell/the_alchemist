import json, os
from utils.notify import send_slack, send_telegram
from pathlib import Path

def detect_and_alert():
    path = Path("data/summary.json")
    if not path.exists():
        print("⚠️ No summary.json found")
        return

    with open(path, "r") as f:
        data = json.load(f)

    messages = []
    for d in data.get("details", []):
        name = d["name"]
        score = d.get("score", 0.5)
        if score > 0.8:
            msg = f"🔥 *{name.upper()}* showing strong uptrend (score {score:.2f})"
            messages.append(msg)
        elif score < 0.3:
            msg = f"⚠️ *{name.upper()}* showing weakness (score {score:.2f})"
            messages.append(msg)

    if not messages:
        print("No significant alerts found.")
        return

    alert_text = "\n".join(messages)
    print(alert_text)
    send_slack(alert_text)
    send_telegram(alert_text)

if __name__ == "__main__":
    detect_and_alert()

