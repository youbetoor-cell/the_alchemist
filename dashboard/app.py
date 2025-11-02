import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
from pathlib import Path
import json
from datetime import datetime
import math

# --- Page Config (must be first Streamlit call) ---
st.set_page_config(
    page_title="⚗️ The Alchemist Dashboard",
    page_icon="🧙‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- CSS: Futuristic Gold–Cyan–Silver theme ---
st.markdown("""
<style>
body {
    background: radial-gradient(circle at 20% 30%, #050505, #0a0a0f);
    color: #e0e0e0;
    font-family: 'Inter', sans-serif;
    overflow-x: hidden;
}

/* Title Glow */
h1, h2, h3 {
    color: #d4af37 !important; /* soft gold */
    text-shadow: 0 0 12px rgba(255, 215, 0, 0.3);
}

/* Buttons */
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

/* Card Container */
.card {
    background: rgba(18,18,22,0.9);
    border: 1px solid rgba(160,160,160,0.3);
    border-radius: 15px;
    padding: 1.3rem;
    margin-bottom: 1rem;
    box-shadow: 0 0 20px rgba(200,200,200,0.05);
    transition: all 0.4s ease;
    text-align: center;
}
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 0 30px rgba(0,255,230,0.4);
}

/* Highlighted top performer */
.highlight {
    border: 1px solid #ffd700;
    box-shadow: 0 0 25px rgba(255, 215, 0, 0.6);
    animation: goldPulse 5s ease-in-out infinite;
}
@keyframes goldPulse {
  0%,100% { box-shadow: 0 0 25px rgba(255,215,0,0.4); }
  50% { box-shadow: 0 0 40px rgba(0,255,230,0.5); }
}

/* Particle backdrop */
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
  background: radial-gradient(circle, rgba(255,215,0,0.4), rgba(255,215,0,0.1));
  animation: floatGold 16s infinite ease-in-out;
}
.particle.cyan {
  background: radial-gradient(circle, rgba(0,255,230,0.5), rgba(0,255,230,0.1));
  animation: floatCyan 22s infinite ease-in-out;
}
@keyframes floatGold {
  0%,100% { transform: translateY(0px); opacity: 0.8; }
  50% { transform: translateY(-35px); opacity: 0.4; }
}
@keyframes floatCyan {
  0%,100% { transform: translateY(0px); opacity: 0.7; }
  50% { transform: translateY(25px); opacity: 0.3; }
}
</style>

<div id="particles">
  <div class="particle" style="width:6px; height:6px; top:20%; left:30%;"></div>
  <div class="particle cyan" style="width:8px; height:8px; top:50%; left:70%;"></div>
  <div class="particle" style="width:10px; height:10px; top:80%; left:20%;"></div>
  <div class="particle cyan" style="width:5px; height:5px; top:30%; left:80%;"></div>
</div>
""", unsafe_allow_html=True)

# --- Auto-refresh every 10 min ---
st_autorefresh(interval=10 * 60 * 1000, key="refresh")

# --- Header ---
st.title("⚗️ The Alchemist Intelligence Dashboard")
st.caption("Fused in gold, silver, and light — rebalanced design ✨")

# --- Load summary data ---
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

    # --- Bar chart overview ---
    st.markdown("### 📊 Domain Scores Overview")
    fig = px.bar(
        df_sorted,
        y="name",
        x="score",
        orientation="h",
        color="score",
        color_continuous_scale=["#b8860b", "#d4af37", "#00e6b8"],
        text_auto=".3f",
        title="Performance Across Domains",
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

else:
    st.warning("No data found — run `python main.py` to generate new reports.")

st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#d4af37;'>🧠 The Alchemist AI — balanced elegance ✨</p>",
    unsafe_allow_html=True,
)
