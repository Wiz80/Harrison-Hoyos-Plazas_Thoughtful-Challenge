import requests
import csv
import os
from dotenv import load_dotenv
from robocorp import vault

load_dotenv()


API_KEY = vault.get_secret('API_KEY')
WORKSPACE_ID = vault.get_secret('WORKSPACE_ID')
API_URL = f"https://cloud.robocorp.com/api/v1/workspaces/{WORKSPACE_ID}/work-items"

with open('input_data.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        payload = {
            "payload": {
                "search_phrase": row["search_phrase"],
                "news_category": row["news_category"],
                "months": int(row["months"])
            }
        }
        response = requests.post(API_URL, json=payload, headers={
            "Authorization": f"RC-WSKEY {API_KEY}",
            "Content-Type": "application/json"
        })
        print(response.json())
