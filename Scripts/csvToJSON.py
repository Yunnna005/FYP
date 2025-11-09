import pandas as pd
import os

input_file = "../Other Dataset/spending_patterns_detailed.csv"

output_folder = "split_accounts"
os.makedirs(output_folder, exist_ok=True)

df = pd.read_csv(input_file)

account_column = "Customer_ID"

unique_accounts = df[account_column].unique()

for i, account in enumerate(unique_accounts, start=1):
    account_data = df[df[account_column] == account]
    output_file = os.path.join(output_folder, f"custom_{i}.csv")
    account_data.to_csv(output_file, index=False)
    print(f"Saved {output_file} for account {account}")

print("All files have been created successfully!")
