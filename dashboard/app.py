import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests, json, os, httpx, numpy as np, yfinance as yf
from pathlib import Path
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from openai import OpenAI

# --- Config ---
st.set_page_config(page_title="⚗️ The Alchemist", page_icon="🧙‍♂️", layout="wide")
st.title("⚗️ The Alchemist Intelligence Dashboard")
st.caption("💡 AI + Inline Micro Trends + Volume Detection ✨")
st_autorefresh(interval=10 * 60 * 1000, key="refresh")

# --- Load Summary ---
summary_path = Path("data/summary.json")
if summary_path.exists():
    with open(summary_path, "r") as f:
        summary_data = json.load(f)
    df = pd.DataFrame(summary_data["details"])
    df_sorted = df.sort_values("score", ascending=False).reset_index(drop=True)

# --- Initialize OpenAI ---
api_key = os.getenv("OPENAI_API_KEY", "").strip()
client = None
if api_key:
    try:
        client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=True))
    except Exception as e:
        st.warning(f"⚠️ AI unavailable: {e}")

# --- Intelligence Feed ---
st.markdown("## 💡 Unified Intelligence Feed")

for _, row in df_sorted.iterrows():
    domain = row["name"]
    summary = row["summary"]

    with st.expander(f"🔹 {domain.capitalize()} Intelligence", expanded=False):
        # --- AI Sentiment ---
        ai_summary = "💤 (Skipped — no API key)"
        if client:
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are The Alchemist AI — a concise market analyst."},
                        {"role": "user", "content": f"Summarize sentiment and movement for {domain} from: {summary}"}
                    ],
                    max_tokens=60
                )
                ai_summary = resp.choices[0].message.content.strip()
            except Exception as e:
                ai_summary = f"⚠️ AI unavailable: {e}"

        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown(f"<p style='color:#00e6b8;'>🔮 {ai_summary}</p>", unsafe_allow_html=True)

        # --- Adaptive Inline Sparkline ---
        with col2:
            fig = go.Figure()
            try:
                if domain.lower() == "crypto":
                    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
                    params = {"vs_currency": "usd", "days": "1"}
                    data = requests.get(url, params=params, timeout=10).json()
                    prices = pd.DataFrame(data["prices"], columns=["ts", "price"])
                    prices["dt"] = pd.to_datetime(prices["ts"], unit="ms")
                    fig.add_trace(go.Scatter(x=prices["dt"], y=prices["price"],
                                             mode="lines", line=dict(color="#00e6b8", width=2),
                                             fill="tozeroy", fillcolor="rgba(0,230,184,0.2)"))
                elif domain.lower() == "stocks":
                    df_aapl = yf.download("AAPL", period="1d", interval="15m", progress=False)
                    fig.add_trace(go.Scatter(x=df_aapl.index, y=df_aapl["Close"],
                                             mode="lines", line=dict(color="#d4af37", width=2),
                                             fill="tozeroy", fillcolor="rgba(212,175,55,0.2)"))
                elif domain.lower() == "music":
                    # Mock: simulated Spotify trend
                    trend = np.abs(np.sin(np.linspace(0, 2*np.pi, 24)) + np.random.normal(0, 0.1, 24))
                    times = pd.date_range(end=datetime.utcnow(), periods=24, freq="H")
                    fig.add_trace(go.Scatter(x=times, y=trend,
                                             mode="lines", line=dict(color="#1db954", width=2),
                                             fill="tozeroy", fillcolor="rgba(29,185,84,0.2)"))
                elif domain.lower() == "sports":
                    trend = np.random.normal(0.5, 0.05, 24)
                    times = pd.date_range(end=datetime.utcnow(), periods=24, freq="H")
                    fig.add_trace(go.Scatter(x=times, y=trend,
                                             mode="lines", line=dict(color="#ff4500", width=2),
                                             fill="tozeroy", fillcolor="rgba(255,69,0,0.2)"))
                else:
                    trend = np.random.normal(1, 0.03, 24)
                    times = pd.date_range(end=datetime.utcnow(), periods=24, freq="H")
                    fig.add_trace(go.Scatter(x=times, y=trend,
                                             mode="lines", line=dict(color="#888", width=2),
                                             fill="tozeroy", fillcolor="rgba(136,136,136,0.2)"))
                fig.update_layout(
                    height=70, margin=dict(l=0, r=0, t=10, b=0),
                    xaxis=dict(visible=False), yaxis=dict(visible=False),
                    plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ Sparkline unavailable: {e}")
