from the_alchemist import TheAlchemist
from agents.sports_agent import SportsAgent
from agents.stocks_agent import StocksAgent
from agents.forex_agent import ForexAgent
from agents.crypto_agent import CryptoAgent
from agents.social_agent import SocialAgent
from agents.music_agent import MusicAgent
import json
from pathlib import Path
from datetime import datetime

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
        try:
            report = a.run()
            reports[a.name] = report
            print(f"✅ Wrote report for {a.name}: {report.get('summary','')[:80]}")
        except Exception as e:
            print(f"⚠️ Error in {a.name}: {e}")
            reports[a.name] = {"score": 0.0, "summary": f"Error: {e}"}

    # --- Create summary for dashboard ---
    summary = {
        "generated_at": datetime.utcnow().isoformat(),
        "details": [
            {
                "name": name,
                "score": report.get("score", 0.5),
                "summary": report.get("summary", "")
            }
            for name, report in reports.items()
        ]
    }

    # Sort by score descending
    summary["details"].sort(key=lambda x: x["score"], reverse=True)

    # Save summary
    Path("data").mkdir(exist_ok=True)
    summary_path = Path("data/summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n✅ Saved summary to {summary_path.resolve()}")
    return summary


if __name__ == "__main__":
    summary = run_once()

    # --- Historical tracking ---
    history_file = Path("data/history.json")

    # Load existing history
    if history_file.exists():
        with open(history_file, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    else:
        history = []

    # Append this run
    timestamp = datetime.utcnow().isoformat()
    for item in summary["details"]:
        history.append({
            "timestamp": timestamp,
            "domain": item["name"],
            "score": item["score"],
            "sentiment": item.get("sentiment", "neutral")
        })

    # Keep last 500 records
    history = history[-500:]

    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

    print(f"🧠 Historical data updated — {len(history)} total records")
    print("✅ The Alchemist data pipeline completed successfully.")
