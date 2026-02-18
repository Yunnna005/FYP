import pandas as pd

transactions_df = pd.read_csv("transactions.csv")
accounts_df = pd.read_csv("accounts.csv")

transactions_df['date'] = pd.to_datetime(transactions_df['date'])

for _, account in accounts_df.iterrows():
    account_user = account['user_id']
    account_id = account['account_id']

    total_spending_per_month = {}
    total_transactions_per_month = {}

    account_transactions = transactions_df[transactions_df['account_id'] == account_id].copy()

    for _, transaction in account_transactions.iterrows():
        month = transaction['date'].strftime('%Y-%m')  
        amount = transaction['amount']
        if month in total_spending_per_month:
            total_spending_per_month[month] = round(total_spending_per_month[month] + amount, 2)
            total_transactions_per_month[month] += 1
        else:
            total_spending_per_month[month] = round(amount, 2)
            total_transactions_per_month[month] = 1

    for month in sorted(total_spending_per_month.keys()):
        total_amount = total_spending_per_month[month]
        num_transactions = total_transactions_per_month[month]
        average_amount = round(total_amount / num_transactions, 2)
        print(f"{account_user} | {account_id} | {month} | Total: {total_amount} | Transactions: {num_transactions} | Avg: {average_amount}")
