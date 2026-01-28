import pandas as pd
import uuid

df = pd.read_csv("FYP/Data/Real_Dataset/Transactions_Adrian.csv")

normalized = pd.DataFrame({
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

normalized.to_csv("normalized_transactions4.csv", index=False)