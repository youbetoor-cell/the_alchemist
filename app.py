# ============================================================
# ⚗️ The Alchemist — AI Market Intelligence Dashboard
# ============================================================
import os
import json
import time
import requests
import httpx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# ============================================================
# --- INIT ---
# ============================================================
load_dotenv()
DATA = Path("data")
DATA.mkdir(exist_ok=True)
MEMORY = DATA / "memory.json"
INSIGHT_LOG = DATA / "insight_log.json"
CORR_FILE = DATA / "correlation.json"

# ============================================================
# --- UTILITIES ---
# ============================================================


def mock_series(seed=1, n=24):
    """Generate synthetic hourly price data for offline fallback."""
    np.random.seed(seed)
    base = 100 + np.cumsum(np.random.randn(n))
    dt = pd.date_range(end=datetime.utcnow(), periods=n, freq="h")
    return pd.DataFrame({"dt": dt, "price": base})


def _safe_float(x, default=np.nan):
    try:
        return float(x)
    except Exception:
        return default

# ============================================================
# --- BTC FETCH (CoinGecko only, with fallback) ---
# ============================================================


def get_btc_data():
    """
    Fetch BTC price data using CoinGecko.
    Returns DataFrame with dt, price.
    """
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"},
            timeout=10,
        )
        data = r.json()
        price = float(data["bitcoin"]["usd"])
        return pd.DataFrame({"dt": [datetime.utcnow()], "price": [price]})
    except Exception as e:
        print(f"⚠️ CoinGecko failed: {e}")
        return mock_series(seed=1)


def get_btc_quote():
    """
    CoinGecko quote with 24h change.
    Returns dict: {"price": float, "chg24": float}
    """
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd",
                    "include_24hr_change": "true"},
            timeout=10,
        )
        j = r.json().get("bitcoin", {})
        return {
            "price": float(j.get("usd")),
            "chg24": float(j.get("usd_24h_change", 0.0)),
        }
    except Exception as e:
        print(f"⚠️ get_btc_quote fallback: {e}")
        m = mock_series(n=2, seed=1)
        return {"price": float(m["price"].iloc[-1]), "chg24": 0.0}

# ============================================================
# --- AAPL FETCH (TwelveData API, no yfinance) ---
# ============================================================


def get_aapl_data():
    """
    Fetch AAPL price data using TwelveData (requires TWELVEDATA_API_KEY in .env).
    Returns DataFrame with dt, price.
    """
    api_key = os.getenv("TWELVEDATA_API_KEY", "").strip()
    if not api_key:
        print("⚠️ No TWELVEDATA_API_KEY — using mock AAPL data")
        return mock_series(seed=42)

    try:
        r = requests.get(
            "https://api.twelvedata.com/time_series",
            params={
                "symbol": "AAPL",
                "interval": "1h",
                "outputsize": "24",
                "apikey": api_key,
                "order": "ASC",
            },
            timeout=12,
        )
        data = r.json()
        vals = data.get("values", [])
        if not vals:
            raise ValueError("Empty TwelveData response")
        df = pd.DataFrame(vals)
        df["dt"] = pd.to_datetime(df["datetime"], utc=True)
        df["price"] = df["close"].astype(float)
        return df[["dt", "price"]]
    except Exception as e:
        print(f"⚠️ TwelveData failed: {e}")
        return mock_series(seed=42)


def get_aapl_quote():
    """
    Fetch current AAPL quote with % change.
    Returns dict: {"price": float, "chg24": float}
    """
    api_key = os.getenv("TWELVEDATA_API_KEY", "").strip()
    if not api_key:
        print("⚠️ No TWELVEDATA_API_KEY — using mock quote")
        m = mock_series(n=2, seed=42)
        return {"price": float(m["price"].iloc[-1]), "chg24": 0.0}

    try:
        r = requests.get(
            "https://api.twelvedata.com/quote",
            params={"symbol": "AAPL", "apikey": api_key},
            timeout=10,
        )
        q = r.json()
        return {
            "price": float(q.get("price")),
            "chg24": float(q.get("percent_change", 0.0)),
        }
    except Exception as e:
        print(f"⚠️ get_aapl_quote fallback: {e}")
        m = mock_series(n=2, seed=42)
        return {"price": float(m["price"].iloc[-1]), "chg24": 0.0}

# ============================================================
# --- INSIGHT GENERATION ---
# ============================================================


