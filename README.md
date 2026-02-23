# Natural Language to SQL Agent (LangGraph + Groq + Streamlit)

- Simple mock transaction data in SQLite
- Natural-language query input
- LangGraph agent with SQL tool calling (`get_schema`, `run_sql`)
- SQL execution and table rendering in Streamlit

## Tech Stack
- LangGraph + LangChain tools
- Groq LLM (`GROQ_API_KEY`)
- SQLite for mock data
- Streamlit frontend

## Local Run

```bash
cd "/Users/punamichowdary/Documents/New project"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY="your_groq_key"
python scripts/seed_mock_db.py
streamlit run app.py
```

## What the App Does
1. Shows mock tables (`transactions`, `failed_transactions`, `counterparties`)
2. Accepts a natural-language question
3. Agent calls SQL tools via LangGraph
4. Executes read-only SQL on SQLite
5. Displays generated SQL + result table + summary

## Deploy and Share a Link
1. Push this repo to GitHub.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Create a new app from your repo with entrypoint: `app.py`.
4. In app settings, add secret:
   - `GROQ_API_KEY = "your_groq_key"`
5. Deploy and share the app URL.

## Suggested Demo Questions
- "Show all failed transactions with reason and retry count."
- "List transactions with amount greater than 10000."
- "Count failed transactions by counterparty."
- "Show average transaction amount by payment method."
