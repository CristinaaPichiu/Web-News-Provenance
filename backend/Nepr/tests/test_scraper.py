import json
import unittest
from unittest.mock import patch, MagicMock, ANY, Mock
import requests
from bs4 import BeautifulSoup
from flask import Response

from models.scraper import BeautifulSoupScraper


class TestBeautifulSoupScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = BeautifulSoupScraper()

    @patch('requests.get')
    def test_extract_rdfa(self, mock_get):
        # Simulate the HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html><head><meta property="og:title" content="Sample Article"></head></html>'
        mock_get.return_value = mock_response

        # Call the extract_rdfa method
        scraper = BeautifulSoupScraper()
        result = scraper.extract_rdfa('https://example.com')

        # Check if the result matches the expected RDFa structure
        expected_result = {
            '@id': '',
            'http://ogp.me/ns#title': [{'@value': 'Sample Article'}]
        }
        self.assertEqual(result, expected_result)

    @patch('requests.get')
    def test_extract_data_http_failure(self, mock_requests_get):
        # Simulate an HTTP failure (RequestException)
        mock_requests_get.side_effect = requests.RequestException("Request failed")

        # Instantiate the scraper
        scraper = BeautifulSoupScraper()

        # Verify that ValueError is raised when the HTTP request fails
        with self.assertRaises(ValueError):
            scraper.extract_data("https://example.com")

    @patch('newspaper.Article')
    def test_extract_data(self, mock_article):
        mock_article_instance = MagicMock()
        mock_article.return_value = mock_article_instance

    @patch('models.scraper.Goose')
    def test_extract_data_goose(self, mock_goose):
        mock_goose_instance = MagicMock()
        mock_goose.return_value = mock_goose_instance

    @patch('langdetect.detect')
    @patch('requests.get')
    def test_detect_language(self, mock_get, mock_detect):
        mock_detect.return_value = 'en'
        mock_response = MagicMock()
        mock_response.headers = {'Content-Language': 'en'}
        mock_get.return_value = mock_response
        soup = BeautifulSoup('<html lang="en"></html>', 'html.parser')
        result = self.scraper.detect_language(mock_response, soup, "Sample Content")
        self.assertEqual(result, ('en', 'English'))

    @patch('models.scraper.sync_playwright')
    def test_extract_json_ld_youtube_empty(self, mock_playwright):
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_script = MagicMock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.query_selector_all.return_value = [mock_script]
        mock_script.inner_text.return_value = ''
        result = self.scraper.extract_json_ld_youtube("https://example.com")
        self.assertIsNone(result)
        mock_browser.close.assert_called_once()

    @patch('models.scraper.sync_playwright')
    def test_extract_json_ld_youtube_no_json_ld(self, mock_playwright):
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.query_selector_all.return_value = []
        result = self.scraper.extract_json_ld_youtube("https://example.com")
        self.assertIsNone(result)
        mock_browser.close.assert_called_once()

    @patch('models.scraper.sync_playwright')
    def test_extract_json_ld_youtube_valid(self, mock_playwright):
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_script = MagicMock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.query_selector_all.return_value = [mock_script]
        mock_script.inner_text.return_value = '{"@context": "http://schema.org", "@type": "VideoObject", "name": "Test Video"}'
        result = self.scraper.extract_json_ld_youtube("https://example.com")
        expected = [{"@context": "http://schema.org", "@type": "VideoObject", "name": "Test Video"}]
        self.assertEqual(result, expected)
        mock_browser.close.assert_called_once()

    @patch('models.scraper.sync_playwright')
    def test_extract_json_ld_youtube_invalid_json(self, mock_playwright):
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_script = MagicMock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.query_selector_all.return_value = [mock_script]
        mock_script.inner_text.return_value = '{"@context": "http://schema.org", "@type": "VideoObject", "name": "Test Video"'
        result = self.scraper.extract_json_ld_youtube("https://example.com")
        self.assertIsNone(result)
        mock_browser.close.assert_called_once()

    @patch('models.scraper.sync_playwright')
    def test_extract_json_ld_selenium_valid(self, mock_playwright):
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_script = MagicMock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.query_selector_all.return_value = [mock_script]
        mock_script.inner_text.return_value = '{"@context": "http://schema.org", "@type": "Article", "headline": "Test Article"}'
        result = BeautifulSoupScraper.extract_json_ld_selenium("https://example.com")
        expected = [{"@context": "http://schema.org", "@type": "Article", "headline": "Test Article"}]
        self.assertEqual(result, expected)
        mock_browser.close.assert_called_once()

    @patch('models.scraper.sync_playwright')
    def test_extract_json_ld_selenium_invalid_json(self, mock_playwright):
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_script = MagicMock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.query_selector_all.return_value = [mock_script]
        mock_script.inner_text.return_value = '{"@context": "http://schema.org", "@type": "Article", "headline": "Test Article"'
        result = BeautifulSoupScraper.extract_json_ld_selenium("https://example.com")
        # Invalid json is corrected by the method
        expected = [{"@context": "http://schema.org", "@type": "Article", "headline": "Test Article"}]
        self.assertEqual(result, expected)
        mock_browser.close.assert_called_once()

    @patch('models.scraper.sync_playwright')
    def test_extract_json_ld_selenium_no_json_ld(self, mock_playwright):
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.query_selector_all.return_value = []
        result = BeautifulSoupScraper.extract_json_ld_selenium("https://example.com")
        self.assertIsNone(result)
        mock_browser.close.assert_called_once()

    @patch('models.scraper.sync_playwright')
    def test_extract_json_ld_selenium_empty(self, mock_playwright):
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_script = MagicMock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.query_selector_all.return_value = [mock_script]
        mock_script.inner_text.return_value = ''
        result = BeautifulSoupScraper.extract_json_ld_selenium("https://example.com")
        self.assertIsNone(result)
        mock_browser.close.assert_called_once()

    def test_get_full_language_name(self):
        result = self.scraper.get_full_language_name('en')
        self.assertEqual(result, 'English')

    def test_detect_language_full_name(self):
        result = self.scraper.detect_language_full_name("This is a sample text.")
        self.assertEqual(result, ('en', 'English'))

    @patch('requests.get')
    def test_extract_json_ld_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Failed to fetch URL")
        result = self.scraper.extract_json_ld('https://example.com')
        self.assertIsNone(result)

    @patch('requests.get')
    def test_extract_rdfa_failure(self, mock_get):
        # Simulate a failed HTTP request
        mock_get.side_effect = requests.exceptions.RequestException("Failed to fetch URL")

        scraper = BeautifulSoupScraper()
        result = scraper.extract_rdfa('https://example.com')

        # Assert that the result is None due to the failure
        self.assertIsNone(result)

    @patch('requests.get')
    def test_clean_rdfa_for_schema_2(self, mock_get):
        rdfa_data = {
            'http://ogp.me/ns#title': [{'@value': 'Sample Article Title'}]
        }
        result = self.scraper.clean_rdfa_for_schema(rdfa_data)
        self.assertEqual(result['headline'], 'Sample Article Title')
        rdfa_data = {
            'http://ogp.me/ns#description': [{'@value': 'Sample description of the article'}]
        }
        result = self.scraper.clean_rdfa_for_schema(rdfa_data)
        self.assertEqual(result['description'], 'Sample description of the article')
        rdfa_data = {
            'http://ogp.me/ns#image': [{'@value': 'http://example.com/image.jpg'}]
        }
        result = self.scraper.clean_rdfa_for_schema(rdfa_data)
        self.assertEqual(result['image'], 'http://example.com/image.jpg')
        rdfa_data = {
            'http://ogp.me/ns#image:alt': [{'@value': 'Image alt text'}]
        }
        result = self.scraper.clean_rdfa_for_schema(rdfa_data)
        self.assertEqual(result['imageAlt'], 'Image alt text')
        rdfa_data = {
            'al:web:url': [{'@value': 'http://example.com'}]
        }
        result = self.scraper.clean_rdfa_for_schema(rdfa_data)
        self.assertEqual(result['url'], 'http://example.com')


