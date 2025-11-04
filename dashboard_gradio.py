# ============================================================
# ⚗️ The Alchemist — Live AI Market Dashboard (Stable Final)
# ============================================================
import gradio as gr
import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path
import plotly.graph_objects as go
import threading, time

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
DATA = Path("data")
MEMORY = DATA / "memory.json"
INSIGHT_LOG = DATA / "insight_log.json"
CORR_FILE = DATA / "correlation.json"

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def mock_series(seed=1, n=48):
    np.random.seed(seed)
    base = 100 + np.cumsum(np.random.randn(n))
    dt = pd.date_range(end=datetime.utcnow(), periods=n, freq="h")
    return pd.DataFrame({"dt": dt, "price": base})

def load_memory_df():
    if not MEMORY.exists():
        return pd.DataFrame()
    try:
        raw = json.loads(MEMORY.read_text())
        if not isinstance(raw, list) or len(raw) == 0:
            return pd.DataFrame()
        df = pd.DataFrame(raw)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])
        return df
    except Exception:
        return pd.DataFrame()

def get_latest_insight():
    if INSIGHT_LOG.exists():
        try:
            logs = json.loads(INSIGHT_LOG.read_text())
            if isinstance(logs, list) and len(logs) > 0:
                return logs[-1]["text"]
        except Exception:
            pass
    return "(No recent insight available.)"

def load_corr_report():
    if CORR_FILE.exists():
        try:
            return json.loads(CORR_FILE.read_text())
        except Exception:
            pass
    return {}

# ------------------------------------------------------------
# Dashboard sections
# ------------------------------------------------------------
def plot_market():
    df = load_memory_df()
    if df.empty:
        df_btc = mock_series(seed=1)
        df_aapl = mock_series(seed=42)
    else:
        df_btc = pd.DataFrame({
            "dt": df["timestamp"],
            "price": df["btc_price"].astype(float)
        })
        df_aapl = pd.DataFrame({
            "dt": df["timestamp"],
            "price": df["aapl_price"].astype(float)
        })

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_btc["dt"], y=df_btc["price"],
                             mode="lines", name="BTC/USD", line=dict(width=2)))
    fig.add_trace(go.Scatter(x=df_aapl["dt"], y=df_aapl["price"],
                             mode="lines", name="AAPL", line=dict(width=2)))
    fig.update_layout(
        title="📊 BTC & AAPL Price Overview",
        xaxis_title="Time (UTC)",
        yaxis_title="Price",
        template="plotly_dark",
        height=400,
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    return fig.to_html(include_plotlyjs="cdn", full_html=False)

def show_correlation():
    corr = load_corr_report()
    if not corr:
        return "⚠️ No correlation data yet."
    latest = corr.get("latest_corr", "n/a")
    regime = corr.get("regime", "Unknown")
    avg = corr.get("avg_corr", "n/a")
    hint = corr.get("hint", "")
    ts = corr.get("timestamp", "")
    return f"""
🧩 **Correlation Report**  
**Timestamp:** {ts}  
**Latest Corr:** {latest}  
**Avg Corr:** {avg}  
**Regime:** {regime}  
**Hint:** {hint}
"""

def update_dashboard():
    chart_html = plot_market()
    insight = get_latest_insight()
    corr_text = show_correlation()
    return chart_html, insight, corr_text

# ------------------------------------------------------------
# Background thread for auto-refresh
# ------------------------------------------------------------
latest_data = {"chart": "", "insight": "", "corr": ""}

def auto_update_loop():
    while True:
        chart, ins, corr = update_dashboard()
        latest_data["chart"], latest_data["insight"], latest_data["corr"] = chart, ins, corr
        time.sleep(30)

# ------------------------------------------------------------
# Build Gradio App
# ------------------------------------------------------------
def build_ui():
    with gr.Blocks(theme="gradio/soft", title="🧠 The Alchemist — Live AI Dashboard") as demo:
        gr.Markdown("# 🧠 The Alchemist — AI Market Intelligence Dashboard")

        with gr.Tabs():
            with gr.TabItem("📈 Market Overview"):
                chart_plot = gr.HTML(value=plot_market)
                gr.Markdown("Live BTC + AAPL trends (auto-refreshing every 30s).")

            with gr.TabItem("🧠 Insights"):
                insight_box = gr.Textbox(value=get_latest_insight(), label="Latest AI Insight", interactive=False, lines=4)

            with gr.TabItem("🔗 Correlations"):
                corr_box = gr.Markdown(value=show_correlation())

        refresh = gr.Button("🔄 Refresh Now")
        refresh.click(update_dashboard, outputs=[chart_plot, insight_box, corr_box])

        # Manual simulated auto-refresh using JS polling
        js = """
        function refreshEvery30s() {
            setInterval(() => {
                document.querySelector('button:contains("🔄 Refresh Now")')?.click();
            }, 30000);
        }
        refreshEvery30s();
        """
        gr.HTML(f"<script>{js}</script>")

        gr.Markdown("---")
        gr.Markdown("© The Alchemist — AI-Driven Market Intelligence")

    return demo

# ------------------------------------------------------------
# Main entry
# ------------------------------------------------------------
if __name__ == "__main__":
    threading.Thread(target=auto_update_loop, daemon=True).start()
    app = build_ui()
    app.launch(server_name="0.0.0.0", server_port=7860)
