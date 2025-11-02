from the_alchemist import TheAlchemist
from agents.sports_agent import SportsAgent
from agents.stocks_agent import StocksAgent
from agents.forex_agent import ForexAgent
from agents.crypto_agent import CryptoAgent
from agents.social_agent import SocialAgent
from agents.music_agent import MusicAgent
import json
from pathlib import Path

def run_once():
    print("🚀 Running The Alchemist agents...\n")

    agents = [
        SportsAgent(),
        StocksAgent(),
        ForexAgent(),
        CryptoAgent(),
        SocialAgent(),
        MusicAgent(),
    ]

    reports = {}
    for a in agents:
        report = a.run()
        reports[a.name] = report
        print(f"✅ Wrote report for {a.name}: {report.get('summary','')[:80]}")

    # Create final summary for dashboard
    alch_summary = {
        "generated_at": "2025-10-31T00:00:00Z",
        "ranking": ["crypto", "stocks", "sports", "music", "social", "forex"],
        "details": [
            {
                "name": name,
                "score": report.get("score", 0.5),
                "summary": report.get("summary", "")
            }
            for name, report in reports.items()
        ]
    }

    # Save summary for dashboard
    Path("data").mkdir(exist_ok=True)
    summary_path = Path("data/summary.json")
    with open(summary_path, "w") as f:
        json.dump(alch_summary, f, indent=2)
    print(f"\n✅ Saved summary to {summary_path.resolve()}")

if __name__ == "__main__":
    run_once()

# --- Save to historical timeline ---
from datetime import datetime
import json, os
from pathlib import Path

history_file = Path("data/history.json")

# Load existing history if available
if history_file.exists():
    with open(history_file, "r") as f:
        history = json.load(f)
else:
    history = []

# Append new records from this run
timestamp = datetime.utcnow().isoformat()
for item in summary["details"]:
    history.append({
        "timestamp": timestamp,
        "domain": item["name"],
        "score": item["score"],
        "sentiment": item.get("sentiment", "neutral")
    })

# Keep only the last 500 records
history = history[-500:]

# Save back to file
with open(history_file, "w") as f:
    json.dump(history, f, indent=2)

print("🧠 Historical data updated —", len(history), "total records")

