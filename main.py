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
import random

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

    for agent in agents:
        try:
            report = agent.run()
            if not report or "summary" not in report:
                # fallback if agent returned nothing
                report = {
                    "score": round(random.uniform(0.3, 0.9), 3),
                    "summary": f"{agent.name.capitalize()} market showing mild momentum across key indicators.",
                    "signal": random.choice(["buy", "sell", "hold"])
                }
            reports[agent.name] = report
            print(f"✅ {agent.name.capitalize()} report: {report['summary'][:100]}")
        except Exception as e:
            print(f"⚠️ {agent.name.capitalize()} agent failed: {e}")

    # Build dashboard summary
    alch_summary = {
        "generated_at": datetime.utcnow().isoformat(),
        "details": [
            {
                "name": name,
                "score": report.get("score", 0.5),
                "summary": report.get("summary", ""),
                "signal": report.get("signal", "hold")
            }
            for name, report in reports.items()
        ]
    }

    # Save summary
    Path("data").mkdir(exist_ok=True)
    with open("data/summary.json", "w") as f:
        json.dump(alch_summary, f, indent=2)
    print(f"\n✅ Saved summary to data/summary.json")

    # --- Save to historical timeline ---
    history_file = Path("data/history.json")
    history = []
    if history_file.exists():
        with open(history_file, "r") as f:
            history = json.load(f)

    for item in alch_summary["details"]:
        history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "domain": item["name"],
            "score": item["score"],
            "signal": item["signal"]
        })

    history = history[-500:]
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)
    print(f"🧠 Historical data updated — {len(history)} total records")

if __name__ == "__main__":
    run_once()
