import os
import time
from selenium.webdriver.common.by import By
from loguru import logger
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import uuid
import tempfile
import pandas as pd

class Scraper:
    def __init__(self):
        self.name = "lcbo"

    def get_chrome_common_settings(self, headless=True, extension=None, proxy=False):
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-remote-font")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--ignore-certificate-errors-spki-list")
        chrome_options.add_argument("--ignore-ssl-errors")

        profile_unique_name = str(uuid.uuid4())

        if headless:
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
            )
            chrome_options.add_argument("--headless")  # Run Chrome in headless mode
            profile_directory = tempfile.mkdtemp()
            self.profile_download = f"{profile_directory}/downloads"
            os.makedirs(self.profile_download, exist_ok=True)
            os.makedirs(profile_directory, exist_ok=True)
        else:
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            profile_directory = tempfile.mkdtemp()
            self.profile_download = f"{profile_directory}/downloads"
            os.makedirs(profile_directory, exist_ok=True)
            os.makedirs(self.profile_download, exist_ok=True)

        chrome_options.add_argument(f"--user-data-dir={profile_directory}")
        prefs = {
            "download.default_directory": self.profile_download,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.default_content_settings.popups": 0,
            "plugins.plugins_disabled": ["Chrome PDF Viewer"],
            "plugins.always_open_pdf_externally": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)

        if extension:
            extension_path = os.path.join(os.getcwd(), extension)
            chrome_options.add_extension(extension_path)
        else:
            chrome_options.add_argument("--incognito")
            chrome_options.add_argument("--disable-extensions")

        proxy_settings = {
            "proxy": {
                "https": "https://5Q8qPA7a3lasc0EJ:tLf6cU0jLr6MZFwR_country-us_state-texas@geo.iproyal.com:12321",
                "http": "https://5Q8qPA7a3lasc0EJ:tLf6cU0jLr6MZFwR_country-us_state-texas@geo.iproyal.com:12321",
                "no_proxy": "localhost,127.0.0.1",
            }
        }

        self.initiate_driver(
            chrome_options=chrome_options,
            proxy_settings=proxy_settings if proxy else None,
        )
        logger.debug(
            f'Chrome version: {self.driver.execute_script("return navigator.userAgent")}'
        )

    def initiate_driver(self, chrome_options, proxy_settings=None, max_retries=3):
        for i in range(max_retries):
            try:
                if proxy_settings:
                    from seleniumwire import webdriver

                    logger.debug(f"Loading seleniumwire with {proxy_settings}")
                    self.driver = webdriver.Chrome(
                        executable_path=ChromeDriverManager().install(),
                        seleniumwire_options=proxy_settings,
                        options=chrome_options,
                    )
                else:
                    from selenium import webdriver

                    logger.debug(f"Loading Chrome..✅ ... attempt {i}")
                    self.driver = webdriver.Chrome(
                        service=Service(ChromeDriverManager().install()),
                        options=chrome_options,
                    )
            except Exception:
                if i < max_retries - 1:
                    continue
                else:
                    raise
            else:
                return

    def specific_clicker(self, ele, max_retries=2):
        wait = WebDriverWait(self.driver, 20)
        for _ in range(max_retries):
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, ele)))
                if element := self.driver.find_element(By.XPATH, ele):
                    webdriver.ActionChains(self.driver).move_to_element_with_offset(
                        element, 1, 0
                    ).click(element).perform()
                    return element
            except Exception:
                time.sleep(1)

        raise NoSuchElementException

    def get_elements(self, ele):
        elements = self.driver.find_elements(By.XPATH, ele)

        if not elements:
            logger.debug(f"No element found with XPATH = {ele}")
            return None
        else:
            return elements

    def find_elements(self, ele, timeout=2):
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.presence_of_element_located((By.XPATH, ele)))
        elements = self.driver.find_elements(By.XPATH, ele)
        if not elements:
            logger.debug(f"No element found with XPATH = {ele}")
            return None
        else:
            return elements

    def run(self):
        self.get_chrome_common_settings(headless=False) # launch Chrome browser
        self.driver.get(
            "https://www.lcbo.com/en/products/wine/red-wine#t=clp-products-wine-red_wine&sort=%40ec_final_price%20descending"
        )
        self.get_elements('//a[@id="my_store"]')[0].click()
        self.get_elements('//*[@id="my_store_change_store"]')[0].click()

        input_t = self.get_elements('//*[@aria-label="Find by Address, City, or Postal Code, Tab to Suggested Search location"]')
        input_t[0].send_keys('MANULIFE')

        locations = self.get_elements('//div[@class="pac-item"]')
        locations[0].click()





        while True:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight-1000);"
            )
            try:
                self.specific_clicker('//*[@id="loadMore"]')
            except NoSuchElementException:
                break
            else:
                time.sleep(1)

        products = self.get_elements('//*[@id="coveo-result-list2"]/div/div/div/div[2]')
        product_details = [extract_details(i) for i in products]
        df = pd.DataFrame(product_details)  # Create a DataFrame with the extracted details
        print(df)  # Print or save the DataFrame

        df.to_csv('scraped_products.csv', index=False)  # Saves the DataFrame to a CSV file without row indices


def extract_details(ele):
    try:
        badge = ele.find_element(By.XPATH, './/div[@class="coveo-product-badging"]').text
    except NoSuchElementException:
        badge = None

    try:
        name = ele.find_element(
            By.XPATH, './/div[@class="coveo-result-row product-item-name"]'
        ).text
    except NoSuchElementException:
        name = None

    try:
        volume = ele.find_element(
            By.XPATH, './/div[@class="coveo-result-row product-item-volume"]'
        ).text
    except NoSuchElementException:
        volume = None

    try:
        price = ele.find_element(
            By.XPATH, './/div[@class="coveo-result-row product-item-price"]'
        ).text
    except NoSuchElementException:
        price = None

    try:
        stock = ele.find_element(
            By.XPATH, './/div[@class="coveo-result-row stock-threshold"]'
        ).text
    except NoSuchElementException:
        stock = None

    return {
        "badge": badge,
        "name": name,
        "volume": volume,
        "price": price,
        "stock": stock,
    }
