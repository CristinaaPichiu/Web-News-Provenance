import requests
from dotenv import load_dotenv
from SPARQLWrapper import SPARQLWrapper, JSON
from databases.db_fuseki_conn import insert_data, check_connection, run_sparql_query, delete_data
import os
# Load environment variables from .env file
load_dotenv()


def test_endpoints():
    """
    Tests all the given endpoints for the Fuseki server.
    :param fuseki_url: Base URL of the Fuseki server.
    :param endpoints: List of endpoints to test.
    """
    endpoints = [
        "/NEPR-2024/get",  # Graph Store Protocol (Read)
        "/NEPR-2024/data",  # Graph Store Protocol
        "/#/dataset/NEPR-2024/query",  # SPARQL Query
        "/#/dataset/NEPR-2024/sparql",  # SPARQL Query (Alternate)
        "/#/dataset/NEPR-2024/update"  # SPARQL Update
    ]
    fuseki_url = os.getenv("FUSEKI_URL")
    for endpoint in endpoints:
        full_url = f"{fuseki_url}{endpoint}"
        print(f"Testing endpoint: {full_url}")
        check_connection(full_url)

def test_insert():
    """
    Tests inserting data into the Fuseki server.
    :param fuseki_url: URL of the Fuseki server.
    """
    fuseki_url = os.getenv("FUSEKI_URL")
    subject = "http://example.org/subject1"
    predicate = "http://example.org/property1"
    obj = "object1"
    response = insert_data(fuseki_url, subject, predicate, obj)
    if response:
        print("Data inserted successfully.")
    else:
        print("Data insertion failed.")

def test_sparql_query():
    """
    Tests a sample SPARQL query on the Fuseki server.
    :param fuseki_url: URL of the Fuseki server.
    """
    fuseki_url = os.getenv("FUSEKI_URL")
    query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
    results = run_sparql_query(fuseki_url, query)
    if results:
        print("SPARQL Query Results:")
        print(results)
    else:
        print("No results or an error occurred.")

def test_delete():
    """
    Tests deleting data from the Fuseki server.
    :param fuseki_url: URL of the Fuseki server.
    """
    fuseki_url = os.getenv("FUSEKI_URL")
    subject = "http://example.org/subject1"
    predicate = "http://example.org/property1"
    obj = "object1"
    response = delete_data(fuseki_url, subject, predicate, obj)
    if response:
        print("Data deleted successfully.")
    else:
        print("Data deletion failed.")
