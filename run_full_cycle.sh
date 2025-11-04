#!/bin/bash
# ============================================================
# ⚗️ The Alchemist — Full Daily Automation Cycle
# ============================================================

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# 1) Pull fresh
git pull --rebase || true

# 2) One cycle of data + memory + correlation + alerts
python app.py

# 3) Send the HTML email digest
python scripts/email_digest.py

# 4) Commit artifacts (optional)
git add data/*.json || true
git commit -m "Daily auto-update: insights & memory" || true
git push || true


cd ~/Downloads/the_alchemist || exit
source venv/bin/activate

echo "🧠 Running The Alchemist intelligence cycle..."
python app.py

echo "🌐 Starting Gradio dashboard..."
nohup python dashboard_gradio.py > logs_dashboard.txt 2>&1 &

sleep 10
echo "📧 Sending daily report + pushing GitHub backup..."
python scripts/report_and_backup.py

echo "✅ Cycle complete. Sleeping 24h..."
sleep 86400
