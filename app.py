import os
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.mock_data import seed_mock_db
from src.sql_langgraph_agent import LangGraphSQLAgent

DB_PATH = Path("transactions_mock.db")
TABLES = ["transactions", "failed_transactions", "counterparties"]


def load_table(table_name: str) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)


@st.cache_resource
def get_agent() -> LangGraphSQLAgent:
    return LangGraphSQLAgent(db_path=str(DB_PATH))


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Manrope', sans-serif;
        }

        .stApp {
            background: radial-gradient(circle at 10% 10%, #f5fbff 0%, #f8fafc 40%, #eef2ff 100%);
        }

        .hero {
            background: linear-gradient(120deg, #0f172a 0%, #1e3a8a 45%, #0ea5e9 100%);
            color: white;
            border-radius: 18px;
            padding: 20px 24px;
            margin-bottom: 16px;
            box-shadow: 0 10px 30px rgba(30, 58, 138, 0.25);
        }

        .pill {
            display: inline-block;
            padding: 6px 10px;
            margin-right: 6px;
            border-radius: 999px;
            background: rgba(255,255,255,0.16);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.2px;
        }

        .section-card {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 14px;
            padding: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    st.sidebar.header("Configuration")
    st.sidebar.write("Model provider: Groq")
    st.sidebar.write("Framework: LangGraph + LangChain tools")
    key_exists = bool(os.environ.get("GROQ_API_KEY"))
    st.sidebar.write(f"GROQ_API_KEY loaded: {'Yes' if key_exists else 'No'}")


load_dotenv()
st.set_page_config(page_title="Natural Language to SQL Agent", layout="wide")
apply_styles()

if "GROQ_API_KEY" in st.secrets and not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# Always reseed on app boot so data schema stays predictable across deploys.
seed_mock_db(str(DB_PATH))

st.markdown(
    """
    <div class="hero">
      <div class="pill">SQL Tool Calling AI Agent</div>
      <div class="pill">Natural Language Querying</div>
      <h1 style="margin:10px 0 8px 0;">Natural Language to SQL</h1>
      <p style="margin:0; max-width:880px;">
        This is an AI Agent that calls an SQL tool. Ask a question below, it will convert your question into an SQL query,
        run it against the data, and return the resulting table. You can explore the mock data in the tables below.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)
render_sidebar()

if not os.environ.get("GROQ_API_KEY"):
    st.error("GROQ_API_KEY is not set. Add it as an environment variable (or Streamlit secrets).")
    st.stop()

transactions_df = load_table("transactions")
failed_count = int((transactions_df["status"] == "FAILED").sum())
over_10k_count = int((transactions_df["amount"] > 10000).sum())

col1, col2, col3 = st.columns(3)
col1.metric("Total Transactions", len(transactions_df))
col2.metric("Failed Transactions", failed_count)
col3.metric("Transactions > 10,000", over_10k_count)

st.subheader("Dataset")
with st.expander("View mock tables", expanded=True):
    selected = st.selectbox("Choose table", TABLES, index=0)
    st.dataframe(load_table(selected), use_container_width=True, height=330)

st.subheader("Ask in natural language")
example_questions = [
    "Show all failed transactions with reason and retry count.",
    "List transactions with amount greater than 10000.",
    "Count failed transactions by counterparty.",
    "Show average transaction amount by payment method.",
]
st.write("Try one of these:")
for ex in example_questions:
    st.code(ex)

question = st.text_area(
    "Enter your query",
    height=110,
    placeholder="e.g., list transactions with amount greater than 10000",
)
run = st.button("Run Query", type="primary")

if run:
    if not question.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Converting natural language to SQL and running query..."):
            agent = get_agent()
            try:
                result = agent.ask(question)
            except Exception as exc:
                st.exception(exc)
            else:
                st.markdown("### Generated SQL")
                st.code(result.sql or "No SQL generated.", language="sql")

                st.markdown("### Result Table")
                df = pd.DataFrame(result.rows)
                if df.empty:
                    st.info("Query ran but returned no rows.")
                else:
                    st.dataframe(df, use_container_width=True, height=340)

                st.markdown("### Agent Summary")
                st.write(result.final_answer)
