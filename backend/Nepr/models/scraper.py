import demjson3
from playwright.sync_api import sync_playwright
import json
from goose3 import Goose
import extruct
import langcodes
import requests
from bs4 import BeautifulSoup
import logging
import time
from langdetect import DetectorFactory, detect_langs
import spacy
from newspaper import Article
import pythonmonkey

class BeautifulSoupScraper:
    """A scraper class using BeautifulSoup to extract data from web pages."""

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        DetectorFactory.seed = 0
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        self.max_attempts = 3
        self.timeout = 10
        self.nlp = spacy.load("en_core_web_sm")
        self.driver = None
        self.soup = None

    def extract_json_ld(self, url):
        """
        Extracts structured metadata (JSON-LD, RDFa, etc.) from a given URL.
        Args:
            url (str): The URL of the webpage to extract metadata from.
        Returns:
            dict: A dictionary containing all extracted metadata.
        """
        try:

            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            response.raise_for_status()
            html_content = response.text
            self.soup = soup
            json_ld_data = self.extract_main_article_json_ld(soup, html_content, url)
            return json_ld_data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL: {e}")
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
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            rdfa_extracted = extruct.extract(html_content, syntaxes=['rdfa'])
            print(f"Extracted RDFa data: {rdfa_extracted}")

            rdfa_data_extracted = rdfa_extracted.get('rdfa', [])
            if rdfa_data_extracted:
                return rdfa_data_extracted[0]
            else:
                return None

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except Exception as e:
            print(f"Error extracting RDFa: {e}")
            return None
    @staticmethod
    def clean_rdfa_for_schema(rdfa_data_extracted):
        """
        Clean up the RDFa data and prepare it for schema.org Article schema.
        Args:
            rdfa_data_extracted (list): The list containing extracted RDFa data.
        Returns:
            dict: Cleaned-up dictionary with necessary fields for schema.org Article schema.
        """
        cleaned_data = {}
        if rdfa_data_extracted:
            for key, value in rdfa_data_extracted.items():
                # Extract relevant information for schema.org Article
                if key == 'http://ogp.me/ns#title':
                    cleaned_data["headline"] = value[0].get('@value', '')
                elif key == 'http://ogp.me/ns#description':
                    cleaned_data["description"] = value[0].get('@value', '')
                elif key == 'http://ogp.me/ns#image':
                    cleaned_data["image"] = value[0].get('@value', '')
                elif key == 'http://ogp.me/ns#image:alt':
                    cleaned_data["imageAlt"] = value[0].get('@value', '')
                elif key == 'al:web:url':
                    cleaned_data["url"] = value[0].get('@value', '')
                elif key == 'http://ogp.me/ns#site_name':
                    cleaned_data["publisher"] = value[0].get('@value', '')
                elif key == 'http://ogp.me/ns#type':
                    cleaned_data["articleType"] = value[0].get('@value', '')
                elif key == 'http://ogp.me/ns#updated_time':
                    cleaned_data["dateModified"] = value[0].get('@value', '')
                elif key == 'http://ogp.me/ns#published_time':
                    cleaned_data["datePublished"] = value[0].get('@value', '')
                elif key == 'http://ogp.me/ns#author':
                    cleaned_data["author"] = value[0].get('@value', '')
        return cleaned_data

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
            print(f"Error parsing article: {e}")
            return None

    def extract_data(self, url):
        """Extracts data from a webpage."""
        response = self._get_html_content(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Goose for article extraction
        g = Goose()
        article_goose = g.extract(url=url)

        # Newspaper for article parsing
        article = Article(url)
        article = self._parse_article(article)

        content = article_goose.cleaned_text
        language_code, language_name = self.detect_language(response, soup, content)
        keywords = article.keywords if article else None

        return {
            "content": content,
            "language_code": language_code,
            "language_name": language_name,
            "keywords": keywords
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
        # Check the `Content-Language` header
        content_language = response.headers.get('Content-Language')
        if content_language:
            lang_code = content_language.split(',')[0]
            full_name = self.get_full_language_name(lang_code)
            return lang_code, full_name

        # Check the `lang` attribute in the HTML `<html>` tag
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
        print(f"Detected language: {language_code}")
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
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state('domcontentloaded')
            json_ld_scripts = page.query_selector_all('script[type="application/ld+json"]')
            json_ld_data = []
            for script in json_ld_scripts:
                script_content = script.inner_text()
                try:
                    json_data = json.loads(script_content)
                    json_ld_data.append(json_data)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from script: {script_content}")

            browser.close()
            if not json_ld_data:
                print("No JSON-LD scripts found.")
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
            Returns the first matching item or None.
            """
            if isinstance(json_data, dict):
                item_type = json_data.get('@type')
                if is_valid_type(item_type, valid_types):
                    if json_data.get("mainEntityOfPage", {}).get("@id") == page_url:
                        print(f"Exact match found: {json_data}")
                        return json_data
                    return json_data  # Add to potential matches
            elif isinstance(json_data, list):
                for item in json_data:
                    result = extract_matching_item(item, valid_types, page_url)
                    if result:
                        return result
            return None

        # Step 1: Determine the source of JSON-LD data
        if 'youtube.com' in page_url:
            json_ld_scripts = self.extract_json_ld_youtube(page_url)
        else:
            json_ld_scripts = self.extract_json_ld_selenium(page_url)

        if not json_ld_scripts:
            print("No JSON-LD scripts found.")
            return None

        # Step 2: Define valid types
        valid_types = {
            "NewsArticle", "Article", "BackgroundNewsArticle",
            "ReportageNewsArticle", "VideoObject", "BlogPosting",
            "PodcastEpisode"
        }

        # Step 3: Process each JSON-LD script
        potential_matches = []
        for script in json_ld_scripts:
            try:
                # Handle @graph if present
                if '@graph' in script:
                    print(f"Processing @graph data: {script['@graph']}")
                    for item in script['@graph']:
                        result = extract_matching_item(item, valid_types, page_url)
                        if result:
                            return result
                else:
                    result = extract_matching_item(script, valid_types, page_url)
                    if result:
                        return result
            except Exception as e:
                print(f"Error processing script: {e}")
                continue

        # Step 4: Fallback logic if no exact match is found
        if potential_matches:
            print("Returning the first potential match.")
            return potential_matches[0]

        print("No matching JSON-LD found.")
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
                print(f"Failed to fix JSON: {e}")
                return None

        # Initialize Playwright and run in headless mode
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
                        # First, try parsing as-is
                        json_ld_data = json.loads(json_ld_content)
                    except json.JSONDecodeError:
                        # If it fails, attempt to fix the JSON
                        print(f"Attempting to fix malformed JSON:\n{json_ld_content[:100]}...")
                        fixed_json = make_json_valid(json_ld_content)
                        if fixed_json:
                            json_ld_data = json.loads(fixed_json)
                        else:
                            continue

                    all_json_ld_data.append(json_ld_data)
                except Exception as e:
                    print(f"An error occurred while processing script: {e}")
                    continue

            browser.close()
            return all_json_ld_data if all_json_ld_data else None