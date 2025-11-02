import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
from pathlib import Path
import json
from datetime import datetime
import os
import requests

# --- Page Config ---
st.set_page_config(
    page_title="⚗️ The Alchemist Dashboard",
    page_icon="🧙‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Futuristic Gold–Cyan–Silver Theme ---
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
.stButton>button {
    background: linear-gradient(90deg, #b8860b, #00e6b8);
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 0.6em 1.4em;
    font-weight: bold;
    box-shadow: 0 0 10px rgba(255,215,0,0.4);
}
.stButton>button:hover {
    background: linear-gradient(90deg, #ffd700, #00ffff);
    box-shadow: 0 0 18px rgba(0,255,255,0.6);
}
.card {
    background: rgba(18,18,22,0.85);
    border: 1px solid rgba(160,160,160,0.25);
    border-radius: 15px;
    padding: 1.2rem;
    margin: 0.5rem;
    text-align: center;
    box-shadow: 0 0 25px rgba(255,215,0,0.05);
    transition: all 0.3s ease;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 25px rgba(0,255,230,0.3);
}
.highlight {
    border: 1px solid #ffd700;
    box-shadow: 0 0 30px rgba(255,215,0,0.5);
}
@media (max-width: 900px) {
    .stColumn { width: 100% !important; display: block; }
}
</style>
""", unsafe_allow_html=True)

# --- Auto-refresh every 10 minutes ---
st_autorefresh(interval=10 * 60 * 1000, key="refresh")

st.title("⚗️ The Alchemist Intelligence Dashboard")
st.caption("Gold, silver & light — now with sentiment and flow ✨")

summary_path = Path("data/summary.json")

if summary_path.exists():
    with open(summary_path, "r") as f:
        data = json.load(f)

    st.markdown(f"🕒 **Last update:** `{data.get('generated_at', datetime.utcnow())}`")

    df = pd.DataFrame(data.get("details", []))
    df_sorted = df.sort_values("score", ascending=False).reset_index(drop=True)

    top_name = df_sorted.iloc[0]["name"]
    top_score = df_sorted.iloc[0]["score"]

    st.markdown(f"🏆 **Top Performer:** `{top_name.capitalize()}` — **{top_score:.3f}**")

    # --- Horizontal domain cards ---
    st.markdown("### 🧩 Domain Performance Overview")
    cols = st.columns(len(df_sorted))
    for i, row in df_sorted.iterrows():
        style = "card"
        if row["name"] == top_name:
            style += " highlight"

        with cols[i]:
            st.markdown(f"<div class='{style}'><h3>{row['name'].capitalize()}</h3>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color:#f7e28f;'>Score: {row['score']:.3f}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.9em;color:#bfbfbf;'>{row['summary'][:100]}...</p></div>", unsafe_allow_html=True)

    # --- Bar chart (horizontal layout) ---
    st.markdown("### 📊 Domain Scores Overview")
    fig = px.bar(
        df_sorted,
        y="name", x="score",
        orientation="h",
        color="score",
        color_continuous_scale=["#b8860b", "#d4af37", "#00e6b8"],
        text_auto=".3f",
        title="Performance Across Domains"
    )
    fig.update_traces(textposition="outside", marker_line_color="#202020", marker_line_width=1.2)
    fig.update_layout(
        plot_bgcolor="#0a0a0f",
        paper_bgcolor="#0a0a0f",
        font=dict(color="#e0e0e0"),
        title_font=dict(color="#f7e28f", size=22),
        yaxis=dict(title="", tickfont=dict(size=13)),
        xaxis=dict(gridcolor="#1e1e1e"),
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Historical Performance Chart ---
hist_path = Path("data/history.json")
if hist_path.exists():
    with open(hist_path, "r") as f:
        hist = json.load(f)
    hist_df = pd.DataFrame(hist)
    hist_df["timestamp"] = pd.to_datetime(hist_df["timestamp"])

    st.markdown("### ⏳ Performance Over Time")
    domain_choice = st.selectbox("Select domain:", hist_df["domain"].unique())

    filtered = hist_df[hist_df["domain"] == domain_choice].sort_values("timestamp")
    fig_hist = px.line(
        filtered,
        x="timestamp",
        y="score",
        title=f"{domain_choice.capitalize()} — Score Trend",
        markers=True,
        line_shape="spline",
        color_discrete_sequence=["#00e6b8"]
    )
    fig_hist.update_layout(
        plot_bgcolor="#0a0a0f",
        paper_bgcolor="#0a0a0f",
        font=dict(color="#e0e0e0"),
        title_font=dict(color="#d4af37", size=20),
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # --- 7-Day Bitcoin Chart (safe version) ---
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {"vs_currency": "usd", "days": "7"}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            btc_data = r.json()
            btc_prices = btc_data["prices"]
            btc_df = pd.DataFrame(btc_prices, columns=["timestamp", "price"])
            btc_df["date"] = pd.to_datetime(btc_df["timestamp"], unit="ms")

            st.markdown("### 💹 Bitcoin 7-Day Trend")
            fig_btc = px.line(
                btc_df, x="date", y="price",
                title="Bitcoin Price (USD, 7 Days)",
                markers=True, line_shape="spline"
            )
            fig_btc.update_layout(
                plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f",
                font=dict(color="#e0e0e0"),
                title_font=dict(color="#00e6b8", size=20),
            )
            st.plotly_chart(fig_btc, use_container_width=True)
        else:
            st.warning("⚠️ Unable to fetch crypto data.")
    except Exception as e:
        st.warning(f"⚠️ Crypto chart unavailable: {e}")

# --- AI Sentiment Summaries ---
from openai import OpenAI
import httpx

st.markdown("### 🧠 AI Domain Insights")

api_key = os.getenv("OPENAI_API_KEY", "").strip()
client = None

try:
    if api_key:
        # Proxy-safe client for Streamlit Cloud
        client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=True))
        _ = client.models.list()  # test connection
        st.success("✅ AI connection established successfully.")
    else:
        st.warning("⚠️ AI summaries disabled — missing API key.")
except Exception as e:
    st.warning(f"⚠️ Connection failed: {e}")
    client = None

if client:
    for _, row in df_sorted.iterrows():
        prompt = f"Provide a concise market sentiment summary for {row['name']} based on: {row['summary']}"
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
            # Graceful fallback for API quota issues
            if "insufficient_quota" in str(e):
                ai_summary = "💤 AI paused — quota exceeded."
            elif "authentication_error" in str(e).lower():
                ai_summary = "⚠️ Invalid or expired API key."
            else:
                ai_summary = "⚠️ AI summary temporarily unavailable."

        st.markdown(
            f"<div class='card'><b>{row['name'].capitalize()}</b><br>"
            f"<span style='color:#00e6b8;'>{ai_summary}</span></div>",
            unsafe_allow_html=True
        )
