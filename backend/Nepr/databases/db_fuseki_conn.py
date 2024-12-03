import os
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from dotenv import load_dotenv

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


def test_endpoints(fuseki_url, endpoints):
    """
    Tests all the given endpoints for the Fuseki server.
    :param fuseki_url: Base URL of the Fuseki server.
    :param endpoints: List of endpoints to test.
    """
    for endpoint in endpoints:
        full_url = f"{fuseki_url}{endpoint}"
        print(f"Testing endpoint: {full_url}")
        check_connection(full_url)

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


def test_sparql_query(fuseki_url):
    """
    Tests a sample SPARQL query on the Fuseki server.
    :param fuseki_url: URL of the Fuseki server.
    """
    query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
    results = run_sparql_query(fuseki_url, query)
    if results:
        print("SPARQL Query Results:")
        print(results)
    else:
        print("No results or an error occurred.")

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


def test_insert(fuseki_url):
    """
    Tests inserting data into the Fuseki server.
    :param fuseki_url: URL of the Fuseki server.
    """
    subject = "http://example.org/subject1"
    predicate = "http://example.org/property1"
    obj = "object1"
    response = insert_data(fuseki_url, subject, predicate, obj)
    if response:
        print("Data inserted successfully.")
    else:
        print("Data insertion failed.")

from SPARQLWrapper import SPARQLWrapper, JSON
import os

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


def test_delete(fuseki_url):
    """
    Tests deleting data from the Fuseki server.
    :param fuseki_url: URL of the Fuseki server.
    """
    subject = "http://example.org/subject1"
    predicate = "http://example.org/property1"
    obj = "object1"
    response = delete_data(fuseki_url, subject, predicate, obj)
    if response:
        print("Data deleted successfully.")
    else:
        print("Data deletion failed.")
def main():
    fuseki_url = os.getenv("FUSEKI_URL")
    print(f"Fuseki Base URL: {fuseki_url}")
    test_endpoints(fuseki_url, ENDPOINTS)
    test_insert(fuseki_url)
    test_sparql_query(fuseki_url)
    test_delete(fuseki_url)
    test_sparql_query(fuseki_url)


if __name__ == "__main__":
    main()
