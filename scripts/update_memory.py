# scripts/update_memory.py
# ============================================================
# 🧠 The Alchemist — AI Memory Expansion Script
# ============================================================

from pathlib import Path
import json
from datetime import datetime
import json, math, statistics, smtplib, gzip, shutil, os
from email.message import EmailMessage

DATA = Path("data")
DATA.mkdir(exist_ok=True)
INSIGHT_LOG = DATA / "insight_log.json"
SUMMARY = DATA / "summary.json"
MEMORY = DATA / "memory.json"

def load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return []
    return []

def main():
    insights = load_json(INSIGHT_LOG)
    summary = load_json(SUMMARY)
    memory = load_json(MEMORY)

    if not isinstance(memory, list):
        memory = []

    # Grab latest insight entry
    latest_insight = insights[-1] if insights else None
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "btc_price": summary.get("btc_price") if isinstance(summary, dict) else None,
        "aapl_price": summary.get("aapl_price") if isinstance(summary, dict) else None,
        "btc_anomalies": summary.get("btc_anomalies") if isinstance(summary, dict) else None,
        "aapl_anomalies": summary.get("aapl_anomalies") if isinstance(summary, dict) else None,
        "insight": latest_insight.get("text") if latest_insight else None,
    }

    memory.append(entry)
    memory = memory[-500:]  # Keep last 500 entries
    MEMORY.write_text(json.dumps(memory, indent=2))
    print(f"✅ Memory updated — total {len(memory)} records")

if __name__ == "__main__":
    main()
