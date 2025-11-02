import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from datetime import datetime
import os, requests, httpx
from openai import OpenAI

# --- Page Config ---
st.set_page_config(
    page_title="⚗️ The Alchemist Dashboard",
    page_icon="🧙‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Futuristic Theme ---
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
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 25px rgba(0,255,230,0.3);
}
</style>
""", unsafe_allow_html=True)

# --- Auto Refresh ---
st_autorefresh(interval=10 * 60 * 1000, key="refresh")

st.title("⚗️ The Alchemist Intelligence Dashboard")
st.caption("Gold, silver & light — unified with AI, volume, and flow ✨")

# --- Load Summary Data ---
summary_path = Path("data/summary.json")
df_sorted = pd.DataFrame()
if summary_path.exists():
    with open(summary_path, "r") as f:
        data = json.load(f)
    df_sorted = pd.DataFrame(data.get("details", []))
    df_sorted = df_sorted.sort_values("score", ascending=False).reset_index(drop=True)
    st.markdown(f"🕒 **Last update:** `{data.get('generated_at', datetime.utcnow())}`")

# --- AI Client Setup ---
api_key = os.getenv("OPENAI_API_KEY", "").strip()
client = None
if api_key:
    try:
        client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=True))
        client.models.list()
        st.success("✅ AI connection established successfully.")
    except Exception as e:
        st.warning(f"⚠️ AI connection failed: {e}")
else:
    st.warning("⚠️ Missing API key — AI summaries disabled.")

# --- Helper: Crypto data fetch ---
def get_coin_chart(coin_id, days="1"):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    r = requests.get(url, params=params, timeout=15)
    if r.status_code != 200:
        return None
    data = r.json()
    prices = pd.DataFrame(data.get("prices", []), columns=["ts", "price"])
    volumes = pd.DataFrame(data.get("total_volumes", []), columns=["ts", "volume"])
    prices["dt"] = pd.to_datetime(prices["ts"], unit="ms")
    volumes["dt"] = pd.to_datetime(volumes["ts"], unit="ms")
    return prices, volumes

# --- Intelligence Feed ---
st.markdown("## 💡 The Alchemist Intelligence Feed")
st.caption("Real-time AI, volume analysis, and sentiment insights for all domains ⚡")

domains = ["crypto", "stocks", "sports", "forex", "social", "music"]

for domain in domains:
    with st.expander(f"💠 {domain.capitalize()} Intelligence", expanded=(domain == "crypto")):
        ai_summary = None
        if not df_sorted.empty and client:
            row = df_sorted[df_sorted["name"] == domain]
            if not row.empty:
                prompt = f"Provide a concise market sentiment summary for {domain} based on: {row.iloc[0]['summary']}"
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are The Alchemist AI, a concise financial sentiment analyst."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=60
                    )
                    ai_summary = response.choices[0].message.content.strip()
                except Exception as e:
                    ai_summary = f"⚠️ AI summary unavailable: {e}"

        if ai_summary:
            st.markdown(
                f"<div class='card'><p style='color:#00e6b8;'>🔮 {ai_summary}</p></div>",
                unsafe_allow_html=True
            )

        # --- Domain-specific content ---
        if domain == "crypto":
            try:
                url = "https://api.coingecko.com/api/v3/coins/markets"
                params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10, "page": 1}
                res = requests.get(url, params=params, timeout=20)
                if res.status_code == 200:
                    crypto_df = pd.DataFrame(res.json())
                    cols = ["name", "symbol", "current_price", "price_change_percentage_24h", "total_volume"]
                    crypto_df = crypto_df[cols]
                    st.dataframe(crypto_df.set_index("symbol"))

                    # BTC mini chart
                    chart_data = get_coin_chart("bitcoin", "1")
                    if chart_data:
                        prices, volumes = chart_data
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=prices["dt"], y=prices["price"],
                                                 mode="lines", line=dict(color="#d4af37", width=2),
                                                 name="BTC Price (USD)"))
                        fig.add_trace(go.Bar(x=volumes["dt"], y=volumes["volume"] / 1e9,
                                             name="Volume (B)", marker_color="#00e6b8", opacity=0.5, yaxis="y2"))
                        fig.update_layout(
                            title="Bitcoin (BTC) — 24h Price & Volume",
                            yaxis=dict(title="Price (USD)"),
                            yaxis2=dict(title="Volume (B)", overlaying="y", side="right"),
                            height=300, paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f",
                            font=dict(color="#e0e0e0")
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ Unable to fetch crypto data.")
            except Exception as e:
                st.warning(f"⚠️ Crypto feed unavailable: {e}")

        elif domain == "stocks":
            st.info("📈 Stocks data module coming soon — will integrate live Yahoo Finance feeds.")

        elif domain == "sports":
            st.info("🏟️ Sports intelligence coming — real-time event sentiment in next update.")

        elif domain == "forex":
            st.info("💱 Forex AI module in development (USD, EUR, GBP, JPY tracking).")

        elif domain == "social":
            st.info("🌐 Social media sentiment (Reddit + Twitter) integration coming soon.")

        elif domain == "music":
            st.info("🎵 Music trends module (Spotify/YouTube analytics) launching later this month.")
