# ============================================================
# ⚗️ The Alchemist — Terminal Intelligence Dashboard
# ============================================================

import os
import json
import time
import httpx
import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from openai import OpenAI
import requests

# ============================================================
# --- CONFIGURATION ---
# ============================================================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
SUMMARY_PATH = DATA_DIR / "summary.json"
HISTORY_PATH = DATA_DIR / "history.json"
INSIGHT_LOG = DATA_DIR / "insight_log.json"

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK", "")

client = None
if OPENAI_KEY:
    try:
        client = OpenAI(api_key=OPENAI_KEY, http_client=httpx.Client(verify=True))
        _ = client.models.list()
        print("✅ Connected to OpenAI API.")
    except Exception as e:
        print(f"⚠️ Could not connect to OpenAI: {e}")
else:
    print("💤 No OpenAI API key detected — AI summaries disabled.")


# ============================================================
# --- ALERT HELPERS ---
# ============================================================

def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=payload, timeout=5)
        print(f"📨 Telegram alert sent: {message}")
    except Exception as e:
        print(f"⚠️ Telegram alert failed: {e}")

def send_slack_alert(message):
    if not SLACK_WEBHOOK:
        return
    try:
        requests.post(SLACK_WEBHOOK, json={"text": message}, timeout=5)
        print(f"📨 Slack alert sent: {message}")
    except Exception as e:
        print(f"⚠️ Slack alert failed: {e}")


# ============================================================
# --- DATA HELPERS ---
# ============================================================

def mock_series(seed=0):
    np.random.seed(seed)
    vals = np.cumsum(np.random.normal(0, 0.1, 60)) + 100
    times = pd.date_range(end=datetime.utcnow(), periods=60, freq="min")
    return pd.DataFrame({"dt": times, "price": vals})

def get_aapl_data():
    """Download AAPL price data with safe fallback."""
    try:
        df = yf.download("AAPL", period="1d", interval="15m", progress=False)
        if not df.empty:
            return df.rename_axis("dt").reset_index()[["dt", "Close"]].rename(columns={"Close": "price"})
        else:
            raise ValueError("Empty Yahoo data")
    except Exception as e:
        print("⚠️ get_aapl_data fallback:", e)
        return mock_series(seed=42)

def get_btc_data():
    """Fetch Bitcoin market data from CoinGecko with fallback."""
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {"vs_currency": "usd", "days": "1"}
        data = requests.get(url, params=params, timeout=10).json()
        prices = pd.DataFrame(data["prices"], columns=["ts", "price"])
        prices["dt"] = pd.to_datetime(prices["ts"], unit="ms")
        return prices
    except Exception as e:
        print(f"⚠️ get_btc_data fallback: {e}")
        return mock_series(seed=7)


# ============================================================
# --- ANOMALY DETECTOR ---
# ============================================================

def detect_anomalies(df, window=20, threshold=2.0):
    if df is None or df.empty:
        return []
    df["change"] = df["price"].pct_change()
    df["z"] = (df["change"] - df["change"].rolling(window).mean()) / df["change"].rolling(window).std()
    return df[df["z"].abs() > threshold]


# ============================================================
# --- AI DAILY INSIGHT GENERATOR ---
# ============================================================

def generate_insight():
    if not client or not SUMMARY_PATH.exists():
        print("⚠️ Missing summary.json or API key. Skipping insight generation.")
        return

    summary = json.loads(SUMMARY_PATH.read_text())
    details = summary.get("details", [])
    if not details:
        print("⚠️ summary.json empty — skipping insight generation.")
        return

    prompt = (
        "You are The Alchemist AI. Given domain scores and summaries, "
        "produce a short daily commentary (2 bullets max) noting correlations "
        "or divergences and one actionable hint. Keep under 60 words.\n\n"
        f"DATA: {details}"
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Write concise, insightful market commentary."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=120,
            temperature=0.4,
        )
        text = resp.choices[0].message.content.strip()
        print(f"🧠 Insight: {text}")
    except Exception as e:
        text = f"(Insight generation failed: {e})"
        print(text)

    entry = {"timestamp": datetime.utcnow().isoformat(), "text": text}
    log = json.loads(INSIGHT_LOG.read_text()) if INSIGHT_LOG.exists() else []
    if not isinstance(log, list):
        log = []
    log.append(entry)
    log = log[-200:]
    INSIGHT_LOG.write_text(json.dumps(log, indent=2))
    print("✅ Insight appended to log.")


# ============================================================
# --- MAIN DASHBOARD LOOP ---
# ============================================================

def run_dashboard():
    print("\n⚗️ The Alchemist — Terminal Intelligence Dashboard")
    print("------------------------------------------------------")
    print(datetime.utcnow().strftime("🕒 %Y-%m-%d %H:%M UTC"))

    btc = get_btc_data()
    aapl = get_aapl_data()

    anomalies_btc = detect_anomalies(btc)
    anomalies_aapl = detect_anomalies(aapl)

    print(f"BTC latest price: ${btc['price'].iloc[-1]:,.2f}")
    print(f"AAPL latest price: ${aapl['price'].iloc[-1]:,.2f}")
    print(f"Detected anomalies — BTC: {len(anomalies_btc)}, AAPL: {len(anomalies_aapl)}")

    # Alert on surge/drop
    if len(btc) >= 2:
        chg_1h = (btc['price'].iloc[-1] / btc['price'].iloc[-2] - 1) * 100
        if chg_1h > 2.5:
            msg = f"🔥 BTC surged +{chg_1h:.2f}% in the past hour!"
            send_telegram_alert(msg)
            send_slack_alert(msg)
        elif chg_1h < -2.5:
            msg = f"⚠️ BTC dropped {chg_1h:.2f}% in the past hour!"
            send_telegram_alert(msg)
            send_slack_alert(msg)

    # Log update
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "btc_price": btc["price"].iloc[-1],
        "aapl_price": aapl["price"].iloc[-1],
        "btc_anomalies": len(anomalies_btc),
        "aapl_anomalies": len(anomalies_aapl),
    }
    history = json.loads(HISTORY_PATH.read_text()) if HISTORY_PATH.exists() else []
    if not isinstance(history, list):
        history = []
    history.append(entry)
    history = history[-500:]
    HISTORY_PATH.write_text(json.dumps(history, indent=2))

    generate_insight()
    print("------------------------------------------------------\n")


# ============================================================
# --- ENTRY POINT ---
# ============================================================

if __name__ == "__main__":
    run_dashboard()
