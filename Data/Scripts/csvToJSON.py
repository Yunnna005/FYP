import pandas as pd
import os
import json

input_file = "../Plaid Dataset/transactions2.csv"

output_folder = "split_customers_json"
os.makedirs(output_folder, exist_ok=True)

df = pd.read_csv(input_file)

account_column = "account_id"

for customer_id, group in df.groupby(account_column):
    transactions = group.drop(columns=[account_column]).to_dict(orient="records")

    customer_data = {
        "account_id": customer_id,
        "Transactions": transactions
    }

    output_file = os.path.join(output_folder, f"{customer_id}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(customer_data, f, indent=4)

    print(f"Saved {output_file}")

print("All customer JSON files created successfully!")
