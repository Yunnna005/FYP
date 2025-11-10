import requests
import csv

ACCESS_TOKEN = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjBhNWVkOWE2LTBmZTEtNGFiNC1hMWVmLTY5MjU3NjFmNjk5NSIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjIwMzc5MDgsImlhdCI6MTc2MjAzMDcwOCwiaXNzIjoidGluazovL2F1dGgiLCJqdGkiOiI4MmQxNTM1Yy1lNjlmLTRhOTUtYjlhYy1hMjM0ZTEyZjZmNzMiLCJvcmlnaW4iOiJtYWluIiwic2NvcGVzIjpbImJhbGFuY2VzOnJlYWQiLCJhY2NvdW50czpyZWFkIiwidHJhbnNhY3Rpb25zOnJlYWQiXSwic3ViIjoidGluazovL2F1dGgvdXNlci9lYmE1OTdlMzdjMjA0ZGUzOTQ4NmY3ODgyOTE2YWUzNSIsInRpbms6Ly9hcHAvaWQiOiJmNmNlOGVkNTY1YjU0MzM1YTJlYjc3NmE2YmU1MTNlMSIsInRpbms6Ly9hcHAvdmVyaWZpZWQiOiJmYWxzZSIsInRpbms6Ly9jbGllbnQvaWQiOiI2MDYwOGZhYzMwN2Y0NjhjYjZlNGE0NTNkNjBlZTE0OSJ9.ZDRN7MiSV2dDS1YaCQFukyf9YRfS-6Os7QbHpeEz7MqeQLarhKwBzoV7ozun_n2HBRvDX5isUCMtWQL6GMEuVw"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
# Fetch accounts
accounts_url = "https://api.tink.com/data/v2/accounts"
accounts_resp = requests.get(accounts_url, headers=headers)
accounts_data = accounts_resp.json()

# Save accounts with correct balance
with open("accounts_SE.csv", "w", newline="") as csvfile:
    fieldnames = ["id", "name", "type", "balance", "currency", "iban", "lastRefreshed"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for acc in accounts_data.get("accounts", []):
        bal = acc.get("balances", {}).get("available", {}).get("amount", {})
        unscaled = int(bal.get("value", {}).get("unscaledValue", 0))
        scale = int(bal.get("value", {}).get("scale", 0))
        balance = unscaled * (10 ** -scale)  # corrected
        writer.writerow({
            "id": acc.get("id"),
            "name": acc.get("name"),
            "type": acc.get("type"),
            "balance": balance,
            "currency": bal.get("currencyCode"),
            "iban": acc.get("identifiers", {}).get("iban", {}).get("iban"),
            "lastRefreshed": acc.get("dates", {}).get("lastRefreshed")
        })

# Fetch and save transactions (unchanged)
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
        amount = unscaled * (10 ** -scale)  # corrected
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
