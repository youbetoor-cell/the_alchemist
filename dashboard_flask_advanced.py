# ============================================================
# ⚗️ The Alchemist — Flask Smart Insight Dashboard (Phase 3)
# ============================================================
from flask import Flask, render_template_string
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

app = Flask(__name__)

DATA = Path("data")
MEMORY = DATA / "memory.json"
INSIGHT_LOG = DATA / "insight_log.json"
CORR_FILE = DATA / "correlation.json"

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def mock_series(seed=1, n=24):
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
        if "btc_price" not in df or "aapl_price" not in df:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()

def get_latest_insight():
    if INSIGHT_LOG.exists():
        try:
            logs = json.loads(INSIGHT_LOG.read_text())
            if isinstance(logs, list) and len(logs) > 0:
                return logs[-1].get("text", "(No insight text)")
        except Exception:
            pass
    return "No recent AI insight — run `python app.py` to generate one."

def get_insight_feed():
    if INSIGHT_LOG.exists():
        try:
            logs = json.loads(INSIGHT_LOG.read_text())
            if isinstance(logs, list):
                return logs[-50:]
        except Exception:
            pass
    return [{"timestamp": datetime.utcnow().isoformat(), "text": "(No insights yet — run app.py once.)"}]

def load_corr_report():
    if CORR_FILE.exists():
        try:
            return json.loads(CORR_FILE.read_text())
        except Exception:
            pass
    return {"latest_corr": "n/a", "regime": "n/a"}

def plot_market():
    df = load_memory_df()
    if df.empty:
        df_btc = mock_series(seed=1)
        df_aapl = mock_series(seed=42)
    else:
        df_btc = pd.DataFrame({"dt": df["timestamp"], "price": df["btc_price"].astype(float)})
        df_aapl = pd.DataFrame({"dt": df["timestamp"], "price": df["aapl_price"].astype(float)})

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_btc["dt"], y=df_btc["price"], mode="lines", name="BTC/USD"))
    fig.add_trace(go.Scatter(x=df_aapl["dt"], y=df_aapl["price"], mode="lines", name="AAPL"))
    fig.update_layout(template="plotly_dark", title="📊 BTC & AAPL Price Overview", height=400)
    return fig.to_html(include_plotlyjs="cdn", full_html=False)

def plot_volatility():
    df = load_memory_df()
    if df.empty:
        df = mock_series(seed=5)
        df["btc_ret"] = df["price"].pct_change() * 100
        df["aapl_ret"] = df["price"].pct_change() * 100
    else:
        df["btc_ret"] = df["btc_price"].pct_change() * 100
        df["aapl_ret"] = df["aapl_price"].pct_change() * 100

    df["volatility"] = (df["btc_ret"]**2 + df["aapl_ret"]**2)**0.5
    fig = px.density_heatmap(df, x="timestamp", y="btc_ret", z="volatility",
                             color_continuous_scale="Viridis", nbinsx=20)
    fig.update_layout(title="🔥 Volatility & Anomaly Heatmap", template="plotly_dark", height=400)
    return fig.to_html(include_plotlyjs="cdn", full_html=False)

# ------------------------------------------------------------
# Routes
# ------------------------------------------------------------
@app.route("/")
def home():
    corr = load_corr_report()
    df = load_memory_df()
    btc = df["btc_price"].iloc[-1] if not df.empty else 99233.50
    aapl = df["aapl_price"].iloc[-1] if not df.empty else 268.76
    ai_insight = get_latest_insight()

    html = f"""
    <html>
    <head><title>⚗️ The Alchemist — Smart Overview</title></head>
    <body style="background-color:#111;color:#EEE;font-family:Arial;padding:20px;">
        <h1>🧠 The Alchemist — Smart Overview</h1>
        <div style="background:#222;padding:15px;border-radius:10px;">
            <b>🧩 AI Insight:</b> <i>{ai_insight}</i>
        </div>
        <p>💰 BTC: ${btc:,.2f} | 📈 AAPL: ${aapl:,.2f}</p>
        <p>🔗 Corr: {corr.get('latest_corr','n/a')} | Regime: {corr.get('regime','n/a')}</p>
        <p>
            <a href='/charts'>📊 Market Charts</a> |
            <a href='/heatmap'>🔥 Volatility Heatmap</a> |
            <a href='/insights'>🧠 AI Insights</a>
        </p>
        <hr>
        <p style="color:gray;">Auto-refresh every 30s. © The Alchemist — AI Market Intelligence</p>
    </body></html>
    """
    return render_template_string(html)

@app.route("/charts")
def charts():
    return render_template_string(f"""
    <html><body style="background:#111;color:#EEE;">
    <h2>📊 Market Charts</h2>
    {plot_market()}
    <p><a href='/'>🏠 Home</a></p>
    </body></html>
    """)

@app.route("/heatmap")
def heatmap():
    return render_template_string(f"""
    <html><body style="background:#111;color:#EEE;">
    <h2>🔥 Volatility Heatmap</h2>
    {plot_volatility()}
    <p><a href='/'>🏠 Home</a></p>
    </body></html>
    """)

@app.route("/insights")
def insights():
    insights = get_insight_feed()
    insight_html = "".join([
        f"<p><b>{i['timestamp']}</b><br>{i['text']}</p><hr>"
        for i in insights
    ])
    return render_template_string(f"""
    <html><body style="background:#111;color:#EEE;">
    <h2>🧠 AI Insights Feed</h2>
    {insight_html}
    <p><a href='/'>🏠 Home</a></p>
    </body></html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
