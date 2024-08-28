from RPA.Browser.Selenium import Selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        """Open the News website."""
        self.browser.open_available_browser(url)

    def click_search_button(self):
        """Wait for the search button to be clickable and click it."""
        try:
            # Espera explícita para que el botón esté disponible
            wait = WebDriverWait(self.browser.driver, 10)
            
            # Localiza el formulario por su clase
            form_element = wait.until(EC.presence_of_element_located((By.XPATH, '//form[contains(@class, "search-bar__form")]')))
            
            # Dentro del formulario, busca el botón con el texto 'Search'
            search_button = form_element.find_element(By.XPATH, './/button[@type="submit" and contains(@class, "css-sp7gd")]')
            
            # Haz clic en el botón
            search_button.click()
            
            print("Search button clicked successfully.")
        except Exception as e:
            print(f"Error clicking the search button: {e}")

        
    def click_show_more(self):
        """Click the 'Show More' button after scrolling it into view."""
        try:
            # Encuentra el botón "Show More"
            show_more_button = self.browser.find_element('//button[contains(@class, "show-more-button")]')
            
            # Desplaza la página hasta que el botón sea visible
            self.browser.scroll_element_into_view(show_more_button)
            
            # Haz clic en el botón
            self.browser.click_element(show_more_button)
            
            print("Clicked 'Show More' button")
        except Exception as e:
            print("No more 'Show More' button available or an error occurred", e)

    def extract_news_data(self, search_phrase, months):
        """Extract news data from the page."""
        current_date = datetime.now()

        try:
            # Espera explícita para que se carguen los elementos de noticias
            wait = WebDriverWait(self.browser.driver, 10)
            
            # Espera hasta que se encuentren los elementos de noticias
            wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "gc__content")]')))
            
            # Encuentra todos los elementos de noticias usando el método de RPA.Browser.Selenium
            news_elements = self.browser.find_elements("xpath://div[contains(@class, 'gc__content')]")

            for news in news_elements:
                try:
                    # Extrae el título
                    title_element = news.find_element("xpath:.//h3[contains(@class, 'gc__title')]/a")
                    title = title_element.find_element_by_xpath(".//span").text  # Extrae el texto del span dentro del tag <a>
                    url = title_element.get_attribute("href")

                    # Extrae la descripción
                    description_element = news.find_element("xpath:.//div[contains(@class, 'gc__excerpt')]")
                    description = description_element.text if description_element else "N/A"

                    # Extrae la fecha
                    date_text = description.split('...')[0].strip()  # Extrae la fecha del texto de la descripción
                    date = self.parse_date(date_text)

                    # Calcula la diferencia en meses desde que se publicó la noticia
                    months_difference = (current_date.year - date.year) * 12 + (current_date.month - date.month)
                    if months_difference > months:
                        continue

                    # Cuenta las apariciones de la frase de búsqueda en el título y la descripción
                    phrase_count = title.lower().count(search_phrase.lower()) + description.lower().count(search_phrase.lower())

                    # Verifica si el título o la descripción contienen alguna cantidad de dinero
                    contains_money = self.contains_money(title) or self.contains_money(description)

                    # Añade los datos de la noticia a la lista
                    self.news_data.append({
                        "Title": title,
                        "Date": date.strftime("%Y-%m-%d"),
                        "Description": description,
                        "URL": url,
                        "Search Phrase Count": phrase_count,
                        "Contains Money": contains_money
                    })

                except Exception as e:
                    print(f"Error extracting data from news element: {e}")

        except Exception as e:
            print(f"Error waiting for news elements to load: {e}")

    def filter_category(self, category=None):
        """Filter news by category if specified (optional step)."""
        if category:
            # Implement filtering logic here if the site supports it
            pass

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