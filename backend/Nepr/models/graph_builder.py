import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from langcodes import Language
from rdflib import Graph, URIRef, Literal
import requests
import extruct
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from models.scraper import BeautifulSoupScraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class GraphBuilder:
    def __init__(self):
        self.graph = Graph()
        self.json_ld_data = []
        self.rdfa_data = []
        self.scraper = BeautifulSoupScraper()
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=Options().add_argument("--headless"))
        self.soup = None
    def extract_metadata(self, url):
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
            metadata = extruct.extract(
                html_content,
                base_url=url,
                syntaxes=["json-ld", "microdata", "rdfa", "opengraph"]
            )
            self.soup = soup
            self.json_ld_data = self.extract_main_article_json_ld(soup, html_content, url)
            print(self.json_ld_data)
            self.rdfa_data = metadata.get("rdfa", [])
            return metadata
        except requests.exceptions.RequestException as e:
            return {"json-ld": [], "rdfa": []}

    def extract_json_ld_from_html(self,url):
        if 'youtube' not in url:
            json_ld_scripts = self.soup.find_all("script", type="application/ld+json")
            if json_ld_scripts:
                return json_ld_scripts
            else:
                return None;
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

        json_ld_script = []
        types = {"NewsArticle", "Article", "ReportageNewsArticle", "VideoObject", "BlogPosting"}
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

    def extract_author(self):
        for json_ld in self.json_ld_data:
            author = json_ld.get('author')
            if isinstance(author, list) and author:
                return author[0].get('name')
            elif isinstance(author, dict):
                return author.get('name')
        return None

    def extract_publisher(self):
        for json_ld in self.json_ld_data:
            publisher = json_ld.get('publisher')
            if isinstance(publisher, list) and publisher:
                return publisher[0].get('name')
            elif isinstance(publisher, dict):
                return publisher.get('name')
        return None

    def add_entity_to_graph(self, article_url, entity_name, is_organization=False, entity_type='author'):
        entity_uri = URIRef(f"/{entity_type}s/{entity_name.replace(' ', '_')}")
        self.graph.add((URIRef(article_url), URIRef(f"http://schema.org/{entity_type}"), entity_uri))
        self.graph.add((entity_uri, URIRef("http://schema.org/name"), Literal(entity_name)))

        if is_organization:
            self.add_organization_details(entity_uri, entity_name)
        else:
            self.add_additional_person_details(entity_uri, entity_name)

    def add_additional_person_details(self, entity_uri, entity_name):
        wikidata_data = self.get_wikidata_data(entity_name)
        if wikidata_data:
            for key, value in wikidata_data.items():
                if value:
                    self.graph.add((entity_uri, URIRef(f"http://schema.org/{key}"), Literal(value)))

    def add_organization_details(self, entity_uri, entity_name):
        wikidata_data = self.get_organization_wikidata_data(entity_name)
        if wikidata_data:
            for key, value in wikidata_data.items():
                if value:
                    self.graph.add((entity_uri, URIRef(f"http://schema.org/{key}"), Literal(value)))

    def get_wikidata_data(self, entity_name):
        """
        Fetch structured data for an entity (author or organization) from Wikidata.
        """
        sparql_endpoint = "https://query.wikidata.org/sparql"
        query = f"""
        SELECT ?entity ?entityLabel ?nationality ?nationalityLabel ?occupation ?occupationLabel 
               ?birthDate ?birthPlace ?birthPlaceLabel ?deathDate ?deathPlace ?deathPlaceLabel 
               ?affiliation ?affiliationLabel ?gender WHERE {{
          ?entity rdfs:label "{entity_name}"@en;
                  OPTIONAL {{ ?entity wdt:P27 ?nationality. }} 
                  OPTIONAL {{ ?entity wdt:P106 ?occupation. }} 
                  OPTIONAL {{ ?entity wdt:P569 ?birthDate. }} 
                  OPTIONAL {{ ?entity wdt:P19 ?birthPlace. }} 
                  OPTIONAL {{ ?entity wdt:P20 ?deathPlace. }} 
                  OPTIONAL {{ ?entity wdt:P570 ?deathDate. }} 
                  OPTIONAL {{ ?entity wdt:P108 ?affiliation. }} 
                  OPTIONAL {{ ?entity wdt:P21 ?gender. }} 
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
        }}
        LIMIT 1
        """
        try:
            response = requests.get(sparql_endpoint, params={"query": query, "format": "json"})
            response.raise_for_status()

            data = response.json()
            if data['results']['bindings']:
                result = data['results']['bindings'][0]
                return {
                    'nationality': result['nationalityLabel']['value'] if 'nationalityLabel' in result else None,
                    'jobTitle': result['occupationLabel']['value'] if 'occupationLabel' in result else None,
                    'birthDate': result['birthDate']['value'] if 'birthDate' in result else None,
                    'birthPlace': result['birthPlaceLabel']['value'] if 'birthPlaceLabel' in result else None,
                    'deathDate': result['deathDate']['value'] if 'deathDate' in result else None,
                    'deathPlace': result['deathPlaceLabel']['value'] if 'deathPlaceLabel' in result else None,
                    'affiliation': result['affiliationLabel']['value'] if 'affiliationLabel' in result else None,
                    'gender': result['genderLabel']['value'] if 'genderLabel' in result else None
                }
            return None
        except requests.exceptions.RequestException as e:
            return None

    def get_organization_wikidata_data(self, entity_name):
        """
        Fetch structured data for an organization (e.g., nationality, industry, CEO, publishing principles) from Wikidata.
        """
        sparql_endpoint = "https://query.wikidata.org/sparql"
        query = f"""
        SELECT ?entity ?entityLabel ?industry ?industryLabel ?foundingDate ?headquartersLocation 
               ?CEO ?CEOLabel ?officialWebsite ?publishingPrinciples WHERE {{
          ?entity rdfs:label "{entity_name}"@en;
                 wdt:P31 wd:Q43229;  # Organization class
                 wdt:P452 ?industry;  # Industry
                 wdt:P571 ?foundingDate;  # Founding Date
                 wdt:P159 ?headquartersLocation;  # Headquarters Location
                 wdt:P1323 ?CEO;  # CEO
                 wdt:P856 ?officialWebsite.  # Official Website
                 OPTIONAL {{ ?entity wdt:P1454 ?publishingPrinciples. }}  # Optional: publishing principles, ethical guidelines, etc.
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
        }}
        LIMIT 1
        """
        try:
            response = requests.get(sparql_endpoint, params={"query": query, "format": "json"})
            response.raise_for_status()

            data = response.json()
            if data['results']['bindings']:
                result = data['results']['bindings'][0]
                return {
                    'industry': result['industryLabel']['value'] if 'industryLabel' in result else None,
                    'foundingDate': result['foundingDate']['value'] if 'foundingDate' in result else None,
                    'headquartersLocation': result['headquartersLocation'][
                        'value'] if 'headquartersLocation' in result else None,
                    'CEO': result['CEOLabel']['value'] if 'CEOLabel' in result else None,
                    'officialWebsite': result['officialWebsite']['value'] if 'officialWebsite' in result else None,
                    'publishingPrinciples': result['publishingPrinciples'][
                        'value'] if 'publishingPrinciples' in result else None
                }
            return None
        except requests.exceptions.RequestException as e:
            return None

    def insert_metadata_to_graph(self, article_url, metadata):
        for json_ld in metadata:
            self.insert_json_ld_to_graph(article_url, json_ld)

    def insert_json_ld_to_graph(self, article_url, json_ld):
        for key, value in json_ld.items():
            # Create the full URI using a base URI
            uri = f"http://schema.org/{key}"

            # Check if the value is a list or other complex structure, and handle accordingly
            if isinstance(value, list):
                for item in value:
                    self.graph.add((URIRef(article_url), URIRef(uri), Literal(item)))
            else:
                self.graph.add((URIRef(article_url), URIRef(uri), Literal(value)))

    def insert_rdfa_to_graph(self, article_url, rdfa):
        if 'author' in rdfa:
            author_name = rdfa['author']
            self.add_entity_to_graph(article_url, author_name)
        if 'publisher' in rdfa:
            publisher_name = rdfa['publisher']
            self.add_entity_to_graph(article_url, publisher_name, is_organization=True, entity_type='publisher')

    def add_content_length_to_graph(self, article_url):
        article_data = self.scraper.extract_data(article_url)
        content = article_data.get("content")
        content_words_count = len(content.split())
        self.graph.add(
            (URIRef(article_url), URIRef("http://schema.org/wordCount"), Literal(content_words_count))
        )

    def add_inLanguage_to_graph(self, article_url):
        article_data = self.scraper.extract_data(article_url)
        language_code = article_data.get("language")
        if not language_code:
            return
        try:
            language_full_name = Language.get(language_code.lower()).display_name()
        except Exception as e:
            language_full_name = "Unknown Language"

        if language_full_name == "Unknown Language":
            language_full_name = language_code.upper()  # Fallback to code as full name (e.g., EN)
        self.graph.add(
            (URIRef(article_url), URIRef("http://schema.org/inLanguage"), Literal(language_full_name))
        )

