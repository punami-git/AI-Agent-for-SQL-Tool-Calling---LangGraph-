import sqlite3
from pathlib import Path


DDL = """
DROP TABLE IF EXISTS failed_transactions;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS counterparties;

CREATE TABLE counterparties (
    counterparty_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL
);

CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    amount REAL NOT NULL,
    txn_time TEXT NOT NULL,
    counterparty_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    category TEXT NOT NULL,
    FOREIGN KEY (counterparty_id) REFERENCES counterparties(counterparty_id)
);

CREATE TABLE failed_transactions (
    failure_id INTEGER PRIMARY KEY,
    transaction_id TEXT NOT NULL,
    fail_reason TEXT NOT NULL,
    retry_count INTEGER NOT NULL,
    last_retry_time TEXT,
    is_resolved INTEGER NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
);
"""


def seed_mock_db(db_path: str = "transactions_mock.db") -> Path:
    path = Path(db_path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript(DDL)

    counterparties = [
        (1, "Alpha Retail", "US"),
        (2, "BlueSky Foods", "US"),
        (3, "Core Logistics", "EU"),
        (4, "Delta Health", "US"),
        (5, "Echo Energy", "APAC"),
    ]

    transactions = [
        ("T1001", 980.0, "2026-02-20 10:00", 1, "SUCCESS", "CARD", "Office Supplies"),
        ("T1002", 11250.0, "2026-02-20 10:05", 2, "FAILED", "WIRE", "Vendor Payment"),
        ("T1003", 1200.0, "2026-02-20 10:10", 3, "SUCCESS", "ACH", "Shipping"),
        ("T1004", 15800.0, "2026-02-20 10:20", 4, "FAILED", "WIRE", "Equipment"),
        ("T1005", 7600.0, "2026-02-20 10:30", 5, "PENDING", "ACH", "Utilities"),
        ("T1006", 10500.0, "2026-02-20 10:35", 1, "SUCCESS", "WIRE", "Rent"),
        ("T1007", 300.0, "2026-02-20 10:40", 2, "SUCCESS", "CARD", "Travel"),
        ("T1008", 22000.0, "2026-02-20 10:45", 3, "FAILED", "WIRE", "Bulk Purchase"),
        ("T1009", 4500.0, "2026-02-20 10:55", 4, "SUCCESS", "ACH", "Insurance"),
        ("T1010", 13400.0, "2026-02-20 11:00", 5, "FAILED", "WIRE", "Consulting"),
        ("T1011", 870.0, "2026-02-20 11:05", 1, "SUCCESS", "CARD", "Meals"),
        ("T1012", 10100.0, "2026-02-20 11:10", 2, "PENDING", "ACH", "Payroll"),
    ]

    failed = [
        (1, "T1002", "Insufficient funds", 2, "2026-02-20 10:12", 0),
        (2, "T1004", "Account number mismatch", 1, "2026-02-20 10:28", 0),
        (3, "T1008", "Compliance hold", 3, "2026-02-20 10:57", 0),
        (4, "T1010", "Daily transfer limit exceeded", 2, "2026-02-20 11:14", 1),
    ]

    cur.executemany("INSERT INTO counterparties VALUES (?, ?, ?)", counterparties)
    cur.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?)", transactions)
    cur.executemany("INSERT INTO failed_transactions VALUES (?, ?, ?, ?, ?, ?)", failed)

    conn.commit()
    conn.close()
    return path


if __name__ == "__main__":
    db = seed_mock_db()
    print(f"Created {db} with mock transaction data.")
