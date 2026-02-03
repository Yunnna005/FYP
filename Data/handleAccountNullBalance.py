import pandas as pd
from pathlib import Path

DATA_FILE = Path("/workspaces/python/FYP/Data/Final/accounts_noneBalanceAvailable.csv")
OUT_DIR = Path("/workspaces/python/FYP/Data/Final")
OUT_FILE = "accounts.csv"

df = pd.read_csv(DATA_FILE, dtype=str)

df["balances_available"] = df["balances_available"].fillna(df["balances_current"])
df.loc[df["balances_available"].isna(), "balances_available"] = df["balances_current"]

OUT_DIR.mkdir(parents=True, exist_ok=True)
output_path = OUT_DIR / OUT_FILE
df.to_csv(output_path, index=False)