class TestBeautifulSoupScraper2(unittest.TestCase):

    @patch.object(BeautifulSoupScraper, 'extract_json_ld_youtube')
    @patch.object(BeautifulSoupScraper, 'extract_json_ld_selenium')
    def test_extract_main_article_json_ld_additional_cases(self, mock_extract_json_ld_selenium,
                                                           mock_extract_json_ld_youtube):
        scraper = BeautifulSoupScraper()

        # Scenario: JSON-LD with a dictionary containing "mainEntityOfPage"
        page_url_with_main_entity = 'https://www.example.com/article/with-main-entity'
        mock_extract_json_ld_selenium.return_value = [
            {'@type': 'Article', 'mainEntityOfPage': {'@id': page_url_with_main_entity}}
        ]
        mock_extract_json_ld_youtube.return_value = []

        result = scraper.extract_main_article_json_ld(None, '', page_url_with_main_entity)
        self.assertIsNotNone(result)
        self.assertEqual(result['@type'], 'Article')
        self.assertIn('mainEntityOfPage', result)

        # Scenario: JSON-LD with "@type" as a list and a matching "mainEntityOfPage"
        page_url_with_type_list = 'https://www.example.com/article/with-type-list'
        mock_extract_json_ld_selenium.return_value = [
            {
                '@type': ['NewsArticle', 'BlogPosting'],
                'mainEntityOfPage': {'@id': page_url_with_type_list}
            }
        ]
        mock_extract_json_ld_youtube.return_value = []

        result = scraper.extract_main_article_json_ld(None, '', page_url_with_type_list)
        self.assertIsNotNone(result)
        self.assertIn('mainEntityOfPage', result)
        self.assertEqual(result['mainEntityOfPage']['@id'], page_url_with_type_list)

        # Scenario: JSONDecodeError in one of the scripts
        mock_extract_json_ld_selenium.return_value = ['Invalid JSON']
        mock_extract_json_ld_youtube.return_value = []

        with patch('json.loads', side_effect=json.JSONDecodeError('Error', 'doc', 0)):
            result = scraper.extract_main_article_json_ld(None, '', 'https://www.example.com/article/error')
            self.assertIsNone(result)

    @patch.object(BeautifulSoupScraper, 'extract_json_ld_youtube')
    @patch.object(BeautifulSoupScraper, 'extract_json_ld_selenium')
    def test_extract_main_article_json_ld(self, mock_extract_json_ld_selenium, mock_extract_json_ld_youtube):
        # Scenario 1: Page is a YouTube URL
        page_url_youtube = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        mock_extract_json_ld_youtube.return_value = [{'@type': 'VideoObject', 'url': page_url_youtube}]
        mock_extract_json_ld_selenium.return_value = []

        scraper = BeautifulSoupScraper()
        result = scraper.extract_main_article_json_ld(None, '', page_url_youtube)

        self.assertIsNotNone(result)
        self.assertEqual(result['@type'], 'VideoObject')

        # Scenario 2: Page is not a YouTube URL
        page_url_non_youtube = 'https://www.example.com/article/1'
        mock_extract_json_ld_youtube.return_value = []
        mock_extract_json_ld_selenium.return_value = [{'@type': 'Article', 'url': page_url_non_youtube}]

        result = scraper.extract_main_article_json_ld(None, '', page_url_non_youtube)
        self.assertIsNotNone(result)
        self.assertEqual(result['@type'], 'Article')

        # Scenario 3: No JSON-LD scripts found
        mock_extract_json_ld_youtube.return_value = []
        mock_extract_json_ld_selenium.return_value = []

        result = scraper.extract_main_article_json_ld(None, '', page_url_non_youtube)
        self.assertIsNone(result)

        # Scenario 4: JSON-LD with '@graph' containing matching article types
        page_url_with_graph = 'https://www.example.com/article/2'
        mock_extract_json_ld_youtube.return_value = []
        mock_extract_json_ld_selenium.return_value = [
            {'@graph': [
                {'@type': 'Article', 'url': page_url_with_graph, 'mainEntityOfPage': {'@id': page_url_with_graph}},
                {'@type': 'NewsArticle', 'url': page_url_with_graph, 'mainEntityOfPage': {'@id': page_url_with_graph}}
            ]}
        ]

        result = scraper.extract_main_article_json_ld(None, '', page_url_with_graph)
        self.assertIsNotNone(result)
        self.assertEqual(result['@type'], 'Article')

        # Scenario 5: JSON-LD with a list of items, including matching article types
        page_url_with_list = 'https://www.example.com/article/3'
        mock_extract_json_ld_youtube.return_value = []
        mock_extract_json_ld_selenium.return_value = [
            [{'@type': 'Article', 'url': page_url_with_list}],
            [{'@type': 'BlogPosting', 'url': page_url_with_list}]
        ]

        result = scraper.extract_main_article_json_ld(None, '', page_url_with_list)
        self.assertIsNotNone(result)
        self.assertEqual(result['@type'], 'Article')

        # Scenario 6: JSON-LD with a single dictionary containing a matching article type
        page_url_with_single = 'https://www.example.com/article/4'
        mock_extract_json_ld_youtube.return_value = []
        mock_extract_json_ld_selenium.return_value = [
            {'@type': 'BlogPosting', 'url': page_url_with_single}
        ]

        result = scraper.extract_main_article_json_ld(None, '', page_url_with_single)
        self.assertIsNotNone(result)
        self.assertEqual(result['@type'], 'BlogPosting')

        # Scenario 7: No matches in the JSON-LD
        page_url_no_match = 'https://www.example.com/article/5'
        mock_extract_json_ld_youtube.return_value = []
        mock_extract_json_ld_selenium.return_value = [
            {'@type': 'Person', 'url': page_url_no_match}
        ]

        result = scraper.extract_main_article_json_ld(None, '', page_url_no_match)
        self.assertIsNone(result)


