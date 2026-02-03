import random
import pandas as pd
from pathlib import Path

DATA_FILE = Path("/workspaces/python/FYP/Data/Final/transactions_noneValues.csv")
OUT_DIR = Path("/workspaces/python/FYP/Data/Final")
OUT_FILE = "transactions.csv"

invalid_payment_values = [
    None,
    "none",
    "Debit Card",
    "Digital Wallet",
    "Credit Card",
    "Cash"
]

valid_payment_values = ["online", "in store", "other"]

def fix_payment_channel(value):
    if pd.isna(value) or value in invalid_payment_values:
        return random.choice(valid_payment_values)
    return value

df = pd.read_csv(DATA_FILE, dtype=str)

df["description"] = df["description"].astype(str).str.strip().str.lower()
df["description"] = df["description"].replace("none", "no description")

df["payment_channel"] = df["payment_channel"].apply(fix_payment_channel)

OUT_DIR.mkdir(parents=True, exist_ok=True)
output_path = OUT_DIR / OUT_FILE
df.to_csv(output_path, index=False)
