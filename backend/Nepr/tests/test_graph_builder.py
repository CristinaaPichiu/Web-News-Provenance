import logging
import unittest
from unittest.mock import patch, MagicMock
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import requests
from rdflib import Graph, URIRef, Literal
from langcodes import Language
from models.graph_builder import GraphBuilder
from models.scraper import BeautifulSoupScraper


class TestGraphBuilder(unittest.TestCase):

    def setUp(self):
        self.test_url = "http://example.com"
        self.service = Service(ChromeDriverManager().install())
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.graph_builder = GraphBuilder(self.test_url, self.service, self.options)
        self.graph_builder.scraper = MagicMock()
        self.graph_builder.scraper.extract_data = MagicMock()

    @patch('models.scraper.BeautifulSoupScraper.extract_json_ld',
           return_value=[{"@type": "Article", "author": "Test Author"}])
    def test_init(self, mock_extract_json_ld):
        graph_builder = GraphBuilder(self.test_url, self.service, self.options)
        self.assertEqual(len(graph_builder.json_ld_data), 1)
        self.assertIsInstance(graph_builder.graph, Graph)

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
        graph_builder = GraphBuilder("http://example.com", self.service, self.options)

        # Mock the extract_data method to return article data
        with patch.object(graph_builder.scraper, 'extract_data', return_value=article_data):
            graph_builder.add_content_length_to_graph("http://example.com")

        # Create the expected triple based on the word count (5 words)
            expected_triple = (URIRef("http://example.com"), URIRef("http://schema.org/wordCount"),
                               Literal(24, datatype=URIRef("http://www.w3.org/2001/XMLSchema#integer")))
        # Check if the triple is in the graph
        triples = list(graph_builder.graph)
        self.assertIn(expected_triple, triples)

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


    @patch("requests.get", side_effect=requests.exceptions.RequestException("Error"))
    def test_fetch_organization_data_request_exception(self, mock_get):
        data = self.graph_builder.get_organization_wikidata_data("Invalid Org")
        self.assertIsNone(data)

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
        article_url = "http://example.com/article"
        self.graph_builder.article_data = {}

        self.graph_builder.add_inLanguage_to_graph(article_url)

        triples = list(self.graph_builder.graph)
        self.assertEqual(len(triples), 0)

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
        graph_builder = GraphBuilder(article_url,self.service, self.options)

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
        graph_builder = GraphBuilder(article_url, self.service, self.options)

        # Call the method to add keywords to the graph
        graph_builder.add_keywords_to_graph(article_url)

        # Retrieve the triples in the graph
        triples = list(graph_builder.graph)

        # Assert that no triples were added to the graph
        self.assertEqual(len(triples), 0)

