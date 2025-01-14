import unittest
from unittest.mock import patch, Mock
from io import BytesIO
import requests
from models.scraper import BeautifulSoupScraper


class TestBeautifulSoupScraper(unittest.TestCase):
    @patch('requests.get')
    def test_extract_data_success(self, mock_get):
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html><body>
        <div class="article-content"><p>Test content for the article.</p></div>
        </body></html>
        """
        mock_get.return_value = mock_response

        # Initialize the scraper
        scraper = BeautifulSoupScraper()
        result = scraper.extract_data("https://mockurl.com")

        # Assert the expected behavior
        self.assertEqual(result['content'], "Test content for the article.")

    @patch('requests.get')
    def test_extract_data_failure(self, mock_get):
        # Mock a failed HTTP response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        scraper = BeautifulSoupScraper()
        with self.assertRaises(ValueError):
            scraper.extract_data("https://mockurl.com")

    @patch('requests.get')
    def test_extract_data_request_exception(self, mock_get):
        # Mock a request exception
        mock_get.side_effect = requests.RequestException("Request failed")

        scraper = BeautifulSoupScraper()
        with self.assertRaises(ValueError):
            scraper.extract_data("https://mockurl.com")

    @patch('requests.get')
    def test_extract_data_no_content(self, mock_get):
        # Mock a successful response, but no valid content
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html><body><div class="article-content"></div></body></html>
        """
        mock_get.return_value = mock_response

        scraper = BeautifulSoupScraper()
        result = scraper.extract_data("https://mockurl.com")
        self.assertEqual(result['content'], "No content available")

    @patch('requests.get')
    def test_extract_content_no_selector_found(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html><body><div class="non-existent-content"></div></body></html>
        """
        mock_get.return_value = mock_response

        scraper = BeautifulSoupScraper()
        result = scraper.extract_data("https://mockurl.com")
        self.assertEqual(result['content'], "No content available")

    @patch('requests.get')
    def test_extract_content_with_paragraphs(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html><body>
        <div class="article-content">
            <p>This is the first paragraph with some content.</p>
            <p>This is the second paragraph with more content.</p>
        </div>
        </body></html>
        """
        mock_get.return_value = mock_response

        scraper = BeautifulSoupScraper()
        result = scraper.extract_data("https://mockurl.com")

        # Assert that the extracted content is concatenated correctly
        self.assertEqual(result['content'],
                         "This is the first paragraph with some content.\nThis is the second paragraph with more content.")

    @patch('requests.get')
    def test_extract_content_with_filtered_paragraphs(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html><body>
        <div class="article-content">
            <p>To short.</p>
            <p>This paragraph has enough content to be included.</p>
            <p>short x2</p>
        </div>
        </body></html>
        """
        mock_get.return_value = mock_response

        scraper = BeautifulSoupScraper()
        result = scraper.extract_data("https://mockurl.com")

        # Assert that only the filtered paragraph is included
        self.assertEqual(result['content'], "This paragraph has enough content to be included.")

    @patch('requests.get')
    def test_extract_content_handle_special_characters(self, mock_get):
        # Mock a response with special characters in content
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html><body>
        <div class="article-content">
            <p>This is a paragraph with a special character: &#xA9;</p>
        </div>
        </body></html>
        """
        mock_get.return_value = mock_response
        scraper = BeautifulSoupScraper()
        result = scraper.extract_data("https://mockurl.com")
        self.assertEqual(result['content'], "This is a paragraph with a special character: ©")

    @patch('requests.get')
    def test_extract_content_tag_decomposition(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html><body>
        <header>This is a header that should be removed</header>
        <footer>This is a footer that should be removed</footer>
        <nav>This is a nav that should be removed</nav>
        <div class="article-content">
            <p>This is the main article content.</p>
        </div>
        <aside>This is an aside that should be removed</aside>
        <img src="image.jpg" />
        <form>This is a form that should be removed</form>
        </body></html>
        """
        mock_get.return_value = mock_response

        scraper = BeautifulSoupScraper()
        result = scraper.extract_data("https://mockurl.com")

        expected_content = "This is the main article content."
        self.assertEqual(result['content'], expected_content)

if __name__ == "__main__":
    unittest.main()