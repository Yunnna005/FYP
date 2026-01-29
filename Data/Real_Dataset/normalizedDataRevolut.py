import pandas as pd
import uuid
from pathlib import Path

DATA_DIR = Path("/workspaces/python/FYP/Data/Real_Dataset/Transactions/Raw")

OUT_TRANSACTIONS = Path("/workspaces/python/FYP/Data/Real_Dataset/Transactions/Normalized")

def normalize_transactions(df):
    return pd.DataFrame({
    "transaction_id": [str(uuid.uuid4()) for _ in range(len(df))],
    "account_id": "11111111",
    "category_id": "none",
    "date": pd.to_datetime(df["Completed Date"], format="mixed", dayfirst=True).dt.date,
    "merchant_name": df["Description"],
    "description": "none",
    "amount": df["Amount"].astype(float),
    "currency_code": df["Currency"],
    "payment_channel": "none",
    "pending": df["State"].str.lower().ne("complete"),
})

normalized_frames = []

for file in DATA_DIR.glob("Transactions_Revolut_*.csv"):
    df = pd.read_csv(file)
    normalized = normalize_transactions(df)
    normalized_frames.append(normalized)

final_df = pd.concat(normalized_frames, ignore_index=True)

final_df = final_df.dropna(subset=["transaction_id", "account_id", "amount", "date"])

final_df = final_df.sort_values("date")

final_df.to_csv(OUT_TRANSACTIONS / "normalized_transactions_revolut.csv", index=False)