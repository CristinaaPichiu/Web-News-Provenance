from rdflib import Graph, URIRef, Literal
import requests
import extruct
from models.scraper import BeautifulSoupScraper


class GraphBuilder:
    def __init__(self):
        self.graph = Graph()
        self.json_ld_data = []
        self.scraper = BeautifulSoupScraper()

    def extract_metadata(self, url):
        try:
            response = requests.get(url)
            html_content = response.text
            self.json_ld_data = extruct.extract(
                html_content, base_url=url, syntaxes=["json-ld", "microdata", "rdfa", "opengraph"]
            ).get("json-ld", [])
            return self.json_ld_data
        except requests.exceptions.RequestException:
            return []

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
                    'occupation': result['occupationLabel']['value'] if 'occupationLabel' in result else None,
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
        if 'title' in json_ld:
            self.graph.add((URIRef(article_url), URIRef("http://schema.org/title"), Literal(json_ld['title'])))
        if 'datePublished' in json_ld:
            self.graph.add(
                (URIRef(article_url), URIRef("http://schema.org/datePublished"), Literal(json_ld['datePublished']))
            )

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
