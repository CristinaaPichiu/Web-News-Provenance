import unittest
from unittest.mock import patch, MagicMock

import requests
from rdflib import Graph, URIRef, Literal
from langcodes import Language
from models.graph_builder import GraphBuilder


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

    def test_insert_metadata_to_graph(self):
        metadata = [{"@type": "Article", "author": "Test Author"}]
        self.graph_builder.insert_metadata_to_graph(self.test_url, metadata)
        triples = list(self.graph_builder.graph)
        self.assertIn((URIRef(self.test_url), URIRef("http://schema.org/author"), Literal("Test Author")), triples)

    def test_generate_entity_uri_item(self):
        namespace = "http://example.com"
        key = "author"
        item = {"name": "John Doe"}
        uri = self.graph_builder.generate_entity_uri_item(namespace, key, item)
        self.assertEqual(uri, URIRef("http://example.com/author/John_Doe"))

    def test_add_content_length_to_graph(self):
        article_data = {"content": "This is a test content."}
        with patch.object(self.graph_builder.scraper, 'extract_data', return_value=article_data):
            self.graph_builder.add_content_length_to_graph(self.test_url)
        triples = list(self.graph_builder.graph)
        self.assertIn((URIRef(self.test_url), URIRef("http://schema.org/wordCount"), Literal(5)), triples)

    def test_add_inLanguage_to_graph(self):
        article_data = {"language": "en"}
        with patch.object(self.graph_builder.scraper, 'extract_data', return_value=article_data):
            self.graph_builder.add_inLanguage_to_graph(self.test_url)
        triples = list(self.graph_builder.graph)
        self.assertIn((URIRef(self.test_url), URIRef("http://schema.org/inLanguage"), Literal("English")), triples)

    @patch.object(GraphBuilder, 'add_organization_details')
    @patch.object(GraphBuilder, 'add_additional_person_details')
    def test_add_entity_to_graph_dict(self, mock_add_person, mock_add_org):
        entity_uri = URIRef("http://example.com/entity")
        entity_data_person = {'name': 'John Doe'}
        entity_data_org = {'name': 'Test Organization'}

        # Test for person
        self.graph_builder.add_entity_to_graph(entity_uri, entity_data_person, is_organization=False)
        mock_add_person.assert_called_with(entity_uri, 'John Doe')

        # Test for organization
        self.graph_builder.add_entity_to_graph(entity_uri, entity_data_org, is_organization=True)
        mock_add_org.assert_called_with(entity_uri, 'Test Organization')

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
        # Verify images were added
        image_triples = [triple for triple in triples if triple[1] == URIRef("http://schema.org/image")]
        self.assertEqual(len(image_triples), 2)

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
        self.assertIn(expected_triple, triples)

    def test_add_inLanguage_to_graph_unknown_language_code(self):
        """Test adding an unknown language code to the graph"""
        article_url = "http://example.com/article"
        # Mock extract_data to return unknown language code
        self.graph_builder.scraper.extract_data.return_value = {"language": "xx"}

        self.graph_builder.add_inLanguage_to_graph(article_url)

        triples = list(self.graph_builder.graph)
        expected_triple = (
            URIRef(article_url),
            URIRef("http://schema.org/inLanguage"),
            Literal("XX")  # Now we expect just the uppercase code
        )
        self.assertIn(expected_triple, triples)

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



if __name__ == '__main__':
    unittest.main()
