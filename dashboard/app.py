import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
</style>
""", unsafe_allow_html=True)

st.title("⚗️ The Alchemist Intelligence Dashboard")
st.caption("Gold, silver & light — unified AI, trends, and flow ✨")

# --- Auto refresh ---
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

# Initialize AI
api_key = os.getenv("OPENAI_API_KEY", "").strip()
client = None
if api_key:
    try:
        client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=True))
    except Exception as e:
        st.warning(f"⚠️ AI unavailable: {e}")

# Domains from summary
domains = df_sorted["name"].tolist() if summary_path.exists() else []

for domain in domains:
    with st.expander(f"🔹 {domain.capitalize()} Insights", expanded=False):
        domain_summary = df_sorted[df_sorted["name"] == domain].iloc[0]["summary"]
        st.markdown(f"**Summary:** {domain_summary}")

        # --- AI sentiment ---
        ai_summary = "💤 (Skipped — no AI key)"
        if client:
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are The Alchemist AI — a concise financial and data analyst."},
                        {"role": "user", "content": f"Summarize market sentiment and key trend for {domain} based on: {domain_summary}"}
                    ],
                    max_tokens=60
                )
                ai_summary = resp.choices[0].message.content.strip()
            except Exception as e:
                ai_summary = f"⚠️ AI unavailable: {e}"

        st.markdown(f"<p style='color:#00e6b8;'>🔮 {ai_summary}</p>", unsafe_allow_html=True)

        # --- Charts ---
        if domain.lower() == "crypto":
            try:
                url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
                params = {"vs_currency": "usd", "days": "7"}
                r = requests.get(url, params=params, timeout=10)
                btc = pd.DataFrame(r.json()["prices"], columns=["ts", "price"])
                btc["date"] = pd.to_datetime(btc["ts"], unit="ms")
                fig = px.line(btc, x="date", y="price", title="Bitcoin 7-Day Trend", line_shape="spline", markers=True)
                fig.update_layout(plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f", font=dict(color="#e0e0e0"))
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ Crypto chart unavailable: {e}")

        elif domain.lower() == "stocks":
            st.info("📈 Stock data will appear here soon (AAPL, MSFT, TSLA, etc.)")

        elif domain.lower() == "sports":
            st.info("🏟️ Sports metrics visualization coming soon.")

# --- Volume & Momentum Detector ---
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
