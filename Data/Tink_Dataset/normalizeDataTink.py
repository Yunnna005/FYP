import pandas as pd
from pathlib import Path

DATA_DIR = Path("FYP/Data/Tink Dataset")

def normalize_dataset(df):
    return pd.DataFrame({
        "transaction_id": df["id"].astype(str),
        "account_id": df["accountId"].astype(str),
        "category_id": "none",
        "date": pd.to_datetime(df["date"]),
        "merchant_name": df["description"],
        "description": "none" ,
        "amount": df["amount"].astype(float),
        "currency_code": df["currency"],
        "payment_channel": "online",
        "pending": False
    })

normalized_frames = []

for file in DATA_DIR.glob("transactions_*.csv"):
    df = pd.read_csv(file)
    normalized = normalize_dataset(df)
    normalized_frames.append(normalized)

final_df = pd.concat(normalized_frames, ignore_index=True)

final_df = final_df.dropna(
    subset=["transaction_id", "account_id", "amount", "date"]
)

final_df = final_df.sort_values("date")

final_df.to_csv("all_normalized_transactions.csv", index=False)