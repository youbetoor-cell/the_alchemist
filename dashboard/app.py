# ============================================================
# ⚗️ The Alchemist Intelligence Dashboard — v7
# ============================================================

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from datetime import datetime
import requests, os, yfinance as yf, httpx
from openai import OpenAI

# ============================================================
# --- ALERT HELPERS (Telegram & Slack) ---
# ============================================================

def send_telegram_alert(message):
    token = os.getenv("TELEGRAM_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
            timeout=5,
        )
    except Exception as e:
        print(f"⚠️ Telegram alert failed: {e}")

def send_slack_alert(message):
    webhook = os.getenv("SLACK_WEBHOOK_URL", "")
    if not webhook:
        return
    try:
        requests.post(webhook, json={"text": message}, timeout=5)
    except Exception as e:
        print(f"⚠️ Slack alert failed: {e}")

# ============================================================
# --- PAGE SETUP ---
# ============================================================

st.set_page_config(page_title="⚗️ The Alchemist Dashboard", page_icon="🧙‍♂️", layout="wide")
st_autorefresh(interval=10 * 60 * 1000, key="refresh")

st.title("⚗️ The Alchemist Intelligence Dashboard")
st.caption("Gold, silver & light — unified with AI, volume, sentiment, and insight ✨")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
SUMMARY_PATH = DATA_DIR / "summary.json"
INSIGHT_LOG = DATA_DIR / "insight_log.json"
ALERT_LOG = DATA_DIR / "alert_log.json"

# ============================================================
# --- THEME ---
# ============================================================

