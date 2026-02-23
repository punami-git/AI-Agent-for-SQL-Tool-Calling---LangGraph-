import sqlite3


def main() -> None:
    conn = sqlite3.connect("sample.db")
    cur = conn.cursor()

    cur.executescript(
        """
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            order_date TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
        """
    )

    customers = [
        (1, "Ava", "Austin", "2025-01-05"),
        (2, "Noah", "Seattle", "2025-01-10"),
        (3, "Mia", "Austin", "2025-01-22"),
    ]
    orders = [
        (1, 1, 120.50, "paid", "2025-02-01"),
        (2, 1, 85.00, "paid", "2025-02-10"),
        (3, 2, 43.25, "pending", "2025-02-12"),
        (4, 3, 220.00, "paid", "2025-02-15"),
    ]

    cur.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", customers)
    cur.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders)

    conn.commit()
    conn.close()
    print("Created sample.db with customers and orders tables.")


if __name__ == "__main__":
    main()
