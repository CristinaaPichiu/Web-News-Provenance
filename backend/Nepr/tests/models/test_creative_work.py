import unittest
from models.creative_work import CreativeWork

class TestCreativeWork(unittest.TestCase):

    def setUp(self):
        self.creative_work = CreativeWork(
            abstract="Sample abstract",
            audio_uri="audio_uri",
            author_uri="author_uri",
            dateCreated="2023-01-01",
            dateModified="2023-01-02",
            datePublished="2023-01-03",
            editor_uri="editor_uri",
            headline="Sample headline",
            inLanguage="en",
            keywords=["keyword1", "keyword2"],
            publisher_uri="publisher_uri",
            text="Sample text",
            thumbnail_uri="thumbnail_uri",
            thumbnailUrl="http://example.com/thumbnail.jpg",
            video_uri="video_uri",
            node_uri="node_uri"
        )

    def test_creative_work_initialization(self):
        self.assertEqual(self.creative_work.abstract, "Sample abstract")
        self.assertEqual(self.creative_work.audio_uri, "audio_uri")
        self.assertEqual(self.creative_work.author_uri, "author_uri")
        self.assertEqual(self.creative_work.dateCreated, "2023-01-01")
        self.assertEqual(self.creative_work.dateModified, "2023-01-02")
        self.assertEqual(self.creative_work.datePublished, "2023-01-03")
        self.assertEqual(self.creative_work.editor_uri, "editor_uri")
        self.assertEqual(self.creative_work.headline, "Sample headline")
        self.assertEqual(self.creative_work.inLanguage, "en")
        self.assertEqual(self.creative_work.keywords, ["keyword1", "keyword2"])
        self.assertEqual(self.creative_work.publisher_uri, "publisher_uri")
        self.assertEqual(self.creative_work.text, "Sample text")
        self.assertEqual(self.creative_work.thumbnail_uri, "thumbnail_uri")
        self.assertEqual(self.creative_work.thumbnailUrl, "http://example.com/thumbnail.jpg")
        self.assertEqual(self.creative_work.video_uri, "video_uri")
        self.assertEqual(self.creative_work.node_uri, "node_uri")

    def test_creative_work_to_dict(self):
        expected_dict = {
            "abstract": "Sample abstract",
            "audio_uri": "audio_uri",
            "author_uri": "author_uri",
            "dateCreated": "2023-01-01",
            "dateModified": "2023-01-02",
            "datePublished": "2023-01-03",
            "editor_uri": "editor_uri",
            "headline": "Sample headline",
            "inLanguage": "en",
            "keywords": ["keyword1", "keyword2"],
            "publisher_uri": "publisher_uri",
            "text": "Sample text",
            "thumbnail_uri": "thumbnail_uri",
            "thumbnailUrl": "http://example.com/thumbnail.jpg",
            "video_uri": "video_uri",
            "node_uri": "node_uri"
        }
        self.assertEqual(self.creative_work.__dict__(), expected_dict)

    def test_set_abstract(self):
        self.creative_work.set_abstract("New abstract")
        self.assertEqual(self.creative_work.abstract, "New abstract")

    def test_set_audio_uri(self):
        self.creative_work.set_audio_uri("new_audio_uri")
        self.assertEqual(self.creative_work.audio_uri, "new_audio_uri")

    def test_set_author_uri(self):
        self.creative_work.set_author_uri("new_author_uri")
        self.assertEqual(self.creative_work.author_uri, "new_author_uri")

    def test_set_dateCreated(self):
        self.creative_work.set_dateCreated("2023-02-01")
        self.assertEqual(self.creative_work.dateCreated, "2023-02-01")

    def test_set_dateModified(self):
        self.creative_work.set_dateModified("2023-02-02")
        self.assertEqual(self.creative_work.dateModified, "2023-02-02")

    def test_set_datePublished(self):
        self.creative_work.set_datePublished("2023-02-03")
        self.assertEqual(self.creative_work.datePublished, "2023-02-03")

    def test_set_editor_uri(self):
        self.creative_work.set_editor_uri("new_editor_uri")
        self.assertEqual(self.creative_work.editor_uri, "new_editor_uri")

    def test_set_headline(self):
        self.creative_work.set_headline("New headline")
        self.assertEqual(self.creative_work.headline, "New headline")

    def test_set_inLanguage(self):
        self.creative_work.set_inLanguage("fr")
        self.assertEqual(self.creative_work.inLanguage, "fr")

    def test_set_keywords(self):
        self.creative_work.set_keywords(["new_keyword1", "new_keyword2"])
        self.assertEqual(self.creative_work.keywords, ["new_keyword1", "new_keyword2"])

    def test_set_publisher_uri(self):
        self.creative_work.set_publisher_uri("new_publisher_uri")
        self.assertEqual(self.creative_work.publisher_uri, "new_publisher_uri")

    def test_set_text(self):
        self.creative_work.set_text("New text")
        self.assertEqual(self.creative_work.text, "New text")

    def test_set_thumbnail_uri(self):
        self.creative_work.set_thumbnail_uri("new_thumbnail_uri")
        self.assertEqual(self.creative_work.thumbnail_uri, "new_thumbnail_uri")

    def test_set_thumbnailUrl(self):
        self.creative_work.set_thumbnailUrl("http://example.com/new_thumbnail.jpg")
        self.assertEqual(self.creative_work.thumbnailUrl, "http://example.com/new_thumbnail.jpg")

    def test_set_video_uri(self):
        self.creative_work.set_video_uri("new_video_uri")
        self.assertEqual(self.creative_work.video_uri, "new_video_uri")

    def test_set_node_uri(self):
        self.creative_work.set_node_uri("new_node_uri")
        self.assertEqual(self.creative_work.node_uri, "new_node_uri")

if __name__ == '__main__':
    unittest.main()