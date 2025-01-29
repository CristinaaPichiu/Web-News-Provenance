import demjson3
from playwright.sync_api import sync_playwright
import json
from goose3 import Goose
import langcodes
import requests
from bs4 import BeautifulSoup
import logging
import time
from langdetect import DetectorFactory, detect_langs
import spacy
from newspaper import Article
import pythonmonkey
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class BeautifulSoupScraper:
    """A scraper class using BeautifulSoup to extract data from web pages."""

    def __init__(self,service,options):
        logging.basicConfig(level=logging.INFO)
        DetectorFactory.seed = 0
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        self.max_attempts = 3
        self.timeout = 10
        self.nlp = spacy.load("en_core_web_sm")
        self.driver = None
        self.soup = None
        self.service = service
        self.options = options

    def extract_json_ld(self, url):
        """
        Extracts structured metadata (JSON-LD, RDFa, etc.) from a given URL.
        Args:
            url (str): The URL of the webpage to extract metadata from.
        Returns:
            dict: A dictionary containing all extracted metadata.
        """

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            html_content = response.text
            self.soup = soup
            json_ld_data = self.extract_main_article_json_ld(soup, html_content, url)
            return json_ld_data

        except requests.exceptions.Timeout:
            logging.error(f"Request timed out while trying to fetch the URL: {url}")
            return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching URL: {e}")
            return None

    def extract_rdfa(self, url):
        """
        Extracts RDFa metadata from a given URL, excluding application-related data.
        Args:
            url (str): The URL of the webpage to extract metadata from.
        Returns:
            dict: A dictionary containing all extracted RDFa metadata without application details.
        """
        try:
            g = Goose()
            article_goose = g.extract(url=url)
            logging.info(f"Goose article: {article_goose.opengraph}")
            rdfa_data_extracted = article_goose.opengraph
            if 'title' in rdfa_data_extracted:
                rdfa_data_extracted['headline'] = rdfa_data_extracted.pop('title')
            if 'rich_attachment' in rdfa_data_extracted:
                del rdfa_data_extracted['rich_attachment']
            if rdfa_data_extracted:
                return rdfa_data_extracted
            else:
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed- Rdfa: {e}")
            return None
        except Exception as e:
            logging.error(f"Error extracting RDFa: {e}")
            return None

    def _get_html_content(self, url):
        """Fetches the HTML content of a page with retry mechanism."""
        headers = {"User-Agent": self.user_agent}

        for attempt in range(self.max_attempts):
            try:
                response = requests.get(url, headers=headers, timeout=self.timeout)
                if response.status_code == 200:
                    return response
            except requests.RequestException:
                time.sleep(2)
        raise ValueError("Failed to retrieve webpage after multiple attempts.")

    def _parse_article(self, article):
        """Downloads, parses and processes an article."""
        try:
            article.download()
            article.parse()
            article.nlp()
            return article
        except Exception as e:
            logging.error(f"Error parsing article: {e}")
            return None

    def extract_data(self, url):
        """Extracts data from a webpage.
        Args: url (str): The URL of the webpage to extract data from.
        Returns: dict: A dictionary containing the extracted data.
            """

        response = self._get_html_content(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        g = Goose()
        article_goose = g.extract(url=url)
        article = Article(url)
        article = self._parse_article(article)
        content = article_goose.cleaned_text
        headline = article_goose.title
        logging.info(f"Goose content: {content}")
        language_code, language_name = self.detect_language(response, soup, headline)
        keywords = []
        if article:
            keywords = article.keywords
            logging.info(f"Keywords: {article.keywords}")
        logging.info(f"Goose keywords: {article_goose.meta_keywords}")
        if article_goose.meta_keywords:
            goose_keywords = article_goose.meta_keywords.split(',')
            keywords = list(set(keywords + goose_keywords))

        return {
            "content": content,
            "language_code": language_code,
            "language_name": language_name,
            "keywords": keywords,
            "videos": article_goose.movies,
            "abstract": article_goose.meta_description
        }

    def detect_language(self, response, soup, content):
        """
        Detects the language of the article using headers, HTML attributes, or text analysis.
        Args:
            response (requests.Response): The response object from the request.
            soup (BeautifulSoup): The parsed HTML content of the page.
            content (str): The raw text content of the article.
        Returns:
            tuple: A tuple containing the language code and the full language name.
        """
        content_language = response.headers.get('Content-Language')
        if content_language:
            lang_code = content_language.split(',')[0]
            full_name = self.get_full_language_name(lang_code)
            return lang_code, full_name

        html_lang = soup.html.get('lang') if soup.html else None
        if html_lang:
            lang_code = html_lang.split('-')[0]
            full_name = self.get_full_language_name(lang_code)
            return lang_code, full_name

        if content:
            lang_code, full_name = self.detect_language_full_name(content)
            if lang_code:
                return lang_code, full_name
        return None, "Unknown language"

    @staticmethod
    def get_full_language_name(code):
        """
        Get the full language name from the language code.
        Args:
            code (str): The language code.
        Returns:
            str: The full language name
        """
        full_name = langcodes.Language.get(code).language_name()
        return full_name

    @staticmethod
    def detect_language_full_name(text):
        """
        Detects the language of the text using the langdetect library.
        Args:
            text (str): The text to analyze.
        Returns:
            tuple: A tuple containing the language code and the full language name.
        """
        language_code = detect_langs(text)
        if not language_code:
            return None, "Unknown language"
        language_code = language_code[0].lang
        language_name = langcodes.Language.get(language_code).language_name()
        return language_code, language_name

    def extract_json_ld_youtube(self, url):
        """
        Extracts JSON-LD from a webpage using the 'application/ld+json' script type.
        Args:
            url (str): The URL of the webpage to extract JSON-LD from.
        Returns:
            list: A list of JSON-LD scripts or None if none are found.
        """

        driver = webdriver.Chrome(service=self.service, options=self.options)
        driver.get(url)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'player-microformat-renderer')))
        json_ld_scripts = driver.find_elements(By.XPATH, '//script[@type="application/ld+json"]')
        json_ld_data = []
        for script in json_ld_scripts:
            script_content = script.get_attribute('innerHTML')
            try:
                json_data = json.loads(script_content)
                json_ld_data.append(json_data)
            except json.JSONDecodeError:
                logging.error(f"Error decoding JSON from script: {script_content}")

        driver.quit()
        if not json_ld_data:
            logging.info("No JSON-LD scripts found.")
            return None

        return json_ld_data

    def extract_main_article_json_ld(self, soup, html_content, page_url):
        """
        Extracts the main article JSON-LD object, prioritizing one with matching 'mainEntityOfPage' or 'url'.
        Args:
            soup (BeautifulSoup): The parsed HTML content of the page.
            html_content (str): The raw HTML content of the webpage.
            page_url (str): The URL of the webpage.
        Returns:
            dict: The JSON-LD object for the main article, or None if no match is found.
        """

        def is_valid_type(item_type, valid_types):
            """Check if the @type field matches the desired types."""
            if isinstance(item_type, str):
                return item_type in valid_types
            if isinstance(item_type, list):
                return any(t in valid_types for t in item_type)
            return False

        def extract_matching_item(json_data, valid_types, page_url):
            """
            Inspect JSON-LD data for matches based on type and mainEntityOfPage.
            Args:
                json_data (dict): The JSON-LD data to inspect.
                valid_types (set): A set of valid types to match against.
                page_url (str): The URL of the webpage.
            Returns:
                dict: The matching JSON-LD data or None if no match is found.
            """
            logging.info(f"Inspecting JSON-LD data: {json_data}")
            if isinstance(json_data, dict):
                item_type = json_data.get('@type')
                if is_valid_type(item_type, valid_types):
                    main_entity = json_data.get("mainEntityOfPage")
                    logging.info(f"Item type: {item_type}, mainEntityOfPage: {main_entity}")

                    if isinstance(main_entity, str):
                        if main_entity == page_url:
                            logging.info(f"Exact match found with string mainEntityOfPage: {json_data}")
                            return json_data
                    elif isinstance(main_entity, dict):
                        if main_entity.get("@id") == page_url:
                            logging.info(f"Exact match found with dict mainEntityOfPage: {json_data}")
                            return json_data

                    return json_data
            elif isinstance(json_data, list):
                for item in json_data:
                    result = extract_matching_item(item, valid_types, page_url)
                    if result:
                        return result
            else:
                logging.info(f"Unexpected JSON-LD format: {type(json_data)} - {json_data}")
            return None

        if 'youtube.com' in page_url:
            json_ld_scripts = self.extract_json_ld_youtube(page_url)
        else:
            json_ld_scripts = self.extract_json_ld_selenium(page_url)

        if not json_ld_scripts:
            logging.info("No JSON-LD scripts found.")
            return None

        valid_types = {
            "NewsArticle", "Article", "BackgroundNewsArticle",
            "ReportageNewsArticle", "VideoObject", "BlogPosting",
            "PodcastEpisode"
        }

        potential_matches = []
        for script in json_ld_scripts:
            try:
                logging.info(f"Processing script: {script}")
                if isinstance(script, dict) and '@graph' in script:
                    logging.info(f"Processing @graph data: {script['@graph']}")
                    for item in script['@graph']:
                        result = extract_matching_item(item, valid_types, page_url)
                        if result:
                            return result
                elif isinstance(script, dict):
                    result = extract_matching_item(script, valid_types, page_url)
                    if result:
                        return result
                else:
                    logging.info(f"Script is not a dictionary: {type(script)} - {script}")
            except Exception as e:
                logging.error(f"Error processing script: {e}")
                continue

        if potential_matches:
            logging.info("Returning the first potential match.")
            return potential_matches[0]

        logging.info("No matching JSON-LD found.")
        return None


    @staticmethod
    def extract_json_ld_selenium(url: str):
        """
        Extracts JSON-LD data from a webpage using Selenium.
        Args:
            url (str): The URL of the webpage to extract JSON-LD from.
        Returns:
            list: A list of JSON-LD objects extracted from the webpage.
        """
        def make_json_valid(malformed_json: str) -> str:
            """
            Attempts to fix malformed JSON strings and return valid JSON.
            Args:
                malformed_json (str): The malformed JSON string.
            Returns:
                str: A corrected JSON string or raises an error if unfixable.
            """
            try:
                jsonrepair = pythonmonkey.require('jsonrepair').jsonrepair
                repaired = jsonrepair(malformed_json)
                return repaired
            except demjson3.JSONDecodeError as e:
                logging.error(f"Failed to fix JSON: {e}")
                return None

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state('domcontentloaded')

            json_ld_scripts = page.query_selector_all('script[type="application/ld+json"]')
            all_json_ld_data = []
            for script in json_ld_scripts:
                try:
                    json_ld_content = script.inner_text()
                    try:
                        json_ld_data = json.loads(json_ld_content)
                    except json.JSONDecodeError:
                        logging.info(f"Attempting to fix malformed JSON:\n{json_ld_content[:100]}...")
                        fixed_json = make_json_valid(json_ld_content)
                        if fixed_json:
                            json_ld_data = json.loads(fixed_json)
                        else:
                            continue

                    all_json_ld_data.append(json_ld_data)
                except Exception as e:
                    logging.error(f"An error occurred while processing script: {e}")
                    continue

            browser.close()
            return all_json_ld_data if all_json_ld_data else None