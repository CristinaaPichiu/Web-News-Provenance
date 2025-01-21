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
        self.rdfa_data = self.scraper.extract_rdfa(url)

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
            name = entity_data.get('name')
            print(f"Adding additional details for {entity_type}: {entity_data}")

            if is_organization:
                self.add_organization_details(entity_uri, name)
            else:
                self.add_additional_person_details(entity_uri, name)

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
                        if predicate_uri in ['<http://schema.org/cssSelector>', '<http://schema.org/height>']:
                            continue
                        self.graph.add((URIRef(article_url), predicate_uri, Literal(item)))

            elif isinstance(value, dict):
                if key in ['image', 'thumbnailUrl', 'cssSelector', 'height', 'width', 'logo']:
                    continue
                else:
                    node_uri = self.generate_entity_uri_item(namespace, key, value)
                    self.graph.add((URIRef(article_url), predicate_uri, node_uri))
                    if key == 'author' or key == 'publisher':
                        self.add_entity_to_graph(node_uri, value, is_organization=(key == 'publisher'), entity_type=key)
                    # Recursively add the dictionary as a node
                    self.insert_json_ld_to_graph(node_uri, value)
            else:
                if predicate_uri in ['<http://schema.org/cssSelector>', '<http://schema.org/height>']:
                    continue
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

    def insert_rdfa_to_graph(self, article_url, cleaned_data):
        """
        Inserts cleaned RDFa data into the RDF graph, ensuring no duplicate triples are added.

        Args:
            article_url (str): The URL of the article.
            cleaned_data (dict): Cleaned RDFa data with relevant fields for schema.org Article.
        """
        # List of schema.org fields for the Article
        schema_fields = {
            "headline": "http://schema.org/headline",
            "description": "http://schema.org/description",
            "image": "http://schema.org/image",
            "imageAlt": "http://schema.org/image",
            "url": "http://schema.org/url",
            "publisher": "http://schema.org/publisher",
            "articleType": "http://schema.org/articleType",
            "dateModified": "http://schema.org/dateModified",
            "datePublished": "http://schema.org/datePublished",
            "author": "http://schema.org/author",
        }

        # Iterate through the cleaned data to populate the graph
        for key, value in cleaned_data.items():
            if key in schema_fields:
                # Get the schema.org URI for the field
                predicate_uri = URIRef(schema_fields[key])

                # Check if the value is a string and handle it
                if isinstance(value, str):
                    # Check if the triple already exists
                    if (URIRef(article_url), predicate_uri, Literal(value)) not in self.graph:
                        self.graph.add((URIRef(article_url), predicate_uri, Literal(value)))

                # Handle lists of strings (e.g., authors or other multi-value fields)
                elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], str):
                    for item in value:
                        if (URIRef(article_url), predicate_uri, Literal(item)) not in self.graph:
                            self.graph.add((URIRef(article_url), predicate_uri, Literal(item)))

                # Check if the key is 'author' or 'publisher' and treat them as entities
                elif key == 'author' or key == 'publisher':
                    # Create a node URI for the entity (author or publisher)
                    node_uri = self.generate_entity_uri_item(article_url, key, value)

                    # Add the entity to the graph, if it's not already there
                    if (URIRef(article_url), predicate_uri, node_uri) not in self.graph:
                        self.graph.add((URIRef(article_url), predicate_uri, node_uri))

                    # Add the entity itself to the graph if it's not there yet
                    self.add_entity_to_graph(node_uri, value, is_organization=(key == 'publisher'), entity_type=key)

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
        language_code = article_data.get("language_code")
        language_name = article_data.get("language_name")
        if not language_code or language_name == "Unknown language":
            return

        print(f"Detected language: {language_name}")
        print(f"Detected language code: {language_code}")
        self.graph.add(
            (URIRef(article_url), URIRef("http://schema.org/inLanguage"), Literal(language_name))
        )

    def add_keywords_to_graph(self, article_url):
        """
        Adds the keywords of an article to the graph.

        Args:
            article_url (str): The URL of the article.

        Returns:
            None
        """
        article_data = self.scraper.extract_data(article_url)
        keywords = article_data.get("keywords")
        if not keywords:
            return

        for keyword in keywords:
            self.graph.add(
                (URIRef(article_url), URIRef("http://schema.org/keywords"), Literal(keyword))
            )