import streamlit as st
import pandas as pd
import json
import plotly.express as px
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

# --- Page Configuration ---
st.set_page_config(
    page_title="🧙‍♂️ The Alchemist Dashboard",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Auto-refresh every 5 minutes ---
st_autorefresh(interval=5 * 60 * 1000, key="datarefresh")

# --- HEADER ---
st.markdown("""
    <style>
        body {
            background-color: #0E1117;
            color: #E0E0E0;
            font-family: 'Inter', sans-serif;
        }
        h1, h2, h3 {
            color: #00C9A7;
            text-shadow: 0 0 15px #00C9A7AA;
        }
        .stDataFrame, .stTable {
            background-color: #111827;
            border-radius: 10px;
        }
        hr {
            border: 1px solid #333;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; color: #E0E0E0;'>
        🧙‍♂️ The Alchemist: <span style='color:#00C9A7;'>Intelligence Dashboard</span>
    </h1>
    <p style='text-align:center; color:#A0A0A0; font-size:18px;'>
        Real-time AI insights across <b>Crypto</b>, <b>Stocks</b>, <b>Sports</b>, and more.<br>
        <small>Auto-refreshes every 5 minutes | Powered by The Alchemist AI System ⚡</small>
    </p>
""", unsafe_allow_html=True)

# --- Load summary data ---
summary_path = Path("data/summary.json")

if not summary_path.exists():
    st.warning("⚠️ No summary found yet. Run `python main.py` to generate reports.")
    st.stop()

with open(summary_path, "r") as f:
    data = json.load(f)

st.markdown(f"### 🗓️ Generated at: `{data.get('generated_at', 'Unknown')}`")

# --- Ranking Table ---
ranking_df = pd.DataFrame(data["details"])
ranking_df = ranking_df.sort_values(by="score", ascending=False)

st.markdown("## 🏆 Current Domain Rankings")
st.dataframe(
    ranking_df[["name", "score", "summary"]],
    use_container_width=True,
    hide_index=True
)

# --- Highlight Top Performer ---
top = ranking_df.iloc[0]
st.success(
    f"🔥 **Top Performer:** {top['name'].capitalize()} with score **{top['score']:.2f}**\n\n"
    f"💡 *{top['summary']}*"
)

# --- Plotly Chart ---
fig = px.bar(
    ranking_df,
    x="name",
    y="score",
    color="score",
    color_continuous_scale="tealrose",
    title="📊 Domain Performance Overview",
    height=400
)
fig.update_layout(
    plot_bgcolor="#0E1117",
    paper_bgcolor="#0E1117",
    font=dict(color="#E0E0E0", size=14),
)
st.plotly_chart(fig, use_container_width=True)

# --- Crypto Snapshot ---
crypto_report = Path("data/reports/crypto_report.json")
if crypto_report.exists():
    st.markdown("## 💰 Crypto Snapshot (Live Data)")
    with open(crypto_report, "r") as f:
        crypto_data = json.load(f)
    st.json(crypto_data)
else:
    st.info("No crypto report found yet — run `python main.py` to fetch live data.")

# --- Footer ---
st.markdown("""
    <hr style='border: 1px solid #444;'/>
    <div style='text-align:center; color:#888; font-size:14px;'>
        ⌛ Dashboard auto-updates hourly · Designed by <b>The Alchemist AI</b>
    </div>
""", unsafe_allow_html=True)
