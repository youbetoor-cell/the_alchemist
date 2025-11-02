import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
from pathlib import Path
import json
from datetime import datetime

# --- Set Page Config FIRST ---
st.set_page_config(
    page_title="🧙‍♂️ The Alchemist Dashboard",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Global CSS for Futuristic Dark Theme ---
st.markdown("""
<style>
body {
    background-color: #0d1117;
    color: #c9d1d9;
}
h1, h2, h3 {
    color: #58a6ff !important;
    text-shadow: 0 0 10px #1f6feb;
}
div[data-testid="stMetricValue"] {
    color: #00ffc8;
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
.reportview-container .markdown-text-container {
    color: #c9d1d9;
}
div.block-container {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# --- Auto Refresh (every 10 minutes) ---
st_autorefresh(interval=10 * 60 * 1000, key="datarefresh")

# --- Header ---
st.title("🧙‍♂️ The Alchemist: Intelligence Dashboard")
st.markdown("### Real-time insights across crypto, stocks, sports and more ⚡")

# --- Load Latest Summary ---
summary_path = Path("data/summary.json")
if summary_path.exists():
    with open(summary_path, "r") as f:
        data = json.load(f)

    st.markdown(f"🕒 Last update: `{data.get('generated_at', datetime.utcnow())}`")

    df = pd.DataFrame(data.get("details", []))
    df_sorted = df.sort_values("score", ascending=False)

    # Ranking table
    st.subheader("🏆 Current Rankings")
    st.dataframe(
        df_sorted.style.background_gradient(
            cmap="cool", subset=["score"]
        ).format({"score": "{:.3f}"})
    )

    top_name = df_sorted.iloc[0]["name"]
    top_score = df_sorted.iloc[0]["score"]
    st.markdown(f"🔥 **Top Performer:** `{top_name.capitalize()}` with score **{top_score:.3f}**")

    # Plotly chart
    fig = px.bar(
        df_sorted,
        x="name",
        y="score",
        color="score",
        color_continuous_scale="Viridis",
        title="📊 Performance Scores",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data yet — run `python main.py` to generate reports.")

# --- Footer ---
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown(
    "🧠 **The Alchemist AI** — fusing data alchemy and machine intelligence ✨",
)
