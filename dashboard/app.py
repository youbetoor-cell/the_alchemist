# --- Intelligence Feed ---
st.markdown("## 💡 Unified Intelligence Feed")

@st.cache_data(ttl=300)
def get_btc_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {"vs_currency": "usd", "days": "1"}
        data = requests.get(url, params=params, timeout=10).json()
        prices = pd.DataFrame(data["prices"], columns=["ts", "price"])
        prices["dt"] = pd.to_datetime(prices["ts"], unit="ms")
        return prices
    except Exception:
        return None

@st.cache_data(ttl=300)
def get_aapl_data():
    try:
        df_aapl = yf.download("AAPL", period="1d", interval="15m", progress=False)
        if not df_aapl.empty:
            df_aapl = df_aapl.rename_axis("dt").reset_index()[["dt", "Close"]].rename(columns={"Close": "price"})
            return df_aapl
        return None
    except Exception:
        return None

def mock_series(label="mock", seed=0):
    np.random.seed(seed)
    vals = np.cumsum(np.random.normal(0, 0.1, 60)) + 100
    times = pd.date_range(end=datetime.utcnow(), periods=60, freq="min")
    return pd.DataFrame({"dt": times, "price": vals})

for _, row in df_sorted.iterrows():
    domain = row["name"].capitalize()
    summary = row["summary"]

    with st.expander(f"🔹 {domain} Intelligence", expanded=False):
        # --- AI Sentiment ---
        ai_summary = "💤 (Skipped — no API key)"
        sentiment_color = "#bfbfbf"
        sentiment_tag = "⚪ neutral"

        if client:
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are The Alchemist AI — concise sentiment analyst."},
                        {"role": "user", "content": f"Classify and summarize market tone for {domain}: {summary}"}
                    ],
                    max_tokens=60
                )
                ai_summary = resp.choices[0].message.content.strip().lower()

                # --- Detect sentiment ---
                if any(x in ai_summary for x in ["bullish", "positive", "rising", "optimistic"]):
                    sentiment_color = "#00e676"
                    sentiment_tag = "🟢 bullish"
                elif any(x in ai_summary for x in ["bearish", "negative", "falling", "pessimistic"]):
                    sentiment_color = "#ff4d4d"
                    sentiment_tag = "🔴 bearish"
                else:
                    sentiment_color = "#bfbfbf"
                    sentiment_tag = "⚪ neutral"
            except Exception as e:
                ai_summary = f"⚠️ AI unavailable: {e}"

        # --- Columns for summary + sparkline ---
        col1, col2 = st.columns([3, 2])

        with col1:
            st.markdown(
                f"<p style='color:{sentiment_color};'>🔮 {sentiment_tag}: {ai_summary}</p>",
                unsafe_allow_html=True
            )

            # --- Contextual Metrics ---
            metrics_text = ""
            try:
                if "crypto" in domain.lower():
                    url = "https://api.coingecko.com/api/v3/coins/bitcoin"
                    data = requests.get(url, timeout=10).json()
                    price = data["market_data"]["current_price"]["usd"]
                    chg = data["market_data"]["price_change_percentage_24h"]
                    vol = data["market_data"]["total_volume"]["usd"] / 1e9
                    metrics_text = f"💰 BTC ${price:,.0f} ({chg:+.2f}%) | 24h Vol: ${vol:.1f}B"

                elif "stocks" in domain.lower():
                    df_aapl = get_aapl_data()
                    if df_aapl is not None and len(df_aapl) > 2:
                        last = df_aapl["price"].iloc[-1]
                        prev = df_aapl["price"].iloc[-2]
                        chg = ((last - prev) / prev) * 100
                        metrics_text = f"💵 AAPL ${last:.2f} ({chg:+.2f}%)"
                    else:
                        metrics_text = "💵 AAPL data unavailable"

                elif "music" in domain.lower():
                    metrics_text = f"🎧 Top Track Streams: +{np.random.randint(10,30)}% (24h est.)"

                elif "sports" in domain.lower():
                    metrics_text = f"🏅 Activity Index: {np.random.uniform(0.8, 1.2):.2f}"

                elif "forex" in domain.lower():
                    url = "https://api.exchangerate.host/latest?base=USD"
                    fx = requests.get(url, timeout=10).json()
                    eur = fx["rates"]["EUR"]
                    gbp = fx["rates"]["GBP"]
                    metrics_text = f"💱 EUR/USD {eur:.3f} | GBP/USD {gbp:.3f}"

                elif "social" in domain.lower():
                    metrics_text = f"💬 Engagement Rate: {np.random.uniform(2, 7):.1f}%"

            except Exception as e:
                metrics_text = f"⚠️ Metrics unavailable: {e}"

            st.markdown(f"<p style='font-size:0.9em;color:#bfbfbf;'>{metrics_text}</p>", unsafe_allow_html=True)

        with col2:
            try:
                # ---- Dynamic Sparkline ----
                if "crypto" in domain.lower():
                    df = get_btc_data() or mock_series(domain, 1)
                elif "stocks" in domain.lower():
                    df = get_aapl_data() or mock_series(domain, 2)
                else:
                    df = mock_series(domain, 3)

                fig = go.Figure()
                color = sentiment_color
                fig.add_trace(go.Scatter(
                    x=df["dt"], y=df["price"], mode="lines",
                    line=dict(color=color, width=2),
                    fill="tozeroy", fillcolor=f"rgba(255,255,255,0.07)"
                ))
                fig.update_layout(
                    height=70, margin=dict(l=0, r=0, t=10, b=0),
                    xaxis=dict(visible=False), yaxis=dict(visible=False),
                    plot_bgcolor="#0a0a0f", paper_bgcolor="#0a0a0f"
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            except Exception as e:
                st.warning(f"⚠️ Sparkline unavailable: {e}")
