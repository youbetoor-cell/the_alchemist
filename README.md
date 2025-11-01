# The Alchemist - Multi-Agent MVP (Starter)

Branded 'The Alchemist' — Manager AI that coordinates six domain agents.

## Quick start

1. Unzip and open the project folder.
2. Create and activate a virtualenv.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run: `python main.py` to generate mock reports.
5. Run: `streamlit run dashboard/app.py` to view the dashboard.

## Notes
- Agents currently use mock data. Replace `fetch_data()` with real API calls.
- To use OpenAI for summaries, set `OPENAI_API_KEY` env var and update `utils/openai_client.py`.
