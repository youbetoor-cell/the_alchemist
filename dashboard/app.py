import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="🧙‍♂️ The Alchemist", layout="wide")

# --- Header ---
st.markdown("""
<div style='text-align:center; padding: 1.5rem; background: linear-gradient(90deg, #1f1c2c, #928dab); border-radius: 15px;'>
<h1 style='color:white;'>🧙‍♂️ The Alchemist Intelligence Dashboard</h1>
<p style='color:#e0e0e0; font-size:1.2rem;'>Real-time AI-powered insights across markets and trends</p>
</div>
""", unsafe_allow_html=True)

summary_path = Path("data/summary.json")
if not summary_path.exists():
    st.warning("No summary file found yet. Run `python main.py` or wait for the next auto-update.")
    st.stop()

# --- Load summary ---
with open(summary_path) as f:
    summary = json.load(f)

st.sidebar.markdown("### 🕒 Last Updated")
st.sidebar.info(summary.get("generated_at", "N/A"))

ranking = pd.DataFrame(summary.get("details", []))

# --- Display Leaderboard ---
st.markdown("## 🏆 Domain Performance Rankings")
st.dataframe(
    ranking[["name", "score", "summary"]]
    .sort_values(by="score", ascending=False)
    .reset_index(drop=True),
    use_container_width=True
)

# --- Chart Section ---
st.markdown("## 📈 Visual Performance Overview")

fig = px.bar(
    ranking.sort_values(by="score", ascending=False),
    x="name",
    y="score",
    color="score",
    color_continuous_scale="Blues",
    title="Agent Confidence Scores"
)
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white")
)
st.plotly_chart(fig, use_container_width=True)

# --- Insights ---
top_agent = ranking.sort_values("score", ascending=False).iloc[0]
st.markdown(f"""
### 🧠 The Alchemist Insight  
> **Top Performer:** `{top_agent['name'].capitalize()}`  
> **Score:** `{round(top_agent['score'], 3)}`  
> **Summary:** {top_agent['summary']}
""")

# --- Footer ---
st.markdown("""
<hr>
<p style='text-align:center; color:gray; font-size:0.8rem;'>
© 2025 The Alchemist AI — Automated Intelligence Framework
</p>
""", unsafe_allow_html=True)
