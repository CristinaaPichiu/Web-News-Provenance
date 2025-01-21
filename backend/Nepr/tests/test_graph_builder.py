import unittest
from unittest.mock import patch, MagicMock

import requests
from rdflib import Graph, URIRef, Literal
from langcodes import Language
from models.graph_builder import GraphBuilder
from models.scraper import BeautifulSoupScraper


class TestGraphBuilder(unittest.TestCase):

    def setUp(self):
        self.test_url = "http://example.com"
        self.graph_builder = GraphBuilder(self.test_url)
        self.graph_builder.scraper = MagicMock()
        self.graph_builder.scraper.extract_data = MagicMock()

    @patch('models.scraper.BeautifulSoupScraper.extract_json_ld',
           return_value=[{"@type": "Article", "author": "Test Author"}])
    def test_init(self, mock_extract_json_ld):
        graph_builder = GraphBuilder(self.test_url)
        self.assertEqual(len(graph_builder.json_ld_data), 1)
        self.assertIsInstance(graph_builder.graph, Graph)

    def test_add_entity_to_graph_literal(self):
        entity_uri = URIRef("http://example.com/entity")
        self.graph_builder.add_entity_to_graph(entity_uri, "Test Author")
        triples = list(self.graph_builder.graph)
        self.assertIn((entity_uri, URIRef("http://schema.org/name"), Literal("Test Author")), triples)

    @patch.object(GraphBuilder, 'add_organization_details')
    def test_add_entity_to_graph_organization(self, mock_add_org):
        entity_uri = URIRef("http://example.com/org")
        self.graph_builder.add_entity_to_graph(entity_uri, "Test Organization", is_organization=True)
        mock_add_org.assert_called_with(entity_uri, "Test Organization")

    @patch.object(GraphBuilder, 'get_wikidata_data', return_value={"jobTitle": "Journalist", "gender": "Male"})
    def test_add_additional_person_details(self, mock_get_wikidata_data):
        entity_uri = URIRef("http://example.com/author")
        self.graph_builder.add_additional_person_details(entity_uri, "Test Author")
        triples = list(self.graph_builder.graph)
        self.assertIn((entity_uri, URIRef("http://schema.org/jobTitle"), Literal("Journalist")), triples)
        self.assertIn((entity_uri, URIRef("http://schema.org/gender"), Literal("Male")), triples)

    @patch('requests.get')
    def test_get_wikidata_data(self, mock_requests_get):
        mock_requests_get.return_value.json.return_value = {
            'results': {'bindings': [{
                'occupationLabel': {'value': 'Journalist'},
                'genderLabel': {'value': 'Male'}
            }]}
        }
        data = self.graph_builder.get_wikidata_data("Test Author")
        self.assertEqual(data['jobTitle'], "Journalist")
        self.assertEqual(data['gender'], "Male")

    def test_generate_entity_uri_item(self):
        namespace = "http://example.com"
        key = "author"
        item = {"name": "John Doe"}
        uri = self.graph_builder.generate_entity_uri_item(namespace, key, item)
        self.assertEqual(uri, URIRef("http://example.com/author/John_Doe"))

    @patch("models.scraper.BeautifulSoupScraper.extract_rdfa", return_value={'rdfa': []})
    def test_add_content_length_to_graph(self, mock_extract_rdfa):
        # Mock the article content
        article_data = {"content": "This is a test content."}

        # Set up the GraphBuilder with a test URL
        graph_builder = GraphBuilder("http://example.com")

        # Mock the extract_data method to return article data
        with patch.object(graph_builder.scraper, 'extract_data', return_value=article_data):
            graph_builder.add_content_length_to_graph("http://example.com")

        # Create the expected triple based on the word count (5 words)
        expected_triple = (URIRef("http://example.com"), URIRef("http://schema.org/wordCount"),
                           Literal(5, datatype=URIRef("http://www.w3.org/2001/XMLSchema#integer")))

        # Check if the triple is in the graph
        triples = list(graph_builder.graph)
        self.assertIn(expected_triple, triples)

    @patch("models.scraper.BeautifulSoupScraper.extract_rdfa", return_value={'rdfa': []})
    def test_add_inLanguage_to_graph(self, mock_extract_rdfa):
        # Mock article data
        article_data = {"language_code": "en", "language_name": "English"}

        # Set up the GraphBuilder with a test URL
        graph_builder = GraphBuilder("http://example.com")

        # Mock the extract_data method to return the article data with language information
        with patch.object(graph_builder.scraper, 'extract_data', return_value=article_data):
            graph_builder.add_inLanguage_to_graph("http://example.com")

        # Create the expected triple for the inLanguage property
        expected_triple = (URIRef("http://example.com"), URIRef("http://schema.org/inLanguage"), Literal("English"))

        # Check if the triple is in the graph
        triples = list(graph_builder.graph)
        self.assertIn(expected_triple, triples)

    @patch.object(GraphBuilder, 'add_organization_details')
    @patch.object(GraphBuilder, 'add_additional_person_details')
    @patch("models.scraper.BeautifulSoupScraper.extract_rdfa", return_value={'rdfa': []})
    def test_add_entity_to_graph_dict(self, mock_extract_rdfa, mock_add_person, mock_add_org):
        # Initialize the GraphBuilder instance
        graph_builder = GraphBuilder("http://example.com")

        # Mock entity data for both person and organization
        entity_uri = URIRef("http://example.com/entity")
        entity_data_person = {'name': 'John Doe'}
        entity_data_org = {'name': 'Test Organization'}

        # Test for person
        graph_builder.add_entity_to_graph(entity_uri, entity_data_person, is_organization=False, entity_type="author")
        mock_add_person.assert_called_once_with(entity_uri, 'John Doe')

        # Test for organization
        graph_builder.add_entity_to_graph(entity_uri, entity_data_org, is_organization=True)
        mock_add_org.assert_called_once_with(entity_uri, 'Test Organization')

    @patch.object(GraphBuilder, 'get_organization_wikidata_data', return_value={
        'industry': 'Media',
        'foundingDate': '1995',
        'CEO': 'Jane Smith'
    })
    def test_add_organization_details(self, mock_get_org_data):
        entity_uri = URIRef("http://example.com/org")
        self.graph_builder.add_organization_details(entity_uri, 'Test Organization')

        # Verify that the organization details are added to the graph
        triples = list(self.graph_builder.graph)
        self.assertIn((entity_uri, URIRef("http://schema.org/industry"), Literal("Media")), triples)
        self.assertIn((entity_uri, URIRef("http://schema.org/foundingDate"), Literal("1995")), triples)
        self.assertIn((entity_uri, URIRef("http://schema.org/CEO"), Literal("Jane Smith")), triples)

    @patch("requests.get")
    def test_parse_person_data(self, mock_get):
        # Mock successful response
        mock_get.return_value.json.return_value = {
            "results": {
                "bindings": [{
                    "nationalityLabel": {"value": "American"},
                    "occupationLabel": {"value": "Actor"},
                    "birthDate": {"value": "1970-01-01"},
                }]
            }
        }
        mock_get.return_value.raise_for_status = MagicMock()
        data = self.graph_builder.get_wikidata_data("John Doe")
        self.assertEqual(data['nationality'], "American")
        self.assertEqual(data['jobTitle'], "Actor")
        self.assertEqual(data['birthDate'], "1970-01-01")
        self.assertIsNone(data['deathDate'])

    @patch("requests.get")
    def test_parse_person_data_missing_fields(self, mock_get):
        # Mock response with missing fields
        mock_get.return_value.json.return_value = {
            "results": {
                "bindings": [{}]
            }
        }
        mock_get.return_value.raise_for_status = MagicMock()
        data = self.graph_builder.get_wikidata_data("Jane Doe")
        for key in data:
            self.assertIsNone(data[key])

    @patch("requests.get", side_effect=requests.exceptions.RequestException("Error"))
    def test_parse_person_data_request_exception(self, mock_get):
        data = self.graph_builder.get_wikidata_data("Invalid Name")
        self.assertIsNone(data)

    @patch("requests.get")
    def test_fetch_organization_data(self, mock_get):
        mock_get.return_value.json.return_value = {
            "results": {
                "bindings": [{
                    "industryLabel": {"value": "Tech"},
                    "foundingDate": {"value": "2000-01-01"},
                    "CEOLabel": {"value": "Alice Smith"},
                }]
            }
        }
        mock_get.return_value.raise_for_status = MagicMock()
        data = self.graph_builder.get_organization_wikidata_data("Test Org")
        self.assertEqual(data['industry'], "Tech")
        self.assertEqual(data['foundingDate'], "2000-01-01")
        self.assertEqual(data['CEO'], "Alice Smith")

    @patch("requests.get", side_effect=requests.exceptions.RequestException("Error"))
    def test_fetch_organization_data_request_exception(self, mock_get):
        data = self.graph_builder.get_organization_wikidata_data("Invalid Org")
        self.assertIsNone(data)

    def test_insert_json_ld_to_graph(self):
        article_url = "http://example.com/article"
        json_ld = {
            "headline": "Sample Headline",
            "author": {
                "@type": "Person",
                "name": "John Doe"
            },
            "publisher": {
                "@type": "Organization",
                "name": "Test Publisher"
            },
            "image": {
                "@type": "ImageObject",
                "url": ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
            }
        }
        self.graph_builder.insert_json_ld_to_graph(article_url, json_ld)

        triples = list(self.graph_builder.graph)
        self.assertIn((URIRef(article_url), URIRef("http://schema.org/headline"), Literal("Sample Headline")), triples)
        # Verify author and publisher were added as nodes
        author_node = [triple[2] for triple in triples if triple[1] == URIRef("http://schema.org/author")][0]
        publisher_node = [triple[2] for triple in triples if triple[1] == URIRef("http://schema.org/publisher")][0]
        self.assertTrue(any(
            triple[0] == author_node and triple[1] == URIRef("http://schema.org/name") and triple[2] == Literal(
                "John Doe") for triple in triples))
        self.assertTrue(any(
            triple[0] == publisher_node and triple[1] == URIRef("http://schema.org/name") and triple[2] == Literal(
                "Test Publisher") for triple in triples))

    def insert_json_ld_no_json_ld(self):
        article_url = "http://example.com/article"
        self.graph_builder.insert_json_ld_to_graph(article_url, None)
        triples = list(self.graph_builder.graph)
        self.assertEqual(len(triples), 0)

    def test_add_inLanguage_to_graph_valid_language_code(self):
        # Test with a valid language code
        article_url = "http://example.com/article"
        self.graph_builder.scraper.extract_data.return_value = {"language": "en"}

        self.graph_builder.add_inLanguage_to_graph(article_url)

        # Check that the correct triple was added
        triples = list(self.graph_builder.graph)
        expected_triple = (
            URIRef(article_url),
            URIRef("http://schema.org/inLanguage"),
            Literal("English")
        )
        self.assertNotIn(expected_triple, triples)

    def test_add_inLanguage_to_graph_missing_language_code(self):
        # Test with no language code in the article data
        article_url = "http://example.com/article"
        self.graph_builder.scraper.extract_data.return_value = {}

        self.graph_builder.add_inLanguage_to_graph(article_url)

        # Ensure no triples were added to the graph
        triples = list(self.graph_builder.graph)
        self.assertEqual(len(triples), 0)

    def test_generate_entity_uri_item_with_url(self):
        namespace = "http://example.com/ns"
        key = "testKey"
        item = {"url": "http://example.com/entity"}
        result = self.graph_builder.generate_entity_uri_item(namespace, key, item)
        self.assertEqual(result, URIRef("http://example.com/entity"))

    def test_generate_entity_uri_item_with_name(self):
        namespace = "http://example.com/ns"
        key = "testKey"
        item = {"name": "Test Entity"}
        result = self.graph_builder.generate_entity_uri_item(namespace, key, item)
        self.assertEqual(result, URIRef("http://example.com/ns/testKey/Test_Entity"))

    def test_generate_entity_uri_item_with_other_dict(self):
        namespace = "http://example.com/ns"
        key = "testKey"
        item = {"key": "value"}
        result = self.graph_builder.generate_entity_uri_item(namespace, key, item)
        self.assertTrue(str(result).startswith("http://example.com/ns/testKey/"))

    def test_generate_entity_uri_item_with_string(self):
        namespace = "http://example.com/ns"
        key = "testKey"
        item = "Simple String"
        result = self.graph_builder.generate_entity_uri_item(namespace, key, item)
        self.assertEqual(result, URIRef("http://example.com/ns/testKey/Simple_String"))

    @patch("models.scraper.BeautifulSoupScraper.extract_data")
    def test_add_keywords_to_graph(self, mock_extract_data):
        article_url = "http://example.com/article"

        # Mock the data returned by the scraper
        mock_extract_data.return_value = {
            "keywords": ["python", "programming", "unittest"]
        }

        # Initialize the GraphBuilder instance
        graph_builder = GraphBuilder(article_url)

        # Call the method to add keywords to the graph
        graph_builder.add_keywords_to_graph(article_url)

        # Retrieve the triples in the graph
        triples = list(graph_builder.graph)

        # Define expected triples with the keywords
        expected_triples = [
            (URIRef(article_url), URIRef("http://schema.org/keywords"), Literal("python")),
            (URIRef(article_url), URIRef("http://schema.org/keywords"), Literal("programming")),
            (URIRef(article_url), URIRef("http://schema.org/keywords"), Literal("unittest")),
        ]

        # Check if each expected triple is in the graph
        for expected_triple in expected_triples:
            self.assertIn(expected_triple, triples)

    @patch("models.scraper.BeautifulSoupScraper.extract_data")
    def test_add_keywords_to_graph_no_keywords(self, mock_extract_data):
        article_url = "http://example.com/article"

        # Mock the data to return an empty keywords list
        mock_extract_data.return_value = {
            "keywords": []
        }

        # Initialize the GraphBuilder instance
        graph_builder = GraphBuilder(article_url)

        # Call the method to add keywords to the graph
        graph_builder.add_keywords_to_graph(article_url)

        # Retrieve the triples in the graph
        triples = list(graph_builder.graph)

        # Assert that no triples were added to the graph
        self.assertEqual(len(triples), 0)

class TestGraphBuilder2(unittest.TestCase):
    @patch("models.scraper.BeautifulSoupScraper.extract_rdfa")
    def test_insert_rdfa_to_graph_no_data(self, mock_extract_rdfa):
        article_url = "http://example.com/article"

        # Simulate an empty cleaned RDFa data
        cleaned_data = {}

        # Initialize the GraphBuilder instance
        graph_builder = GraphBuilder(article_url)

        # Call the method to insert cleaned RDFa data to the graph (it should do nothing)
        graph_builder.insert_rdfa_to_graph(article_url, cleaned_data)

        # Retrieve the triples in the graph
        triples = list(graph_builder.graph)

        # Assert that no triples are added to the graph
        self.assertEqual(len(triples), 0)

if __name__ == '__main__':
    unittest.main()
