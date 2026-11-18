import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import requests

load_dotenv()

TARGET_DATE = datetime.now().strftime("%Y-%m-%d")
DATA_DIR = os.path.join("data", "raw")

def fetch_fx_rates(date_str: str) -> dict:
    url = f"https://api.frankfurter.dev/v1/{date_str}?base=EUR"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("rates", {})
    except Exception as e:
        print(f"[Warning] Could not fetch live FX rates for {date_str}: {e}. Using fallback rates.")
        return {"USD": 1.08, "GBP": 0.85, "CAD": 1.47, "AUD": 1.65}

def generate_mock_payments(num_records: int = 1000) -> pd.DataFrame:
    currencies = ["EUR", "USD", "GBP", "CAD", "AUD"]
    gateways = ["stripe_eu", "adyen_global", "checkout_com"]
    card_networks = ["visa", "mastercard", "amex", "discover"]
    statuses = ["succeeded", "failed", "refunded", "disputed"]
    decline_reasons = [None, "insufficient_funds", "do_not_honor", "expired_card", "fraudulent"]

    records = []
    start_time = datetime.utcnow() - timedelta(hours=24)

    for i in range(num_records):
        currency = random.choices(currencies, weights=[0.4, 0.3, 0.15, 0.1, 0.05])[0]
        amount = round(random.lognormvariate(4.0, 0.8), 2)
        status = random.choices(statuses, weights=[0.75, 0.15, 0.07, 0.03])[0]
        decline_reason = random.choice(decline_reasons[1:]) if status == "failed" else None
        fee = round((amount * 0.015) + 0.25, 2)

        record = {
            "payment_id": f"pay_{random.randint(10000000, 99999999)}",
            "customer_id": f"cust_{random.randint(1000, 9999)}",
            "merchant_id": f"merch_{random.randint(100, 150)}",
            "gateway": random.choice(gateways),
            "amount": amount,
            "currency": currency,
            "processor_fee": fee,
            "status": status,
            "decline_reason": decline_reason,
            "card_network": random.choice(card_networks),
            "issuing_country": random.choice(["FI", "DE", "GB", "US", "SE", "FR"]),
            "created_at": (start_time + timedelta(seconds=random.randint(0, 86400))).isoformat(),
            "dt": TARGET_DATE,
        }
        records.append(record)

    return pd.DataFrame(records)

def main():
    print(f"🚀 Starting PayOps ingestion pipeline for execution date: {TARGET_DATE}...")
    
    print("🌐 Fetching currency exchange rates from Frankfurter API...")
    fx_rates = fetch_fx_rates(TARGET_DATE)
    fx_df = pd.DataFrame([
        {"base": "EUR", "target_currency": k, "rate": v, "dt": TARGET_DATE}
        for k, v in fx_rates.items()
    ])

    print("💳 Generating synthetic payment transactions...")
    payments_df = generate_mock_payments(1000)

    fx_output_dir = os.path.join(DATA_DIR, "exchange_rates", f"dt={TARGET_DATE}")
    payments_output_dir = os.path.join(DATA_DIR, "transactions", f"dt={TARGET_DATE}")

    os.makedirs(fx_output_dir, exist_ok=True)
    os.makedirs(payments_output_dir, exist_ok=True)

    fx_file_path = os.path.join(fx_output_dir, "rates.parquet")
    payments_file_path = os.path.join(payments_output_dir, "transactions.parquet")

    fx_df.to_parquet(fx_file_path, index=False)
    payments_df.to_parquet(payments_file_path, index=False)

    print(f"✅ Saved FX rates to: {fx_file_path}")
    print(f"✅ Saved 1,000 payment records to: {payments_file_path}")
    print("🎉 Ingestion batch completed successfully!")

if __name__ == "__main__":
    main()
