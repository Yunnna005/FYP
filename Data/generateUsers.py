import csv
import random
import pandas as pd
from pathlib import Path
from faker import Faker

fake = Faker()

DATA_DIR_ACCOUNTS = Path("/workspaces/python/FYP/Data/Final/accounts.csv")

OUT_FILE = "users.csv"

OUT_DIR = "/workspaces/python/FYP/Data/Final"

def generate_users(input_file, output_dir):
    df = pd.read_csv(input_file, usecols=["user_id"])

    rows = []
    for user_id in df["user_id"].unique():
        password_length = random.randint(8, 12)
        rows.append(
            {
                "user_id": user_id,
                "email": fake.simple_profile()["mail"],
                "password": fake.password(length=password_length),
                "full_name": fake.name(),
                "phone_number": fake.msisdn(),
                "plaid_access_token": "none",
                "plaid_item_id": "none",
                "is_active": random.choice([True, False]),
            }
        )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / OUT_FILE
    pd.DataFrame(rows).to_csv(output_path, index=False)

generate_users(DATA_DIR_ACCOUNTS, OUT_DIR)