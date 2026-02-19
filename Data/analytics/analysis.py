import json
import pandas as pd

transactions = pd.read_csv("transactions.csv")
accounts = pd.read_csv("accounts.csv")
transactions['date'] = pd.to_datetime(transactions['date'])
transactions['month'] = transactions['date'].dt.strftime('%Y-%m')

all_time_rows = []
monthly_rows = []

all_time_counter = 1
monthly_counter = 1

for _, account in accounts.iterrows():
    user_id = str(account['user_id'])
    account_id = str(account['account_id'])

    account_transactions = transactions[transactions['account_id'] == account_id]
    if account_transactions.empty:
        continue

    #All Time Analysis
    all_amounts = account_transactions['amount']
    total_transactions_all = len(all_amounts)
    avg_transaction_all = round(all_amounts.mean(), 2)
    largest_transaction_all = round(all_amounts.max(), 2)

    all_time_rows.append({
        "stats_id": f"stats_{all_time_counter}",
        "user_id": user_id,
        "account_id": account_id,
        "total_transactions": total_transactions_all,
        "avg_transactions_value": avg_transaction_all,
        "largest_transaction": largest_transaction_all
    })
    all_time_counter += 1

    #Monthly Analysis
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

        monthly_rows.append({
            "stats_id": f"stats_{monthly_counter}",
            "user_id": user_id,
            "account_id": account_id,
            "month_start_date": f"{month}-01",
            "total_amount": total,
            "total_transactions": count,
            "total_spend": spent,
            "total_receive": received,
            "avg_transaction_value": avg,
            "largest": largest,
            "largest_abs": largest_abs,
            "spending_by_category": categories
        })
        monthly_counter += 1

all_time_df = pd.DataFrame(all_time_rows)
monthly_df = pd.DataFrame(monthly_rows)

all_time_df.to_csv("user_all_time_stats.csv", index=False)
monthly_df.to_csv("user_monthly_stats.csv", index=False)

print("CSV files created: user_all_time_stats.csv and user_monthly_stats.csv")