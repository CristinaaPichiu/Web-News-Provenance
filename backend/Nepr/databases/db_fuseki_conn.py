import requests
from dotenv import load_dotenv
from SPARQLWrapper import SPARQLWrapper, JSON, POST
import os
# Load environment variables from .env file
load_dotenv()

# List of Fuseki endpoints to check
ENDPOINTS = [
    "/NEPR-2024/get",         # Graph Store Protocol (Read)
    "/NEPR-2024/data",        # Graph Store Protocol
    "/#/dataset/NEPR-2024/query",       # SPARQL Query
    "/#/dataset/NEPR-2024/sparql",      # SPARQL Query (Alternate)
    "/#/dataset/NEPR-2024/update"       # SPARQL Update
]

def check_connection(fuseki_url):
    """
    Verifies if the Fuseki server is accessible.
    :param fuseki_url: URL of the Fuseki server, e.g., 'http://localhost:3030'
    """
    try:
        response = requests.get(fuseki_url)
        if response.status_code == 200:
            print(f"Successfully connected to Fuseki server at {fuseki_url}.")
        else:
            print(f"Connection to {fuseki_url} failed: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Connection to {fuseki_url} failed: {e}")

def run_sparql_query(fuseki_url, query):
    """
    Runs a SPARQL query on the Fuseki server using SPARQLWrapper.
    :param fuseki_url: URL of the Fuseki server.
    :param query: SPARQL query string.
    :return: JSON response from the server.
    """
    sparql_endpoint = f"{fuseki_url}/NEPR-2024/sparql"  # Ensure this is the correct SPARQL endpoint for your dataset
    sparql = SPARQLWrapper(sparql_endpoint)

    # Set the query
    sparql.setQuery(query)

    # Set the return format to JSON
    sparql.setReturnFormat(JSON)

    try:
        # Execute the query and return the results in JSON format
        results = sparql.query().convert()
        return results
    except Exception as e:
        print(f"Error executing SPARQL query: {e}")
        return None


def insert_graph_data(fuseki_url, graph_uri, triples):
    """
    Inserts data into a named graph in a Fuseki server.

    Args:
        fuseki_url (str): The endpoint URL of the Fuseki dataset (e.g., http://localhost:3030/dataset).
        graph_uri (str): The URI of the named graph (e.g., http://example.org/myGraph).
        triples (str): The triples to insert in Turtle format.

    Returns:
        dict: The response from the Fuseki server.
    """
    try:
        # SPARQL Update endpoint URL
        update_url = f"{fuseki_url}/update"

        # SPARQL query to insert data
        query = f"""
        INSERT DATA {{
          GRAPH <{graph_uri}> {{
            {triples}
          }}
        }}
        """

        # Initialize SPARQLWrapper
        sparql = SPARQLWrapper(update_url)
        sparql.setMethod(POST)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)

        # Execute the query
        response = sparql.query().convert()

        return {"status": "success", "response": response}

    except Exception as e:
        return {"status": "error", "message": str(e)}

def insert_data(fuseki_url, subject, predicate, obj):
    """
    Inserts a new triple into the Fuseki dataset.
    :param fuseki_url: URL of the Fuseki server.
    :param subject: The subject of the triple.
    :param predicate: The predicate of the triple.
    :param obj: The object of the triple.
    :return: The response from the server.
    """
    sparql_endpoint = f"{fuseki_url}/NEPR-2024/update"  # The endpoint for SPARQL Update
    sparql = SPARQLWrapper(sparql_endpoint)

    # Construct the SPARQL INSERT DATA query
    query = f"""
    INSERT DATA {{
        <{subject}> <{predicate}> "{obj}".
    }}
    """

    sparql.setQuery(query)
    sparql.setMethod("POST")  # POST method for SPARQL Update
    sparql.setReturnFormat(JSON)

    try:
        # Execute the query to insert the data
        response = sparql.query().convert()
        print(f"Inserted data: {subject} {predicate} {obj}")
        return response
    except Exception as e:
        print(f"Error inserting data: {e}")
        return None


def delete_data(fuseki_url, subject, predicate, obj):
    """
    Deletes a triple from the Fuseki dataset.
    :param fuseki_url: URL of the Fuseki server.
    :param subject: The subject of the triple.
    :param predicate: The predicate of the triple.
    :param obj: The object of the triple.
    :return: The response from the server.
    """
    sparql_endpoint = f"{fuseki_url}/NEPR-2024/update"  # The endpoint for SPARQL Update
    sparql = SPARQLWrapper(sparql_endpoint)

    # Construct the SPARQL DELETE DATA query
    query = f"""
    DELETE DATA {{
        <{subject}> <{predicate}> "{obj}".
    }}
    """

    sparql.setQuery(query)
    sparql.setMethod("POST")  # POST method for SPARQL Update
    sparql.setReturnFormat(JSON)

    try:
        # Execute the query to delete the data
        response = sparql.query().convert()
        print(f"Deleted data: {subject} {predicate} {obj}")
        return response
    except Exception as e:
        print(f"Error deleting data: {e}")
        return None

if __name__ == "__main__":
    fuseki_url = os.getenv("FUSEKI_URL")
    print(f"Fuseki Base URL: {fuseki_url}")
    check_connection(fuseki_url)
