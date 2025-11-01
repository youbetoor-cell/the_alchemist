import requests
import json
from pathlib import Path
from datetime import datetime

class CryptoAgent:
    name = "crypto"

    def run(self):
        print("🔹 Running CryptoAgent (live CoinGecko)…")

        try:
            # Fetch top coins
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 5,
                "page": 1,
                "sparkline": False
            }
            data = requests.get(url, params=params, timeout=10).json()

            top_coin = data[0]
            name = top_coin["name"]
            symbol = top_coin["symbol"].upper()
            price = top_coin["current_price"]
            change = top_coin["price_change_percentage_24h"]

            # Decide "buy/sell/hold" based on 24h price change
            if change > 0.5:
                signal = "buy"
            elif change < -0.5:
                signal = "sell"
            else:
                signal = "hold"

            report = {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "top_coin": name,
                "symbol": symbol,
                "price_usd": price,
                "change_24h": change,
                "signal": signal,
                "summary": f"Top coin: {name} ({symbol}), price ${price}, 24h change {change:.2f}%, signal={signal}",
                "score": round((change + 5) / 10, 3)
            }

        except Exception as e:
            report = {
                "error": str(e),
                "summary": f"❌ Failed to fetch crypto data: {e}",
                "score": 0.5
            }

        # Save report for dashboard
        Path("data/reports").mkdir(parents=True, exist_ok=True)
        with open("data/reports/crypto_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"✅ Saved live crypto report for {name}")
        return report
