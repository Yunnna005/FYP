import pandas as pd

transactions_df = pd.read_csv('transactions.csv')
accounts_df = pd.read_csv("accounts.csv")

transactions_df['date'] = pd.to_datetime(transactions_df['date'])

for _, account in accounts_df.iterrows():
    account_user = account['user_id']
    account_id = account['account_id']

    total_transactions_per_month = {}

    account_transactions = transactions_df[transactions_df['account_id'] == account_id].copy()

    for _, transaction in account_transactions.iterrows():
        month = transaction['date'].strftime('%Y-%m')  
        amount = transaction['amount']

        if month in total_transactions_per_month:
            total_transactions_per_month[month] += 1
        else:
            total_transactions_per_month[month] = 1

    for month in sorted(total_transactions_per_month.keys()):
            total = total_transactions_per_month[month]
            print(f"{account_user} | {account_id} | {month} | {total}")