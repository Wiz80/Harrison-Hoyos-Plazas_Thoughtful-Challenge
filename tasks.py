from RPA.Robocorp.WorkItems import WorkItems
from robocorp.tasks import task
import json
import requests
import time
from urllib.parse import quote
from datetime import datetime, timedelta
from robocorp import browser, vault, storage
from robocorp.tasks import task
from RPA.Excel.Files import Files as Excel
from news_scraper_bot import NewsScraper

url = storage.get_text("URL")

@task
def scrape_news():
    search_phrase = "Artificial intelligence"
    news_category = "Technology"
    months = 3

    page_search = url + f"/search/{quote(search_phrase)}?sort=date"

    scraper = NewsScraper()
    scraper.open_website(page_search)
    scraper.click_search_button()

    while True:
        scraper.extract_news_data(search_phrase, months)
        # Check if more results should be loaded
        scraper.click_show_more()
        time.sleep(2)
        break

    scraper.search_news(search_phrase)
    scraper.select_category(news_category)
    news_data = scraper.get_news_data(months)
    scraper.save_to_excel(news_data)
    

@task
def store_work_items():
    secrets = vault.get_secret('NewsScraper')
    API_KEY = secrets['API_KEY']
    WORKSPACE_ID = secrets['WORKSPACE_ID']
    PROCESS_ID = secrets['PROCESS_ID']
    API_URL = f"https://cloud.robocorp.com/api/v1/workspaces/{WORKSPACE_ID}/work-items"

    with open('workitems.json') as jsonfile:
        data = json.load(jsonfile)
        for item in data:
            payload = {
                "process": {
                    "id": PROCESS_ID
                },
                "payload": {
                    "search_phrase": item["search_phrase"],
                    "news_category": item["news_category"],
                    "months": int(item["months"])
                }
            }
            response = requests.post(API_URL, json=payload, headers={
                "Authorization": f"RC-WSKEY {API_KEY}",
                "Content-Type": "application/json"
            })

            if response.status_code == 200:
                print(response.json())
            else:
                print("Error en la solicitud. No se pudo decodificar la respuesta como JSON.")
