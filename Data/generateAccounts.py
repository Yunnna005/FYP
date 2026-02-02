import csv
import random
import pandas as pd
from pathlib import Path
from faker import Faker

fake = Faker()

DATA_DIR_OTHERDATA = Path("/workspaces/python/FYP/Data/Other_Dataset/Transactions/Normalized/normalized_transactions.csv")
DATA_DIR_REALDATA = Path("/workspaces/python/FYP/Data/Real_Dataset/Transactions/Normalized/normalized_transactions.csv")

OUT_OTHER = "generated_accounts.csv"
OUT_REAL = "generated_accounts.csv"

OUT_DIR_OTHER = "/workspaces/python/FYP/Data/Other_Dataset/Accounts"
OUT_DIR_REAL = "/workspaces/python/FYP/Data/Real_Dataset/Accounts"

ACCOUNT_TYPES = [
    "Checking",
    "Savings"
]

def generate_accounts(input_file, output_dir):
    df = pd.read_csv(input_file, usecols=["account_id"])

    rows = []
    for account_id in df["account_id"].unique():
        balance = round(random.uniform(100.0, 10000.0), 2)

        rows.append(
            {
                "account_id": account_id,
                "user_id": fake.bothify("USR###??"),
                "name": fake.credit_card_provider(),
                "type": random.choice(ACCOUNT_TYPES),
                "mask": fake.bothify("####"),
                "balances_current": balance,
                "balances_available": balance,
                "currency_code": df["currency_code"].iloc[0] if "currency_code" in df.columns else "USD",
            }
        )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "generated_accounts.csv"
    pd.DataFrame(rows).to_csv(output_path, index=False)

generate_accounts(DATA_DIR_OTHERDATA, OUT_DIR_OTHER)
generate_accounts(DATA_DIR_REALDATA, OUT_DIR_REAL)