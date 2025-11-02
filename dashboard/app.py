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

# --- Balanced Dark-Gold-Cyan Theme with Subtle Glow Animations ---
st.markdown("""
<style>
body {
    background: radial-gradient(circle at 20% 30%, #0a0a0f, #000);
    color: #e0e0e0;
    font-family: 'Inter', sans-serif;
    overflow-x: hidden;
}

/* Headings */
h1, h2, h3 {
    color: #f7e28f !important;
    text-shadow: 0 0 18px rgba(255, 215, 0, 0.4);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #b8860b, #00b3b3);
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 0.6em 1.4em;
    font-weight: bold;
    box-shadow: 0 0 10px rgba(255,215,0,0.4);
}
.stButton>button:hover {
    background: linear-gradient(90deg, #ffd700, #00e6b8);
    box-shadow: 0 0 18px rgba(255,215,0,0.6);
}

/* Cards */
.card {
    background: rgba(18,18,22,0.9);
    border: 1px solid rgba(180,180,180,0.2);
    border-radius: 15px;
    padding: 1.3rem;
    margin-bottom: 1rem;
    box-shadow: 0 0 20px rgba(255,215,0,0.05);
    transition: all 0.4s ease;
    text-align: center;
    animation: softPulse 6s ease-in-out infinite;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 25px rgba(255,215,0,0.25);
}

/* Pulse glow for energy effect */
@keyframes softPulse {
  0% { box-shadow: 0 0 15px rgba(255,215,0,0.08); }
  50% { box-shadow: 0 0 25px rgba(0,255,230,0.25); }
  100% { box-shadow: 0 0 15px rgba(255,215,0,0.08); }
}

/* Highlighted card (top performer) */
.highlight {
    border: 1px solid #ffd700;
    box-shadow: 0 0 35px rgba(255, 215, 0, 0.5);
    animation: pulseGold 4s ease-in-out infinite;
}
@keyframes pulseGold {
  0% { box-shadow: 0 0 30px rgba(255,215,0,0.3); }
  50% { box-shadow: 0 0 45px rgba(255,215,0,0.6); }
  100% { box-shadow: 0 0 30px rgba(255,215,0,0.3); }
}

/* Circular Rings */
svg { transform: rotate(-90deg); }
circle.bg { stroke: rgba(255, 255, 255, 0.08); stroke-width: 8; }
circle.fg {
    stroke: url(#alchemyGradient);
    stroke-width: 8;
    stroke-linecap: round;
    filter: drop-shadow(0 0 6px #ffd700);
    transition: stroke-dashoffset 1s ease-in-out;
    animation: glowPulse 5s ease-in-out infinite;
}
@keyframes glowPulse {
  0%, 100% { filter: drop-shadow(0 0 6px #ffd700); }
  50% { filter: drop-shadow(0 0 12px #00e6b8); }
}

/* Particles */
#particles {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  z-index: -1;
  overflow: hidden;
}
.particle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,215,0,0.7), rgba(255,215,0,0.1));
  animation: floatGold 20s infinite ease-in-out;
}
.particle.cyan {
  background: radial-gradient(circle, rgba(0,255,230,0.5), rgba(0,255,230,0.1));
  animation: floatCyan 24s infinite ease-in-out;
}
@keyframes floatGold {
  0%,100% { transform: translateY(0px) translateX(0px); opacity: 0.7; }
  50% { transform: translateY(-40px) translateX(30px); opacity: 0.3; }
}
@keyframes floatCyan {
  0%,100% { transform: translateY(0px) translateX(0px); opacity: 0.6; }
  50% { transform: translateY(30px) translateX(-25px); opacity: 0.2; }
}
</style>

<div id="particles">
  <div class="particle" style="width:6px; height:6px; top:20%; left:30%;"></div>
  <div class="particle cyan" style="width:8px; height:8px; top:50%; left:70%;"></div>
  <div class="particle" style="width:10px; height:10px; top:80%; left:20%;"></div>
  <div class="particle cyan" style="width:5px; height:5px; top:30%; left:80%;"></div>
  <div class="particle" style="width:7px; height:7px; top:65%; left:40%;"></div>
</div>
""", unsafe_allow_html=True)

# --- Gold + Cyan Gradient Definition ---
st.markdown("""
<svg width="0" height="0">
  <defs>
    <linearGradient id="alchemyGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ffd700"/>
      <stop offset="100%" stop-color="#00e6b8"/>
    </linearGradient>
  </defs>
</svg>
""", unsafe_allow_html=True)

# --- Auto-refresh ---
st_autorefresh(interval=10 * 60 * 1000, key="refresh")

# --- Header ---
st.title("⚗️ The Alchemist Intelligence Dashboard")
st.markdown("### Where precision meets beauty ⚡")

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

    # --- Cards with Rings ---
    st.markdown("### 🧩 Domain Performance Overview")
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
            <h2 style='color:#f7e28f;margin-top:-10px;'>Score: {row['score']:.3f}</h2>
            """, unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.9em;color:#bfbfbf;'>{row['summary'][:120]}...</p></div>", unsafe_allow_html=True)

    # --- Fixed Domain Scores Overview Chart ---
    st.markdown("### 📊 Domain Scores Overview")
    fig = px.bar(
        df_sorted,
        x="name",
        y="score",
        text_auto=".3f",
        color="score",
        color_continuous_scale=["#b8860b", "#ffd700", "#00e6b8"],
        title="Performance Across Domains",
    )
    fig.update_traces(
        textposition="outside",
        marker_line_width=1.2,
        marker_line_color="#202020",
    )
    fig.update_layout(
        plot_bgcolor="#0a0a0f",
        paper_bgcolor="#0a0a0f",
        font=dict(color="#e0e0e0"),
        title_font=dict(color="#f7e28f", size=22),
        xaxis=dict(title="", tickfont=dict(size=14)),
        yaxis=dict(gridcolor="#1e1e1e"),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data found — run `python main.py` to generate reports.")

# --- Footer ---
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#f7e28f;'>🧠 The Alchemist AI — elegance in equilibrium ✨</p>",
    unsafe_allow_html=True,
)