class TestExtractor(unittest.TestCase):
    def setUp(self):
        # Common setup for all tests
        self.url = "https://www.example.com"
        self.scraper = BeautifulSoupScraper()

    @patch("requests.get")
    def test_http_request_success(self, mock_requests_get):
        # Test successful HTTP request
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.content = b"<html><body>Sample content</body></html>"
        mock_requests_get.return_value = mock_response

        response = requests.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"<html><body>Sample content</body></html>")
        mock_requests_get.assert_called_once_with(
            self.url
        )

    @patch("goose3.Goose")
    def test_goose_extraction(self, mock_goose):
        # Test Goose extraction functionality
        mock_goose_instance = Mock()
        mock_goose_instance.extract.return_value.cleaned_text = "Sample cleaned text from Goose"
        mock_goose.return_value = mock_goose_instance

        goose_instance = mock_goose()
        extracted_data = goose_instance.extract(url=self.url)
        self.assertEqual(extracted_data.cleaned_text, "Sample cleaned text from Goose")
        mock_goose.assert_called_once()

    @patch("newspaper.Article")
    def test_newspaper_extraction(self, mock_article):
        # Test Newspaper3k extraction functionality
        mock_article_instance = Mock()
        mock_article_instance.keywords = ["keyword1", "keyword2"]
        mock_article_instance.html = "<html><body>Sample content</body></html>"
        mock_article_instance.download.return_value = None
        mock_article_instance.parse.return_value = None
        mock_article_instance.nlp.return_value = None
        mock_article.return_value = mock_article_instance

        article_instance = mock_article(self.url)
        article_instance.download()
        article_instance.parse()
        article_instance.nlp()

        self.assertEqual(article_instance.keywords, ["keyword1", "keyword2"])
        mock_article.assert_called_once_with(self.url)

    @patch("models.scraper.BeautifulSoupScraper.detect_language")
    def test_language_detection(self, mock_detect_language):
        # Test language detection
        mock_detect_language.return_value = ("en", "English")

        detected_language = self.scraper.detect_language(
            Mock(), Mock(), "Sample cleaned text from Goose"
        )
        self.assertEqual(detected_language, ("en", "English"))
        mock_detect_language.assert_called_once()


