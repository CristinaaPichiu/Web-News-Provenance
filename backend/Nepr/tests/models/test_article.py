import unittest
from models.article import Article
from models.multimedia import AudioObject, VideoObject, ImageObject
from models.entity import Author, Publisher, Person, Organization

class TestArticle(unittest.TestCase):

    def test_article_initialization(self):
        article = Article(
            articleBody="This is the body of the article.",
            articleSection="Technology",
            wordCount=1200,
            abstract="This is an abstract.",
            audio_uri="audio_uri",
            author_uri="author_uri",
            dateCreated="2023-01-01",
            dateModified="2023-01-02",
            datePublished="2023-01-03",
            editor_uri="editor_uri",
            headline="This is a headline.",
            inLanguage="en",
            keywords=["example", "test"],
            publisher_uri="publisher_uri",
            text="This is the text content.",
            thumbnail_uri="thumbnail_uri",
            thumbnailUrl="http://example.com/thumbnail.jpg",
            video_uri="video_uri"
        )

        self.assertEqual(article.articleBody, "This is the body of the article.")
        self.assertEqual(article.articleSection, "Technology")
        self.assertEqual(article.wordCount, 1200)
        self.assertEqual(article.abstract, "This is an abstract.")
        self.assertEqual(article.audio_uri, "audio_uri")
        self.assertEqual(article.author_uri, "author_uri")
        self.assertEqual(article.dateCreated, "2023-01-01")
        self.assertEqual(article.dateModified, "2023-01-02")
        self.assertEqual(article.datePublished, "2023-01-03")
        self.assertEqual(article.editor_uri, "editor_uri")
        self.assertEqual(article.headline, "This is a headline.")
        self.assertEqual(article.inLanguage, "en")
        self.assertEqual(article.keywords, ["example", "test"])
        self.assertEqual(article.publisher_uri, "publisher_uri")
        self.assertEqual(article.text, "This is the text content.")
        self.assertEqual(article.thumbnail_uri, "thumbnail_uri")
        self.assertEqual(article.thumbnailUrl, "http://example.com/thumbnail.jpg")
        self.assertEqual(article.video_uri, "video_uri")

    def test_article_dict(self):

        article = Article(
            articleBody="This is the body of the article.",
            articleSection="Technology",
            wordCount=1200,
            abstract="This is an abstract.",
            audio_uri="audio_uri",
            author_uri="author_uri",
            dateCreated="2023-01-01",
            dateModified="2023-01-02",
            datePublished="2023-01-03",
            editor_uri="editor_uri",
            headline="This is a headline.",
            inLanguage="en",
            keywords=["example", "test"],
            publisher_uri="publisher_uri",
            text="This is the text content.",
            thumbnail_uri="thumbnail_uri",
            thumbnailUrl="http://example.com/thumbnail.jpg",
            video_uri="video_uri"
        )

        expected_dict = {
            "articleBody": "This is the body of the article.",
            "articleSection": "Technology",
            "wordCount": 1200,
            "abstract": "This is an abstract.",
            "audio_uri": "audio_uri",
            "author_uri": "author_uri",
            "dateCreated": "2023-01-01",
            "dateModified": "2023-01-02",
            "datePublished": "2023-01-03",
            "editor_uri": "editor_uri",
            "headline": "This is a headline.",
            "inLanguage": "en",
            "keywords": ["example", "test"],
            "publisher_uri": "publisher_uri",
            "text": "This is the text content.",
            "thumbnail_uri": "thumbnail_uri",
            "thumbnailUrl": "http://example.com/thumbnail.jpg",
            "video_uri": "video_uri",
        }

        self.assertEqual(article.__dict__(), expected_dict)

    def test_set_articleBody(self):
        article = Article()
        article.set_articleBody("New article body.")
        self.assertEqual(article.articleBody, "New article body.")

    def test_set_articleSection(self):
        article = Article()
        article.set_articleSection("Technology")
        self.assertEqual(article.articleSection, "Technology")

    def test_set_wordCount(self):
        article = Article()
        article.set_wordCount(1200)
        self.assertEqual(article.wordCount, 1200)

if __name__ == '__main__':
    unittest.main()