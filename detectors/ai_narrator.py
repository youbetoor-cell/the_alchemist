# detectors/ai_narrator.py
import os, json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

try:
    from openai import OpenAI
    HAS_OPENAI = True
except Exception:
    HAS_OPENAI = False

DEF_MODEL = "gpt-4o-mini"

def _load_history(history_path: str = "data/history.json") -> pd.DataFrame:
    p = Path(history_path)
    if not p.exists():
        return pd.DataFrame()
    with p.open("r") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    if df.empty:
        return df
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

def _compact_context(df: pd.DataFrame, domain: str, hours: int = 48) -> dict:
    if df.empty:
        return {"domain": domain, "points": []}

    now = df["timestamp"].max() if "timestamp" in df.columns else datetime.utcnow()
    start = now - timedelta(hours=hours)
    d = df[(df.get("domain") == domain) & (df["timestamp"] >= start)].sort_values("timestamp")

    if d.empty:
        return {"domain": domain, "points": []}

    # Take at most 24 evenly-spaced points to keep prompt small
    take = min(len(d), 24)
    sampled = d.iloc[:: max(1, len(d)//take)].copy()
    points = [
        {"t": ts.isoformat() if hasattr(ts, "isoformat") else str(ts), "score": float(s)}
        for ts, s in zip(sampled["timestamp"], sampled["score"])
    ]
    delta = float(d["score"].iloc[-1] - d["score"].iloc[0])
    return {"domain": domain, "points": points, "delta": delta}

def narrate_anomalies(anomalies: list, history_path: str = "data/history.json") -> list:
    """
    Input: anomalies = [{"domain","timestamp","score","zscore","direction"}, ...]
    Output: list with narration text attached per anomaly.
    """
    if not anomalies:
        return []

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or not HAS_OPENAI:
        # Graceful fallback: return templated “no-AI” narration
        out = []
        for a in anomalies:
            direction = "surge" if a.get("direction") == "surge" else "drop"
            arrow = "📈" if direction == "surge" else "📉"
            out.append({
                **a,
                "narration": f"{arrow} {a['domain'].capitalize()} anomaly detected (z={a['zscore']}). "
                             f"AI explanation unavailable (no API key)."
            })
        return out

    # Build client
    from openai import OpenAI
    import httpx
    client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=True))

    # History context
    hist_df = _load_history(history_path)

    narrated = []
    for a in anomalies:
        ctx = _compact_context(hist_df, a["domain"], hours=48)

        system = (
            "You are The Alchemist AI. Explain anomalies in 1–2 concise lines. "
            "Include a sentiment tag (🟢 bullish / 🔴 bearish / ⚪ neutral) and confidence (0–100%). "
            "Be specific and avoid generic language."
        )
        user = {
            "anomaly": a,
            "context": ctx,
            "instructions": {
                "style": "1–2 lines, crisp, finance-oriented",
                "include": ["sentiment_tag", "confidence_percent"],
            },
        }

        try:
            resp = client.chat.completions.create(
                model=DEF_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": json.dumps(user)}
                ],
                max_tokens=120,
                temperature=0.4,
            )
            text = resp.choices[0].message.content.strip()
        except Exception as e:
            # Robust fallback (rate-limit/quota/etc.)
            direction = "surge" if a.get("direction") == "surge" else "drop"
            arrow = "📈" if direction == "surge" else "📉"
            text = (f"{arrow} {a['domain'].capitalize()} anomaly detected (z={a['zscore']}). "
                    f"AI explanation temporarily unavailable: {e}")

        narrated.append({**a, "narration": text})

    return narrated

if __name__ == "__main__":
    # quick manual test (no output if no anomalies.json provided)
    test_anoms = []
    p = Path("data/anomalies.json")
    if p.exists():
        with p.open("r") as f:
            test_anoms = json.load(f)
    out = narrate_anomalies(test_anoms)
    print(json.dumps(out, indent=2))

