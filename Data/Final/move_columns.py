import pandas as pd

accounts = pd.read_csv("accounts.csv")
users = pd.read_csv("users.csv")

users = users.merge(accounts[['user_id', 'account_id']], on='user_id', how='left')

accounts = accounts.drop(columns=['user_id'])

users.to_csv("users.csv", index=False)
accounts.to_csv("accounts.csv", index=False)

print("Columns moved successfully!")