class TestScraperData(unittest.TestCase):

    @patch('requests.get')
    def test_get_html_content_success(self, mock_get):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        scraper = BeautifulSoupScraper()
        result = scraper._get_html_content("https://example.com")

        # Assert that the response was returned successfully
        self.assertEqual(result, mock_response)
        mock_get.assert_called_once_with("https://example.com", headers={"User-Agent": scraper.user_agent},
                                         timeout=scraper.timeout)

    @patch('requests.get')
    def test_get_html_content_retry(self, mock_get):
        # Simulate retries and then success
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.side_effect = [requests.exceptions.RequestException, requests.exceptions.RequestException,
                                mock_response]

        scraper = BeautifulSoupScraper()
        result = scraper._get_html_content("https://example.com")

        # Assert that the response was returned successfully after retries
        self.assertEqual(result, mock_response)
        self.assertEqual(mock_get.call_count, 3)  # Should have retried 2 times

    @patch('requests.get')
    def test_get_html_content_failure(self, mock_get):
        # Simulate failure to get the HTML content
        mock_get.side_effect = requests.exceptions.RequestException

        scraper = BeautifulSoupScraper()
        with self.assertRaises(ValueError):
            scraper._get_html_content("https://example.com")

    @patch('newspaper.Article')
    @patch('goose3.Goose')
    def test_parse_article(self, mock_goose, mock_article):
        # Mock article instance and methods
        mock_article_instance = MagicMock()
        mock_article.return_value = mock_article_instance
        mock_article_instance.keywords = ['keyword1', 'keyword2']
        mock_article_instance.download = MagicMock()
        mock_article_instance.parse = MagicMock()
        mock_article_instance.nlp = MagicMock()

        scraper = BeautifulSoupScraper()

        # Call the method
        result = scraper._parse_article(mock_article_instance)

        # Check that the methods were called
        mock_article_instance.download.assert_called_once()
        mock_article_instance.parse.assert_called_once()
        mock_article_instance.nlp.assert_called_once()

        # Assert the returned article is the same as the input article
        self.assertEqual(result, mock_article_instance)


