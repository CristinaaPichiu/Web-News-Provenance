import json
import os
from bs4 import BeautifulSoup
from langcodes import Language
from rdflib import Graph, URIRef, Literal
import requests
import extruct
from models.scraper import BeautifulSoupScraper


class GraphBuilder:
    def __init__(self, url):
        self.graph = Graph()
        self.json_ld_data = []
        self.rdfa_data = []
        self.scraper = BeautifulSoupScraper()
        self.json_ld_data = self.scraper.extract_json_ld(url)

    def add_entity_to_graph(self, entity_uri, entity_data, is_organization=False, entity_type='author'):
        """
        Adds an entity to the graph, handling both authors and publishers, and enriching their details if available.
        """
        # Check if the entity is a literal (name) or a dictionary (additional details)
        if isinstance(entity_data, str):
            self.graph.add((entity_uri, URIRef("http://schema.org/name"), Literal(entity_data)))

            # Add additional details (from Wikidata or other sources) for authors or organizations
            if is_organization:
                self.add_organization_details(entity_uri, entity_data)
            else:
                self.add_additional_person_details(entity_uri, entity_data)

        elif isinstance(entity_data, dict):
            # If it's a dictionary (additional details), only add the details
            # In this case, we assume the entity's name has already been added
            print(f"Adding additional details for {entity_type}: {entity_data}")
            if is_organization:
                self.add_organization_details(entity_uri, entity_data['name'])
            else:
                self.add_additional_person_details(entity_uri, entity_data['name'])

    def add_additional_person_details(self, entity_uri, entity_name):
        wikidata_data = self.get_wikidata_data(entity_name)
        print(f"Adding additional details for person: {wikidata_data}")
        if wikidata_data:
            for key, value in wikidata_data.items():
                if value:
                    self.graph.add((URIRef(entity_uri), URIRef(f"http://schema.org/{key}"), Literal(value)))

    def add_organization_details(self, entity_uri, entity_name):
        wikidata_data = self.get_organization_wikidata_data(entity_name)
        print(f"Adding additional details for organization: {wikidata_data}")
        if wikidata_data:
            for key, value in wikidata_data.items():
                if value:
                    self.graph.add((URIRef(entity_uri), URIRef(f"http://schema.org/{key}"), Literal(value)))

    def get_wikidata_data(self, entity_name):
        """
        Fetch structured data for an entity (author or organization) from Wikidata with occupation filter for "science journalist".
        """
        sparql_endpoint = "https://query.wikidata.org/sparql"

        query = f"""
        SELECT ?entity ?entityLabel ?nationality ?nationalityLabel ?occupation ?occupationLabel 
               ?birthDate ?birthPlace ?birthPlaceLabel ?deathDate ?deathPlace ?deathPlaceLabel 
               ?affiliation ?affiliationLabel ?gender ?genderLabel WHERE {{
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
        LIMIT 5
        """

        try:
            response = requests.get(sparql_endpoint, params={"query": query, "format": "json"})
            response.raise_for_status()

            data = response.json()
            if data['results']['bindings']:
                for result in data['results']['bindings']:
                    occupation = result.get('occupationLabel', {}).get('value', '')
                    if "journalist" in occupation.lower():
                        print(f"Found journalist: {result}")
                        # Filter for a result with 'journalist' in occupation
                        return {
                            'nationality': result['nationalityLabel'][
                                'value'] if 'nationalityLabel' in result else None,
                            'jobTitle': occupation,
                            'birthDate': result['birthDate']['value'] if 'birthDate' in result else None,
                            'birthPlace': result['birthPlaceLabel']['value'] if 'birthPlaceLabel' in result else None,
                            'deathDate': result['deathDate']['value'] if 'deathDate' in result else None,
                            'deathPlace': result['deathPlaceLabel']['value'] if 'deathPlaceLabel' in result else None,
                            'affiliation': result['affiliationLabel'][
                                'value'] if 'affiliationLabel' in result else None,
                            'gender': result['genderLabel']['value'] if 'genderLabel' in result else None
                        }
                take_first = data['results']['bindings'][0]
                return {
                    'nationality': take_first['nationalityLabel'][
                        'value'] if 'nationalityLabel' in take_first else None,
                    'jobTitle': take_first['occupationLabel']['value'] if 'occupationLabel' in take_first else None,
                    'birthDate': take_first['birthDate']['value'] if 'birthDate' in take_first else None,
                    'birthPlace': take_first['birthPlaceLabel']['value'] if 'birthPlaceLabel' in take_first else None,
                    'deathDate': take_first['deathDate']['value'] if 'deathDate' in take_first else None,
                    'deathPlace': take_first['deathPlaceLabel']['value'] if 'deathPlaceLabel' in take_first else None,
                    'affiliation': take_first['affiliationLabel'][
                        'value'] if 'affiliationLabel' in take_first else None,
                    'gender': take_first['genderLabel']['value'] if 'genderLabel' in take_first else None
                }
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_organization_wikidata_data(self, entity_name):
        """
        Fetch structured data for an organization (e.g., nationality, industry, CEO, publishing principles) from Wikidata.
        """
        sparql_endpoint = "https://query.wikidata.org/sparql"

        # Construct the SPARQL query for fetching data about the organization
        query = f"""
                SELECT ?entity ?entityLabel ?industry ?industryLabel ?foundingDate ?headquartersLocation 
                       ?CEO ?CEOLabel ?officialWebsite ?publishingPrinciples WHERE {{
                  ?entity rdfs:label "{entity_name}"@en;
                          wdt:P31 wd:Q43229;  # Organization class
                          OPTIONAL {{ ?entity wdt:P452 ?industry. }}  # Industry
                          OPTIONAL {{ ?entity wdt:P571 ?foundingDate. }}  # Founding Date
                          OPTIONAL {{ ?entity wdt:P159 ?headquartersLocation. }}  # Headquarters Location
                          OPTIONAL {{ ?entity wdt:P1323 ?CEO. }}  # CEO
                          OPTIONAL {{ ?entity wdt:P856 ?officialWebsite. }}  # Official Website
                          OPTIONAL {{ ?entity wdt:P1454 ?publishingPrinciples. }}  # Publishing Principles
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
                }}
                LIMIT 5
                """

        try:
            # Make the request to the SPARQL endpoint
            response = requests.get(sparql_endpoint, params={"query": query, "format": "json"})
            response.raise_for_status()

            # Print the response for debugging
            print(f"Response: {response.json()}")

            # Parse the JSON response
            data = response.json()

            if data['results']['bindings']:
                # Get the first result if available
                result = data['results']['bindings'][0]
                print(f"Found organization: {result}")
                # Extract the values, returning None if the key doesn't exist
                return {
                    'industry': result.get('industryLabel', {}).get('value', None),
                    'foundingDate': result.get('foundingDate', {}).get('value', None),
                    'headquartersLocation': result.get('headquartersLocation', {}).get('value', None),
                    'CEO': result.get('CEOLabel', {}).get('value', None),
                    'officialWebsite': result.get('officialWebsite', {}).get('value', None),
                    'publishingPrinciples': result.get('publishingPrinciples', {}).get('value', None)
                }

            # If no results are found, return None
            return None
        except requests.exceptions.RequestException as e:
            # Handle errors gracefully by returning None
            print(f"Request failed: {e}")
            return None

    def insert_metadata_to_graph(self, article_url, metadata):
        for json_ld in metadata:
            self.insert_json_ld_to_graph(article_url, json_ld)

    def insert_json_ld_to_graph(self, article_url, json_ld):
        if json_ld is None:
            return None

        for key, value in json_ld.items():
            predicate_uri = URIRef(f"http://schema.org/{key}")
            namespace = os.getenv("NAMESPACE")
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        node_uri = self.generate_entity_uri_item(namespace, key, item)
                        self.graph.add((URIRef(article_url), predicate_uri, node_uri))
                        self.insert_json_ld_to_graph(node_uri, item)
                    elif isinstance(item, str) and item.startswith("http"):  # Check if item is a URL
                        # Ensure the URL is treated as a URIRef
                        url_uri = URIRef(item)
                        self.graph.add((URIRef(article_url), predicate_uri, url_uri))
                    else:
                        self.graph.add((URIRef(article_url), predicate_uri, Literal(item)))

            elif isinstance(value, dict):
                if key == "image" and "@type" in value and value["@type"] == "ImageObject":

                    if "url" in value:
                        # If the 'url' field is a list of URLs, process each one
                        for url in value["url"]:
                            node_uri = self.generate_entity_uri_item(namespace, key, url)
                            self.graph.add((URIRef(node_uri), predicate_uri, URIRef(url)))
                else:
                    node_uri = self.generate_entity_uri_item(namespace, key, value)
                    self.graph.add((URIRef(article_url), predicate_uri, node_uri))
                    if key == 'author' or key == 'publisher':
                        self.add_entity_to_graph(node_uri, value, is_organization=(key == 'publisher'), entity_type=key)
                    # Recursively add the dictionary as a node
                    self.insert_json_ld_to_graph(node_uri, value)
            else:
                self.graph.add((URIRef(article_url), predicate_uri, Literal(value)))

    @staticmethod
    def generate_entity_uri_item(namespace, key, item):
        if isinstance(item, dict):
            if 'url' in item and item['url'] != "":
                return URIRef(item['url'])
            elif 'name' in item:
                name_normalized = item['name'].replace(' ', '_')
                return URIRef(f"{namespace}/{key}/{name_normalized}")
            else:
                return URIRef(f"{namespace}/{key}/{hash(str(item))}")
        else:
            normalized_item = item.replace(' ', '_')
            return URIRef(f"{namespace}/{key}/{normalized_item}")

    def insert_rdfa_to_graph(self, article_url, rdfa):
        if 'author' in rdfa:
            author_name = rdfa['author']
            self.add_entity_to_graph(URIRef(article_url), author_name)
        if 'publisher' in rdfa:
            publisher_name = rdfa['publisher']
            self.add_entity_to_graph(URIRef(article_url), publisher_name, is_organization=True, entity_type='publisher')

    def add_content_length_to_graph(self, article_url):
        article_data = self.scraper.extract_data(article_url)
        content = article_data.get("content")
        content_words_count = len(content.split())
        self.graph.add(
            (URIRef(article_url), URIRef("http://schema.org/wordCount"), Literal(content_words_count))
        )

    def add_inLanguage_to_graph(self, article_url):
        """
        Adds the language information of an article to the graph.

        Args:
            article_url (str): The URL of the article.

        Returns:
            None
        """
        # Extract language code from the article's metadata
        article_data = self.scraper.extract_data(article_url)
        language_code = article_data.get("language")

        if not language_code:
            return


        language_full_name = Language.get(language_code.lower()).display_name()
        if "Unknown language" in language_full_name:
            language_full_name = language_code.upper()

        print(f"Detected language: {language_full_name}")
        print(f"Detected language code: {language_code}")
        self.graph.add(
            (URIRef(article_url), URIRef("http://schema.org/inLanguage"), Literal(language_full_name))
        )
