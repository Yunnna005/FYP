import pandas as pd
import uuid

REVOLUT_TYPE_MAP = {
    "CARD PAYMENT": "card_payment",
    "CARD_PAYMENT": "card_payment",
    "CARD REFUND":  "refund",
    "CARD_REFUND":  "refund",
    "FEE":          "fee",
    "REWARD":       "reward",
    "TOPUP":        "topup",
    "TRANSFER":     "transfer",
    "EXCHANGE":     "exchange",
    "TEMP_BLOCK":   "pending",
}

INTERNAL_DESC_PATTERNS = [
    "savings vault",
    "saving vault",
    "prefunding wallet",
    "flexible cash",
    "flexible account",
    "to pocket",
    "from pocket",
    "pocket withdrawal",
    "investment account",
    "bold stack",
    "balanced bundle",
    "portfolio",
]

def read_revolut_file(file_path: str) -> pd.DataFrame:
    with open(file_path, "rb") as f:
        head = f.read(8)
    if head.startswith(b"PK") or head.startswith(b"\xd0\xcf\x11\xe0"):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
    df.columns = [c.strip() for c in df.columns] 
    return df

def classify_revolut_type(row) -> str:
    raw_type = str(row.get("Type", "")).upper().strip()
    base_class = REVOLUT_TYPE_MAP.get(raw_type, "unknown")

    if base_class in ("card_payment", "refund", "fee"):
        return base_class

    desc = str(row.get("Description", "")).lower()
    if any(pattern in desc for pattern in INTERNAL_DESC_PATTERNS):
        return "internal_transfer"

    if base_class == "transfer":
        return "transfer"  

    if base_class == "topup":
        return "topup"

    return base_class

def normalize_revolut(file_path: str, account_id: str):
    df = read_revolut_file(file_path)

    transaction_classes = df.apply(classify_revolut_type, axis=1)

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
        "transaction_class": transaction_classes,
    })
    normalized = normalized.dropna(subset=["transaction_id", "account_id", "amount", "date"])
    normalized = normalized.sort_values("date").reset_index(drop=True)

    last_balance = float(df["Balance"].iloc[-1]) if "Balance" in df.columns and not df["Balance"].isna().all() else float(df["Amount"].sum())
    currency = df["Currency"].iloc[0] if "Currency" in df.columns and len(df) > 0 else "EUR"

    return normalized, {"balance": last_balance, "currency": currency}

def read_aib_file(file_path: str) -> pd.DataFrame:
    with open(file_path, "rb") as f:
        head = f.read(512).lstrip().lower()

    if head.startswith(b"<") or b"<html" in head or b"<table" in head:
        tables = pd.read_html(file_path)
        if not tables:
            raise ValueError("No tables found in AIB HTML export")
        df = tables[0]
    else:
        df = pd.read_csv(file_path, skipinitialspace=True)

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

def classify_aib(description_text: str, amount: float) -> str:
    d = str(description_text).upper().strip()

    if d.startswith("VDP-") or d.startswith("VDC-") or d.startswith("VDA-"):
        return "card_payment"
    if d.startswith("ATM") or d[:8].find("ATM") >= 0:
        return "atm"

    if d.startswith("DD-") or "DIRECT DEBIT" in d:
        return "fee"  
    if d.startswith("SO-") or "STANDING ORDER" in d:
        return "fee"

    if amount > 0:
        return "topup"

    return "card_payment"

def normalize_aib(file_path: str, account_id: str):
    df = read_aib_file(file_path)

    df["debit_amount"] = pd.to_numeric(df.get("debit_amount"), errors="coerce")
    df["credit_amount"] = pd.to_numeric(df.get("credit_amount"), errors="coerce")
    df["amount"] = df["debit_amount"].fillna(0) * -1 + df["credit_amount"].fillna(0)

    desc_parts = []
    for col in ["description1", "description2", "description3"]:
        if col in df.columns:
            desc_parts.append(df[col].fillna("").astype(str).str.strip())
        else:
            desc_parts.append(pd.Series([""] * len(df)))

    merchant_name = (desc_parts[0] + " " + desc_parts[1] + " " + desc_parts[2]) \
        .str.replace(r"\s+", " ", regex=True).str.strip()

    transaction_classes = [
        classify_aib(desc, amt)
        for desc, amt in zip(merchant_name, df["amount"])
    ]

    normalized = pd.DataFrame({
        "transaction_id": [str(uuid.uuid4()) for _ in range(len(df))],
        "account_id": account_id,
        "category_id": "none",
        "date": pd.to_datetime(df["posted_transactions_date"], format="mixed", dayfirst=True).dt.strftime("%Y-%m-%d"),
        "merchant_name": merchant_name,
        "description": "none",
        "amount": df["amount"].astype(float),
        "currency_code": "EUR",
        "payment_channel": "none",
        "pending": False,
        "transaction_class": transaction_classes,
    })
    normalized = normalized.dropna(subset=["transaction_id", "account_id", "amount", "date"])
    normalized = normalized.sort_values("date").reset_index(drop=True)

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