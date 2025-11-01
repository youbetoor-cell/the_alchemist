import streamlit as st
import json
from pathlib import Path
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="🧙‍♂️ The Alchemist", layout="wide")

st.title("🧙‍♂️ The Alchemist: Intelligence Dashboard")
st.caption("Real-time insights across domains — crypto, stocks, sports, and more.")

# --- Load summary file ---
summary_path = Path("data/summary.json")
if summary_path.exists():
    with open(summary_path, "r") as f:
        summary = json.load(f)

    st.write("📅 Generated at:", summary["generated_at"])
    df = pd.DataFrame(summary["details"])
    st.dataframe(df, use_container_width=True)

    top = max(summary["details"], key=lambda x: x["score"])
    st.success(f"🔥 Top performer: {top['name'].capitalize()} with score {top['score']}")

else:
    st.warning("No summary file found yet. Run `python main.py` to generate data.")
    st.stop()

# --- Live Crypto Data ---
crypto_path = Path("data/reports/crypto_report.json")
if crypto_path.exists():
    with open(crypto_path, "r") as f:
        crypto = json.load(f)
    st.header("💰 Live Crypto Snapshot")
    st.json(crypto)
    fig = px.bar(
        x=["Change (24h)"],
        y=[crypto["change_24h"]],
        title=f"{crypto['top_coin']} (24h % change)",
        labels={"x": "Metric", "y": "Change (%)"},
        color=[crypto["change_24h"]],
        color_continuous_scale=["red", "green"],
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No crypto report found yet.")

# --- Live Stocks Data ---
stocks_path = Path("data/reports/stocks_report.json")
if stocks_path.exists():
    with open(stocks_path, "r") as f:
        stocks = json.load(f)
    st.header("💹 Live Stock Snapshot")
    st.json(stocks)
    fig2 = px.bar(
        x=["Change (1d)"],
        y=[stocks["change_1d"]],
        title=f"{stocks['ticker']} (1-day % change)",
        labels={"x": "Metric", "y": "Change (%)"},
        color=[stocks["change_1d"]],
        color_continuous_scale=["red", "green"],
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No stocks report found yet.")