class TestGraphBuilder2(unittest.TestCase):
    def setUp(self):
        self.test_url = "http://example.com"
        self.service = Service(ChromeDriverManager().install())
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.graph_builder = GraphBuilder(self.test_url, self.service, self.options)

    @patch("models.scraper.BeautifulSoupScraper.extract_rdfa")
    @patch("models.scraper.BeautifulSoupScraper.extract_data", return_value={})
    def test_insert_rdfa_to_graph_no_data(self, mock_extract_rdfa, mock_extract_data):
        article_url = "http://example.com/article"

        # Simulate an empty cleaned RDFa data
        cleaned_data = {}

        # Initialize the GraphBuilder instance
        graph_builder = GraphBuilder(article_url, self.service, self.options)

        # Call the method to insert cleaned RDFa data to the graph (it should do nothing)
        graph_builder.insert_rdfa_to_graph(article_url, cleaned_data)

        # Retrieve the triples in the graph
        triples = list(graph_builder.graph)

        # Assert that no triples are added to the graph
        self.assertEqual(len(triples), 0)

    @patch("models.scraper.BeautifulSoupScraper.extract_rdfa")
    @patch("models.scraper.BeautifulSoupScraper.extract_data", return_value={})
    def test_insert_rdfa_to_graph_with_data(self, mock_extract_data, mock_extract_rdfa):
        article_url = "http://example.com/article"

        # Simulate cleaned RDFa data
        cleaned_data = {
            "headline": "Test Headline",
            "abstract": "Test Abstract",
            "thumbnailUrl": "http://example.com/image.jpg",
            "url": "http://example.com/article",
            "publisher": "Test Publisher",
            "article:modified_time": "2023-01-01T00:00:00Z",
            "article:published_time": "2023-01-01T00:00:00Z",
            "article:author": "Test Author",
            "type": "Test Type"
        }

        # Initialize the GraphBuilder instance
        graph_builder = GraphBuilder(article_url, self.service, self.options)

        # Call the method to insert cleaned RDFa data to the graph
        graph_builder.insert_rdfa_to_graph(article_url, cleaned_data)

        # Retrieve the triples in the graph
        triples = list(graph_builder.graph)

        # Assert that the correct triples are added to the graph
        expected_triples = [
            (URIRef(article_url), URIRef("http://schema.org/headline"), Literal("Test Headline")),
            (URIRef(article_url), URIRef("http://schema.org/abstract"), Literal("Test Abstract")),
            (URIRef(article_url), URIRef("http://schema.org/thumbnailUrl"), Literal("http://example.com/image.jpg")),
            (URIRef(article_url), URIRef("http://schema.org/url"), Literal("http://example.com/article")),
            (URIRef(article_url), URIRef("http://schema.org/publisher"), Literal("Test Publisher")),
            (URIRef(article_url), URIRef("http://schema.org/dateModified"), Literal("2023-01-01T00:00:00Z")),
            (URIRef(article_url), URIRef("http://schema.org/datePublished"), Literal("2023-01-01T00:00:00Z")),
            (URIRef(article_url), URIRef("http://schema.org/author"), Literal("Test Author")),
            (URIRef(article_url), URIRef("http://schema.org/articleType"), Literal("Test Type"))
        ]

        for expected_triple in expected_triples:
            self.assertIn(expected_triple, triples, f"Expected triple {expected_triple} not found in {triples}")
import unittest
from unittest.mock import patch, MagicMock
from rdflib import Graph, URIRef, Literal
from models.graph_builder import GraphBuilder

