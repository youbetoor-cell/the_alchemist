import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from datetime import datetime
import os, requests, httpx, numpy as np
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
st.caption("Gold, silver & light — with AI, volume, and flow ✨")

# --- Load summary ---
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

    # --- Domain Cards ---
    st.markdown("### 🧩 Domain Performance Overview")
    cols = st.columns(len(df_sorted))
    for i, row in df_sorted.iterrows():
        highlight = " highlight" if row["name"] == top_name else ""
        with cols[i]:
            st.markdown(
                f"<div class='card{highlight}'><h3>{row['name'].capitalize()}</h3>"
                f"<h2 style='color:#f7e28f;'>Score: {row['score']:.3f}</h2>"
                f"<p style='font-size:0.9em;color:#bfbfbf;'>{row['summary'][:100]}...</p></div>",
                unsafe_allow_html=True
            )

    # --- Domain Bar Chart ---
    st.markdown("### 📊 Domain Scores Overview")
    fig = px.bar(
        df_sorted, y="name", x="score", orientation="h",
        color="score", color_continuous_scale=["#b8860b", "#d4af37", "#00e6b8"],
        text_auto=".3f", title="Performance Across Domains"
    )
    fig.update_layout(
        plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f",
        font=dict(color="#e0e0e0")
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Historical Chart ---
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
        filtered, x="timestamp", y="score",
        title=f"{domain_choice.capitalize()} — Score Trend",
        markers=True, line_shape="spline",
        color_discrete_sequence=["#00e6b8"]
    )
    fig_hist.update_layout(
        plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f",
        font=dict(color="#e0e0e0")
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# --- Dynamic BTC Chart ---
st.markdown("### 💹 Bitcoin Trend (Dynamic Range)")
ranges = {
    "30 Days": "30", "7 Days": "7", "1 Day": "1",
    "4 Hours": "0.1666", "1 Hour": "0.0416",
    "30 Minutes": "0.0208", "15 Minutes": "0.0104",
    "5 Minutes": "0.0034", "1 Minute": "0.0007"
}
choice = st.selectbox("Select range:", list(ranges.keys()), index=1)

try:
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": ranges[choice]}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code == 200:
        df_btc = pd.DataFrame(r.json()["prices"], columns=["ts", "price"])
        df_btc["date"] = pd.to_datetime(df_btc["ts"], unit="ms")
        fig_btc = px.line(df_btc, x="date", y="price",
                          title=f"Bitcoin Price (USD, {choice})",
                          line_shape="spline", markers=True)
        fig_btc.update_layout(
            plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f",
            font=dict(color="#e0e0e0")
        )
        st.plotly_chart(fig_btc, use_container_width=True)
except Exception as e:
    st.warning(f"⚠️ BTC chart unavailable: {e}")

# --- Volume & Momentum Detector ---
st.markdown("### 🚨 Volume & Momentum Detector (Top 100 Coins)")
force_show = ["bitcoin", "ethereum", "solana"]

try:
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }

    response = requests.get(url, params=params, timeout=25)
    if response.status_code != 200:
        raise ValueError(f"CoinGecko API returned {response.status_code}")

    markets = response.json()
    if not isinstance(markets, list) or not markets:
        raise ValueError("Empty or invalid CoinGecko response")

    df = pd.DataFrame(markets)
    valid_cols = [c for c in ["id", "symbol", "name", "total_volume", "current_price", "price_change_percentage_24h"] if c in df.columns]
    df = df[valid_cols]

    if df.empty:
        st.warning("⚠️ No valid data returned from CoinGecko.")
    else:
        st.success(f"💹 Loaded {len(df)} coins successfully from CoinGecko.")

        # Display BTC, ETH, SOL mini-charts
        df_force = df[df["id"].isin(force_show)]
        for _, row in df_force.iterrows():
            mc_url = f"https://api.coingecko.com/api/v3/coins/{row['id']}/market_chart"
            mc_params = {"vs_currency": "usd", "days": "1"}
            mc = requests.get(mc_url, params=mc_params, timeout=25).json()

            prices = pd.DataFrame(mc.get("prices", []), columns=["ts", "price"])
            volumes = pd.DataFrame(mc.get("total_volumes", []), columns=["ts", "volume"])
            prices["dt"] = pd.to_datetime(prices["ts"], unit="ms")
            volumes["dt"] = pd.to_datetime(volumes["ts"], unit="ms")

            if len(prices) > 5 and len(volumes) > 5:
                fig = go.Figure()
                fig.add_trace(go.Bar(x=volumes["dt"], y=volumes["volume"],
                                     name="Volume", marker_color="#00e6b8", yaxis="y1"))
                fig.add_trace(go.Scatter(x=prices["dt"], y=prices["price"],
                                         mode="lines", line=dict(color="#d4af37", width=2),
                                         name="Price (USD)", yaxis="y2"))
                fig.update_layout(
                    title=f"{row['name']} ({row['symbol'].upper()}) — 30m Volume & Price",
                    barmode="overlay", height=180,
                    paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f",
                    font=dict(color="#e0e0e0", size=10),
                    margin=dict(l=0, r=0, t=30, b=0),
                    yaxis=dict(title="Volume"),
                    yaxis2=dict(title="Price", overlaying="y", side="right")
                )
                st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.warning(f"⚠️ Detector unavailable: {e}")

# --- 🧠 AI Domain Insights ---
st.markdown("### 🧠 AI Domain Insights")
api_key = os.getenv("OPENAI_API_KEY", "").strip()
client = None

if st.button("🔍 Test AI Connection"):
    if not api_key:
        st.warning("⚠️ Missing API key. Add it in Streamlit Secrets.")
    else:
        try:
            test_client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=True))
            test_client.models.list()
            st.success("✅ Connection successful — models fetched!")
        except Exception as e:
            st.error(f"⚠️ Connection test failed: {e}")

try:
    if api_key:
        client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=True))
        client.models.list()
        st.success("✅ AI connection established successfully.")
    else:
        st.warning("⚠️ Missing API key — AI summaries disabled.")
except Exception as e:
    st.warning(f"⚠️ Connection failed: {e}")
    client = None

if client and summary_path.exists():
    for _, row in df_sorted.iterrows():
        prompt = f"Provide a concise market sentiment summary for {row['name']} based on: {row['summary']}"
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are The Alchemist AI, a concise market analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60
            )
            ai_summary = response.choices[0].message.content.strip()
        except Exception as e:
            if "insufficient_quota" in str(e):
                ai_summary = "💤 AI paused — quota exceeded."
            else:
                ai_summary = f"⚠️ Error: {e}"

        st.markdown(
            f"""
            <div class='card'>
                <b>{row['name'].capitalize()}</b><br>
                <p style='color:#00e6b8;'>🔮 {ai_summary}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
