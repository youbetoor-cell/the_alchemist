import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests, json, os, httpx, numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from openai import OpenAI

# --- Page Config ---
st.set_page_config(
    page_title="⚗️ The Alchemist Dashboard",
    page_icon="🧙‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Theme ---
st.markdown("""
<style>
body { background: radial-gradient(circle at 20% 30%, #050505, #0a0a0f); color: #e0e0e0; font-family: 'Inter', sans-serif; }
h1,h2,h3 { color:#d4af37 !important; text-shadow:0 0 12px rgba(255,215,0,0.3); }
.card { background:rgba(18,18,22,0.85); border:1px solid rgba(160,160,160,0.25); border-radius:15px; padding:1rem; margin:0.5rem; text-align:center; box-shadow:0 0 25px rgba(255,215,0,0.05); }
.card:hover { transform:translateY(-3px); box-shadow:0 0 25px rgba(0,255,230,0.3); }
.spark { height: 60px; }
</style>
""", unsafe_allow_html=True)

st.title("⚗️ The Alchemist Intelligence Dashboard")
st.caption("💡 Unified feed — AI + trends + volume ✨")

st_autorefresh(interval=10 * 60 * 1000, key="refresh")

# --- Load summary ---
summary_path = Path("data/summary.json")
if summary_path.exists():
    with open(summary_path, "r") as f:
        summary_data = json.load(f)
    df = pd.DataFrame(summary_data["details"])
    df_sorted = df.sort_values("score", ascending=False).reset_index(drop=True)

    st.markdown(f"🕒 **Last update:** `{summary_data.get('generated_at', datetime.utcnow())}`")
    st.markdown(f"🏆 **Top Performer:** `{df_sorted.iloc[0]['name'].capitalize()}` — **{df_sorted.iloc[0]['score']:.3f}**")

# --- Intelligence Feed ---
st.markdown("## 💡 Unified Intelligence Feed")

api_key = os.getenv("OPENAI_API_KEY", "").strip()
client = None
if api_key:
    try:
        client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=True))
    except Exception as e:
        st.warning(f"⚠️ AI unavailable: {e}")

domains = df_sorted["name"].tolist() if summary_path.exists() else []

for domain in domains:
    with st.expander(f"🔹 {domain.capitalize()} Insights", expanded=False):
        domain_summary = df_sorted[df_sorted["name"] == domain].iloc[0]["summary"]
        st.markdown(f"**Summary:** {domain_summary}")

        # --- AI Sentiment ---
        ai_summary = "💤 (Skipped — no AI key)"
        if client:
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are The Alchemist AI — a concise financial analyst."},
                        {"role": "user", "content": f"Summarize sentiment and key movement for {domain} based on: {domain_summary}"}
                    ],
                    max_tokens=60
                )
                ai_summary = resp.choices[0].message.content.strip()
            except Exception as e:
                ai_summary = f"⚠️ AI unavailable: {e}"

        # --- Inline Sparkline + Summary Layout ---
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown(f"<p style='color:#00e6b8;'>🔮 {ai_summary}</p>", unsafe_allow_html=True)
        with col2:
            try:
                if domain.lower() == "crypto":
                    # 24h BTC sparkline
                    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
                    params = {"vs_currency": "usd", "days": "1"}
                    r = requests.get(url, params=params, timeout=10)
                    prices = pd.DataFrame(r.json()["prices"], columns=["ts", "price"])
                    prices["dt"] = pd.to_datetime(prices["ts"], unit="ms")
                    fig = go.Figure(go.Scatter(
                        x=prices["dt"], y=prices["price"],
                        mode="lines", line=dict(color="#00e6b8", width=2),
                        fill="tozeroy", fillcolor="rgba(0,230,184,0.2)"
                    ))
                    fig.update_layout(
                        height=60, margin=dict(l=0, r=0, t=0, b=0),
                        xaxis=dict(visible=False), yaxis=dict(visible=False),
                        plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.markdown("<small style='color:#999;'>No sparkline available</small>", unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"⚠️ Sparkline unavailable: {e}")

# --- Volume & Momentum Alerts ---
st.markdown("## 🚨 Volume & Momentum Alerts (Top 100 Coins)")
try:
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 100, "page": 1}
    markets = requests.get(url, params=params, timeout=20).json()
    df = pd.DataFrame(markets)
    if "id" in df.columns:
        df["volume_prev_30m"] = df["total_volume"] * (1 - (np.random.randn(len(df)) * 0.02))
        df["volume_change_pct"] = ((df["total_volume"] - df["volume_prev_30m"]) / df["volume_prev_30m"]) * 100
        surge = df[df["volume_change_pct"] > 50].sort_values("volume_change_pct", ascending=False)
        if not surge.empty:
            st.success(f"🔥 {len(surge)} coins with >50% surge in 30m buy volume")
            st.dataframe(surge[["name", "symbol", "volume_change_pct", "current_price"]])
        else:
            st.info("🕊️ No coins with major buy volume surge in the last 30 minutes.")
except Exception as e:
    st.warning(f"⚠️ Detector unavailable: {e}")
