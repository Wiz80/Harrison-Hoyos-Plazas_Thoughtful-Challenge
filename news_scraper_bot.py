from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from datetime import datetime
import os
import re

class NewsScraper:
    def __init__(self):
        self.browser = Selenium()
        self.excel = Files()
        self.http = HTTP()
        self.output_dir = "output/"
        os.makedirs(self.output_dir, exist_ok=True)
        self.excel_file = os.path.join(self.output_dir, "news_data.xlsx")
        self.news_data = []

    def open_website(self, url):
        """Open the Yahoo News website."""
        self.browser.open_available_browser(url)

    def search_news(self, search_phrase):
        """Enter the search phrase in the search field and perform the search."""
        self.browser.input_text("//input[@id='header-search-input']", search_phrase)
        self.browser.press_keys("//input[@id='header-search-input']", "ENTER")

    def filter_category(self, category=None):
        """Filter news by category if specified (optional step)."""
        if category:
            # Implement filtering logic here if the site supports it
            pass

    def scrape_news(self, months=0):
        """Scrape the latest news within the given time period."""
        articles = self.browser.find_elements("//li[contains(@class, 'js-stream-content')]")
        current_date = datetime.now()

        for article in articles:
            try:
                # Extract title, date, and description
                title_element = article.find_element_by_xpath(".//h3")
                title = title_element.text
                date_element = article.find_element_by_xpath(".//time")
                date_str = date_element.get_attribute("datetime")
                date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                description_element = article.find_element_by_xpath(".//p")
                description = description_element.text if description_element else "N/A"
                
                # Calculate the number of months since the news was published
                months_difference = (current_date.year - date.year) * 12 + (current_date.month - date.month)
                if months_difference > months:
                    continue

                # Count occurrences of the search phrase
                phrase_count = title.lower().count(search_phrase.lower()) + description.lower().count(search_phrase.lower())

                # Check if the title or description contains any amount of money
                contains_money = self.contains_money(title) or self.contains_money(description)

                # Download the news picture
                image_element = article.find_element_by_xpath(".//img")
                image_url = image_element.get_attribute("src")
                image_filename = self.download_image(image_url)

                # Append news data to the list
                self.news_data.append({
                    "Title": title,
                    "Date": date.strftime("%Y-%m-%d"),
                    "Description": description,
                    "Picture Filename": image_filename,
                    "Search Phrase Count": phrase_count,
                    "Contains Money": contains_money
                })

            except Exception as e:
                print(f"Error scraping article: {e}")

    def contains_money(self, text):
        """Check if the text contains any amount of money."""
        money_pattern = r"\$\d+(?:,\d{3})*(?:\.\d+)?|\d+ (?:dollars|USD)"
        return bool(re.search(money_pattern, text))

    def download_image(self, image_url):
        """Download the image and return the file name."""
        image_name = os.path.join(self.output_dir, os.path.basename(image_url))
        self.http.download(image_url, target_file=image_name)
        return image_name

    def save_to_excel(self):
        """Save the scraped news data to an Excel file."""
        self.excel.create_workbook(self.excel_file)
        self.excel.append_worksheet(name="News", content=self.news_data, header=True)
        self.excel.save_workbook()

    def close(self):
        """Close the browser."""
        self.browser.close_all_browsers()

def main():
    scraper = YahooNewsScraper()
    try:
        scraper.open_website("https://news.yahoo.com/")
        search_phrase = "economy"  # Define your search phrase
        category = "business"  # Define your category if applicable
        months = 1  # Define the number of months to retrieve news for

        scraper.search_news(search_phrase)
        scraper.filter_category(category)
        scraper.scrape_news(months)
        scraper.save_to_excel()
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
