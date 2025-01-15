import os
import requests
from dotenv import load_dotenv
from rdflib import Graph
from models.graph_builder import GraphBuilder

load_dotenv()

class SPARQLService:
    def __init__(self):
        self.fuseki_url = os.getenv("FUSEKI_URL")
        self.graph_builder = GraphBuilder()

    def insert_graph(self, url):
        """
        Builds an RDF graph for the given URL using GraphBuilder and inserts it into the Fuseki dataset.
        """
        metadata = self.graph_builder.extract_metadata(url)
        self.graph_builder.insert_metadata_to_graph(url, metadata)
        author_name = self.graph_builder.extract_author()
        if author_name:
            self.graph_builder.add_entity_to_graph(url, author_name, entity_type='author')
        publisher_name = self.graph_builder.extract_publisher()
        if publisher_name:
            self.graph_builder.add_entity_to_graph(url, publisher_name, is_organization=True, entity_type='publisher')
        self.graph_builder.add_content_length_to_graph(url)
        rdf_graph = self.graph_builder.graph

        sparql_endpoint = f"{self.fuseki_url}/NEPR-2024/data"
        headers = {'Content-Type': 'text/turtle'}
        graph_data = rdf_graph.serialize(format="turtle")

        try:
            response = requests.post(sparql_endpoint, data=graph_data, headers=headers)
            if response.status_code == 200:
                print("RDF Graph uploaded successfully!")
            else:
                print(f"Failed to upload RDF Graph. Status code: {response.status_code}")
                print("Error message:", response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to SPARQL endpoint: {e}")

# Example usage
# service = SPARQLService()
# service.insert_graph("https://www.bbc.com/news/articles/ce8dz0n8xldo")

