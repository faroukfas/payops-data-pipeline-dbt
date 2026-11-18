import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine

load_dotenv()

# Explicitly using psycopg2 driver for SQLAlchemy
DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/payops_db")
DATA_DIR = os.path.join("data", "raw")

def main():
    print("🔌 Connecting to PostgreSQL database...")
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Tip: Make sure PostgreSQL is running and you have created a database named 'payops_db'.")
        return

    transactions_path = os.path.join(DATA_DIR, "transactions")
    fx_path = os.path.join(DATA_DIR, "exchange_rates")

    if not os.path.exists(transactions_path):
        print("❌ No raw data found. Run python src/ingest.py first!")
        return

    latest_dt_folder = sorted(os.listdir(transactions_path))[-1]
    
    tx_file = os.path.join(transactions_path, latest_dt_folder, "transactions.parquet")
    fx_file = os.path.join(fx_path, latest_dt_folder, "rates.parquet")

    print(f"📂 Loading data from partition: {latest_dt_folder}...")

    tx_df = pd.read_parquet(tx_file)
    fx_df = pd.read_parquet(fx_file)

    print(f"📥 Loading {len(tx_df)} transaction rows into PostgreSQL 'raw_payments'...")
    tx_df.to_sql("raw_payments", engine, schema="public", if_exists="append", index=False)

    print(f"📥 Loading {len(fx_df)} exchange rate rows into PostgreSQL 'raw_exchange_rates'...")
    fx_df.to_sql("raw_exchange_rates", engine, schema="public", if_exists="append", index=False)

    print("🎉 Data successfully loaded into PostgreSQL!")

if __name__ == "__main__":
    main()
