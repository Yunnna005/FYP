import pandas as pd

df = pd.read_csv("FYP/Data/Plaid Dataset/transactions2.csv")

normalized = pd.DataFrame({
    "transaction_id": df["transaction_id"],
    "account_id": df["account_id"],
    "category_id": df["category"],
    "date": pd.to_datetime(df["date"], format="%d/%m/%Y"),
    "merchant_name": df["merchant_name"],
    "description": df["name"],
    "amount": df["amount"].astype(float),
    "currency_code": "USD",
    "payment_channel": df["payment_channel"],
    "pending": df["pending"].astype(bool),
})

normalized.to_csv("normalized_transactions2.csv", index=False)

