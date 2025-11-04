# ============================================================
# ⚗️ The Alchemist — Daily Email + GitHub Backup System
# ============================================================
import os, json, smtplib, subprocess
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

DATA = Path("data")
MEMORY = DATA / "memory.json"
INSIGHT_LOG = DATA / "insight_log.json"
CORR_FILE = DATA / "correlation.json"

def build_html_report():
    memory = json.loads(MEMORY.read_text()) if MEMORY.exists() else []
    insights = json.loads(INSIGHT_LOG.read_text()) if INSIGHT_LOG.exists() else []
    corr = json.loads(CORR_FILE.read_text()) if CORR_FILE.exists() else {}

    latest = memory[-1] if memory else {}
    btc = latest.get("btc_price", "n/a")
    aapl = latest.get("aapl_price", "n/a")
    insight = insights[-1]["text"] if insights else "No insight yet."

    html = f"""
    <html>
      <body style="font-family:Arial; background:#0d1117; color:#e6edf3;">
        <h2>⚗️ The Alchemist — Daily AI Report</h2>
        <p>🕒 {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
        <p><b>BTC:</b> ${btc:,} | <b>AAPL:</b> ${aapl:,}</p>
        <p><b>Correlation:</b> {corr.get('corr', 'n/a')} | Regime: {corr.get('regime', 'n/a')}</p>
        <h3>🧠 Latest AI Insight</h3>
        <p>{insight}</p>
        <hr>
        <p>📊 Memory entries: {len(memory)}</p>
      </body>
    </html>
    """
    return html

def send_email():
    user = os.getenv("EMAIL_USER")
    pwd = os.getenv("EMAIL_PASS")
    to_addr = os.getenv("EMAIL_TO")
    if not all([user, pwd, to_addr]):
        print("⚠️ Missing email credentials.")
        return

    html = build_html_report()
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "The Alchemist — Daily Report"
    msg["From"] = user
    msg["To"] = to_addr
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(user, pwd)
            server.send_message(msg)
        print("📬 Email sent successfully.")
    except Exception as e:
        print("⚠️ Email failed:", e)

def github_backup():
    repo = os.getenv("GITHUB_REPO")
    branch = os.getenv("GITHUB_BRANCH", "main")
    if not repo:
        print("⚠️ No GitHub repo configured.")
        return
    try:
        subprocess.run(["git", "add", "data"], check=True)
        subprocess.run(["git", "commit", "-m", f"Auto backup {datetime.utcnow()}"], check=False)
        subprocess.run(["git", "push", repo, branch], check=False)
        print("💾 GitHub backup pushed.")
    except Exception as e:
        print("⚠️ GitHub backup failed:", e)

if __name__ == "__main__":
    send_email()
    github_backup()
