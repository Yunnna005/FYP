from pathlib import Path
import pandas as pd
import uuid

df = pd.read_csv("/workspaces/python/FYP/Data/Other_Dataset/Raw/spending_patterns_detailed.csv")

OUT_TRANSACTIONS = Path("/workspaces/python/FYP/Data/Other_Dataset/Normalized")

normalizedTransactions = pd.DataFrame({
    "transaction_id": [str(uuid.uuid4()) for _ in range(len(df))],
    "account_id": df["Customer_ID"].astype(str),
    "category_id": df["Category"].fillna("none"),
    "date": pd.to_datetime(df["Transaction Date"], format="%d/%m/%Y", errors='coerce'),
    "merchant_name": df["Location"].fillna("Unknown Merchant"),
    "description": df["Item"],
    "amount": df["Total Spent"].astype(float),
    "currency_code": "USD",
    "payment_channel": df["Payment Method"],
    "pending": False,
})

normalizedTransactions.to_csv(OUT_TRANSACTIONS / "normalized_transactions.csv", index=False)