#!/bin/bash
# ============================================================
# ⚗️ The Alchemist — Automated Daily Runner Script (local)
# ============================================================

set -e  # stop if any command fails

# Move to project directory
cd "$(dirname "$0")"

# Activate the virtual environment
source venv/bin/activate

# Step 1️⃣ — Run the core dashboard once
echo "🚀 Running The Alchemist (single daily run)..."
python app.py --once | tee -a data/daily_run.log

# Step 2️⃣ — Update long-term AI memory
echo "🧠 Updating memory file..."
python scripts/update_memory.py | tee -a data/daily_run.log

# Step 3️⃣ — Completion timestamp
echo "✅ Completed at $(date -u +"%Y-%m-%d %H:%M UTC")"
