from src.mock_data import seed_mock_db


if __name__ == "__main__":
    path = seed_mock_db("transactions_mock.db")
    print(f"Created {path} with mock transaction data.")