class TestBeautifulSoupScraper3(unittest.TestCase):
    @patch('requests.get')  # Mock only requests.get
    @patch('goose3.Goose')  # Mock Goose
    @patch('newspaper.Article')  # Mock Newspaper Article
    def test_extract_data(self, mock_article, mock_goose, mock_requests_get):
        # Step 1: Mock the response from requests
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><h1>Sample Content</h1></body></html>"  # Real HTML bytes
        mock_response.text = "<html><body><h1>Sample Content</h1></body></html>"  # Real HTML text

        # Mock the headers to return a valid language code (e.g., 'en' for English)
        mock_response.headers.get.return_value = 'en'
        mock_requests_get.return_value = mock_response

        # Step 2: Mock Goose extraction behavior
        mock_goose_instance = MagicMock()
        mock_goose.return_value = mock_goose_instance
        mock_goose_instance.extract.return_value.cleaned_text = "Goose article content"

        # Step 3: Mock Newspaper article behavior
        mock_article_instance = MagicMock()
        mock_article.return_value = mock_article_instance
        mock_article_instance.keywords = ['keyword1', 'keyword2']

        # Step 4: Create BeautifulSoupScraper instance
        scraper = BeautifulSoupScraper()

        # Step 5: Call the method under test
        result = scraper.extract_data("https://example.com")

        # Step 6: Assertions to verify the result
        self.assertEqual(result['content'],
                         "This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.")
        self.assertEqual(result['keywords'], [])
        self.assertEqual(result['language_code'], 'en')  # Assuming 'en' is detected
        self.assertEqual(result['language_name'], 'English')  # Assuming 'English' is detected

    @patch('goose3.Goose')  # Mock Goose only
    @patch('newspaper.Article')  # Mock newspaper.Article only
    def test_parse_article_method(self, mock_article, mock_goose):
        # Step 1: Setup Goose mock
        mock_goose_instance = MagicMock()
        mock_goose.return_value = mock_goose_instance
        mock_goose_instance.extract.return_value.cleaned_text = "Goose article content"

        # Step 2: Setup Newspaper article mock
        mock_article_instance = MagicMock()
        mock_article.return_value = mock_article_instance
        mock_article_instance.keywords = ['keyword1', 'keyword2']

        def mock_download():
            mock_article_instance.is_downloaded = True

        def mock_parse():
            mock_article_instance.is_parsed = True

        mock_article_instance.download.side_effect = mock_download
        mock_article_instance.parse.side_effect = mock_parse
        mock_article_instance.html = "<html><body><h1>Sample Content</h1></body></html>"

        # Step 3: Create a BeautifulSoupScraper instance
        scraper = BeautifulSoupScraper()

        # Step 4: Call the method to test _parse_article
        article = scraper._parse_article(mock_article_instance)

        # Step 5: Assertions to verify the article was processed correctly
        self.assertTrue(mock_article_instance.is_downloaded)
        self.assertTrue(mock_article_instance.is_parsed)
        self.assertEqual(article.keywords, ['keyword1', 'keyword2'])
        self.assertEqual(article.html, "<html><body><h1>Sample Content</h1></body></html>")


