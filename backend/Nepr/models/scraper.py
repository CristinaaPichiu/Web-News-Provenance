import html
import urllib
from copy import deepcopy
from functools import wraps
import requests
from bs4 import BeautifulSoup
import logging
import time
import re
import json
import os
import sys

class BeautifulSoupScraper:
    """A scraper class using BeautifulSoup to extract data from web pages."""
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

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

        return {
            "content": content,
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