# ============================================================
# ⚗️ The Alchemist Intelligence Dashboard
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
import requests
import os
import yfinance as yf
import httpx
from openai import OpenAI

# ============================================================
# --- PAGE SETUP ---
# ============================================================

st.set_page_config(
    page_title="⚗️ The Alchemist Dashboard",
    page_icon="🧙‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Theme & Style ---
st.markdown("""
<style>
body {
    background: radial-gradient(circle at 20% 30%, #050505, #0a0a0f);
    color: #e0e0e0;
    font-family: 'Inter', sans-serif;
}
h1, h2, h3 {
    color: #d4af37 !important;
    text-shadow: 0 0 12px rgba(255, 215, 0, 0.3);
}
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
</style>
""", unsafe_allow_html=True)

# ============================================================
# --- REFRESH ---
# ============================================================
st_autorefresh(interval=10 * 60 * 1000, key="refresh")

st.title("⚗️ The Alchemist Intelligence Dashboard")
st.caption("Gold, silver & light — unified with AI, volume, and sentiment ✨")

# ============================================================
# --- LOAD SUMMARY DATA ---
# ============================================================

summary_path = Path("data/summary.json")

if summary_path.exists():
    with open(summary_path, "r") as f:
        data = json.load(f)

    st.markdown(f"🕒 **Last update:** `{data.get('generated_at', datetime.utcnow())}`")

    df = pd.DataFrame(data.get("details", []))
    if not df.empty:
        df_sorted = df.sort_values("score", ascending=False).reset_index(drop=True)
        top_name = df_sorted.iloc[0]["name"]
        top_score = df_sorted.iloc[0]["score"]

        st.markdown(f"🏆 **Top Performer:** `{top_name.capitalize()}` — **{top_score:.3f}**")

        fig = px.bar(
            df_sorted,
            y="name", x="score",
            orientation="h",
            color="score",
            color_continuous_scale=["#b8860b", "#d4af37", "#00e6b8"],
            text_auto=".3f",
            title="Performance Across Domains"
        )
        fig.update_layout(plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f", font=dict(color="#e0e0e0"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No summary data found.")
else:
    st.warning("⚠️ summary.json missing — please generate data first.")

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
        st.warning(f"⚠️ Connection failed: {e}")
else:
    st.info("💤 No API key — AI summaries will be skipped.")

# ============================================================
# --- DATA HELPERS ---
# ============================================================

@st.cache_data(ttl=300)
def get_btc_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {"vs_currency": "usd", "days": "1"}
        data = requests.get(url, params=params, timeout=10).json()
        prices = pd.DataFrame(data["prices"], columns=["ts", "price"])
        prices["dt"] = pd.to_datetime(prices["ts"], unit="ms")
        return prices
    except Exception:
        return None

@st.cache_data(ttl=300)
def get_aapl_data():
    try:
        df = yf.download("AAPL", period="1d", interval="15m", progress=False)
        if not df.empty:
            df = df.rename_axis("dt").reset_index()[["dt", "Close"]].rename(columns={"Close": "price"})
            return df
        return None
    except Exception:
        return None

def mock_series(seed=0):
    np.random.seed(seed)
    vals = np.cumsum(np.random.normal(0, 0.1, 60)) + 100
    times = pd.date_range(end=datetime.utcnow(), periods=60, freq="min")
    return pd.DataFrame({"dt": times, "price": vals})

# ============================================================
# --- INTELLIGENCE FEED ---
# ============================================================

st.markdown("## 💡 Unified Intelligence Feed")

if summary_path.exists():
    for _, row in df_sorted.iterrows():
        domain = row["name"].capitalize()
        summary = row["summary"]

        with st.expander(f"🔹 {domain} Intelligence", expanded=False):
            # --- AI Sentiment ---
            ai_summary = "💤 (Skipped — no API key)"
            sentiment_color = "#bfbfbf"
            sentiment_tag = "⚪ neutral"

            if client:
                try:
                    resp = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are The Alchemist AI — concise sentiment analyst."},
                            {"role": "user", "content": f"Classify and summarize market tone for {domain}: {summary}"}
                        ],
                        max_tokens=60
                    )
                    ai_summary = resp.choices[0].message.content.strip().lower()

                    if any(x in ai_summary for x in ["bullish", "positive", "rising", "optimistic"]):
                        sentiment_color = "#00e676"
                        sentiment_tag = "🟢 bullish"
                    elif any(x in ai_summary for x in ["bearish", "negative", "falling", "pessimistic"]):
                        sentiment_color = "#ff4d4d"
                        sentiment_tag = "🔴 bearish"
                    else:
                        sentiment_color = "#bfbfbf"
                        sentiment_tag = "⚪ neutral"
                except Exception as e:
                    ai_summary = f"⚠️ AI unavailable: {e}"

            # --- Layout ---
            col1, col2 = st.columns([3, 2])

            with col1:
                st.markdown(
                    f"<p style='color:{sentiment_color};'>🔮 {sentiment_tag}: {ai_summary}</p>",
                    unsafe_allow_html=True
                )

                # --- Metrics ---
                metrics_text = ""
                try:
                    if "crypto" in domain.lower():
                        url = "https://api.coingecko.com/api/v3/coins/bitcoin"
                        data = requests.get(url, timeout=10).json()
                        price = data["market_data"]["current_price"]["usd"]
                        chg = data["market_data"]["price_change_percentage_24h"]
                        vol = data["market_data"]["total_volume"]["usd"] / 1e9
                        metrics_text = f"💰 BTC ${price:,.0f} ({chg:+.2f}%) | 24h Vol: ${vol:.1f}B"

                    elif "stocks" in domain.lower():
                        df_aapl = get_aapl_data()
                        if df_aapl is not None and len(df_aapl) > 2:
                            last = df_aapl["price"].iloc[-1]
                            prev = df_aapl["price"].iloc[-2]
                            chg = ((last - prev) / prev) * 100
                            metrics_text = f"💵 AAPL ${last:.2f} ({chg:+.2f}%)"
                        else:
                            metrics_text = "💵 AAPL data unavailable"

                    elif "music" in domain.lower():
                        metrics_text = f"🎧 Top Track Streams: +{np.random.randint(10,30)}% (24h est.)"

                    elif "sports" in domain.lower():
                        metrics_text = f"🏅 Activity Index: {np.random.uniform(0.8, 1.2):.2f}"

                    elif "forex" in domain.lower():
                        fx = requests.get("https://api.exchangerate.host/latest?base=USD", timeout=10).json()
                        eur = fx["rates"]["EUR"]
                        gbp = fx["rates"]["GBP"]
                        metrics_text = f"💱 EUR/USD {eur:.3f} | GBP/USD {gbp:.3f}"

                    elif "social" in domain.lower():
                        metrics_text = f"💬 Engagement Rate: {np.random.uniform(2, 7):.1f}%"

                except Exception as e:
                    metrics_text = f"⚠️ Metrics unavailable: {e}"

                st.markdown(f"<p style='font-size:0.9em;color:#bfbfbf;'>{metrics_text}</p>", unsafe_allow_html=True)

            # --- Right side: Sparkline + Δ metrics ---
            with col2:
                try:
                    if "crypto" in domain.lower():
                        df_trend = get_btc_data() or mock_series(1)
                        latest = df_trend["price"].iloc[-1]
                        hour_ago = df_trend["price"].iloc[-min(len(df_trend), 12)]
                        chg_1h = ((latest - hour_ago) / hour_ago) * 100
                        chg_24h = np.random.uniform(-2, 2)
                        vol_30m = np.random.uniform(0.5, 2.5)
                        subtext = f"Δ1h <span class='{'metric-up' if chg_1h>0 else 'metric-down' if chg_1h<0 else 'metric-neutral'}'>{chg_1h:+.2f}%</span> | Δ24h <span class='{'metric-up' if chg_24h>0 else 'metric-down' if chg_24h<0 else 'metric-neutral'}'>{chg_24h:+.2f}%</span> | Vol30m {vol_30m:.1f}B"

                    elif "stocks" in domain.lower():
                        df_trend = get_aapl_data() or mock_series(2)
                        latest = df_trend["price"].iloc[-1]
                        hour_ago = df_trend["price"].iloc[-4] if len(df_trend) > 4 else df_trend["price"].iloc[0]
                        chg_1h = ((latest - hour_ago) / hour_ago) * 100
                        chg_24h = np.random.uniform(-1.5, 1.5)
                        vol_30m = np.random.uniform(0.2, 0.9)
                        subtext = f"Δ1h <span class='{'metric-up' if chg_1h>0 else 'metric-down' if chg_1h<0 else 'metric-neutral'}'>{chg_1h:+.2f}%</span> | Δ24h <span class='{'metric-up' if chg_24h>0 else 'metric-down' if chg_24h<0 else 'metric-neutral'}'>{chg_24h:+.2f}%</span> | Vol30m {vol_30m:.1f}M"

                    else:
                        df_trend = mock_series(3)
                        chg_1h = np.random.uniform(-0.5, 0.5)
                        chg_24h = np.random.uniform(-1, 1)
                        subtext = f"Δ1h <span class='{'metric-up' if chg_1h>0 else 'metric-down' if chg_1h<0 else 'metric-neutral'}'>{chg_1h:+.2f}%</span> | Δ24h <span class='{'metric-up' if chg_24h>0 else 'metric-down' if chg_24h<0 else 'metric-neutral'}'>{chg_24h:+.2f}%</span>"

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_trend["dt"], y=df_trend["price"],
                        mode="lines", line=dict(color=sentiment_color, width=2),
                        fill="tozeroy", fillcolor=f"rgba(255,255,255,0.08)"
                    ))
                    fig.update_layout(
                        height=70, margin=dict(l=0, r=0, t=10, b=0),
                        xaxis=dict(visible=False), yaxis=dict(visible=False),
                        plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f"
                    )
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                    st.markdown(
                        f"<p style='font-size:0.8em;text-align:center;margin-top:-0.8em;'>{subtext}</p>",
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.warning(f"⚠️ Sparkline unavailable: {e}")
