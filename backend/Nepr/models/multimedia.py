class MediaObject:

    def __init__(self, contentUrl=None, duration=None, embedUrl=None, height=None, uploadDate=None, width=None, node_uri=None):
        self.contentUrl = contentUrl
        self.duration = duration
        self.embedUrl = embedUrl
        self.height = height
        self.uploadDate = uploadDate
        self.width = width
        self.node_uri = node_uri

    def set_contentUrl(self, contentUrl):
        self.contentUrl = contentUrl

    def set_duration(self, duration):
        self.duration = duration

    def set_embedUrl(self, embedUrl):
        self.embedUrl = embedUrl

    def set_height(self, height):
        self.height = height

    def set_uploadDate(self, uploadDate):
        self.uploadDate = uploadDate

    def set_width(self, width):
        self.width = width

    def set_node_uri(self, node_uri):
        self.node_uri = node_uri

    def __dict__(self):
        return {k: v for k, v in {
            "contentUrl": self.contentUrl,
            "duration": self.duration,
            "embedUrl": self.embedUrl,
            "height": self.height,
            "uploadDate": self.uploadDate,
            "width": self.width,
            "node_uri": self.node_uri
        }.items() if v is not None}

class AudioObject(MediaObject):

    def __init__(self, caption=None, transcript=None, **kwargs):
        self.caption = caption
        self.transcript = transcript
        super().__init__(**kwargs)

    def set_caption(self, caption):
        self.caption = caption

    def set_transcript(self, transcript):
        self.transcript = transcript

    def __dict__(self):
        return {**super().__dict__(), **{k: v for k, v in {
            "caption": self.caption,
            "transcript": self.transcript
        }.items() if v is not None}}

class VideoObject(MediaObject):

    def __init__(self, caption=None, director=None, transcript=None, videoFrameSize=None, videoQuality=None, **kwargs):
        self.caption = caption
        self.director = director
        self.transcript = transcript
        self.videoFrameSize = videoFrameSize
        self.videoQuality = videoQuality
        super().__init__(**kwargs)

    def set_caption(self, caption):
        self.caption = caption

    def set_director(self, director):
        self.director = director

    def set_transcript(self, transcript):
        self.transcript = transcript

    def set_videoFrameSize(self, videoFrameSize):
        self.videoFrameSize = videoFrameSize

    def set_videoQuality(self, videoQuality):
        self.videoQuality = videoQuality

    def __dict__(self):
        return {**super().__dict__(), **{k: v for k, v in {
            "caption": self.caption,
            "director": self.director,
            "transcript": self.transcript,
            "videoFrameSize": self.videoFrameSize,
            "videoQuality": self.videoQuality
        }.items() if v is not None}}

class ImageObject(MediaObject):
    def __init__(self, caption=None, embeddedTextCaption=None, **kwargs):
        self.caption = caption
        self.embeddedTextCaption = embeddedTextCaption
        super().__init__(**kwargs)

    def set_caption(self, caption):
        self.caption = caption

    def set_embeddedTextCaption(self, embeddedTextCaption):
        self.embeddedTextCaption = embeddedTextCaption

    def __dict__(self):
        return {**super().__dict__(), **{k: v for k, v in {
            "caption": self.caption,
            "embeddedTextCaption": self.embeddedTextCaption
        }.items() if v is not None}}


