import html
import json

import extruct
import requests
from bs4 import BeautifulSoup
import logging
import time
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class BeautifulSoupScraper:
    """A scraper class using BeautifulSoup to extract data from web pages."""
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        DetectorFactory.seed = 0
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

    def extract_data(self, url):
        """Extracts data from a webpage."""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/87.0.4280.88 Safari/537.36"
            )
        }

        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    break
            except requests.RequestException as e:
                raise ValueError(f"Request failed (Attempt {attempt + 1}).")
                time.sleep(2)
        else:
            raise ValueError("Failed to retrieve webpage after multiple attempts.")

        soup = BeautifulSoup(response.content, 'html.parser')
        content = self.extract_content(soup) or "No content available"
        language = self.detect_language(response, soup, content)
        keywords = self.extract_keywords(content, language)
        return {
            "content": content,
            "language": language,
            "keywords": keywords
        }

    def extract_content(self, soup):
        """Extracts the main content of the article."""
        for tag in soup(['header', 'footer', 'nav', 'aside', 'form', 'iframe', 'img', 'div.social', 'figure']):
            tag.decompose()
        content_selectors = ['article', 'div.article-content', 'div.content-body', 'div.post-content',
                             'div.data-app-meta-article']
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                paragraphs = element.find_all('p')
                print(f"Extracted paragraphs: {[p.get_text(strip=True) for p in paragraphs]}")
                filtered_paragraphs = [
                    html.unescape(p.get_text(strip=True)) for p in paragraphs if len(p.get_text(strip=True)) > 10
                ]
                print(f"Filtered paragraphs: {filtered_paragraphs}")

                if filtered_paragraphs:
                    return "\n".join(filtered_paragraphs)

        return None

    def detect_language(self, response, soup, content):
        """
        Detects the language of the article using headers, HTML attributes, or text analysis.
        """
        # Check the `Content-Language` header
        content_language = response.headers.get('Content-Language')
        if content_language:
            return content_language.split(',')[0]

        # Check the `lang` attribute in the HTML `<html>` tag
        html_lang = soup.html.get('lang') if soup.html else None
        if html_lang:
            return html_lang.split('-')[0]

        if content:
            try:
                detected_lang = detect(content)
                return detected_lang
            except LangDetectException:
                logging.warning("Failed to detect language using text analysis.")

        return None


    def extract_keywords(self, content, language):
        """Extracts keywords from content, based on the language of the article."""
        keywords = []

        if language == "en":
            vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=10)
            tfidf_matrix = vectorizer.fit_transform([content])
            feature_names = vectorizer.get_feature_names_out()
            keywords = feature_names

        else:
            doc = self.nlp(content)
            for token in doc:
                if token.is_stop == False and token.is_punct == False:
                    keywords.append(token.text)

        keywords_string = ", ".join(keywords)

        return keywords_string

    def extract_json_ld_from_html(self, url):
        """
        Extracts JSON-LD from a webpage using the 'application/ld+json' script type.

        Args:
            url (str): The URL of the webpage to extract JSON-LD from.

        Returns:
            list: A list of JSON-LD scripts or None if none are found.
        """
        # Step 1: Make an initial request
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch URL: {url}")
            return None

        # Step 2: Process static content (without dynamic loading)
        if 'youtube' not in url:
            # Initialize BeautifulSoup for static HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            json_ld_scripts = soup.find_all("script", type="application/ld+json")
            if json_ld_scripts:
                return json_ld_scripts
            else:
                return None

        # Step 3: Process dynamic content (for YouTube or other dynamic pages)
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get(url)

        try:
            # Wait for the body tag to be loaded (or another relevant tag or element on your page)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, 'player-microformat-renderer'))
            )
        except Exception as e:
            print(f"Error waiting for page to load: {e}")
            self.driver.quit()
            return None

        # Get the page source after dynamic content has been loaded
        html_content = self.driver.page_source
        self.driver.quit()  # Close the browser

        # Initialize BeautifulSoup for dynamic HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        json_ld_scripts = soup.find_all("script", type="application/ld+json")

        if not json_ld_scripts:
            print("No JSON-LD scripts found.")
            return None

        return json_ld_scripts

    def extract_main_article_json_ld(self, soup, html_content, page_url):
        """
        Extracts the main article JSON-LD object, prioritizing one with matching 'mainEntityOfPage' or 'url'.
        If no match is found, it returns the article with the longest title or the one with the given page URL.

        Args:
            soup (BeautifulSoup): The parsed HTML content of the page.
            html_content (str): The raw HTML content of the webpage.
            page_url (str): The URL of the webpage.

        Returns:
            dict: The JSON-LD object for the main article, or None if no match is found.
        """
        json_ld_scripts = self.extract_json_ld_from_html(page_url)

        if not json_ld_scripts:  # Check if json_ld_scripts is None or empty
            print("No JSON-LD scripts found.")
            return None

        json_ld_script = []
        types = {"NewsArticle", "Article", "ReportageNewsArticle", "VideoObject", "BlogPosting","PodcastEpisode"}
        # Parse all JSON-LD scripts and collect articles
        for script in json_ld_scripts:
            try:
                json_data = json.loads(script.string)
                print(f"Parsed JSON data: {json_data}")

                if isinstance(json_data, list):
                    # Handle the case where json_data is a list
                    for item in json_data:
                        print(f"Inspecting list item: {item}")
                        if isinstance(item.get('@type'), list):
                            # Check if any type in the list matches desired types
                            if any(t in types for t in item.get('@type')):
                                print(f"Match found in list item (with '@type' list): {item}")
                                json_ld_script.append(item)
                                # Compare with @id inside mainEntityOfPage
                                if item.get("mainEntityOfPage") and item["mainEntityOfPage"].get("@id") == page_url:
                                    print("Match found in list item (with '@type' list):")
                                    return item
                        elif isinstance(item.get('@type'), str):
                            # Single type check
                            if item.get('@type') in types:
                                print(f"Match found in list item (with '@type' string): {item}")
                                json_ld_script.append(item)
                                # Compare with @id inside mainEntityOfPage
                                if item.get("mainEntityOfPage") and item["mainEntityOfPage"].get("@id") == page_url:
                                    print("Match found in list item (with '@type' string):")
                                    return item
                elif isinstance(json_data, dict):
                    # Handle the case where json_data is a dictionary
                    print(f"Inspecting dictionary item: {json_data}")
                    if isinstance(json_data.get('@type'), str):
                        if json_data.get('@type') in types:
                            json_ld_script.append(json_data)
                            if json_data.get("mainEntityOfPage"):
                                print("Match found in dictionary item:")
                                return json_data
                    elif isinstance(json_data.get('@type'), list):
                        if any(t in types for t in json_data.get('@type')):
                            json_ld_script.append(json_data)
                            if json_data.get("mainEntityOfPage") and json_data["mainEntityOfPage"].get(
                                    "@id") == page_url:
                                print("Match found in dictionary item (with '@type' list):")
                                return json_data
            except json.JSONDecodeError:
                print("JSONDecodeError occurred, skipping this script.")
                continue

        # If no match found, return the first article if available
        if json_ld_script:
            return json_ld_script[0]

        print("No matching article found.")
        return None


