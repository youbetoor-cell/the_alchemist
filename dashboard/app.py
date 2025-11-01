import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.express as px
import requests
from datetime import datetime, timedelta

# --- Page Config ---
st.set_page_config(page_title="🧙‍♂️ The Alchemist", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 20% 20%, #0f0f1f, #000000 70%);
    color: #e0e0e0;
    font-family: 'Poppins', sans-serif;
}
.alchemist-header {
    text-align: center;
    padding: 2rem;
    border-radius: 20px;
    background: linear-gradient(90deg, #f0b90b, #d4af37, #a37e2c);
    box-shadow: 0 0 25px rgba(240,185,11,0.4);
    color: black;
    font-weight: 600;
}
.alchemist-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(240,185,11,0.3);
    border-radius: 15px;
    padding: 1rem;
    margin: 0.5rem;
    box-shadow: 0 0 15px rgba(240,185,11,0.1);
    transition: 0.3s ease-in-out;
}
.alchemist-card:hover {
    transform: scale(1.02);
    box-shadow: 0 0 20px rgba(240,185,11,0.4);
}
.footer {
    text-align: center;
    color: #777;
    font-size: 0.8rem;
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class='alchemist-header'>
    <h1>🧙‍♂️ The Alchemist AI Terminal</h1>
    <p>Turning Data into Gold — Automated Intelligence for Financial Markets</p>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2821/2821637.png", width=100)
st.sidebar.markdown("### ⚙️ Control Panel")

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.sidebar.success("Running local agents... please wait ⏳")
    import os
    os.system("python main.py")
    st.sidebar.success("✅ Data updated!")

# --- Load summary ---
summary_path = Path("data/summary.json")
if not summary_path.exists():
    st.warning("No summary file found yet. Run `python main.py` or wait for auto-update.")
    st.stop()

with open(summary_path) as f:
    summary = json.load(f)

ranking = pd.DataFrame(summary.get("details", []))
ranking = ranking.sort_values(by="score", ascending=False)

# --- Sidebar Info ---
st.sidebar.markdown("### 🕒 Last Updated")
st.sidebar.info(summary.get("generated_at", "N/A"))
if not ranking.empty:
    st.sidebar.markdown("### 🧠 Top Performer")
    top = ranking.iloc[0]
    st.sidebar.success(f"{top['name'].capitalize()} — Score: {round(top['score'],3)}")

# --- Performance Overview ---
st.markdown("## 🏆 Domain Performance Rankings")
fig = px.bar(
    ranking,
    x="name",
    y="score",
    color="score",
    text_auto=".2f",
    color_continuous_scale="sunset",
    title="Agent Confidence Scores"
)
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
)
st.plotly_chart(fig, use_container_width=True)

# --- Agent Insights ---
st.markdown("## 🧩 Agent Insights")
cols = st.columns(3)
for i, row in enumerate(ranking.itertuples()):
    with cols[i % 3]:
        st.markdown(f"""
        <div class='alchemist-card'>
            <h3 style='color:#f0b90b'>{row.name.capitalize()}</h3>
            <p><strong>Score:</strong> {round(row.score,3)}</p>
            <p><strong>Insight:</strong> {row.summary}</p>
        </div>
        """, unsafe_allow_html=True)

# --- Live Bitcoin Chart ---
st.markdown("## 💰 Live Bitcoin Price (last 24h)")
try:
    # Fetch data from CoinGecko
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "1"}
    data = requests.get(url, params=params).json()
    prices = data.get("prices", [])
    if prices:
        df_btc = pd.DataFrame(prices, columns=["timestamp", "price"])
        df_btc["time"] = pd.to_datetime(df_btc["timestamp"], unit="ms")
        fig_btc = px.line(df_btc, x="time", y="price", title="Bitcoin Price (24h)", color_discrete_sequence=["gold"])
        fig_btc.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig_btc, use_container_width=True)
    else:
        st.info("No price data received from CoinGecko.")
except Exception as e:
    st.error(f"⚠️ Could not load Bitcoin data: {e}")

# --- Footer ---
st.markdown("""
<div class='footer'>
    <hr>
    <p>© 2025 <b>The Alchemist AI</b> — Turning Data into Gold</p>
</div>
""", unsafe_allow_html=True)
