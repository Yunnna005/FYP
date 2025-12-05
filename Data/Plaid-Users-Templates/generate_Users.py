from datetime import datetime
from numpy import require
import pandas as pd
import json
import random
import os
from faker import Faker


fake = Faker('en_US')
Faker.seed(42)

# -----------------------------
# CONFIG
# -----------------------------
INPUT_FILE = "../Real Dataset/Transactions_Anna_AIB2324.csv"
MAX_TRANSACTIONS = 200
SEED_PREFIX = "my-test-user-"
ACH_ROUTING = "322271627"
CURRENCY = "USD"


# -----------------------------
# LOAD DATA
# -----------------------------
def load_dataset(file_path):
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file type")


df = load_dataset(INPUT_FILE)

# -----------------------------
# RANDOM GENERATORS
# -----------------------------
def generate_random_name():
    return fake.name()

def generate_phone_ie():
    return f"+353{random.randint(830000000, 899999999)}"

def generate_email(name):
    return f"{name.lower().replace(' ', '.')}@example.com"

def generate_random_address():
    return {
        "city": fake.city(),
        "region": fake.state(),
        "street": fake.street_address(),
        "postal_code": fake.postcode(),
        "country": "US"
    }


# -----------------------------
# TRANSACTIONS
# -----------------------------
def formatStringToFloat(value):
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)

    v = str(value).strip()
    if v == "":
        return 0.0

    v = v.replace(",", "")

    try:
        return float(v)
    except ValueError:
        return 0.0

def format_date(value):
    """Convert various date formats into strict YYYY-MM-DD."""
    if value is None:
        return ""

    s = str(value).strip()
    if s == "":
        return ""

    # Try multiple common date formats
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # As a last fallback, try pandas parser
    try:
        return pd.to_datetime(s).strftime("%Y-%m-%d")
    except:
        return ""
    
def transform_transactions(user_df):
    transactions = []

    for _, row in user_df.iterrows():
        debit = formatStringToFloat(row.get("debit_amount", 0))
        credit = formatStringToFloat(row.get("credit_amount", 0))

        if debit > 0:
            amount = -abs(debit)
        else:
            amount = abs(credit)

        desc_parts = [
            str(row.get("description1", "")).strip(),
            str(row.get("description2", "")).strip(),
            str(row.get("description3", "")).strip()
        ]

        desc_parts = [
        part for part in desc_parts
        if part and part.lower() not in ("nan", "none", "null", "")
        ]

        description = ": ".join(desc_parts)

        date = format_date(row.get("posted_transactions_date", ""))

        transactions.append({
            "date_transacted": date,
            "date_posted": date,
            "amount": round(amount, 2),
            "description": description,
            "currency": "USD"
        })

    # max 200 transactions
    return transactions[:200]


# -----------------------------
# USER PAYLOAD BUILDER
# -----------------------------
def build_user(user_id, user_df):
    transactions = transform_transactions(user_df)
    last_row = user_df.iloc[-1]
    last_balance = formatStringToFloat(last_row.get("balance", 0))

    name = generate_random_name()
    phone = generate_phone_ie()
    email = generate_email(name)
    address = generate_random_address()

    return {
        "override_accounts": [
            {
                "type": "depository",
                "subtype": "checking",
                "starting_balance": round(last_balance, 2),
                "currency": CURRENCY,
                "meta": {
                    "name": "Basic Checking Account",
                    "official_name": "Basic Checking Account",
                    "mask": str(user_id).zfill(8)[-4:]
                },
                "numbers": {
                    "account": str(user_id).zfill(8),
                    "ach_routing": ACH_ROUTING
                },
                "transactions": transactions,
                "identity": {
                    "names": [name],
                    "phone_numbers": [
                        {
                            "data": phone,
                            "primary": True,
                            "type": "mobile"
                        }
                    ],
                    "emails": [
                        {
                            "data": email,
                            "primary": True,
                            "type": "primary"
                        }
                    ],
                    "addresses": [
                        {
                            "data": address,
                            "primary": True
                        }
                    ]
                }
            }
        ]
    }


# -----------------------------
# EXPORT JSON FILES
# -----------------------------
def generate_users(df):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    user_id = 1
    for i in range(0, len(df), MAX_TRANSACTIONS):
        sub_df = df.iloc[i:i + MAX_TRANSACTIONS]

        payload = build_user(user_id, sub_df)

        filename = f"User {user_id}.json"
        file_path = os.path.join(script_dir, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        print(f"Saved {filename}")
        user_id += 1

generate_users(df)
print("All users generated!")