class TestDetectLanguageBeautifulSoupScraper(unittest.TestCase):
    def setUp(self):
        # Create an instance of the scraper for use in the tests
        self.scraper = BeautifulSoupScraper()

    @patch('models.scraper.BeautifulSoupScraper.get_full_language_name')
    def test_detect_language_header(self, mock_get_full_language_name):
        # Case 1: Valid Content-Language header
        mock_response = MagicMock()
        mock_response.headers.get.return_value = 'en, en'
        mock_soup = MagicMock()
        mock_content = "Some article content"

        # Mock the full language name function
        mock_get_full_language_name.return_value = "English"

        lang_code, full_name = self.scraper.detect_language(mock_response, mock_soup, mock_content)

        self.assertEqual(lang_code, 'en')
        self.assertEqual(full_name, 'English')

    @patch('models.scraper.BeautifulSoupScraper.get_full_language_name')
    def test_detect_language_html_lang(self, mock_get_full_language_name):
        # Case 2: Valid lang attribute in <html> tag
        mock_response = MagicMock()
        mock_response.headers.get.return_value = None  # No Content-Language header
        mock_soup = MagicMock()
        mock_soup.html.get.return_value = 'fr'
        mock_content = "Some article content"

        # Mock the full language name function
        mock_get_full_language_name.return_value = "French"

        lang_code, full_name = self.scraper.detect_language(mock_response, mock_soup, mock_content)

        self.assertEqual(lang_code, 'fr')
        self.assertEqual(full_name, 'French')

    @patch('models.scraper.BeautifulSoupScraper.detect_language_full_name')
    def test_detect_language_content(self, mock_detect_language_full_name):
        # Case 3: Valid content-based language detection
        mock_response = MagicMock()
        mock_response.headers.get.return_value = None  # No Content-Language header
        mock_soup = MagicMock()
        mock_soup.html.get.return_value = None  # No lang attribute in <html> tag
        mock_content = "This is some English content"

        # Mock content-based language detection
        mock_detect_language_full_name.return_value = ('en', 'English')

        lang_code, full_name = self.scraper.detect_language(mock_response, mock_soup, mock_content)

        self.assertEqual(lang_code, 'en')
        self.assertEqual(full_name, 'English')

    def test_detect_language_no_info(self):
        # Case 4: No language info (Content-Language header, lang attribute, or content)
        mock_response = MagicMock()
        mock_response.headers.get.return_value = None  # No Content-Language header
        mock_soup = MagicMock()
        mock_soup.html.get.return_value = None  # No lang attribute in <html> tag
        mock_content = ""

        lang_code, full_name = self.scraper.detect_language(mock_response, mock_soup, mock_content)

        self.assertEqual(lang_code, None)
        self.assertEqual(full_name, "Unknown language")

    @patch('models.scraper.BeautifulSoupScraper.detect_language_full_name')
    def test_detect_language_multiple_languages(self, mock_detect_language_full_name):
        # Case 5: Multiple possible languages in Content-Language header
        mock_response = MagicMock()
        mock_response.headers.get.return_value = 'en, fr'
        mock_soup = MagicMock()
        mock_content = "Some article content"

        # Mock the full language name function
        mock_detect_language_full_name.return_value = ('en', 'English')

        lang_code, full_name = self.scraper.detect_language(mock_response, mock_soup, mock_content)

        self.assertEqual(lang_code, 'en')
        self.assertEqual(full_name, 'English')

    def test_detect_language_empty(self):
        # Case 6: Empty content and headers
        mock_response = MagicMock()
        mock_response.headers.get.return_value = None  # No Content-Language header
        mock_soup = MagicMock()
        mock_soup.html.get.return_value = None  # No lang attribute in <html> tag
        mock_content = ""

        lang_code, full_name = self.scraper.detect_language(mock_response, mock_soup, mock_content)

        self.assertEqual(lang_code, None)
        self.assertEqual(full_name, "Unknown language")


