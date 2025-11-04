# ============================================================
# ⚗️ The Alchemist — Flask Dashboard (Stable Local Version)
# ============================================================
from flask import Flask, render_template_string
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go

app = Flask(__name__)

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
    fig.add_trace(go.Scatter(x=df_btc["dt"], y=df_btc["price"], mode="lines", name="BTC/USD"))
    fig.add_trace(go.Scatter(x=df_aapl["dt"], y=df_aapl["price"], mode="lines", name="AAPL"))
    fig.update_layout(template="plotly_dark", title="📊 BTC & AAPL Price Overview", height=400)
    return fig.to_html(include_plotlyjs="cdn", full_html=False)

# ------------------------------------------------------------
# Flask routes
# ------------------------------------------------------------
@app.route("/")
def dashboard():
    chart_html = plot_market()
    insight = get_latest_insight()
    corr = load_corr_report()
    corr_html = (
        f"<b>Timestamp:</b> {corr.get('timestamp','n/a')}<br>"
        f"<b>Latest Corr:</b> {corr.get('latest_corr','n/a')}<br>"
        f"<b>Avg Corr:</b> {corr.get('avg_corr','n/a')}<br>"
        f"<b>Regime:</b> {corr.get('regime','n/a')}<br>"
        f"<b>Hint:</b> {corr.get('hint','')}"
    )

    html = f"""
    <html>
    <head>
        <title>⚗️ The Alchemist Dashboard</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body {{
                background-color: #111;
                color: #EEE;
                font-family: Arial, sans-serif;
                margin: 20px;
            }}
            h1 {{ color: #FFD700; }}
            .section {{ margin-top: 30px; }}
        </style>
    </head>
    <body>
        <h1>🧠 The Alchemist — AI Market Intelligence Dashboard</h1>
        <p>Auto-refreshing every 30s</p>

        <div class="section">
            {chart_html}
        </div>

        <div class="section">
            <h2>🧠 Latest Insight</h2>
            <p>{insight}</p>
        </div>

        <div class="section">
            <h2>🔗 Correlation Report</h2>
            <p>{corr_html}</p>
        </div>

        <hr>
        <footer>© The Alchemist — AI-Driven Market Intelligence</footer>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
