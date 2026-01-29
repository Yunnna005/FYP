from faker import Faker
import pandas as pd
from pathlib import Path

DATA_DIR_TRANSACTIONS = Path("/workspaces/python/FYP/Data/Plaid_Dataset/Transactions/Raw_csv")
DATA_DIR_ACCOUNTS = Path("/workspaces/python/FYP/Data/Plaid_Dataset/Accounts/Raw")

OUT_TRANSACTIONS = Path("/workspaces/python/FYP/Data/Plaid_Dataset/Transactions/Normalized")
OUT_ACCOUNTS = Path("/workspaces/python/FYP/Data/Plaid_Dataset/Accounts/Normalized")

fake = Faker()

def normalized_transactions(df):
    return pd.DataFrame({
        "transaction_id": df["transaction_id"],
        "account_id": df["account_id"],
        "category_id": df["category"],
        "date": pd.to_datetime(df["date"], format="%d/%m/%Y"),
        "merchant_name": df["merchant_name"],
        "description": df["name"],
        "amount": df["amount"].astype(float),
        "currency_code": "USD",
        "payment_channel": df["payment_channel"],
        "pending": df["pending"].astype(bool)
    })

def normalized_accounts(df):
    return pd.DataFrame({
        "account_id": df["account_id"].unique(),
        "user_id": [fake.bothify("USR###??") for _ in range(len(df))],
        "name": df["name"].astype(str),
        "type": df["subtype"] + " " + df["type"],
        "mask": df["mask"].astype(str),
        "balances_current": df["balances_current"].astype(float),
        "balances_available": df["balances_available"].astype(float),
        "currency_code": df["iso_currency_code"].astype(str),
    })

normalized_frames = []
normalized_frames2 = []

for file in DATA_DIR_TRANSACTIONS.glob("transaction*.csv"):
    df = pd.read_csv(file)
    normalized = normalized_transactions(df)
    normalized_frames.append(normalized)

for file in DATA_DIR_ACCOUNTS.glob("accounts*.csv"):
    df = pd.read_csv(file)
    normalizedAccounts = normalized_accounts(df)
    normalized_frames2.append(normalizedAccounts)

final_df = pd.concat(normalized_frames, ignore_index=True)
final_df2 = pd.concat(normalized_frames2, ignore_index=True)

final_df = final_df.dropna(subset=["transaction_id", "account_id", "amount", "date"])
final_df2 = final_df2.dropna(subset=["account_id", "account_id"])

final_df = final_df.sort_values("date")

final_df.to_csv(OUT_TRANSACTIONS / "normalized_transactions.csv", index=False)
final_df2.to_csv(OUT_ACCOUNTS / "normalized_accounts.csv", index=False)