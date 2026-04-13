import pandas as pd
import uuid


def _read_aib_file(file_path: str) -> pd.DataFrame:
    """AIB exports come in two formats: real CSV, or HTML table with .csv.html extension."""
    with open(file_path, "rb") as f:
        head = f.read(512).lstrip().lower()

    if head.startswith(b"<") or b"<html" in head or b"<table" in head:
        tables = pd.read_html(file_path)
        if not tables:
            raise ValueError("No tables found in AIB HTML export")
        df = tables[0]
    else:
        df = pd.read_csv(file_path, skipinitialspace=True)

    # Normalize column names: strip whitespace, lowercase, replace spaces with underscores
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def normalize_revolut(file_path: str, account_id: str):
    df = pd.read_csv(file_path)
    normalized = pd.DataFrame({
        "transaction_id": [str(uuid.uuid4()) for _ in range(len(df))],
        "account_id": account_id,
        "category_id": "none",
        "date": pd.to_datetime(df["Completed Date"], format="mixed", dayfirst=True).dt.date,
        "merchant_name": df["Description"],
        "description": "none",
        "amount": df["Amount"].astype(float),
        "currency_code": df["Currency"],
        "payment_channel": "none",
        "pending": df["State"].str.lower().ne("completed"),
    })
    normalized = normalized.dropna(subset=["transaction_id", "account_id", "amount", "date"])
    normalized = normalized.sort_values("date").reset_index(drop=True)

    last_balance = float(df["Balance"].iloc[-1]) if "Balance" in df.columns and not df["Balance"].isna().all() else float(df["Amount"].sum())
    currency = df["Currency"].iloc[0] if "Currency" in df.columns and len(df) > 0 else "EUR"

    return normalized, {"balance": last_balance, "currency": currency}


def normalize_aib(file_path: str, account_id: str):
    df = _read_aib_file(file_path)

    df["debit_amount"] = pd.to_numeric(df.get("debit_amount"), errors="coerce")
    df["credit_amount"] = pd.to_numeric(df.get("credit_amount"), errors="coerce")
    df["amount"] = df["debit_amount"].fillna(0) * -1 + df["credit_amount"].fillna(0)

    normalized = pd.DataFrame({
        "transaction_id": [str(uuid.uuid4()) for _ in range(len(df))],
        "account_id": account_id,
        "category_id": "none",
        "date": pd.to_datetime(df["posted_transactions_date"], format="mixed", dayfirst=True).dt.strftime("%Y-%m-%d"),
        "merchant_name": df["description"],
        "description": "none",
        "amount": df["amount"].astype(float),
        "currency_code": "EUR",  # AIB exports don't include currency, default to EUR
        "payment_channel": "none",
        "pending": False,
    })
    normalized = normalized.dropna(subset=["transaction_id", "account_id", "amount", "date"])
    normalized = normalized.sort_values("date").reset_index(drop=True)

    # Balance: take the last non-null balance, or fall back to sum of transactions
    if "balance" in df.columns:
        balances = pd.to_numeric(df["balance"], errors="coerce").dropna()
        last_balance = float(balances.iloc[-1]) if not balances.empty else float(normalized["amount"].sum())
    else:
        last_balance = float(normalized["amount"].sum())

    return normalized, {"balance": last_balance, "currency": "EUR"}


def normalize_csv(file_path: str, bank: str, account_id: str):
    if bank == "revolut":
        return normalize_revolut(file_path, account_id)
    elif bank == "aib":
        return normalize_aib(file_path, account_id)
    else:
        raise ValueError(f"Unknown bank: {bank}")