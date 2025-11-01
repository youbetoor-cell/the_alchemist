import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.express as px
from datetime import datetime

# --- App Config ---
st.set_page_config(page_title="🧙‍♂️ The Alchemist", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
/* Background gradient */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 20% 20%, #0f0f1f, #000000 70%);
    color: #e0e0e0;
    font-family: 'Poppins', sans-serif;
}

/* Header */
.alchemist-header {
    text-align: center;
    padding: 2rem;
    border-radius: 20px;
    background: linear-gradient(90deg, #f0b90b, #d4af37, #a37e2c);
    box-shadow: 0 0 25px rgba(240,185,11,0.4);
    color: black;
    font-weight: 600;
}

/* Cards */
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

/* Data Table */
thead tr th {
    background-color: #111 !important;
    color: #f0b90b !important;
}

/* Footer */
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
    <p>Where data transforms into gold — automated intelligence for financial markets</p>
</div>
""", unsafe_allow_html=True)

# --- Load data ---
summary_path = Path("data/summary.json")
if not summary_path.exists():
    st.warning("No summary file found yet. Run `python main.py` or wait for auto-update.")
    st.stop()

with open(summary_path) as f:
    summary = json.load(f)

ranking = pd.DataFrame(summary.get("details", []))
ranking = ranking.sort_values(by="score", ascending=False)

# --- Sidebar ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2821/2821637.png", width=100)
st.sidebar.markdown("### 🕒 Last Updated")
st.sidebar.info(summary.get("generated_at", "N/A"))
st.sidebar.markdown("### ⚙️ Top Performer")
if not ranking.empty:
    st.sidebar.success(f"{ranking.iloc[0]['name'].capitalize()} — Score: {round(ranking.iloc[0]['score'], 3)}")

# --- Main Dashboard ---
st.markdown("## 🏆 Performance Overview")

# Interactive Chart
fig = px.bar(
    ranking,
    x="name",
    y="score",
    color="score",
    text_auto=".2f",
    color_continuous_scale="sunset",
    title="Agent Confidence Scores",
)
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
)
st.plotly_chart(fig, use_container_width=True)

# --- Agent Cards ---
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

# --- Insight Summary ---
if not ranking.empty:
    top = ranking.iloc[0]
    st.markdown(f"""
    <div class='alchemist-card'>
        <h2>🧠 The Alchemist Insight</h2>
        <p><strong>Top performer:</strong> {top['name'].capitalize()}</p>
        <p><strong>Score:</strong> {round(top['score'],3)}</p>
        <p><strong>Summary:</strong> {top['summary']}</p>
    </div>
    """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<div class='footer'>
    <hr>
    <p>© 2025 <b>The Alchemist AI</b> — Turning Data into Gold</p>
</div>
""", unsafe_allow_html=True)
