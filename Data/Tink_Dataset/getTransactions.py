import requests
import csv

ACCESS_TOKEN = "tink_access_token"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

accounts_url = "https://api.tink.com/data/v2/accounts"
accounts_resp = requests.get(accounts_url, headers=headers)
accounts_data = accounts_resp.json()

with open("accounts_SE.csv", "w", newline="") as csvfile:
    fieldnames = ["id", "name", "type", "balance", "currency", "iban", "lastRefreshed"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for acc in accounts_data.get("accounts", []):
        bal = acc.get("balances", {}).get("available", {}).get("amount", {})
        unscaled = int(bal.get("value", {}).get("unscaledValue", 0))
        scale = int(bal.get("value", {}).get("scale", 0))
        balance = unscaled * (10 ** -scale)  
        writer.writerow({
            "id": acc.get("id"),
            "name": acc.get("name"),
            "type": acc.get("type"),
            "balance": balance,
            "currency": bal.get("currencyCode"),
            "iban": acc.get("identifiers", {}).get("iban", {}).get("iban"),
            "lastRefreshed": acc.get("dates", {}).get("lastRefreshed")
        })

transactions_url = "https://api.tink.com/data/v2/transactions"
tx_resp = requests.get(transactions_url, headers=headers)
tx_data = tx_resp.json()

with open("transactions_SE.csv", "w", newline="") as csvfile:
    fieldnames = ["id", "accountId", "date", "description", "amount", "currency", "status", "type", "providerTransactionId"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for tx in tx_data.get("transactions", []):
        amt = tx.get("amount", {})
        unscaled = int(amt.get("value", {}).get("unscaledValue", 0))
        scale = int(amt.get("value", {}).get("scale", 0))
        amount = unscaled * (10 ** -scale) 
        writer.writerow({
            "id": tx.get("id"),
            "accountId": tx.get("accountId"),
            "date": tx.get("dates", {}).get("booked"),
            "description": tx.get("descriptions", {}).get("display"),
            "amount": amount,
            "currency": amt.get("currencyCode"),
            "status": tx.get("status"),
            "type": tx.get("types", {}).get("type"),
            "providerTransactionId": tx.get("identifiers", {}).get("providerTransactionId")
        })

print("Saved accounts.csv and transactions.csv")
