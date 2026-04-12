import pandas as pd
import uuid


def normalize_revolut(file_path: str, account_id: str) -> pd.DataFrame:
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

    # Derive account-level info from CSV
    last_balance = float(df["Balance"].iloc[-1]) if "Balance" in df.columns and not df["Balance"].isna().all() else float(df["Amount"].sum())
    currency = df["Currency"].iloc[0] if "Currency" in df.columns and len(df) > 0 else "EUR"

    return normalized, {"balance": last_balance, "currency": currency}


def normalize_aib(file_path: str, account_id: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df["debit_amount"] = pd.to_numeric(df["debit_amount"], errors="coerce")
    df["credit_amount"] = pd.to_numeric(df["credit_amount"], errors="coerce")
    df["amount"] = df["debit_amount"].fillna(0) * -1 + df["credit_amount"].fillna(0)

    normalized = pd.DataFrame({
        "transaction_id": [str(uuid.uuid4()) for _ in range(len(df))],
        "account_id": account_id,  # generated, not from CSV
        "category_id": "none",
        "date": pd.to_datetime(df["posted_transactions_date"], format="mixed", dayfirst=True).dt.strftime("%Y-%m-%d"),
        "merchant_name": df["description1"],
        "description": df["description2"].fillna("none"),
        "amount": df["amount"].astype(float),
        "currency_code": df["posted_currency"],
        "payment_channel": "none",
        "pending": False,
    })
    normalized = normalized.dropna(subset=["transaction_id", "account_id", "amount", "date"])
    normalized = normalized.sort_values("date").reset_index(drop=True)

    # Derive account-level info from CSV
    last_balance = float(df["balance"].iloc[-1]) if "balance" in df.columns and not df["balance"].isna().all() else float(df["amount"].sum())
    currency = df["posted_currency"].iloc[0] if "posted_currency" in df.columns and len(df) > 0 else "EUR"

    return normalized, {"balance": last_balance, "currency": currency}


def normalize_csv(file_path: str, bank: str, account_id: str):
    if bank == "revolut":
        return normalize_revolut(file_path, account_id)
    elif bank == "aib":
        return normalize_aib(file_path, account_id)
    else:
        raise ValueError(f"Unknown bank: {bank}")