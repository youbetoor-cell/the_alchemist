import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
from pathlib import Path
import json
from datetime import datetime
import math

# --- Page Config ---
st.set_page_config(
    page_title="🧙‍♂️ The Alchemist Dashboard",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Dark + Neon Silver Theme ---
st.markdown("""
<style>
body {
    background: radial-gradient(circle at 20% 30%, #0a0a0f, #000);
    color: #e0e0e0;
    font-family: 'Inter', sans-serif;
}
h1, h2, h3 {
    color: #b0f7ff !important;
    text-shadow: 0 0 15px rgba(0, 255, 200, 0.6);
}
.stButton>button {
    background: linear-gradient(90deg, #00e6b8, #0099cc);
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 0.6em 1.4em;
    font-weight: bold;
    box-shadow: 0 0 10px rgba(0,255,200,0.4);
}
.stButton>button:hover {
    background: linear-gradient(90deg, #00b3ff, #00e6b8);
    box-shadow: 0 0 20px rgba(0,255,200,0.6);
}
.card {
    background: rgba(18,18,22,0.9);
    border: 1px solid rgba(180,180,180,0.3);
    border-radius: 15px;
    padding: 1.3rem;
    margin-bottom: 1rem;
    box-shadow: 0 0 20px rgba(0,255,200,0.1);
    transition: all 0.3s ease;
    text-align: center;
}
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 0 35px rgba(0,255,200,0.3);
}
.highlight {
    border: 1px solid #ffd700;
    box-shadow: 0 0 35px rgba(255, 215, 0, 0.6);
}
svg {
    transform: rotate(-90deg);
}
circle.bg {
    stroke: rgba(255, 255, 255, 0.08);
    stroke-width: 8;
}
circle.fg {
    stroke: url(#neonGradient);
    stroke-width: 8;
    stroke-linecap: round;
    filter: drop-shadow(0 0 6px #00fff0);
    transition: stroke-dashoffset 1s ease-in-out;
}
</style>
""", unsafe_allow_html=True)

# --- Add Neon Gradient Definition ---
st.markdown("""
<svg width="0" height="0">
  <defs>
    <linearGradient id="neonGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00e6b8"/>
      <stop offset="100%" stop-color="#b0f7ff"/>
    </linearGradient>
  </defs>
</svg>
""", unsafe_allow_html=True)

# --- Auto-refresh every 10 min ---
st_autorefresh(interval=10 * 60 * 1000, key="refresh")

# --- Header ---
st.title("⚗️ The Alchemist Intelligence Dashboard")
st.markdown("### Where silver logic meets golden intuition ⚡")

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

    st.markdown(f"🏆 **Top Performer:** `{top_name.capitalize()}` — score **{top_score:.3f}**")

    # --- Neon Circular Gauges ---
    st.markdown("### ✨ Domain Performance Rings")
    cols = st.columns(3)

    for i, row in df_sorted.iterrows():
        style = "card"
        if row["name"] == top_name:
            style += " highlight"

        with cols[i % 3]:
            st.markdown(f"<div class='{style}'><h3>{row['name'].capitalize()}</h3>", unsafe_allow_html=True)

            radius = 45
            circumference = 2 * math.pi * radius
            progress = row["score"]
            offset = circumference * (1 - progress)

            st.markdown(f"""
            <div style="display:flex;justify-content:center;">
                <svg width="120" height="120">
                    <circle class="bg" cx="60" cy="60" r="{radius}" fill="none" />
                    <circle class="fg" cx="60" cy="60" r="{radius}" fill="none"
                        stroke-dasharray="{circumference}" stroke-dashoffset="{offset}">
                    </circle>
                </svg>
            </div>
            <h2 style='color:#b0f7ff;margin-top:-10px;'>Score: {row['score']:.3f}</h2>
            """, unsafe_allow_html=True)

            st.markdown(f"<p style='font-size:0.9em;color:#a8a8a8;'>{row['summary'][:120]}...</p></div>", unsafe_allow_html=True)

    # --- Silver-Neon Bar Chart ---
    st.markdown("### 📊 Comparative Performance")
    fig = px.bar(
        df_sorted,
        x="name",
        y="score",
        color="score",
        color_continuous_scale=["#00e6b8", "#b0f7ff"],
        title="Performance Scores Across Domains",
    )
    fig.update_layout(
        plot_bgcolor="#0a0a0f",
        paper_bgcolor="#0a0a0f",
        font=dict(color="#e0e0e0"),
        title_font=dict(color="#b0f7ff", size=22),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data found — run `python main.py` to generate reports.")

# --- Footer ---
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#00e6b8;'>🧠 The Alchemist AI — forging gold from data and light ✨</p>",
    unsafe_allow_html=True,
)
