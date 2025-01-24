from models.creative_work import CreativeWork

class Article(CreativeWork):
    """
    Represents an article.
    """

    def __init__(self, articleBody=None, articleSection=None, wordCount=None, **kwargs):
        super().__init__(**kwargs)
        self.articleBody = articleBody
        self.articleSection = articleSection
        self.wordCount = wordCount

    def set_articleBody(self, articleBody):
        self.articleBody = articleBody

    def set_articleSection(self, articleSection):
        self.articleSection = articleSection

    def set_wordCount(self, wordCount):
        self.wordCount = wordCount

    def __dict__(self):
        return {**super().__dict__(), **{k: v for k, v in {
            "articleBody": self.articleBody,
            "articleSection": self.articleSection,
            "wordCount": self.wordCount
        }.items() if v is not None}}

