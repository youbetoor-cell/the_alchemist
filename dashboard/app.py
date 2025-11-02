import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
from pathlib import Path
import json
from datetime import datetime

# --- Page Setup ---
st.set_page_config(
    page_title="🧙‍♂️ The Alchemist Dashboard",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Futuristic CSS Theme ---
st.markdown("""
<style>
body {
    background-color: #0d1117;
    color: #c9d1d9;
}
h1, h2, h3 {
    color: #00ffc8 !important;
    text-shadow: 0 0 15px #00ffc8;
}
div[data-testid="stMetricValue"] {
    color: #58a6ff;
}
.stButton>button {
    color: white;
    background: linear-gradient(90deg, #1f6feb, #00ffc8);
    border: none;
    border-radius: 10px;
    padding: 0.6em 1.2em;
    font-weight: bold;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #00ffc8, #1f6feb);
}
div.block-container {
    padding-top: 1.5rem;
}
.card {
    background: rgba(18, 18, 18, 0.85);
    border: 1px solid rgba(0, 255, 200, 0.2);
    border-radius: 15px;
    padding: 1.2rem;
    box-shadow: 0 0 20px rgba(0, 255, 200, 0.15);
    transition: 0.3s;
}
.card:hover {
    box-shadow: 0 0 35px rgba(0, 255, 200, 0.35);
    transform: translateY(-3px);
}
.highlight {
    border: 1px solid rgba(255, 215, 0, 0.5);
    box-shadow: 0 0 35px rgba(255, 215, 0, 0.4);
}
</style>
""", unsafe_allow_html=True)

# --- Auto Refresh every 10 minutes ---
st_autorefresh(interval=10 * 60 * 1000, key="datarefresh")

# --- Header ---
st.title("🧙‍♂️ The Alchemist: Intelligence Dashboard")
st.markdown("### A live fusion of markets, music, and data — reimagined for 2025 ⚡")

# --- Load Summary ---
summary_path = Path("data/summary.json")
if summary_path.exists():
    with open(summary_path, "r") as f:
        data = json.load(f)

    st.markdown(f"🕒 **Last update:** `{data.get('generated_at', datetime.utcnow())}`")

    df = pd.DataFrame(data.get("details", []))
    df_sorted = df.sort_values("score", ascending=False).reset_index(drop=True)

    top_name = df_sorted.iloc[0]["name"]
    top_score = df_sorted.iloc[0]["score"]

    st.markdown(f"🔥 **Top Performer:** `{top_name.capitalize()}` with score **{top_score:.3f}**")

    # --- Cards Layout ---
    st.markdown("### ⚡ Domain Intelligence Overview")
    cols = st.columns(3)

    for i, row in df_sorted.iterrows():
        card_style = "card"
        if row["name"] == top_name:
            card_style += " highlight"

        with cols[i % 3]:
            st.markdown(f"""
            <div class="{card_style}">
                <h3>🔹 {row['name'].capitalize()}</h3>
                <p><b>Score:</b> {row['score']:.3f}</p>
                <p style='font-size:0.9em;color:#9be9a8'>{row['summary'][:120]}...</p>
            </div>
            """, unsafe_allow_html=True)

    # --- Chart ---
    st.markdown("### 📊 Performance Comparison")
    fig = px.bar(
        df_sorted,
        x="name",
        y="score",
        color="score",
        color_continuous_scale="tealrose",
        title="Performance Scores Across Domains",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data found. Run `python main.py` to generate reports.")

# --- Footer ---
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#58a6ff;'>🧠 The Alchemist AI — transforming raw data into gold ✨</p>",
    unsafe_allow_html=True,
)
