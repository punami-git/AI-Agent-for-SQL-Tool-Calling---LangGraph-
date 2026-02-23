# Streamlit App
https://ai-agent-for-sql.streamlit.app/


# Natural Language to SQL Agent (LangGraph + LangChain + Groq)

- Simple mock transaction data in SQLite
- Natural-language query input
- LangGraph agent with SQL tool calling (`get_schema`, `run_sql`)
- SQL execution and table rendering in Streamlit

## Tech Stack
- LangGraph + LangChain tools
- Groq LLM
- Tool Calling
- SQLite for mock data
- Streamlit frontend


## What the App Does
1. Shows mock tables (`transactions`, `failed_transactions`, `counterparties`)
2. Accepts a natural-language question
3. Agent calls SQL tools via LangGraph
4. Executes read-only SQL on SQLite
5. Displays generated SQL + result table + summary


## Suggested Demo Questions
- "Show all failed transactions with reason and retry count."
- "List transactions with amount greater than 10000."
- "Count failed transactions by counterparty."
- "Show average transaction amount by payment method."
