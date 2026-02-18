import json
import pandas as pd

transactions = pd.read_csv("transactions.csv")
accounts = pd.read_csv("accounts.csv")
transactions['date'] = pd.to_datetime(transactions['date'])
transactions['month'] = transactions['date'].dt.strftime('%Y-%m')

for _, account in accounts.iterrows():
    user_id = account['user_id']
    account_id = account['account_id']

    account_transactions = transactions[transactions['account_id'] == account_id]

    print(f"\nUser: {user_id} | Account: {account_id}")
    print("Month | Total | Transactions | Total Spent | Total Received | Avg | Largest | Largest (Abs) | Category")

    for month, group in account_transactions.groupby('month'):
        amounts = group['amount']
        total = round(amounts.sum(), 2)
        count = len(amounts)
        spent = round(amounts[amounts < 0].sum(), 2)
        received = round(amounts[amounts > 0].sum(), 2)
        avg = round(total / count, 2)
        largest = round(amounts.max(), 2)
        largest_abs = round(amounts.loc[amounts.abs().idxmax()], 2)
        categories = json.dumps(group['category_id'].value_counts().to_dict())

        print(f"{month} | {total} | {count} | {spent} | {received} | {avg} | {largest} | {largest_abs} | {categories}")