# scripts/ask_alchemist.py
from pathlib import Path
import json, sys, os, httpx
from openai import OpenAI

MEMORY = Path("data/memory.json")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/ask_alchemist.py \"your question here\"")
        return

    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("❌ Empty question.")
        return

    if not MEMORY.exists():
        print("⚠️ No memory file found — run your daily process first.")
        return

    try:
        data = json.loads(MEMORY.read_text())
        entries = data.get("entries", [])[-10:]
        if not entries:
            print("⚠️ Memory file is empty.")
            return

        context = json.dumps(entries, indent=2)
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""), http_client=httpx.Client(verify=True))

        prompt = (
            "You are The Alchemist. Use this past memory data to answer:\n"
            f"{context}\n\n"
            f"Question: {question}"
        )

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.5
        )

        print("\n🧠 The Alchemist says:")
        print(resp.choices[0].message.content.strip())

    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    main()
