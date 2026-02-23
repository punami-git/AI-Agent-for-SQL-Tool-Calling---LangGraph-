import argparse
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


DISALLOWED_SQL_PATTERNS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bCREATE\b",
    r"\bATTACH\b",
    r"\bDETACH\b",
    r"\bPRAGMA\b",
]


@dataclass
class QueryResult:
    sql: str
    rows: list[dict[str, Any]]


class TextToSQLAgent:
    def __init__(self, db_path: str, model: str = "llama-3.3-70b-versatile") -> None:
        self.db_path = db_path
        self.model = model
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY is not set.")
        self.client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _schema_context(self) -> str:
        with self._connect() as conn:
            table_rows = conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            ).fetchall()

            if not table_rows:
                return "No tables found in database."

            lines: list[str] = []
            for row in table_rows:
                table_name = row["name"]
                columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
                cols = ", ".join(
                    f"{c['name']} {c['type'] or 'TEXT'}"
                    + (" PRIMARY KEY" if c["pk"] else "")
                    for c in columns
                )
                lines.append(f"- {table_name}({cols})")
            return "\n".join(lines)

    @staticmethod
    def _extract_sql(text: str) -> str:
        fenced = re.search(r"```sql\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
        if fenced:
            return fenced.group(1).strip()

        generic_fenced = re.search(r"```\s*(.*?)```", text, flags=re.DOTALL)
        if generic_fenced:
            return generic_fenced.group(1).strip()

        return text.strip()

    @staticmethod
    def _validate_read_only(sql: str) -> None:
        normalized = sql.strip()
        if not normalized:
            raise ValueError("Model did not return SQL.")

        if normalized.count(";") > 1 or (";" in normalized and not normalized.endswith(";")):
            raise ValueError("Only a single SQL statement is allowed.")

        head = normalized.lstrip("(").upper()
        if not (head.startswith("SELECT") or head.startswith("WITH")):
            raise ValueError("Only SELECT/WITH queries are allowed.")

        for pattern in DISALLOWED_SQL_PATTERNS:
            if re.search(pattern, normalized, flags=re.IGNORECASE):
                raise ValueError("Unsafe SQL detected. Read-only queries only.")

    def _generate_sql(self, question: str) -> str:
        schema = self._schema_context()

        system_prompt = (
            "You are a senior data analyst. Convert user questions to SQLite SQL. "
            "Return only one SQL query and nothing else. "
            "Use only tables/columns from the schema. "
            "Prefer explicit column names. "
            "If impossible, return: SELECT 'INSUFFICIENT_SCHEMA' AS error;"
        )

        user_prompt = (
            f"Schema:\n{schema}\n\n"
            f"User question:\n{question}\n\n"
            "Return only SQL."
        )

        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        sql = self._extract_sql(response.output_text)
        self._validate_read_only(sql)
        return sql.rstrip(";")

    def run(self, question: str) -> QueryResult:
        sql = self._generate_sql(question)
        with self._connect() as conn:
            rows = conn.execute(sql).fetchall()
            payload = [dict(row) for row in rows]
        return QueryResult(sql=sql, rows=payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Natural-language to SQL agent")
    parser.add_argument("--db", required=True, help="Path to SQLite database")
    parser.add_argument("--question", required=True, help="Natural language question")
    parser.add_argument(
        "--model",
        default="llama-3.3-70b-versatile",
        help="Groq model name (default: llama-3.3-70b-versatile)",
    )
    return parser


def main() -> None:
    load_dotenv()
    args = build_parser().parse_args()

    if not os.path.exists(args.db):
        raise FileNotFoundError(f"Database not found: {args.db}")

    agent = TextToSQLAgent(db_path=args.db, model=args.model)
    result = agent.run(args.question)

    print("Generated SQL:")
    print(result.sql)
    print("\nRows:")
    print(json.dumps(result.rows, indent=2, default=str))


if __name__ == "__main__":
    main()
