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
