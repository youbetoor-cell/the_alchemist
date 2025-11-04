from pathlib import Path
import json, os, httpx
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


# Paths
DATA = Path("data")
DATA.mkdir(exist_ok=True)
SUMMARY = DATA / "summary.json"
INSIGHT_LOG = DATA / "insight_log.json"

def main():
    if not SUMMARY.exists():
        print("⚠️ No summary.json found. Skipping insight generation.")
        return

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("⚠️ No OPENAI_API_KEY set in environment. Skipping insight generation.")
        return

    summary = json.loads(SUMMARY.read_text())
    details = summary.get("details", [])
    if not details:
        print("⚠️ No details in summary.json. Skipping.")
        return

    client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=True))
    prompt = (
        "You are The Alchemist AI. Given domain scores and summaries, produce a short daily commentary "
        "(2 bullets max) noting correlations or divergences and one actionable hint. Keep under 60 words.\n\n"
        f"DATA: {details}"
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Write concise, insightful market commentary."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=120,
            temperature=0.4
        )
        text = resp.choices[0].message.content.strip()
    except Exception as e:
        text = f"(Insight generation failed: {e})"

    entry = {"timestamp": datetime.utcnow().isoformat(), "text": text}
    if INSIGHT_LOG.exists():
        try:
            log = json.loads(INSIGHT_LOG.read_text())
            if not isinstance(log, list):
                log = []
        except Exception:
            log = []
    else:
        log = []

    log.append(entry)
    log = log[-200:]  # keep last 200 entries
    INSIGHT_LOG.write_text(json.dumps(log, indent=2))
    print("✅ Insight appended:", text)

if __name__ == "__main__":
    main()

