import pandas as pd
import uuid

df = pd.read_csv("FYP/Data/Other Dataset/spending_patterns_detailed.csv")

normalized = pd.DataFrame({
    "transaction_id": [str(uuid.uuid4()) for _ in range(len(df))],
    "account_id": df["Customer_ID"].astype(str),
    "category_id": df["Category"].fillna("none"),
    "date": pd.to_datetime(df["Transaction Date"], format="%d/%m/%Y"),
    "merchant_name": df["Location"],
    "description": df["Item"],
    "amount": df["Total Spent"].astype(float),
    "currency_code": "USD",
    "payment_channel": df["Payment Method"],
    "pending": False,
})

normalized.to_csv("normalized_transactions3.csv", index=False)