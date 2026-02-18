import json
import pandas as pd

transactions_df = pd.read_csv("transactions.csv")
accounts_df = pd.read_csv("accounts.csv")

transactions_df['date'] = pd.to_datetime(transactions_df['date'])

for _, account in accounts_df.iterrows():
    account_user = account['user_id']
    account_id = account['account_id']

    total_amount_per_month = {}
    total_transactions_per_month = {}
    total_spent_per_month = {}
    total_received_per_month = {}
    largest_transaction_per_month = {}
    largest_absolute_transaction_per_month = {}
    category_counts_per_month = {}

    account_transactions = transactions_df[transactions_df['account_id'] == account_id].copy()

    for _, transaction in account_transactions.iterrows():
        month = transaction['date'].strftime('%Y-%m')  
        amount = transaction['amount']
        category = transaction['category_id']

        if month not in total_amount_per_month:
            total_amount_per_month[month] = 0
            total_transactions_per_month[month] = 0
            category_counts_per_month[month] = {}

        if month in total_amount_per_month:
            total_amount_per_month[month] = round(total_amount_per_month[month] + amount, 2)
            total_transactions_per_month[month] += 1
        else:
            total_amount_per_month[month] = round(amount, 2)
            total_transactions_per_month[month] = 1

        if amount < 0:
            if month in total_spent_per_month:
                total_spent_per_month[month] = round(total_spent_per_month[month] + amount, 2)
            else:
                total_spent_per_month[month] = round(amount, 2)

        if amount > 0:
            if month in total_received_per_month:
                total_received_per_month[month] = round(total_received_per_month[month] + amount, 2)
            else:
                total_received_per_month[month] = round(amount, 2)

        if month not in largest_transaction_per_month:
            largest_transaction_per_month[month] = amount
        else:
            largest_transaction_per_month[month] = max(
                largest_transaction_per_month[month], amount
            )

        if month not in largest_absolute_transaction_per_month:
            largest_absolute_transaction_per_month[month] = amount
        else:
            if abs(amount) > abs(largest_absolute_transaction_per_month[month]):
                largest_absolute_transaction_per_month[month] = amount

        if category not in category_counts_per_month[month]:
            category_counts_per_month[month][category] = 0

        category_counts_per_month[month][category] += 1

    print(f"\nUser: {account_user} | Account: {account_id}")
    print("Month | Total | Transactions | Total Spent | Total Received | Avg  | Largest | Largest (Abs)")
    for month in sorted(total_amount_per_month.keys()):
        total_amount = total_amount_per_month[month]
        num_transactions = total_transactions_per_month[month]
        total_spent = total_spent_per_month.get(month, 0.0)
        total_received = total_received_per_month.get(month, 0.0)
        average_amount = round(total_amount / num_transactions, 2)
        largest = round(largest_transaction_per_month[month], 2)
        largest_abs = round(largest_absolute_transaction_per_month[month], 2)
        category_json = category_counts_per_month[month]

        print(f"{month} | {total_amount} | {num_transactions} | "
              f"{total_spent} | {total_received} | {average_amount} | "
              f"{largest} | {largest_abs} | {json.dumps(category_json)}")