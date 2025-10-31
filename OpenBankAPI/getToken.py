import requests
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("OBP_USERNAME")
password = os.getenv("OBP_PASSWORD")
consumer_key = os.getenv("OBP_CONSUMER_KEY")

url = "https://apisandbox.openbankproject.com/my/logins/direct"
headers = {
    "Accept": "application/json",
    "Authorization": f'DirectLogin username="{username}", password="{password}", consumer_key="{consumer_key}"'
}

response = requests.post(url, headers=headers)
print(response.status_code)
print(response.json())

