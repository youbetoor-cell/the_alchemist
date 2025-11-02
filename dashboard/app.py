import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="The Alchemist Dashboard",
    page_icon="🧙‍♂️",
    layout="wide",
)

# --- Auto Refresh every 2 minutes ---
st_autorefresh(interval=120 * 1000, key="datarefresh")


# --- Custom Styling ---
st.markdown("""
    <style>
    body {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    h1, h2, h3 {
        color: #9AE6B4;
        font-weight: 700;
    }
    .stDataFrame { border: 1px solid #333; border-radius: 10px; }
    .metric-card {
        padding: 15px;
        border-radius: 15px;
        background: linear-gradient(135deg, #111, #1A202C);
        box-shadow: 0px 0px 15px rgba(0, 255, 204, 0.2);
        text-align: center;
    }
    .pulse {
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { text-shadow: 0 0 5px #00FFD5; }
        50% { text-shadow: 0 0 20px #00FFD5; }
        100% { text-shadow: 0 0 5px #00FFD5; }
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🧙‍♂️ The Alchemist: Intelligence Dashboard")
st.markdown("### Real-time insights across domains — crypto, stocks, sports, and more.")

summary_path = Path("data/summary.json")

if summary_path.exists():
    with open(summary_path, "r") as f:
        summary = json.load(f)

    st.markdown(f"📅 **Generated at:** `{summary.get('generated_at')}`")

    df = pd.DataFrame(summary["details"])
    st.markdown("## 🏆 Current Rankings")
    st.dataframe(df[["name", "score", "summary"]], use_container_width=True)

    # --- Visualization: Domain Scores ---
    st.markdown("## ⚡ Performance Overview")
    fig = px.bar(
        df,
        x="name",
        y="score",
        color="score",
        color_continuous_scale="teal",
        text_auto=".2f",
        title="Domain Strength Index",
    )
    fig.update_layout(
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font_color="#FAFAFA",
        title_font=dict(size=22, color="#00FFD5"),
        hoverlabel_font_color="#111",
        hoverlabel_bgcolor="#00FFD5",
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Top Performer Card ---
    top = df.sort_values("score", ascending=False).iloc[0]
    st.markdown("## 🔥 Top Performer")
    st.markdown(f"""
        <div class='metric-card pulse'>
            <h2>{top['name'].title()}</h2>
            <h3>Score: {top['score']:.3f}</h3>
            <p>{top['summary']}</p>
        </div>
    """, unsafe_allow_html=True)

else:
    st.warning("⚠️ No summary file found yet. Run `python main.py` to generate data.")

# --- Crypto Snapshot ---
crypto_path = Path("data/reports/crypto_report.json")
if crypto_path.exists():
    with open(crypto_path, "r") as f:
        crypto_data = json.load(f)
    st.markdown("## 💰 Crypto Snapshot")
    st.json(crypto_data)
else:
    st.info("No crypto report found yet — run main.py to fetch live data.")

# --- AI Insight ---
st.markdown("## 🧠 The Alchemist Insight")
st.markdown("""
✨ The Alchemist continuously studies cross-domain data to reveal hidden opportunities.  
Next step: enable live AI summaries and predictive signal tracking.
""")
