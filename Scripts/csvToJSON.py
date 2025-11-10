import pandas as pd
import os
import json

# Input CSV file
input_file = "../Plaid Dataset/transactions2.csv"

# Output folder for JSON files
output_folder = "split_customers_json"
os.makedirs(output_folder, exist_ok=True)

# Read the CSV file
df = pd.read_csv(input_file)

# Column identifying customers
account_column = "account_id"

# Group by each customer
for customer_id, group in df.groupby(account_column):
    # Convert this customer's transactions into a list of dictionaries
    transactions = group.drop(columns=[account_column]).to_dict(orient="records")

    # Create the customer JSON structure
    customer_data = {
        "account_id": customer_id,
        "Transactions": transactions
    }

    # Save to JSON file named after the customer
    output_file = os.path.join(output_folder, f"{customer_id}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(customer_data, f, indent=4)

    print(f"Saved {output_file}")

print("✅ All customer JSON files created successfully!")