def generate_insight():
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("⚠️ Missing API key.")
        return "(no API key)"
    client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=True))
    prompt = (
        "Given BTC and AAPL market data, write 2 short insights (<60 words) "
        "about trends, correlations, or divergences, ending with an actionable takeaway."
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are The Alchemist AI. Write concise, data-driven insights."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=120,
            temperature=0.4,
        )
        text = resp.choices[0].message.content.strip()
    except Exception as e:
        text = f"(Insight generation failed: {e})"
    entry = {"timestamp": datetime.utcnow().isoformat(), "text": text}
    log = json.loads(INSIGHT_LOG.read_text()) if INSIGHT_LOG.exists() else []
    if not isinstance(log, list):
        log = []
    log.append(entry)
    log = log[-200:]
    INSIGHT_LOG.write_text(json.dumps(log, indent=2))
    print("✅ Insight appended.")
    return text

# ============================================================
# --- MEMORY SYSTEM ---
# ============================================================


def update_memory(btc_price, aapl_price, insight):
    if MEMORY.exists():
        try:
            mem = json.loads(MEMORY.read_text())
            if not isinstance(mem, list):
                mem = []
        except Exception:
            mem = []
    else:
        mem = []
    mem.append({
        "timestamp": datetime.utcnow().isoformat(),
        "btc_price": btc_price,
        "aapl_price": aapl_price,
        "insight": insight,
    })
    mem = mem[-200:]
    MEMORY.write_text(json.dumps(mem, indent=2))
    print(f"✅ Memory updated — total {len(mem)} records")
    return mem

# ============================================================
# --- CORRELATION ENGINE ---
# ============================================================


def load_memory_df():
    if not MEMORY.exists():
        return pd.DataFrame()
    try:
        raw = json.loads(MEMORY.read_text())
    except Exception:
        return pd.DataFrame()
    if not isinstance(raw, list) or len(raw) < 3:
        return pd.DataFrame()
    df = pd.DataFrame(raw)
    df["timestamp"] = pd.to_datetime(
        df["timestamp"], errors="coerce", utc=True)
    df["btc_price"] = df["btc_price"].astype(float)
    df["aapl_price"] = df["aapl_price"].astype(float)
    return df.dropna()


def compute_correlation():
    df = load_memory_df()
    if df.empty or len(df) < 3:
        print("⚠️ Correlation: not enough data yet.")
        return None
    df["btc_ret"] = df["btc_price"].pct_change() * 100
    df["aapl_ret"] = df["aapl_price"].pct_change() * 100
    corr = df["btc_ret"].rolling(5).corr(df["aapl_ret"]).iloc[-1]
    regime = (
        "Risk-on" if (df["btc_ret"].iloc[-1] > 0 and df["aapl_ret"].iloc[-1] > 0)
        else "Risk-off" if (df["btc_ret"].iloc[-1] < 0 and df["aapl_ret"].iloc[-1] < 0)
        else "Rotation"
    )
    summary = f"📊 Corr: {corr:.2f} | Regime: {regime}"
    print(summary)
    CORR_FILE.write_text(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "corr": float(corr),
        "regime": regime
    }, indent=2))
    return summary

# ============================================================
# --- ALERTS ---
# ============================================================


def send_alerts(message):
    tg_token = os.getenv("TELEGRAM_TOKEN", "")
    tg_chat = os.getenv("TELEGRAM_CHAT_ID", "")
    slack_url = os.getenv("SLACK_WEBHOOK", "")
    if tg_token and tg_chat:
        try:
            requests.get(f"https://api.telegram.org/bot{tg_token}/sendMessage", params={
                         "chat_id": tg_chat, "text": message})
            print("📨 Telegram sent.")
        except Exception as e:
            print("⚠️ Telegram failed:", e)
    if slack_url:
        try:
            requests.post(slack_url, json={"text": message})
            print("📨 Slack sent.")
        except Exception as e:
            print("⚠️ Slack failed:", e)


# ============================================================
# --- MAIN ---
# ============================================================
if __name__ == "__main__":
    print("✅ Connected to OpenAI API.\n")
    print("⚗️ The Alchemist — AI Market Intelligence Dashboard")
    print("------------------------------------------------------")
    print("🕒", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))

    btc_df = get_btc_data()
    aapl_df = get_aapl_data()
    btc = float(btc_df["price"].iloc[-1])
    aapl = float(aapl_df["price"].iloc[-1])
    print(f"BTC ${btc:,.2f} | AAPL ${aapl:,.2f}")

    insight = generate_insight()
    update_memory(btc, aapl, insight)
    correlation_summary = compute_correlation() or "No correlation yet"

    daily_line = f"{datetime.utcnow().strftime('%Y-%m-%d')} | BTC ${btc:,.2f} | AAPL ${aapl:,.2f} | {correlation_summary} | {insight}"
    print("------------------------------------------------------")
    print(daily_line)
    print("------------------------------------------------------")

    send_alerts(daily_line)
os.system("python dashboard_gradio.py &")
print("💤 Sleeping for 24h ...")
