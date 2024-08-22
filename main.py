from robocorp import workitems
from robocorp.tasks import task
import re
from datetime import datetime, timedelta
from robocorp import browser, vault, storage
from robocorp.tasks import task
from RPA.Excel.Files import Files as Excel
from news_scraper_bot import NewsScraper

url = storage.get_text("URL")

@task
def scrape_news():
    # Obtener parámetros del work item
    item = workitems.inputs.current
    search_phrase = item.payload["search_phrase"]
    news_category = item.payload["news_category"]
    months = item.payload["months"]

    scraper = NewsScraper()
    scraper.open_website(url)
    scraper.search_news(search_phrase)
    scraper.select_category(news_category)
    news_data = scraper.get_news_data(months)
    scraper.save_to_excel(news_data)
