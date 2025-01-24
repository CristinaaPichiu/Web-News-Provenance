import json
import logging
import os
from bs4 import BeautifulSoup
from langcodes import Language
from rdflib import Graph, URIRef, Literal
import requests
import extruct
from selenium.webdriver.support.expected_conditions import none_of

from models.scraper import BeautifulSoupScraper
from models.entity import Person, Organization, Author, Editor, Publisher
from models.article import Article as ArticleModel
from models.multimedia import AudioObject, ImageObject, VideoObject


class GraphBuilder:
    def __init__(self, url,service,options):
        self.graph = Graph()
        self.service = service
        self.options = options
        self.scraper = BeautifulSoupScraper(service,options)
        self.article = ArticleModel(node_uri=URIRef(url))
        self.json_ld_data = self.scraper.extract_json_ld(url)
        self.rdfa_data = self.scraper.extract_rdfa(url)
        self.article_data = self.scraper.extract_data(url)

    def _add_author_to_graph(self,entity_uri, entity_data, is_organization=False):
        logging.info(f"Adding author to graph: {entity_data}")
        author = None
        if is_organization:
            organization = self._set_organization_entity(entity_uri, entity_data)
            author = Author(**organization.__dict__(), type="Organization")
            for key, value in entity_data.items():
                if value:
                    setter_method = f"set_{key}"
                    if hasattr(author.entity, setter_method):
                        getattr(author.entity, setter_method)(value)
        else:
            person = self._set_person_entity(entity_uri, entity_data)
            author = Author(**person.__dict__(), type="Person")
            for key, value in entity_data.items():
                if value:
                    setter_method = f"set_{key}"
                    if hasattr(author.entity, setter_method):
                        getattr(author.entity, setter_method)(value)

        author.entity.node_uri = URIRef(entity_uri)
        for attribute, value in author.entity.__dict__().items():
            if value and attribute != 'node_uri':
                self.graph.add(
                    (URIRef(author.entity.node_uri), URIRef(f"http://schema.org/{attribute}"), Literal(value)))
        self.graph.add((URIRef(author.entity.node_uri), URIRef("http://schema.org/@type"), Literal(author.type)))

    def _add_editor_to_graph(self,entity_uri, entity_data):
        logging.info(f"Adding editor to graph: {entity_data}")
        person = self._set_person_entity(entity_uri, entity_data)
        editor = Editor(**person.__dict__())
        for key, value in entity_data.items():
            if value:
                setter_method = f"set_{key}"
                if hasattr(editor, setter_method):
                    getattr(editor, setter_method)(value)
        editor.entity.node_uri = URIRef(entity_uri)
        for attribute, value in editor.entity.__dict__().items():
            if value and attribute != 'node_uri':
                self.graph.add(
                    (URIRef(editor.entity.node_uri), URIRef(f"http://schema.org/{attribute}"), Literal(value)))
        self.graph.add((URIRef(editor.entity.node_uri), URIRef("http://schema.org/@type"), Literal(editor.type)))

    def _add_publisher_to_graph(self,entity_uri, entity_data, is_organization=False):
        logging.info(f"Adding publisher to graph: {entity_data}")
        publisher = None
        if is_organization:
            organization = self._set_organization_entity(entity_uri, entity_data)
            publisher = Publisher(**organization.__dict__(), type="Organization")
            for key, value in entity_data.items():
                if value:
                    setter_method = f"set_{key}"
                    if hasattr(publisher.entity, setter_method):
                        getattr(publisher.entity, setter_method)(value)
        else:
            person = self._set_person_entity(entity_uri, entity_data)
            publisher = Publisher(**person.__dict__(), type="Person")
            for key, value in entity_data.items():
                if value:
                    setter_method = f"set_{key}"
                    if hasattr(publisher.entity, setter_method):
                        getattr(publisher.entity, setter_method)(value)
        publisher.entity.node_uri = URIRef(entity_uri)
        for attribute, value in publisher.entity.__dict__().items():
            if value and attribute != 'node_uri':
                self.graph.add(
                    (URIRef(publisher.entity.node_uri), URIRef(f"http://schema.org/{attribute}"), Literal(value)))
        self.graph.add((URIRef(publisher.entity.node_uri), URIRef("http://schema.org/@type"), Literal(publisher.type)))

    def _set_person_entity(self, entity_uri, entity_data):
        logging.info(f"Setting person entity: {entity_data}")
        try:
            if isinstance(entity_data, list):
                persons = []
                for item in entity_data:
                    try:
                        if isinstance(item, dict):
                            persons.append(self._set_person_entity(entity_uri, item))
                        else:
                            logging.error(f"Unexpected item type in list: {type(item)}")
                    except Exception as e:
                        logging.error(f"Error processing item in list: {item}. Error: {e}")
                return persons
            if isinstance(entity_data, str):
                try:
                    person = self.add_additional_person_details(entity_uri, entity_data)
                except Exception as e:
                    logging.error(f"Error adding additional person details for string: {entity_data}. Error: {e}")
                    return None
            else:
                person = Person(node_uri=URIRef(entity_uri))
                for key, value in entity_data.items():
                    if value:
                        setter_method = f"set_{key}"
                        try:
                            if hasattr(person, setter_method):
                                getattr(person, setter_method)(value)
                        except Exception as e:
                            logging.error(f"Error setting attribute '{key}' with value '{value}': {e}")
                try:
                    person_addition = self.add_additional_person_details(person.node_uri, person.name)
                    for key, value in person_addition.__dict__().items():
                        if value and not getattr(person, key, None):
                            setattr(person, key, value)
                except Exception as e:
                    logging.error(f"Error adding additional person details: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in _set_person_entity: {e}")
            return None

        return person

    def _set_organization_entity(self, entity_uri, entity_data):
        logging.info(f"Setting organization entity: {entity_data}")
        if isinstance(entity_data, list):
            organizations = []
            for item in entity_data:
                if isinstance(item, dict):
                    organizations.append(self._set_organization_entity(entity_uri, item))
                else:
                    logging.info(f"Unexpected item type in list: {type(item)}")
            return organizations
        if isinstance(entity_data, str):
            organization = self.add_organization_details(entity_uri, entity_data)
        else:
            organization = Organization(node_uri=URIRef(entity_uri))
            for key, value in entity_data.items():
                if value:
                    setter_method = f"set_{key}"
                    if hasattr(organization, setter_method):
                        getattr(organization, setter_method)(value)
            organization_addition = self.add_organization_details(organization.node_uri, organization.name)
            for key, value in organization_addition.__dict__().items():
                if value and not getattr(organization, key):
                    setattr(organization, key, value)
        return organization

    def add_entity_to_graph(self, entity_uri, entity_data,entity_type, is_organization):
        """
        Adds an entity to the graph, handling both authors and publishers, and enriching their details if available.
        """
        logging.info(f"Adding entity to graph: {entity_data}")
        if entity_type == 'author':
            self._add_author_to_graph(entity_uri, entity_data,is_organization)
        elif entity_type == 'editor':
            self._add_editor_to_graph(entity_uri, entity_data)
        elif entity_type == 'publisher':
            self._add_publisher_to_graph(entity_uri, entity_data,is_organization)

    def add_additional_person_details(self, entity_uri, entity_name):
        wikidata_data = self.get_wikidata_data(entity_name)
        logging.info(f"Adding additional details for person: {wikidata_data}")
        if wikidata_data:
            person = Person(name=entity_name,node_uri=URIRef(entity_uri))
            for key, value in wikidata_data.items():
                if value:
                    setter_method = f"set_{key}"
                    if hasattr(person, setter_method):
                        getattr(person, setter_method)(value)
            return person
        return Person(name=entity_name,node_uri=URIRef(entity_uri))

    def add_organization_details(self, entity_uri, entity_name):
        wikidata_data = self.get_organization_wikidata_data(entity_name)
        logging.info(f"Adding additional details for organization: {wikidata_data}")
        if wikidata_data:
            organization = Organization(name=entity_name,node_uri=URIRef(entity_uri))
            if 'publishingPrinciples' in wikidata_data:
                organization.set_publishingPrinciples(wikidata_data['publishingPrinciples'])
            return organization
        return Organization(name=entity_name,node_uri=URIRef(entity_uri))

    def get_wikidata_data(self, entity_name):
        sparql_endpoint = "https://query.wikidata.org/sparql"

        writing_keywords = [
            'journalist', 'reporter', 'writer', 'author',
            'columnist', 'editor', 'correspondent'
        ]

        query = f"""
        SELECT ?entity ?entityLabel ?nationality ?nationalityLabel 
               ?occupation ?occupationLabel ?birthDate ?birthPlace 
               ?birthPlaceLabel ?deathDate ?deathPlace ?deathPlaceLabel 
               ?affiliation ?affiliationLabel ?gender ?genderLabel
        WHERE {{
          {{
            ?entity rdfs:label "{entity_name}"@en.
          }} UNION {{
            ?entity wdt:P2561 "{entity_name}"@en.
          }}

          OPTIONAL {{ ?entity wdt:P27 ?nationality. }}
          OPTIONAL {{ ?entity wdt:P106 ?occupation. }}
          OPTIONAL {{ ?entity wdt:P569 ?birthDate. }}
          OPTIONAL {{ ?entity wdt:P19 ?birthPlace. }}
          OPTIONAL {{ ?entity wdt:P570 ?deathDate. }}
          OPTIONAL {{ ?entity wdt:P20 ?deathPlace. }}
          OPTIONAL {{ ?entity wdt:P108 ?affiliation. }}
          OPTIONAL {{ ?entity wdt:P21 ?gender. }}

          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
        }}
        LIMIT 10
        """

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/sparql-results+json'
            }

            response = requests.get(sparql_endpoint,
                                    params={"query": query, "format": "json"},
                                    headers=headers)
            response.raise_for_status()
            data = response.json()

            if not data['results']['bindings']:
                return None
            matching_results = [
                result for result in data['results']['bindings']
                if 'occupationLabel' in result and
                   result['occupationLabel'].get('value', '').lower() in writing_keywords
            ]
            if matching_results:
                logging.info(f"Matching results: {matching_results}")
                return self._extract_entity_info(matching_results[0])
            return None

        except Exception as e:
            logging.error(f"Wikidata retrieval error: {e}")
            return None

    def _extract_entity_info(self, result):
        return {
            'nationality': result.get('nationalityLabel', {}).get('value'),
            'jobTitle': result.get('occupationLabel', {}).get('value'),
            'birthDate': result.get('birthDate', {}).get('value'),
            'birthPlace': result.get('birthPlaceLabel', {}).get('value'),
            'deathDate': result.get('deathDate', {}).get('value'),
            'deathPlace': result.get('deathPlaceLabel', {}).get('value'),
            'affiliation': result.get('affiliationLabel', {}).get('value'),
            'gender': result.get('genderLabel', {}).get('value')
        }

    def get_organization_wikidata_data(self, entity_name):
        """
        Fetch structured data for an organization (e.g., nationality, industry, CEO, publishing principles) from Wikidata.
        """
        logging.info(f"Fetching Wikidata data for organization: {entity_name}")
        sparql_endpoint = "https://query.wikidata.org/sparql"

        query = f"""
                   SELECT ?entity ?publishingPrinciples WHERE {{
                     ?entity rdfs:label "{entity_name}"@en; 
                     OPTIONAL {{ ?entity wdt:P1454 ?publishingPrinciples. }}  
                   }}
                   LIMIT 10
                   """
        logging.info(query)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/sparql-results+json'
        }

        try:
            response = requests.get(sparql_endpoint, params={"query": query, "format": "json"}, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Process the results to find the first entity with publishing principles
            for result in data['results']['bindings']:
                publishing_principles = result.get('publishingPrinciples', {}).get('value')
                if publishing_principles:  # Check if publishing principles exist
                    return {
                        'organization': result['entity']['value'],  # Use entity URI
                        'publishingPrinciples': publishing_principles
                    }

            # If no entity with publishing principles is found, return None
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed- Wiki: {e}")
            return None

    @staticmethod
    def _set_key(key):
        keys = []
        logging.info(f"Setting key: {key}")
        if key == 'image' or key == 'thumbnail':
            keys = ['contentUrl', 'duration', 'embedUrl', 'height', 'uploadDate', 'width',
                    'caption', 'embeddedTextCaption','@type','url']
        elif key == 'audio':
            keys = ['contentUrl', 'duration', 'embedUrl', 'height', 'uploadDate', 'width',
                    'caption', 'transcript','@type','url']
        elif key == 'video':
            keys = ['contentUrl', 'duration', 'embedUrl', 'height', 'uploadDate', 'width',
                    'caption', 'videoQuality','@type','url']
        return keys

    def insert_json_ld_to_graph(self, article_url, json_ld, keys):

        if json_ld is None:
            return None

        try:
            logging.info(f"Inserting JSON-LD{json_ld} into the graph for article: {article_url}")
            for key, value in json_ld.items():
                predicate_uri = URIRef(f"http://schema.org/{key}")
                namespace = os.getenv("NAMESPACE")
                logging.info(f"Processing key: {key}, value: {value}")
                if key not in keys:
                    continue
                if isinstance(value, list):
                    for item in value:
                        logging.info(f"Processing item: {item}")
                        if isinstance(item, dict):
                            if key == 'author' or key == 'publisher' or key == 'editor':
                                node_uri = self.generate_entity_uri_item(namespace, key, item)
                                self.graph.add((URIRef(article_url), predicate_uri, node_uri))
                                self.add_entity_to_graph(node_uri, item, is_organization=(key == 'publisher'), entity_type=key)
                            else:
                                node_keys = self._set_key(key)
                                node_uri = self.generate_entity_uri_item(namespace, key, item)
                                self.graph.add((URIRef(article_url), predicate_uri, node_uri))
                                self.insert_json_ld_to_graph(node_uri, item, node_keys)
                        else:
                            logging.info(f"Processing value: {item}")
                            if key == 'author' or key == 'publisher' or key == 'editor':
                                node_uri = self.generate_entity_uri_item(namespace, key, item)
                                self.graph.add((URIRef(article_url), predicate_uri, node_uri))
                                self.add_entity_to_graph(node_uri, item, is_organization=(key == 'publisher'), entity_type=key)
                            else:
                                self.graph.add((URIRef(article_url), predicate_uri, Literal(item)))
                elif isinstance(value, dict):
                    logging.info(f"Processing dictionary: {value}")
                    node_uri = self.generate_entity_uri_item(namespace, key, value)
                    self.graph.add((URIRef(article_url), predicate_uri, node_uri))
                    if key == 'author' or key == 'publisher' or key == 'editor':
                        self.add_entity_to_graph(node_uri, value, is_organization=(key == 'publisher'), entity_type=key)
                    else:
                        node_keys = self._set_key(key)
                        self.insert_json_ld_to_graph(node_uri, value, node_keys)
                else:
                    logging.info(f"Processing value: {value}")
                    if key == 'inLanguage':
                            language_code = value.split('-')[0]
                            language_full_name = self.scraper.get_full_language_name(language_code)
                            self.graph.add((URIRef(article_url), predicate_uri, Literal(language_full_name)))
                    elif key == 'author' or key == 'publisher' or key == 'editor':
                        node_uri = self.generate_entity_uri_item(namespace, key, value)
                        self.graph.add((URIRef(article_url), predicate_uri, node_uri))
                        self.add_entity_to_graph(node_uri, value, is_organization=(key == 'publisher'), entity_type=key)
                    else:
                        self.graph.add((URIRef(article_url), predicate_uri, Literal(value)))
        except Exception as e:
            logging.error(f"Error inserting JSON-LD into graph: {e}")
            return None

    @staticmethod
    def generate_entity_uri_item(namespace, key, item):
        logging.info(f"Generating entity URI for item: {item}")
        if isinstance(item, dict):
            if 'name' in item:
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
        logging.info(f"Inserting RDFa data into the graph for article: {article_url}")
        schema_fields = {
            "headline": "http://schema.org/headline",
            "abstract": "http://schema.org/abstract",
            "thumbnailUrl": "http://schema.org/thumbnailUrl",
            "url": "http://schema.org/url",
            "publisher": "http://schema.org/publisher",
            "article:modified_time": "http://schema.org/dateModified",
            "article:published_time": "http://schema.org/datePublished",
            "article:author": "http://schema.org/author",
            "type": "http://schema.org/articleType",
        }
        logging.info(f"Inserting RDFa data into the graph for article: {article_url}")
        logging.info(f"Cleansed data: {cleaned_data}")
        if 'article:tag' in cleaned_data:
            cleaned_data['keyword'] = cleaned_data.pop('article:tag')
        if 'description' in cleaned_data:
            cleaned_data['abstract'] = cleaned_data.pop('description')
        if 'image' in cleaned_data:
            cleaned_data['thumbnailUrl'] = cleaned_data.pop('image')
        for key, value in cleaned_data.items():
            if key in schema_fields:
                predicate_uri = URIRef(schema_fields[key])

                if isinstance(value, str):
                    existing_values = [
                        obj for obj in self.graph.objects(subject=URIRef(article_url), predicate=predicate_uri)
                    ]

                    logging.info(f"Existing values for {key}: {[str(v) for v in existing_values]}")
                    replace_existing = False
                    for existing_value in existing_values:
                        if isinstance(existing_value, Literal):
                            existing_value_str = str(existing_value)
                            if existing_value_str.endswith("..."):  # Replace incomplete value
                                logging.info(f"Replacing incomplete value for {key}: {existing_value_str} with {value}")
                                replace_existing = True
                            elif len(existing_value_str) < len(value):  # Replace shorter value
                                logging.info(f"Replacing shorter value for {key}: {existing_value_str} with {value}")
                                replace_existing = True
                            else:
                                logging.info(
                                    f"Skipping value for {key}, as the existing value is more complete: {existing_value_str}")

                    if not existing_values or replace_existing:
                        if replace_existing:
                            for existing_value in existing_values:
                                self.graph.remove((URIRef(article_url), predicate_uri, existing_value))
                                logging.info(f"Removed value for {key}: {existing_value}")

                        self.graph.add((URIRef(article_url), predicate_uri, Literal(value)))
                        logging.info(f"Added value for {key}: {value}")

                elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], str):
                    for item in value:
                        if not item.endswith("..."):  # Skip truncated list values
                            if (URIRef(article_url), predicate_uri, Literal(item)) not in self.graph:
                                self.graph.add((URIRef(article_url), predicate_uri, Literal(item)))
                                logging.info(f"Added list value for {key}: {item}")

                elif key == 'author' or key == 'publisher':
                    node_uri = self.generate_entity_uri_item(article_url, key, value)
                    if (URIRef(article_url), predicate_uri, node_uri) not in self.graph:
                        self.graph.add((URIRef(article_url), predicate_uri, node_uri))
                        logging.info(f"Added entity for {key}: {node_uri}")
                    self.add_entity_to_graph(node_uri, value, is_organization=(key == 'publisher'), entity_type=key)

    def add_content_length_to_graph(self, article_url):
        """
        Adds the content length of an article to the graph.
        Args:
            article_url (str): The URL of the article.
        Returns:
            None
        """
        logging.info(f"Extracting content length for article: {article_url}")
        if not self.article_data:
            return
        try:
            content = self.article_data.get("content")
            content_words_count = len(content.split())
            self.graph.add(
                (URIRef(article_url), URIRef("http://schema.org/wordCount"), Literal(content_words_count))
            )
        except Exception as e:
            logging.error(f"Error adding content length to graph: {e}")

    def add_inLanguage_to_graph(self, article_url):
        """
        Adds the language information of an article to the graph.

        Args:
            article_url (str): The URL of the article.

        Returns:
            None
        """
        logging.info(f"Extracting language information for article: {article_url}")
        if not self.article_data:
            return
        try:
            language_code = self.article_data.get("language_code")
            language_name = self.article_data.get("language_name")
            if not language_code or language_name == "Unknown language":
                return

            logging.info(f"Detected language: {language_name}")
            logging.info(f"Detected language code: {language_code}")
            self.graph.add(
                (URIRef(article_url), URIRef("http://schema.org/inLanguage"), Literal(language_name))
            )
        except Exception as e:
            logging.error(f"Error adding language information to graph")

    def add_keywords_to_graph(self, article_url):
        """
        Adds the keywords of an article to the graph.

        Args:
            article_url (str): The URL of the article.

        Returns:
            None
        """
        logging.info(f"Extracting keywords for article: {article_url}")
        if not self.article_data:
            return
        try:
            keywords = self.article_data.get("keywords")
            if not keywords:
                return

            for keyword in keywords:
                self.graph.add(
                    (URIRef(article_url), URIRef("http://schema.org/keywords"), Literal(keyword))
                )
        except Exception as e:
            logging.error(f"Error adding keywords to graph: {e}")

    def add_articleBody_to_graph(self, article_url):
        """
        Adds the article body of an article to the graph.

        Args:
            article_url (str): The URL of the article.

        Returns:
            None
        """
        if not self.article_data:
            return

        try:
            article_body = self.article_data.get("content")
            if not article_body:
                return

            predicate_uri = URIRef("http://schema.org/articleBody")
            existing_values = [
                obj for obj in self.graph.objects(subject=URIRef(article_url), predicate=predicate_uri)
            ]

            for existing_value in existing_values:
                self.graph.remove((URIRef(article_url), predicate_uri, existing_value))
                logging.info(f"Removed existing articleBody: {existing_value}")
            self.graph.add((URIRef(article_url), predicate_uri, Literal(article_body)))
            logging.info(f"Added new articleBody: {article_body}")

        except Exception as e:
            logging.error(f"Error adding article body to graph: {e}")