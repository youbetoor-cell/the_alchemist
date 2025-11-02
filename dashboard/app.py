import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
from pathlib import Path
import json
from datetime import datetime
import time
import math

# --- Page Config ---
st.set_page_config(
    page_title="🧙‍♂️ The Alchemist Dashboard",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Dark & Gold Theme ---
st.markdown("""
<style>
body {
    background-color: #0a0a0a;
    color: #f1e5c0;
    font-family: 'Inter', sans-serif;
}
h1, h2, h3 {
    color: #ffd700 !important;
    text-shadow: 0 0 20px rgba(255, 215, 0, 0.6);
}
.stButton>button {
    background: linear-gradient(90deg, #d4af37, #b8860b);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.6em 1.3em;
    font-weight: bold;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #b8860b, #ffd700);
}
.card {
    background: rgba(25, 25, 25, 0.95);
    border: 1px solid rgba(255, 215, 0, 0.3);
    border-radius: 15px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 0 25px rgba(255, 215, 0, 0.15);
    transition: all 0.3s ease;
    text-align: center;
}
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 0 35px rgba(255, 215, 0, 0.35);
}
.highlight {
    border: 1px solid #ffcc00;
    box-shadow: 0 0 40px rgba(255, 215, 0, 0.6);
}
svg {
    transform: rotate(-90deg);
}
circle.bg {
    stroke: rgba(255, 255, 255, 0.08);
    stroke-width: 8;
}
circle.fg {
    stroke: #ffd700;
    stroke-width: 8;
    stroke-linecap: round;
    filter: drop-shadow(0 0 6px #ffcc00);
    transition: stroke-dashoffset 1s ease-in-out;
}
</style>
""", unsafe_allow_html=True)

# --- Auto-refresh every 10 min ---
st_autorefresh(interval=10 * 60 * 1000, key="refresh")

# --- Header ---
st.title("🧙‍♂️ The Alchemist – Intelligence Dashboard")
st.markdown("### Live golden intelligence feed – data alchemy for 2025 ⚡")

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

    st.markdown(f"🏆 **Top Performer:** `{top_name.capitalize()}` with score **{top_score:.3f}**")

    # --- Animated holographic cards ---
    st.markdown("### ✨ Domain Performance Overview")
    cols = st.columns(3)

    for i, row in df_sorted.iterrows():
        style = "card"
        if row["name"] == top_name:
            style += " highlight"

        with cols[i % 3]:
            st.markdown(f"<div class='{style}'><h3>🔸 {row['name'].capitalize()}</h3>", unsafe_allow_html=True)

            # --- Animated circular progress ring ---
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
            <h2 style='color:#ffd700;margin-top:-10px;'>Score: {row['score']:.3f}</h2>
            """, unsafe_allow_html=True)

            st.markdown(f"<p style='font-size:0.9em;color:#e0c97f;'>{row['summary'][:120]}...</p></div>", unsafe_allow_html=True)

    # --- Bar chart ---
    st.markdown("### 📊 Performance Comparison")
    fig = px.bar(
        df_sorted,
        x="name",
        y="score",
        color="score",
        color_continuous_scale=["#b8860b", "#ffd700"],
        title="Performance Scores Across Domains",
    )
    fig.update_layout(
        plot_bgcolor="#0a0a0a",
        paper_bgcolor="#0a0a0a",
        font=dict(color="#f1e5c0"),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data found — run `python main.py` to generate reports.")

# --- Footer ---
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#ffd700;'>🧠 The Alchemist AI — turning data into gold ✨</p>",
    unsafe_allow_html=True,
)
