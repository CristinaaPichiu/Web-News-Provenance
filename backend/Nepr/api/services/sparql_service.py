import os
import requests
from dotenv import load_dotenv
from rdflib import Graph
from models.graph_builder import GraphBuilder

load_dotenv()


class SPARQLService:
    def __init__(self):
        self.fuseki_url = os.getenv("FUSEKI_URL")

    def create_graph(self, url):
        """
        Creates an RDF graph using GraphBuilder.
        """
        graph_builder = GraphBuilder(url)
        if graph_builder.json_ld_data is not None:
            graph_builder.insert_json_ld_to_graph(url, graph_builder.json_ld_data)
        if graph_builder.rdfa_data is not None:
            graph_builder.insert_rdfa_to_graph(url, graph_builder.rdfa_data)
        graph_builder.add_content_length_to_graph(url)
        graph_builder.add_inLanguage_to_graph(url)
        graph_builder.add_keywords_to_graph(url)
        rdf_graph = graph_builder.graph
        graph_turtle = rdf_graph.serialize(format="turtle")
        graph_json = rdf_graph.serialize(format="json-ld")
        return graph_turtle, graph_json

    def insert_graph(self, graph_data):
        """
        Inserts an RDF graph into the Fuseki dataset.
        """
        sparql_endpoint = f"{self.fuseki_url}/NEPR-2024/data"
        headers = {'Content-Type': 'text/turtle'}

        try:
            response = requests.post(sparql_endpoint, data=graph_data, headers=headers)
            if response.status_code == 200:
                print("RDF Graph uploaded successfully!")
            else:
                print(f"Failed to upload RDF Graph. Status code: {response.status_code}")
                print("Error message:", response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to SPARQL endpoint: {e}")

    def create_and_insert_graph(self, url):
        """
        Builds an RDF graph for the given URL using GraphBuilder and inserts it into the Fuseki dataset.
        """
        graph_builder = GraphBuilder(url)
        if graph_builder.json_ld_data is not None:
            graph_builder.insert_json_ld_to_graph(url, graph_builder.json_ld_data)
        if graph_builder.rdfa_data is not None:
            graph_builder.insert_rdfa_to_graph(url, graph_builder.rdfa_data)
        graph_builder.add_keywords_to_graph(url)
        graph_builder.add_content_length_to_graph(url)
        graph_builder.add_inLanguage_to_graph(url)
        rdf_graph = graph_builder.graph

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
service = SPARQLService()
service.create_and_insert_graph("https://www.huffingtonpost.fr/politique/article/un-salut-nazi-fait-par-elon-musk-le-rn-y-voit-tout-autre-chose_245117.html")
# # # service.insert_graph(graph_data)
# # # service.insert_graph("https://english.elpais.com/usa/2025-01-20/the-world-in-trumps-new-era-expansionism-tariffs-greater-focus-on-the-americas-and-a-staredown-with-beijing.html")
# # # service.insert_graph("https://www.bbc.com/future/article/20250117-planetary-parade-what-the-alignment-of-seven-planets-really-means-for-science")
# # # service.insert_graph("")
