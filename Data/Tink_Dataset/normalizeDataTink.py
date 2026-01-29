from faker import Faker
import pandas as pd
from pathlib import Path

DATA_DIR_TRANSACTIONS = Path("/workspaces/python/FYP/Data/Tink_Dataset/Transactions/Raw")
DATA_DIR_ACCOUNTS = Path("/workspaces/python/FYP/Data/Tink_Dataset/Accounts/Raw")

OUT_TRANSACTIONS = Path("/workspaces/python/FYP/Data/Tink_Dataset/Transactions/Normalized")
OUT_ACCOUNTS = Path("/workspaces/python/FYP/Data/Tink_Dataset/Accounts/Normalized")

fake = Faker()

def normalize_transactions(df):
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

def normalized_accounts(df):
    return pd.DataFrame({
        "account_id": df["id"].unique(),
        "user_id": [fake.bothify("USR###??") for _ in range(len(df))],
        "name": df["name"].astype(str),
        "type": df["type"],
        "mask": fake.bothify("####"),
        "balances_current": df["balance"].astype(float),
        "balances_available": df["balance"].astype(float),
        "currency_code": df["currency"].astype(str),
    })

normalized_frames = []
normalized_frames2 = []

for file in DATA_DIR_TRANSACTIONS.glob("transactions_*.csv"):
    df = pd.read_csv(file)
    normalized = normalize_transactions(df)
    normalized_frames.append(normalized)

for file in DATA_DIR_ACCOUNTS.glob("accounts_*.csv"):
    df = pd.read_csv(file)
    normalized = normalized_accounts(df)
    normalized_frames2.append(normalized)

final_df = pd.concat(normalized_frames, ignore_index=True)
final_df2 = pd.concat(normalized_frames2, ignore_index=True)

final_df = final_df.dropna(subset=["transaction_id", "account_id", "amount", "date"])
final_df2 = final_df2.dropna(subset=["account_id", "user_id"])

final_df = final_df.sort_values("date")

final_df.to_csv(OUT_TRANSACTIONS / "normalized_transactions.csv", index=False)
final_df2.to_csv(OUT_ACCOUNTS / "normalized_accounts.csv", index=False)