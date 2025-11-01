import yfinance as yf
import json
from pathlib import Path
from datetime import datetime

class StocksAgent:
    name = "stocks"

    def run(self):
        print("📈 Running StocksAgent (live Yahoo Finance)…")

        try:
            ticker = "AAPL"  # Apple stock
            data = yf.Ticker(ticker)
            hist = data.history(period="1d")

            price = float(hist["Close"].iloc[-1])
            open_price = float(hist["Open"].iloc[-1])
            change = ((price - open_price) / open_price) * 100

            if change > 0.5:
                signal = "buy"
            elif change < -0.5:
                signal = "sell"
            else:
                signal = "hold"

            report = {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "ticker": ticker,
                "price_usd": price,
                "change_1d": change,
                "signal": signal,
                "summary": f"{ticker} closed at ${price:.2f} ({change:.2f}% today) — signal={signal}",
                "score": round((change + 5) / 10, 3)
            }

        except Exception as e:
            report = {
                "error": str(e),
                "summary": f"❌ Failed to fetch stock data: {e}",
                "score": 0.5
            }

        Path("data/reports").mkdir(parents=True, exist_ok=True)
        with open("data/reports/stocks_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"✅ Saved live stock report for {ticker}")
        return report
