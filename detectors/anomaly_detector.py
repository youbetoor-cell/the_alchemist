import json, os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from utils.notify import send_slack, send_telegram

def detect_anomalies(window: int = 30, threshold: float = 2.5):
    path = Path("data/history.json")
    if not path.exists():
        print("⚠️ No history.json found")
        return []

    with open(path, "r") as f:
        hist = json.load(f)

    df = pd.DataFrame(hist)
    if df.empty or "score" not in df.columns:
        print("⚠️ Empty or invalid history data")
        return []

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    anomalies = []

    for domain, group in df.groupby("domain"):
        if len(group) < window:
            continue
        group = group.sort_values("timestamp")
        group["z"] = (group["score"] - group["score"].rolling(window).mean()) / group["score"].rolling(window).std()
        latest = group.iloc[-1]
        z = latest["z"]
        if abs(z) > threshold:
            direction = "surge" if z > 0 else "drop"
            anomalies.append({
                "domain": domain,
                "timestamp": latest["timestamp"].isoformat(),
                "score": latest["score"],
                "zscore": round(z, 2),
                "direction": direction
            })

    if anomalies:
        msg_lines = [f"🚨 *Anomalies Detected* — {datetime.utcnow().strftime('%H:%M UTC')}"]
        for a in anomalies:
            arrow = "📈" if a["direction"] == "surge" else "📉"
            msg_lines.append(f"{arrow} {a['domain'].capitalize()} ({a['score']:.2f}, z={a['zscore']})")
        alert = "\n".join(msg_lines)
        print(alert)
        send_slack(alert)
        send_telegram(alert)
    else:
        print("✅ No anomalies detected.")

    return anomalies

if __name__ == "__main__":
    detect_anomalies()