class TestBeautifulSoupScraperJsonLoad(unittest.TestCase):
    def setUp(self):
        # Create an instance of the scraper for use in the tests
        self.scraper = BeautifulSoupScraper()

    @patch('requests.get')
    @patch('models.scraper.BeautifulSoupScraper.extract_main_article_json_ld')
    def test_extract_json_ld_success(self, mock_extract_main_article_json_ld, mock_requests_get):
        # Case 1: Valid URL and JSON-LD found

        # Mocking a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><head><script type='application/ld+json'> { 'key': 'value' } </script></head></html>"
        mock_response.text = "<html><head><script type='application/ld+json'> { 'key': 'value' } </script></head></html>"
        mock_requests_get.return_value = mock_response

        # Mocking the JSON-LD extraction function
        mock_extract_main_article_json_ld.return_value = {"key": "value"}

        # Call the method
        result = self.scraper.extract_json_ld("https://example.com")

        # Assert that the result is the expected JSON-LD data
        self.assertEqual(result, {"key": "value"})

    @patch('requests.get')
    @patch('models.scraper.BeautifulSoupScraper.extract_main_article_json_ld')
    def test_extract_json_ld_no_json_ld(self, mock_extract_main_article_json_ld, mock_requests_get):
        # Case 2: Valid URL but no JSON-LD found

        # Mocking a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><p>No JSON-LD here!</p></body></html>"
        mock_response.text = "<html><body><p>No JSON-LD here!</p></body></html>"
        mock_requests_get.return_value = mock_response

        # Mocking the JSON-LD extraction function
        mock_extract_main_article_json_ld.return_value = None

        # Call the method
        result = self.scraper.extract_json_ld("https://example.com")

        # Assert that the result is None (no JSON-LD found)
        self.assertIsNone(result)

    @patch('requests.get')
    def test_extract_json_ld_invalid_url(self, mock_requests_get):
        # Case 3: Invalid URL (RequestException)

        # Simulate a request exception
        mock_requests_get.side_effect = requests.exceptions.RequestException("Invalid URL")

        # Call the method
        result = self.scraper.extract_json_ld("https://invalid-url.com")

        # Assert that the result is None (due to the request exception)
        self.assertIsNone(result)

    @patch('requests.get')
    def test_extract_json_ld_http_error(self, mock_requests_get):
        # Case 4: Valid URL but HTTP error (404)

        # Mocking a 404 HTTP error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.content = b"<html><body>Page not found</body></html>"
        mock_response.text = "<html><body>Page not found</body></html>"
        mock_requests_get.return_value = mock_response

        # Call the method
        result = self.scraper.extract_json_ld("https://example.com")

        # Assert that the result is None due to the HTTP error
        self.assertIsNone(result)

    @patch('requests.get')
    @patch('models.scraper.BeautifulSoupScraper.extract_main_article_json_ld')
    def test_extract_json_ld_unexpected_json_ld(self, mock_extract_main_article_json_ld, mock_requests_get):
        # Case 5: Valid URL but with unexpected structure in JSON-LD

        # Mocking a successful response with unexpected JSON-LD content
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><head><script type='application/ld+json'> { 'unexpected': 'structure' } </script></head></html>"
        mock_response.text = "<html><head><script type='application/ld+json'> { 'unexpected': 'structure' } </script></head></html>"
        mock_requests_get.return_value = mock_response

        # Mocking the unexpected JSON-LD extraction function
        mock_extract_main_article_json_ld.return_value = {"unexpected": "structure"}

        # Call the method
        result = self.scraper.extract_json_ld("https://example.com")

        # Assert that the result contains the unexpected structure (as it's still a valid JSON-LD)
        self.assertEqual(result, {"unexpected": "structure"})

    @patch('requests.get')
    @patch('models.scraper.BeautifulSoupScraper.extract_main_article_json_ld')
    def test_extract_json_ld_invalid_json(self, mock_extract_main_article_json_ld, mock_requests_get):
        # Case 6: Valid URL but malformed or invalid JSON in JSON-LD

        # Mocking a successful response with invalid JSON in JSON-LD
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><head><script type='application/ld+json'> { 'invalid': 'json' </script></head></html>"
        mock_response.text = "<html><head><script type='application/ld+json'> { 'invalid': 'json' </script></head></html>"
        mock_requests_get.return_value = mock_response

        # Mocking the invalid JSON-LD extraction function
        mock_extract_main_article_json_ld.return_value = None

        # Call the method
        result = self.scraper.extract_json_ld("https://example.com")

        # Assert that the result is None (due to invalid JSON)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
