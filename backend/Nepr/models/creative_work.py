class CreativeWork:

    def __init__(self, abstract=None, audio_uri=None, author_uri=None, dateCreated=None, dateModified=None, datePublished=None, editor_uri=None, headline=None, inLanguage=None, keywords=None, publisher_uri=None, text=None, thumbnail_uri=None, thumbnailUrl=None, video_uri=None, node_uri=None):
        self.abstract = abstract
        self.audio_uri = audio_uri
        self.author_uri = author_uri
        self.dateCreated = dateCreated
        self.dateModified = dateModified
        self.datePublished = datePublished
        self.editor_uri = editor_uri
        self.headline = headline
        self.inLanguage = inLanguage
        self.keywords = keywords
        self.publisher_uri = publisher_uri
        self.text = text
        self.thumbnail_uri = thumbnail_uri
        self.thumbnailUrl = thumbnailUrl
        self.video_uri = video_uri
        self.node_uri = node_uri

    def set_abstract(self, abstract):
        self.abstract = abstract

    def set_audio_uri(self, audio_uri):
        self.audio_uri = audio_uri

    def set_author_uri(self, author_uri):
        self.author_uri = author_uri

    def set_dateCreated(self, dateCreated):
        self.dateCreated = dateCreated

    def set_dateModified(self, dateModified):
        self.dateModified = dateModified

    def set_datePublished(self, datePublished):
        self.datePublished = datePublished

    def set_editor_uri(self, editor_uri):
        self.editor_uri = editor_uri

    def set_headline(self, headline):
        self.headline = headline

    def set_inLanguage(self, inLanguage):
        self.inLanguage = inLanguage

    def set_keywords(self, keywords):
        self.keywords = keywords

    def set_publisher_uri(self, publisher_uri):
        self.publisher_uri = publisher_uri

    def set_text(self, text):
        self.text = text

    def set_thumbnail_uri(self, thumbnail_uri):
        self.thumbnail_uri = thumbnail_uri

    def set_thumbnailUrl(self, thumbnailUrl):
        self.thumbnailUrl = thumbnailUrl

    def set_video_uri(self, video_uri):
        self.video_uri = video_uri

    def set_node_uri(self, node_uri):
        self.node_uri = node_uri

    def __dict__(self):
        def convert_to_dict(value):
            if isinstance(value, list):
                return [convert_to_dict(item) for item in value]
            return value

        return {
            k: convert_to_dict(v)
            for k, v in {
                "abstract": self.abstract,
                "audio_uri": self.audio_uri,
                "author_uri": self.author_uri,
                "dateCreated": self.dateCreated,
                "dateModified": self.dateModified,
                "datePublished": self.datePublished,
                "editor_uri": self.editor_uri,
                "headline": self.headline,
                "inLanguage": self.inLanguage,
                "keywords": self.keywords,
                "publisher_uri": self.publisher_uri,
                "text": self.text,
                "thumbnail_uri": self.thumbnail_uri,
                "thumbnailUrl": self.thumbnailUrl,
                "video_uri": self.video_uri,
                "node_uri": self.node_uri
            }.items() if v is not None
        }
