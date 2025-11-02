import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
from pathlib import Path
import json
from datetime import datetime
import os
import requests

# --- Page Config ---
st.set_page_config(
    page_title="⚗️ The Alchemist Dashboard",
    page_icon="🧙‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Futuristic Gold–Cyan–Silver Theme ---
st.markdown("""
<style>
body {
    background: radial-gradient(circle at 20% 30%, #050505, #0a0a0f);
    color: #e0e0e0;
    font-family: 'Inter', sans-serif;
}
h1, h2, h3 {
    color: #d4af37 !important;
    text-shadow: 0 0 12px rgba(255, 215, 0, 0.3);
}
.stButton>button {
    background: linear-gradient(90deg, #b8860b, #00e6b8);
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 0.6em 1.4em;
    font-weight: bold;
    box-shadow: 0 0 10px rgba(255,215,0,0.4);
}
.stButton>button:hover {
    background: linear-gradient(90deg, #ffd700, #00ffff);
    box-shadow: 0 0 18px rgba(0,255,255,0.6);
}
.card {
    background: rgba(18,18,22,0.85);
    border: 1px solid rgba(160,160,160,0.25);
    border-radius: 15px;
    padding: 1.2rem;
    margin: 0.5rem;
    text-align: center;
    box-shadow: 0 0 25px rgba(255,215,0,0.05);
    transition: all 0.3s ease;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 25px rgba(0,255,230,0.3);
}
.highlight {
    border: 1px solid #ffd700;
    box-shadow: 0 0 30px rgba(255,215,0,0.5);
}
@media (max-width: 900px) {
    .stColumn { width: 100% !important; display: block; }
}
</style>
""", unsafe_allow_html=True)

# --- Auto-refresh every 10 minutes ---
st_autorefresh(interval=10 * 60 * 1000, key="refresh")

st.title("⚗️ The Alchemist Intelligence Dashboard")
st.caption("Gold, silver & light — now with sentiment and flow ✨")

summary_path = Path("data/summary.json")

if summary_path.exists():
    with open(summary_path, "r") as f:
        data = json.load(f)

    st.markdown(f"🕒 **Last update:** `{data.get('generated_at', datetime.utcnow())}`")

    df = pd.DataFrame(data.get("details", []))
    df_sorted = df.sort_values("score", ascending=False).reset_index(drop=True)

    top_name = df_sorted.iloc[0]["name"]
    top_score = df_sorted.iloc[0]["score"]

    st.markdown(f"🏆 **Top Performer:** `{top_name.capitalize()}` — **{top_score:.3f}**")

    # --- Horizontal domain cards ---
    st.markdown("### 🧩 Domain Performance Overview")
    cols = st.columns(len(df_sorted))
    for i, row in df_sorted.iterrows():
        style = "card"
        if row["name"] == top_name:
            style += " highlight"

        with cols[i]:
            st.markdown(f"<div class='{style}'><h3>{row['name'].capitalize()}</h3>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color:#f7e28f;'>Score: {row['score']:.3f}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:0.9em;color:#bfbfbf;'>{row['summary'][:100]}...</p></div>", unsafe_allow_html=True)

    # --- Bar chart (horizontal layout) ---
    st.markdown("### 📊 Domain Scores Overview")
    fig = px.bar(
        df_sorted,
        y="name", x="score",
        orientation="h",
        color="score",
        color_continuous_scale=["#b8860b", "#d4af37", "#00e6b8"],
        text_auto=".3f",
        title="Performance Across Domains"
    )
    fig.update_traces(textposition="outside", marker_line_color="#202020", marker_line_width=1.2)
    fig.update_layout(
        plot_bgcolor="#0a0a0f",
        paper_bgcolor="#0a0a0f",
        font=dict(color="#e0e0e0"),
        title_font=dict(color="#f7e28f", size=22),
        yaxis=dict(title="", tickfont=dict(size=13)),
        xaxis=dict(gridcolor="#1e1e1e"),
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Historical Performance Chart ---
hist_path = Path("data/history.json")
if hist_path.exists():
    with open(hist_path, "r") as f:
        hist = json.load(f)
    hist_df = pd.DataFrame(hist)
    hist_df["timestamp"] = pd.to_datetime(hist_df["timestamp"])

    st.markdown("### ⏳ Performance Over Time")
    domain_choice = st.selectbox("Select domain:", hist_df["domain"].unique())

    filtered = hist_df[hist_df["domain"] == domain_choice].sort_values("timestamp")
    fig_hist = px.line(
        filtered,
        x="timestamp",
        y="score",
        title=f"{domain_choice.capitalize()} — Score Trend",
        markers=True,
        line_shape="spline",
        color_discrete_sequence=["#00e6b8"]
    )
    fig_hist.update_layout(
        plot_bgcolor="#0a0a0f",
        paper_bgcolor="#0a0a0f",
        font=dict(color="#e0e0e0"),
        title_font=dict(color="#d4af37", size=20),
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # --- 7-Day Bitcoin Chart (safe version) ---
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {"vs_currency": "usd", "days": "7"}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            btc_data = r.json()
            btc_prices = btc_data["prices"]
            btc_df = pd.DataFrame(btc_prices, columns=["timestamp", "price"])
            btc_df["date"] = pd.to_datetime(btc_df["timestamp"], unit="ms")

            st.markdown("### 💹 Bitcoin 7-Day Trend")
            fig_btc = px.line(
                btc_df, x="date", y="price",
                title="Bitcoin Price (USD, 7 Days)",
                markers=True, line_shape="spline"
            )
            fig_btc.update_layout(
                plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f",
                font=dict(color="#e0e0e0"),
                title_font=dict(color="#00e6b8", size=20),
            )
            st.plotly_chart(fig_btc, use_container_width=True)
        else:
            st.warning("⚠️ Unable to fetch crypto data.")
    except Exception as e:
        st.warning(f"⚠️ Crypto chart unavailable: {e}")

# --- 7-Day Bitcoin Chart (multi-range version) ---
import requests

st.markdown("### 💹 Bitcoin Trend (Dynamic Range)")
time_ranges = {
    "30 Days": ("30", "30d"),
    "7 Days": ("7", "7d"),
    "1 Day": ("1", "1d"),
    "4 Hours": ("0.1666", "4h"),
    "1 Hour": ("0.0416", "1h"),
    "30 Minutes": ("0.0208", "30m"),
    "15 Minutes": ("0.0104", "15m"),
    "5 Minutes": ("0.0034", "5m"),
    "1 Minute": ("0.0007", "1m"),
}

# Dropdown for chart range selection
selected_label = st.selectbox("Select time range:", list(time_ranges.keys()), index=1)
selected_days, label = time_ranges[selected_label]

try:
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": selected_days}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code == 200:
        btc_data = r.json()
        btc_prices = btc_data.get("prices", [])
        btc_df = pd.DataFrame(btc_prices, columns=["timestamp", "price"])
        btc_df["date"] = pd.to_datetime(btc_df["timestamp"], unit="ms")

        fig_btc = px.line(
            btc_df,
            x="date",
            y="price",
            title=f"Bitcoin Price (USD, {label})",
            markers=True,
            line_shape="spline",
        )
        fig_btc.update_layout(
            plot_bgcolor="#0a0a0f",
            paper_bgcolor="#0a0a0f",
            font=dict(color="#e0e0e0"),
            title_font=dict(color="#00e6b8", size=20),
        )
        st.plotly_chart(fig_btc, use_container_width=True)
    else:
        st.warning(f"⚠️ Unable to fetch Bitcoin data ({r.status_code}).")
except Exception as e:
    st.warning(f"⚠️ Crypto chart unavailable: {e}")

# --- 🧭 AI Volume Anomaly Detector (Force Display Mode: BTC, ETH, SOL always shown) ---
from streamlit_autorefresh import st_autorefresh
import requests, numpy as np, os, json, httpx
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go

st_autorefresh(interval=5 * 60 * 1000, key="volume_refresh")

st.markdown("### 🚨 Volume & Momentum Detector (Top 100 Coins — Force Display Mode)")

slack_url = os.getenv("SLACK_WEBHOOK_URL", "").strip()
cache_dir = Path("data/cache"); cache_dir.mkdir(parents=True, exist_ok=True)
alerts_cache_path = cache_dir / "volume_alerts.json"

def compute_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    roll_up = gain.ewm(alpha=1/period, adjust=False).mean()
    roll_down = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = roll_up / (roll_down.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi

def pct_change_window(df_, minutes):
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)
    win = df_[df_["dt"] >= cutoff]
    if len(win) >= 2:
        return ((win["price"].iloc[-1] - win["price"].iloc[0]) / win["price"].iloc[0]) * 100
    return np.nan

# Always show these coins + detected anomalies
force_show_ids = ["bitcoin", "ethereum", "solana"]

try:
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 100, "page": 1}
    markets = requests.get(url, params=params, timeout=25).json()
    df = pd.DataFrame(markets)[["id", "symbol", "name", "total_volume", "current_price", "price_change_percentage_24h"]]

    # Detect volume surges (still functional)
    np.random.seed()
    df["volume_prev_30m"] = df["total_volume"] * (1 - (np.random.randn(len(df)) * 0.02))
    df["volume_change_pct"] = ((df["total_volume"] - df["volume_prev_30m"]) / df["volume_prev_30m"]) * 100
    surges = df[df["volume_change_pct"] > 50]

    # Force-show BTC, ETH, SOL
    df_force = df[df["id"].isin(force_show_ids)]
    show_df = pd.concat([surges, df_force]).drop_duplicates(subset="id")

    if show_df.empty:
        st.info("No active coins found (CoinGecko may be throttled). Try again soon.")
    else:
        st.success(f"💹 Showing {len(show_df)} coins (forced display active)")

        for _, row in show_df.iterrows():
            coin_id = row["id"]
            name = row["name"]
            sym = row["symbol"].upper()

            try:
                mc_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
                mc_params = {"vs_currency": "usd", "days": "1"}  # 1 day minute data
                mc = requests.get(mc_url, params=mc_params, timeout=25).json()

                prices = mc.get("prices", [])
                p_df = pd.DataFrame(prices, columns=["ts", "price"])
                p_df["dt"] = pd.to_datetime(p_df["ts"], unit="ms")
                last_60m = p_df[p_df["dt"] > (datetime.utcnow() - timedelta(minutes=60))]

                volumes = mc.get("total_volumes", [])
                v_df = pd.DataFrame(volumes, columns=["ts", "volume"])
                v_df["dt"] = pd.to_datetime(v_df["ts"], unit="ms")
                last_30m = v_df[v_df["dt"] > (datetime.utcnow() - timedelta(minutes=30))]

                # Momentum + RSI
                mom_15 = pct_change_window(last_60m, 15)
                rsi_val = compute_rsi(last_60m["price"]).iloc[-1] if len(last_60m) >= 16 else np.nan

                # Mini chart (dual axis)
                if not last_30m.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=last_30m["dt"], y=last_30m["volume"],
                        name="Volume", marker_color="#00e6b8", yaxis="y1"
                    ))
                    if not last_60m.empty:
                        fig.add_trace(go.Scatter(
                            x=last_60m["dt"], y=last_60m["price"],
                            mode="lines", line=dict(color="#d4af37", width=2),
                            name="Price (USD)", yaxis="y2"
                        ))
                    fig.update_layout(
                        barmode="overlay",
                        height=180,
                        title=f"{name} ({sym}) — 30m Volume & Price",
                        paper_bgcolor="#0a0a0f",
                        plot_bgcolor="#0a0a0f",
                        font=dict(color="#e0e0e0", size=10),
                        margin=dict(l=0, r=0, t=30, b=0),
                        yaxis=dict(title="Volume", showgrid=False),
                        yaxis2=dict(title="Price", overlaying="y", side="right", showgrid=False)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                st.markdown(
                    f"<div class='card'><b>{name} ({sym})</b><br>"
                    f"💰 ${row['current_price']:.4f} | 24h Δ {row['price_change_percentage_24h']:.2f}%<br>"
                    f"🧪 RSI(14): {rsi_val:.1f} | 📈 15m Δ {mom_15:+.2f}%</div>",
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.warning(f"⚠️ Data fetch failed for {name}: {e}")

except Exception as e:
    st.warning(f"⚠️ Detector unavailable: {e}")
(f"<p style='color:#00e6b8;'>🔮 {ai_summary}</p>", unsafe_allow_html=True)
                except Exception:
                    pass

            if slack_url:
                try:
                    lines = []
                    for q in qualified_alerts:
                        tag = "🔥" if (q["rsi"] and q["rsi"] >= RSI_OVERBOUGHT) or (q["mom15"] and q["mom15"] >= 4) else "⚡"
                        rsi_txt = f"RSI {q['rsi']:.1f}" if (q["rsi"] and not np.isnan(q["rsi"])) else "RSI n/a"
                        mom15_txt = f"15m {q['mom15']:+.2f}%" if (q["mom15"] and not np.isnan(q["mom15"])) else "15m n/a"
                        lines.append(
                            f"{tag} *{q['name']} ({q['sym']})*\n"
                            f"Vol +{q['surge']:.1f}% | {mom15_txt} | {rsi_txt}\n"
                            f"Price ${q['price']:.4f} | 24h Δ {q['chg24']:.2f}%"
                        )
                    text = "🧙‍♂️ *The Alchemist Alerts — Volume + Momentum*\n\n" + "\n\n".join(lines)
                    if ai_summary:
                        text += f"\n\n🔮 *AI Insight:* {ai_summary}"
                    httpx.post(slack_url, json={"text": text}, timeout=15)
                    st.success(f"📣 Sent {len(qualified_alerts)} alert(s) to Slack.")
                except Exception as e:
                    st.warning(f"⚠️ Slack alert failed: {e}")
            else:
                st.info("ℹ️ Slack alerts disabled — add SLACK_WEBHOOK_URL to your Streamlit secrets.")

            save_alert_cache(cache)
        else:
            st.write("🕊️ No *qualified* alerts (need volume + momentum/RSI confirmation).")

    with st.expander("⚙️ Alert settings"):
        st.caption(
            f"TTL: {ALERT_TTL_HOURS}h (de-dup), Escalation: +{ESCALATION_THRESHOLD}% extra surge.\n"
            f"Momentum rule: 15m ≥ {MOMENTUM_15M_THRESHOLD}%, RSI rule: RSI≥{RSI_OVERBOUGHT}."
        )
        if st.button("🧹 Clear alert memory (force alerts next run)"):
            try:
                if alerts_cache_path.exists():
                    alerts_cache_path.unlink()
                st.success("Cleared alert memory.")
            except Exception as e:
                st.warning(f"Could not clear cache: {e}")

except Exception as e:
    st.warning(f"⚠️ Detector unavailable: {e}")

# --- 🧠 AI Domain Insights + Test Button ---
from openai import OpenAI
import httpx

st.markdown("### 🧠 AI Domain Insights")

api_key = os.getenv("OPENAI_API_KEY", "").strip()
client = None

# --- Test AI Connection Button ---
if st.button("🔍 Test AI Connection"):
    if not api_key:
        st.warning("⚠️ Missing API key. Add it in Streamlit Secrets.")
    else:
        try:
            test_client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=True))
            models = test_client.models.list()
            st.success("✅ Connection successful — models fetched!")
        except Exception as e:
            st.error(f"⚠️ Connection test failed: {e}")

# --- Regular connection logic ---
try:
    if api_key:
        client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=True))
        _ = client.models.list()
        st.success("✅ AI connection established successfully.")
    else:
        st.warning("⚠️ AI summaries disabled — missing API key.")
except Exception as e:
    st.warning(f"⚠️ Connection failed: {e}")
    client = None

if client:
    for _, row in df_sorted.iterrows():
        prompt = f"Provide a concise market sentiment summary for {row['name']} based on: {row['summary']}"
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are The Alchemist AI, a concise financial sentiment analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60
            )
            ai_summary = response.choices[0].message.content.strip()
        except Exception as e:
            if "insufficient_quota" in str(e):
                ai_summary = "💤 AI paused — quota exceeded."
            elif "authentication_error" in str(e).lower():
                ai_summary = "⚠️ Invalid or expired API key."
            else:
                ai_summary = "⚠️ AI summary temporarily unavailable."

        st.markdown(
            f"<div class='card'><b>{row['name'].capitalize()}</b><br>"
            f"<span style='color:#00e6b8;'>{ai_summary}</span></div>",
            unsafe_allow_html=True
        )
