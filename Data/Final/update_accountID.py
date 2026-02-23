import pandas as pd
import random

accounts_df = pd.read_csv("accounts.csv")
users_df = pd.read_csv("users.csv")
monthly_stats_df = pd.read_csv("user_monthly_stats.csv")
all_time_stats_df = pd.read_csv("user_all_time_stats.csv")
transactions_df = pd.read_csv("transactions.csv")

def generate_card_number():
    """Generate a random 16-digit card number as string."""
    return ''.join([str(random.randint(0, 9)) for _ in range(16)])

account_id_mapping = {}
existing_cards = set()

for old_id in accounts_df["account_id"]:
    new_card = generate_card_number()
    
    while new_card in existing_cards:
        new_card = generate_card_number()
    
    existing_cards.add(new_card)
    account_id_mapping[old_id] = new_card

accounts_df["account_id"] = accounts_df["account_id"].map(account_id_mapping)

users_df["account_id"] = users_df["account_id"].map(account_id_mapping)
monthly_stats_df["account_id"] = monthly_stats_df["account_id"].map(account_id_mapping)
all_time_stats_df["account_id"] = all_time_stats_df["account_id"].map(account_id_mapping)
transactions_df["account_id"] = transactions_df["account_id"].map(account_id_mapping)

accounts_df.to_csv("accounts_updated.csv", index=False)
users_df.to_csv("users_updated.csv", index=False)
monthly_stats_df.to_csv("user_monthly_stats_updated.csv", index=False)
all_time_stats_df.to_csv("user_all_time_stats_updated.csv", index=False)
transactions_df.to_csv("transactions_updated.csv", index=False)

print("Account IDs successfully replaced in all files and saved.")