class TestGraphBuilder3(unittest.TestCase):

    def setUp(self):
        self.url = "http://example.com"
        self.service = Service(ChromeDriverManager().install())
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.graph_builder = GraphBuilder(self.url, self.service, self.options)

    @patch('models.graph_builder.BeautifulSoupScraper')
    def test_add_author_to_graph(self, MockScraper):
        entity_uri = "http://example.com/author"
        entity_data = {"name": "John Doe", "birthDate": "1980-01-01"}
        self.graph_builder._add_author_to_graph(entity_uri, entity_data)
        triples = list(self.graph_builder.graph)
        self.assertTrue((URIRef(entity_uri), URIRef("http://schema.org/name"), Literal("John Doe")) in triples)
        self.assertTrue((URIRef(entity_uri), URIRef("http://schema.org/birthDate"), Literal("1980-01-01")) in triples)

    @patch('models.graph_builder.BeautifulSoupScraper')
    def test_add_editor_to_graph(self, MockScraper):
        entity_uri = "http://example.com/editor"
        entity_data = {"name": "Jane Doe", "birthDate": "1985-01-01"}
        self.graph_builder._add_editor_to_graph(entity_uri, entity_data)
        triples = list(self.graph_builder.graph)
        self.assertTrue((URIRef(entity_uri), URIRef("http://schema.org/name"), Literal("Jane Doe")) in triples)
        self.assertTrue((URIRef(entity_uri), URIRef("http://schema.org/birthDate"), Literal("1985-01-01")) in triples)

    @patch('models.graph_builder.BeautifulSoupScraper')
    def test_add_publisher_to_graph(self, MockScraper):
        entity_uri = "http://example.com/publisher"
        entity_data = {"name": "Publisher Inc.", "foundingDate": "2000-01-01"}
        self.graph_builder._add_publisher_to_graph(entity_uri, entity_data, is_organization=True)
        triples = list(self.graph_builder.graph)
        self.assertTrue((URIRef(entity_uri), URIRef("http://schema.org/name"), Literal("Publisher Inc.")) in triples)

    def test_set_person_entity(self):
        entity_uri = "http://example.com/person"
        entity_data = {"name": "John Doe", "birthDate": "1980-01-01"}
        person = self.graph_builder._set_person_entity(entity_uri, entity_data)
        self.assertEqual(person.name, "John Doe")
        self.assertEqual(person.birthDate, "1980-01-01")

    def test_set_organization_entity(self):
        entity_uri = "http://example.com/organization"
        entity_data = {"name": "Org Inc."}
        organization = self.graph_builder._set_organization_entity(entity_uri, entity_data)
        self.assertEqual(organization.name, "Org Inc.")

    @patch('models.graph_builder.GraphBuilder._add_author_to_graph')
    @patch('models.graph_builder.GraphBuilder._add_editor_to_graph')
    @patch('models.graph_builder.GraphBuilder._add_publisher_to_graph')
    def test_add_entity_to_graph(self, mock_add_publisher, mock_add_editor, mock_add_author):
        entity_uri = "http://example.com/entity"
        entity_data = {"name": "Entity Name"}
        entity_type_author = "author"
        entity_type_editor = "editor"
        entity_type_publisher = "publisher"

        # Call method to add author to the graph
        self.graph_builder.add_entity_to_graph(entity_uri, entity_data, entity_type_author, False)

        # Ensure _add_author_to_graph was called once
        mock_add_author.assert_called_once_with(entity_uri, entity_data, False)

        # Call method to add editor to the graph
        self.graph_builder.add_entity_to_graph(entity_uri, entity_data, entity_type_editor, False)

        # Ensure _add_editor_to_graph was called once
        mock_add_editor.assert_called_once_with(entity_uri, entity_data)

        # Call method to add publisher to the graph
        self.graph_builder.add_entity_to_graph(entity_uri, entity_data, entity_type_publisher, False)

        # Ensure _add_publisher_to_graph was called once
        mock_add_publisher.assert_called_once_with(entity_uri, entity_data, False)

    @patch('models.graph_builder.GraphBuilder.get_wikidata_data')
    def test_add_additional_person_details(self, mock_get_wikidata_data):
        mock_get_wikidata_data.return_value = {"nationality": "American", "jobTitle": "Journalist"}
        entity_uri = "http://example.com/person"
        entity_name = "John Doe"
        person = self.graph_builder.add_additional_person_details(entity_uri, entity_name)
        self.assertEqual(person.nationality, "American")
        self.assertEqual(person.jobTitle, "Journalist")

    @patch('models.graph_builder.GraphBuilder.get_organization_wikidata_data')
    def test_add_organization_details(self, mock_get_organization_wikidata_data):
        mock_get_organization_wikidata_data.return_value = {"publishingPrinciples": "Principles URL"}
        entity_uri = "http://example.com/organization"
        entity_name = "Org Inc."
        organization = self.graph_builder.add_organization_details(entity_uri, entity_name)
        self.assertEqual(organization.publishingPrinciples, "Principles URL")

    @patch('requests.get')
    def test_get_wikidata_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": {
                "bindings": [
                    {
                        "occupationLabel": {"value": "Science Journalist"},
                        "nationalityLabel": {"value": "American"},
                        "birthDate": {"value": "1980-01-01"}
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        data = self.graph_builder.get_wikidata_data("John Doe")
        self.assertEqual(data['nationality'], "American")
        self.assertEqual(data['jobTitle'], "Science Journalist")
        self.assertEqual(data['birthDate'], "1980-01-01")

    @patch('requests.get')
    def test_get_organization_wikidata_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": {
                "bindings": [
                    {
                        "entityLabel": {"value": "Org Inc."},
                        "publishingPrinciples": {"value": "Principles URL"}
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        data = self.graph_builder.get_organization_wikidata_data("Org Inc.")
        self.assertEqual(data[0]['organization'], "Org Inc.")
        self.assertEqual(data[0]['publishingPrinciples'], "Principles URL")

class TestGraphBuilderStaticMethods(unittest.TestCase):
    def setUp(self):
        self.service = Service(ChromeDriverManager().install())
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')

    def test_set_key_image(self):
        expected_keys = ['contentUrl', 'duration', 'embedUrl', 'height', 'uploadDate', 'width',
                         'caption', 'embeddedTextCaption', '@type']
        result = GraphBuilder._set_key('image')
        self.assertEqual(result, expected_keys)

    def test_set_key_thumbnail(self):
        expected_keys = ['contentUrl', 'duration', 'embedUrl', 'height', 'uploadDate', 'width',
                         'caption', 'embeddedTextCaption', '@type']
        result = GraphBuilder._set_key('thumbnail')
        self.assertEqual(result, expected_keys)

    def test_set_key_audio(self):
        expected_keys = ['contentUrl', 'duration', 'embedUrl', 'height', 'uploadDate', 'width',
                         'caption', 'transcript', '@type']
        result = GraphBuilder._set_key('audio')
        self.assertEqual(result, expected_keys)

    def test_set_key_video(self):
        expected_keys = ['contentUrl', 'duration', 'embedUrl', 'height', 'uploadDate', 'width',
                         'caption', 'videoQuality', '@type']
        result = GraphBuilder._set_key('video')
        self.assertEqual(result, expected_keys)

    def test_set_key_other(self):
        expected_keys = []
        result = GraphBuilder._set_key('other')
        self.assertEqual(result, expected_keys)

    @patch("models.scraper.BeautifulSoupScraper.extract_data")
    def test_add_keywords_to_graph_no_keywords(self, mock_extract_data):
        article_url = "http://example.com/article"

        # Mock the data to return an empty keywords list
        mock_extract_data.return_value = {
            "keywords": []
        }

        # Initialize the GraphBuilder instance
        graph_builder = GraphBuilder(article_url, self.service, self.options)

        # Call the method to add keywords to the graph
        graph_builder.add_keywords_to_graph(article_url)

        # Retrieve the triples in the graph
        triples = list(graph_builder.graph)

        # Assert that no triples were added to the graph
        self.assertEqual(len(triples), 0)

class TestAddArticleBodyToGraph(unittest.TestCase):
    def setUp(self):
        self.service = Service(ChromeDriverManager().install())
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')

    @patch("models.scraper.BeautifulSoupScraper.extract_data")
    def test_add_articleBody_to_graph(self, mock_extract_data):
        article_url = "http://example.com/article"

        # Mock the data returned by the scraper
        mock_extract_data.return_value = {
            "content": "This is the body of the article."
        }

        # Initialize the GraphBuilder instance
        graph_builder = GraphBuilder(article_url, self.service, self.options)
        graph_builder.article_data = mock_extract_data.return_value

        # Call the method to add the article body to the graph
        graph_builder.add_articleBody_to_graph(article_url)

        # Retrieve the triples in the graph
        triples = list(graph_builder.graph)

        # Define the expected triple with the article body
        expected_triple = (
            URIRef(article_url),
            URIRef("http://schema.org/articleBody"),
            Literal("This is the body of the article.")
        )

        # Check if the expected triple is in the graph
        self.assertIn(expected_triple, triples)

        @patch("models.scraper.BeautifulSoupScraper.extract_data")
        def test_add_articleBody_to_graph_exception(self, mock_extract_data):
            article_url = "http://example.com/article"

            # Mock the data returned by the scraper to raise an exception
            mock_extract_data.side_effect = Exception("Test Exception")

            # Initialize the GraphBuilder instance
            graph_builder = GraphBuilder(article_url, self.service, self.options)
            graph_builder.article_data = mock_extract_data.return_value

            # Call the method to add the article body to the graph
            with self.assertLogs(level='ERROR') as log:
                graph_builder.add_articleBody_to_graph(article_url)
                self.assertIn("Error adding article body to graph: Test Exception", log.output[0])

class TestInsertJsonLdToGraph(unittest.TestCase):
    def setUp(self):
        self.graph_builder = GraphBuilder("http://example.com", MagicMock(), MagicMock())
        self.graph_builder.graph = Graph()
        self.graph_builder.scraper = MagicMock()
        self.graph_builder.scraper.get_full_language_name = MagicMock(return_value="English")

    def test_insert_json_ld_to_graph_none(self):
        result = self.graph_builder.insert_json_ld_to_graph("http://example.com", None, [])
        self.assertIsNone(result)

    def test_insert_json_ld_to_graph_empty(self):
        json_ld = {}
        self.graph_builder.insert_json_ld_to_graph("http://example.com", json_ld, [])
        triples = list(self.graph_builder.graph)
        self.assertEqual(len(triples), 0)

    def test_insert_json_ld_to_graph_simple(self):
        json_ld = {"name": "Test Article"}
        self.graph_builder.insert_json_ld_to_graph("http://example.com", json_ld, ["name"])
        triples = list(self.graph_builder.graph)
        expected_triple = (URIRef("http://example.com"), URIRef("http://schema.org/name"), Literal("Test Article"))
        self.assertIn(expected_triple, triples)

    def test_insert_json_ld_to_graph_list(self):
        json_ld = {"keywords": ["python", "programming"]}
        self.graph_builder.insert_json_ld_to_graph("http://example.com", json_ld, ["keywords"])
        triples = list(self.graph_builder.graph)
        expected_triples = [
            (URIRef("http://example.com"), URIRef("http://schema.org/keywords"), Literal("python")),
            (URIRef("http://example.com"), URIRef("http://schema.org/keywords"), Literal("programming"))
        ]
        for expected_triple in expected_triples:
            self.assertIn(expected_triple, triples)

    def test_insert_json_ld_to_graph_dict(self):
        json_ld = {"author": {"name": "John Doe"}}
        self.graph_builder.insert_json_ld_to_graph("http://example.com", json_ld, ["author"])
        triples = list(self.graph_builder.graph)
        self.assertTrue(any(str(triple[1]) == "http://schema.org/author" for triple in triples))

    def test_insert_json_ld_to_graph_inLanguage(self):
        json_ld = {"inLanguage": "en"}
        self.graph_builder.insert_json_ld_to_graph("http://example.com", json_ld, ["inLanguage"])
        triples = list(self.graph_builder.graph)
        expected_triple = (URIRef("http://example.com"), URIRef("http://schema.org/inLanguage"), Literal("English"))
        self.assertIn(expected_triple, triples)

    def test_insert_json_ld_to_graph_exception(self):
        with patch.object(self.graph_builder, 'generate_entity_uri_item', side_effect=Exception("Test Exception")):
            result = self.graph_builder.insert_json_ld_to_graph("http://example.com", {"name": "Test"}, ["name"])
            self.assertIsNone(result)

    @patch.object(GraphBuilder, 'generate_entity_uri_item',
                  return_value=URIRef("http://example.com/article/author/John_Doe"))
    def test_insert_json_ld_to_graph_author(self, mock_generate_entity_uri_item):
        article_url = "http://example.com/article"
        json_ld = {"author": {"name": "John Doe"}}
        self.graph_builder.insert_json_ld_to_graph(article_url, json_ld, ["author"])
        triples = list(self.graph_builder.graph)
        expected_triple = (
            URIRef(article_url), URIRef("http://schema.org/author"),
            URIRef("http://example.com/article/author/John_Doe")
        )
        self.assertIn(expected_triple, triples)

    @patch.object(GraphBuilder, 'generate_entity_uri_item',
                  return_value=URIRef("http://example.com/article/publisher/Publisher_Inc."))
    def test_insert_json_ld_to_graph_publisher(self, mock_generate_entity_uri_item):
        article_url = "http://example.com/article"
        json_ld = {"publisher": {"name": "Publisher Inc."}}
        self.graph_builder.insert_json_ld_to_graph(article_url, json_ld, ["publisher"])
        triples = list(self.graph_builder.graph)
        expected_triple = (URIRef(article_url), URIRef("http://schema.org/publisher"),
                           URIRef("http://example.com/article/publisher/Publisher_Inc."))
        self.assertIn(expected_triple, triples)

if __name__ == '__main__':
    unittest.main()
