import os

import requests
from dotenv import load_dotenv
from rdflib import Graph, URIRef, Literal
import extruct
import json

load_dotenv()
class AuthorMetadataExtractor:
    def __init__(self):
        self.author_graph = Graph()
        self.json_ld_data = []
        self.article_content = ""

    def extract_metadata(self, url):
        try:
            response = requests.get(url)
            html_content = response.text
            self.article_content = html_content
            metadata = extruct.extract(html_content, base_url=url,
                                       syntaxes=["json-ld", "microdata", "rdfa", "opengraph"])
            self.json_ld_data = metadata.get("json-ld", [])
            return metadata
        except requests.exceptions.RequestException as e:
            return {}

    def extract_author(self):
        for json_ld in self.json_ld_data:
            author = json_ld.get('author')
            if isinstance(author, list) and author:
                return author[0].get('name')
            elif isinstance(author, dict):
                return author.get('name')
        return None

    def add_author_to_graph(self, article_url, author_name):
        if author_name:
            author_uri = URIRef(f"http://example.org/authors/{author_name.replace(' ', '_')}")
            self.author_graph.add((URIRef(article_url), URIRef("http://schema.org/author"), author_uri))
            self.author_graph.add((author_uri, URIRef("http://schema.org/name"), Literal(author_name)))
            self.add_additional_author_details(author_uri, author_name)

    def add_additional_author_details(self, author_uri, author_name):
        wikipedia_data = self.get_wikipedia_data(author_name)
        if wikipedia_data:
            nationality = wikipedia_data.get('nationality')
            occupation = wikipedia_data.get('occupation')
            if nationality:
                self.author_graph.add((author_uri, URIRef("http://schema.org/nationality"), Literal(nationality)))
            if occupation:
                self.author_graph.add((author_uri, URIRef("http://schema.org/occupation"), Literal(occupation)))

    def get_wikipedia_data(self, author_name):
        formatted_name = author_name.replace(' ', '_')
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={formatted_name}&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            page = next(iter(pages.values()), {})
            if page:
                extract = page.get("extract", "")
                nationality = self.extract_nationality(extract)
                occupation = self.extract_occupation(extract)
                return {'nationality': nationality, 'occupation': occupation}
        return None

    def extract_nationality(self, extract_text):
        if "Irish" in extract_text:
            return "Irish"
        return None

    def extract_occupation(self, extract_text):
        if "foreign correspondent" in extract_text:
            return "Foreign Correspondent"
        return None

    def serialize_graph(self):
        try:
            print(self.author_graph.serialize(format="turtle").decode("utf-8"))
        except Exception as e:
            print(f"Error serializing RDF graph: {e}")

    def insert_graph_to_fuseki_direct(self, fuseki_url):
        sparql_endpoint = f"{fuseki_url}/NEPR-2024/data"
        headers = {'Content-Type': 'text/turtle'}
        author_graph_data = self.author_graph.serialize(format="turtle")
        response = requests.post(sparql_endpoint, data=author_graph_data, headers=headers)
        if response.status_code == 200:
            print("RDF Graph uploaded successfully!")
        else:
            print(f"Failed to upload RDF Graph. Status code: {response.status_code}")
            print("Error message:", response.text)

    def insert_metadata_to_graph(self, article_url, metadata):
        for json_ld in metadata.get("json-ld", []):
            self.insert_json_ld_to_graph(article_url, json_ld)
        for item in metadata.get("microdata", []):
            self.insert_rdfa_to_graph(article_url, item)

    def insert_json_ld_to_graph(self, article_url, json_ld):
        if 'title' in json_ld:
            self.author_graph.add((URIRef(article_url), URIRef("http://schema.org/title"), Literal(json_ld['title'])))
        if 'datePublished' in json_ld:
            self.author_graph.add((URIRef(article_url), URIRef("http://schema.org/datePublished"), Literal(json_ld['datePublished'])))

    def insert_rdfa_to_graph(self, article_url, rdfa):
        if 'author' in rdfa:
            self.add_author_to_graph(article_url, rdfa['author'])
        if 'publisher' in rdfa:
            self.author_graph.add((URIRef(article_url), URIRef("http://schema.org/publisher"), Literal(rdfa['publisher'])))

    def count_article_content(self):
        content_length = len(self.article_content)
        return content_length

    def add_content_length_to_graph(self, article_url):
        content_length = self.count_article_content()
        self.author_graph.add((URIRef(article_url), URIRef("http://schema.org/wordCount"), Literal(content_length)))

# url_test = "https://www.digi24.ro/stiri/externe/premierul-suediei-nu-suntem-in-razboi-dar-nici-pace-nu-este-kristersson-a-aratat-cu-degetul-nu-doar-spre-rusia-ci-si-spre-iran-3077315"
# fuseki_url = os.getenv("FUSEKI_URL")
#
# extractor = AuthorMetadataExtractor()
#
# metadata = extractor.extract_metadata(url_test)
#
# author_name = extractor.extract_author()
#
# if author_name:
#     extractor.add_author_to_graph(url_test, author_name)
#
# extractor.insert_metadata_to_graph(url_test, metadata)
#
# extractor.add_content_length_to_graph(url_test)
#
# extractor.insert_graph_to_fuseki_direct(fuseki_url)
