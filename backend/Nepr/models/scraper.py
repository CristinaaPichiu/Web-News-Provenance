import html
import requests
from bs4 import BeautifulSoup
import logging
import time
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy

class BeautifulSoupScraper:
    """A scraper class using BeautifulSoup to extract data from web pages."""
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        DetectorFactory.seed = 0
        self.nlp = spacy.load("en_core_web_sm")

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
        language = self.detect_language(response, soup, content) or "Language not detected"
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


