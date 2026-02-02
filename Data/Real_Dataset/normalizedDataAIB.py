import pandas as pd
from pathlib import Path
import uuid

DATA_DIR = Path("/workspaces/python/FYP/Data/Real_Dataset/Transactions/Raw")

OUT_TRANSACTIONS = Path("/workspaces/python/FYP/Data/Real_Dataset/Transactions/Normalized")

def normalize_dataset(df):
    df["debit_amount"] = pd.to_numeric(df["debit_amount"], errors="coerce")
    df["credit_amount"] = pd.to_numeric(df["credit_amount"], errors="coerce")
    df["amount"] = df["debit_amount"].fillna(0) * -1 + df["credit_amount"].fillna(0)
    return pd.DataFrame({
        "transaction_id": [str(uuid.uuid4()) for _ in range(len(df))],
        "account_id": df["posted_account"].astype(str),
        "category_id": "none",
        "date": pd.to_datetime(df["posted_transactions_date"], format="mixed", dayfirst=True).dt.strftime("%Y-%m-%d"),
        "merchant_name": df["description1"],
        "description": df["description2"].fillna("none"),
        "amount": df["amount"].astype(float),
        "currency_code": df["posted_currency"],
        "payment_channel": "none",
        "pending": False
    })

normalized_frames = []

for file in DATA_DIR.glob("Transactions_*.csv"):
    df = pd.read_csv(file)
    normalized = normalize_dataset(df)
    normalized_frames.append(normalized)

final_df = pd.concat(normalized_frames, ignore_index=True)

final_df = final_df.dropna(subset=["transaction_id", "account_id", "amount", "date"])

final_df = final_df.sort_values("date")

final_df.to_csv(OUT_TRANSACTIONS / "normalized_transactions.csv", index=False)