st.markdown("""
<style>
body {
    background: radial-gradient(circle at 20% 30%, #050505, #0a0a0f);
    color: #e0e0e0;
    font-family: 'Inter', sans-serif;
}
h1, h2, h3 { color: #d4af37 !important; text-shadow: 0 0 12px rgba(255,215,0,0.3); }
.card {
    background: rgba(18,18,22,0.85);
    border: 1px solid rgba(160,160,160,0.25);
    border-radius: 15px;
    padding: 1rem;
    margin: 0.5rem;
    text-align: center;
    box-shadow: 0 0 25px rgba(255,215,0,0.05);
}
.metric-up { color: #00e676; }
.metric-down { color: #ff4d4d; }
.metric-neutral { color: #cccccc; }
.alert-up { background: rgba(0,230,118,0.15); color: #00e676; padding: 0.4em 0.7em; border-radius: 10px; font-weight: 500; }
.alert-down { background: rgba(255,77,77,0.15); color: #ff4d4d; padding: 0.4em 0.7em; border-radius: 10px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# --- LOAD SUMMARY DATA ---
# ============================================================

df_sorted = pd.DataFrame()
if SUMMARY_PATH.exists():
    with open(SUMMARY_PATH, "r") as f:
        summary_data = json.load(f)
    df = pd.DataFrame(summary_data.get("details", []))
    st.markdown(f"🕒 **Last update:** `{summary_data.get('generated_at', datetime.utcnow())}`")

    if not df.empty:
        df_sorted = df.sort_values("score", ascending=False).reset_index(drop=True)
        top_name = df_sorted.iloc[0]["name"]
        top_score = df_sorted.iloc[0]["score"]
        st.markdown(f"🏆 **Top Performer:** `{top_name.capitalize()}` — **{top_score:.3f}**")

        fig = px.bar(
            df_sorted, y="name", x="score", orientation="h",
            color="score", color_continuous_scale=["#b8860b","#d4af37","#00e6b8"], text_auto=".3f"
        )
        fig.update_layout(plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f", font=dict(color="#e0e0e0"))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Missing data/summary.json — generate or run agents first.")

# ============================================================
# --- AI CONNECTION ---
# ============================================================

api_key = os.getenv("OPENAI_API_KEY", "").strip()
client = None
if api_key:
    try:
        client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=True))
        _ = client.models.list()
        st.success("✅ AI connection established successfully.")
    except Exception as e:
        st.warning(f"⚠️ AI connection failed: {e}")
else:
    st.info("💤 No API key — AI features disabled.")

# ============================================================
# --- DATA HELPERS ---
# ============================================================

@st.cache_data(ttl=300)
def get_btc_data():
    try:
        data = requests.get("https://api.coingecko.com/api/v3/coins/bitcoin/market_chart",
                            params={"vs_currency":"usd","days":"1"}, timeout=10).json()
        prices = pd.DataFrame(data.get("prices", []), columns=["ts","price"])
        prices["dt"] = pd.to_datetime(prices["ts"], unit="ms")
        return prices
    except Exception:
        return None

@st.cache_data(ttl=300)
def get_aapl_data():
    try:
        df = yf.download("AAPL", period="1d", interval="15m", progress=False)
        if df.empty: return None
        return df.rename_axis("dt").reset_index()[["dt","Close"]].rename(columns={"Close":"price"})
    except Exception:
        return None

def mock_series(seed=0):
    np.random.seed(seed)
    vals = np.cumsum(np.random.normal(0, 0.1, 60)) + 100
    times = pd.date_range(end=datetime.utcnow(), periods=60, freq="min")
    return pd.DataFrame({"dt": times, "price": vals})

def detect_anomalies(df, window=20, threshold=2.0):
    """Detect Z-score anomalies."""
    if df is None or df.empty: return pd.DataFrame()
    df["change"] = df["price"].pct_change()
    df["z"] = (df["change"] - df["change"].rolling(window).mean()) / df["change"].rolling(window).std()
    return df[df["z"].abs() > threshold]

def persist_alert(domain, direction, change):
    DATA_DIR.mkdir(exist_ok=True)
    alert = {
        "timestamp": datetime.utcnow().isoformat(),
        "domain": domain, "direction": direction, "change": round(change, 2)
    }
    if ALERT_LOG.exists():
        alerts = json.loads(ALERT_LOG.read_text())
    else:
        alerts = []
    alerts.append(alert)
    ALERT_LOG.write_text(json.dumps(alerts[-200:], indent=2))

# ============================================================
# --- ANOMALY CONTROL SLIDERS ---
# ============================================================

st.markdown("## 🚨 Anomaly Watch")
window = st.slider("Rolling window (bars)", 10, 60, 20)
threshold = st.slider("Z-score threshold (higher=fewer alerts)", 1.5, 4.0, 2.0, 0.1)

# ============================================================
# --- MULTI-DOMAIN AI INSIGHTS ---
# ============================================================

st.markdown("## 🧠 AI Correlation Insights")

if client and not df_sorted.empty:
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are The Alchemist AI. Summarize relationships between domains."},
                {"role":"user","content":f"DATA: {df_sorted.to_dict(orient='records')}"}
            ],
            max_tokens=120, temperature=0.4
        )
        text = resp.choices[0].message.content.strip()
        st.markdown(f"<div class='card'><b>💡 Correlation Summary:</b><br>{text}</div>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"⚠️ AI correlation unavailable: {e}")

# ============================================================
# --- UNIFIED FEED ---
# ============================================================

st.markdown("## 💡 Unified Intelligence Feed")

if not df_sorted.empty:
    for _, row in df_sorted.iterrows():
        domain = row["name"].capitalize()
        summary = row["summary"]
        with st.expander(f"🔹 {domain} Intelligence", expanded=False):
            ai_summary = "💤 (Skipped — no API key)"
            sentiment_color = "#bfbfbf"
            sentiment_tag = "⚪ neutral"

            if client:
                try:
                    resp = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role":"system","content":"You are The Alchemist AI — concise sentiment analyst."},
                            {"role":"user","content":f"Classify tone for {domain}: {summary}"}
                        ], max_tokens=60
                    )
                    ai_summary = resp.choices[0].message.content.strip().lower()
                    if any(x in ai_summary for x in ["bullish","positive","rising"]):
                        sentiment_color, sentiment_tag = "#00e676","🟢 bullish"
                    elif any(x in ai_summary for x in ["bearish","negative","falling"]):
                        sentiment_color, sentiment_tag = "#ff4d4d","🔴 bearish"
                except Exception as e:
                    ai_summary = f"⚠️ AI unavailable: {e}"

            col1, col2 = st.columns([3,2])

            with col1:
                st.markdown(f"<p style='color:{sentiment_color};'>🔮 {sentiment_tag}: {ai_summary}</p>", unsafe_allow_html=True)

with col2:
    try:
        df_trend = (
            get_btc_data() if "crypto" in domain.lower()
            else get_aapl_data() if "stocks" in domain.lower()
            else mock_series(3)
        )
        if df_trend is None:
            df_trend = mock_series(1)

        latest = df_trend["price"].iloc[-1]
        hour_ago = df_trend["price"].iloc[-min(len(df_trend), 12)]
        chg_1h = ((latest - hour_ago) / hour_ago) * 100
        anomalies = detect_anomalies(df_trend, window, threshold)

        # --- Alerts ---
        if chg_1h > 2.5:
            msg = f"🔥 {domain} surged +{chg_1h:.2f}% in the past hour!"
            st.markdown(f"<div class='alert-up'>{msg}</div>", unsafe_allow_html=True)
            persist_alert(domain, "surge", chg_1h)
            send_telegram_alert(msg)
            send_slack_alert(msg)
        elif chg_1h < -2.5:
            msg = f"⚠️ {domain} dropped {chg_1h:.2f}% in the past hour!"
            st.markdown(f"<div class='alert-down'>{msg}</div>", unsafe_allow_html=True)
            persist_alert(domain, "drop", chg_1h)
            send_telegram_alert(msg)
            send_slack_alert(msg)

        # --- Sparkline Chart ---
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_trend["dt"], y=df_trend["price"],
            mode="lines", line=dict(color=sentiment_color, width=2),
            fill="tozeroy", fillcolor="rgba(255,255,255,0.08)"
        ))
        for _, a in anomalies.iterrows():
            fig.add_vline(x=a["dt"], line_color="#ff4d4d", opacity=0.4)
        fig.update_layout(
            height=70, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f"
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    except Exception as e:
        st.warning(f"⚠️ Sparkline error: {e}")


# ============================================================
# --- ALERT FEED ---
# ============================================================

st.markdown("## 🧾 Alert Feed")
if ALERT_LOG.exists():
    alerts = json.loads(ALERT_LOG.read_text())
    if alerts:
        for a in alerts[-20:][::-1]:
            color = "#00e676" if a["direction"]=="surge" else "#ff4d4d"
            emoji = "🟢" if a["direction"]=="surge" else "🔴"
            st.markdown(f"<div class='card' style='text-align:left'>{emoji} <b>{a['domain']}</b> — {a['direction']} ({a['change']}%)<br><small>{a['timestamp']}</small></div>", unsafe_allow_html=True)
    else:
        st.info("No alerts yet.")
else:
    st.info("No alert log found.")

# ============================================================
# --- DAILY AI INSIGHT GENERATOR (INLINE VERSION OF generate_insight.py) ---
# ============================================================

st.markdown("## 🧠 AI Daily Commentary")

if st.button("✨ Generate New Daily Insight"):
    if not client:
        st.warning("⚠️ No OPENAI_API_KEY found.")
    elif not SUMMARY_PATH.exists():
        st.warning("⚠️ summary.json not found.")
    else:
        summary = json.loads(SUMMARY_PATH.read_text())
        details = summary.get("details", [])
        if not details:
            st.warning("⚠️ No details in summary.json.")
        else:
            prompt = (
                "You are The Alchemist AI. Given domain scores and summaries, produce a short daily commentary "
                "(2 bullets max) noting correlations or divergences and a single actionable hint. Keep <60 words.\n\n"
                f"DATA: {details}"
            )
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role":"system","content":"Write concise, insightful market commentary."},
                        {"role":"user","content": prompt}
                    ],
                    max_tokens=120, temperature=0.4
                )
                text = resp.choices[0].message.content.strip()
            except Exception as e:
                text = f"(Insight generation failed: {e})"

            entry = {"timestamp": datetime.utcnow().isoformat(), "text": text}
            if INSIGHT_LOG.exists():
                log = json.loads(INSIGHT_LOG.read_text())
                if not isinstance(log, list): log = []
            else:
                log = []
            log.append(entry)
            log = log[-200:]
            INSIGHT_LOG.write_text(json.dumps(log, indent=2))
            st.success("✅ Insight appended.")
            st.markdown(f"<div class='card' style='text-align:left'><b>{entry['timestamp']}</b><br>{entry['text']}</div>", unsafe_allow_html=True)

# ============================================================
# --- INSIGHT FEED ---
# ============================================================

if INSIGHT_LOG.exists():
    st.markdown("### Recent Insights")
    insights = json.loads(INSIGHT_LOG.read_text())
    for i in insights[-5:][::-1]:
        st.markdown(f"<div class='card' style='text-align:left'><b>{i['timestamp']}</b><br>{i['text']}</div>", unsafe_allow_html=True)
else:
    st.info("No insights logged yet.")
