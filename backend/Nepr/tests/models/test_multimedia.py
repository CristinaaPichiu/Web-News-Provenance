import unittest
from models.multimedia import AudioObject, VideoObject, ImageObject

class TestMediaObjects(unittest.TestCase):

    def test_audio_object_initialization(self):
        audio = AudioObject(contentUrl="http://example.com/audio.mp3", duration="PT2M", caption="Audio Caption", transcript="Audio Transcript")
        self.assertEqual(audio.contentUrl, "http://example.com/audio.mp3")
        self.assertEqual(audio.duration, "PT2M")
        self.assertEqual(audio.caption, "Audio Caption")
        self.assertEqual(audio.transcript, "Audio Transcript")

    def test_video_object_initialization(self):
        video = VideoObject(contentUrl="http://example.com/video.mp4", duration="PT5M", videoQuality="HD", caption="Video Caption", director="Director Name", transcript="Video Transcript")
        self.assertEqual(video.contentUrl, "http://example.com/video.mp4")
        self.assertEqual(video.duration, "PT5M")
        self.assertEqual(video.videoQuality, "HD")
        self.assertEqual(video.caption, "Video Caption")
        self.assertEqual(video.director, "Director Name")
        self.assertEqual(video.transcript, "Video Transcript")

    def test_image_object_initialization(self):
        image = ImageObject(contentUrl="http://example.com/image.jpg", height=600, width=800, caption="Image Caption", embeddedTextCaption="Embedded Text")
        self.assertEqual(image.contentUrl, "http://example.com/image.jpg")
        self.assertEqual(image.height, 600)
        self.assertEqual(image.width, 800)
        self.assertEqual(image.caption, "Image Caption")
        self.assertEqual(image.embeddedTextCaption, "Embedded Text")

    def test_audio_object_dict(self):
        audio = AudioObject(contentUrl="http://example.com/audio.mp3", duration="PT2M", caption="Audio Caption", transcript="Audio Transcript")
        expected_dict = {
            "contentUrl": "http://example.com/audio.mp3",
            "duration": "PT2M",
            "caption": "Audio Caption",
            "transcript": "Audio Transcript"
        }
        self.assertEqual(audio.__dict__(), expected_dict)

    def test_video_object_dict(self):
        video = VideoObject(contentUrl="http://example.com/video.mp4", duration="PT5M", videoQuality="HD", caption="Video Caption", director="Director Name", transcript="Video Transcript")
        expected_dict = {
            "contentUrl": "http://example.com/video.mp4",
            "duration": "PT5M",
            "videoQuality": "HD",
            "caption": "Video Caption",
            "director": "Director Name",
            "transcript": "Video Transcript"
        }
        self.assertEqual(video.__dict__(), expected_dict)

    def test_image_object_dict(self):
        image = ImageObject(contentUrl="http://example.com/image.jpg", height=600, width=800, caption="Image Caption", embeddedTextCaption="Embedded Text")
        expected_dict = {
            "contentUrl": "http://example.com/image.jpg",
            "height": 600,
            "width": 800,
            "caption": "Image Caption",
            "embeddedTextCaption": "Embedded Text"
        }
        self.assertEqual(image.__dict__(), expected_dict)

    def test_set_audio_contentUrl(self):
        audio = AudioObject()
        audio.set_contentUrl("http://example.com/audio.mp3")
        self.assertEqual(audio.contentUrl, "http://example.com/audio.mp3")

    def test_set_audio_duration(self):
        audio = AudioObject()
        audio.set_duration("PT2M")
        self.assertEqual(audio.duration, "PT2M")

    def test_set_audio_node_uri(self):
        audio = AudioObject()
        audio.set_node_uri("http://example.com/audio")
        self.assertEqual(audio.node_uri, "http://example.com/audio")

    def test_set_audio_caption(self):
        audio = AudioObject()
        audio.set_caption("Audio Caption")
        self.assertEqual(audio.caption, "Audio Caption")

    def test_set_audio_transcript(self):
        audio = AudioObject()
        audio.set_transcript("Audio Transcript")
        self.assertEqual(audio.transcript, "Audio Transcript")

    def test_set_video_contentUrl(self):
        video = VideoObject()
        video.set_contentUrl("http://example.com/video.mp4")
        self.assertEqual(video.contentUrl, "http://example.com/video.mp4")

    def test_set_video_duration(self):
        video = VideoObject()
        video.set_duration("PT5M")
        self.assertEqual(video.duration, "PT5M")

    def test_set_video_videoQuality(self):
        video = VideoObject()
        video.set_videoQuality("HD")
        self.assertEqual(video.videoQuality, "HD")

    def test_set_video_caption(self):
        video = VideoObject()
        video.set_caption("Video Caption")
        self.assertEqual(video.caption, "Video Caption")

    def test_set_video_director(self):
        video = VideoObject()
        video.set_director("Director Name")
        self.assertEqual(video.director, "Director Name")

    def test_set_video_transcript(self):
        video = VideoObject()
        video.set_transcript("Video Transcript")
        self.assertEqual(video.transcript, "Video Transcript")

    def test_set_image_contentUrl(self):
        image = ImageObject()
        image.set_contentUrl("http://example.com/image.jpg")
        self.assertEqual(image.contentUrl, "http://example.com/image.jpg")

    def test_set_image_height(self):
        image = ImageObject()
        image.set_height(600)
        self.assertEqual(image.height, 600)

    def test_set_image_width(self):
        image = ImageObject()
        image.set_width(800)
        self.assertEqual(image.width, 800)

    def test_set_image_caption(self):
        image = ImageObject()
        image.set_caption("Image Caption")
        self.assertEqual(image.caption, "Image Caption")

    def test_set_image_embeddedTextCaption(self):
        image = ImageObject()
        image.set_embeddedTextCaption("Embedded Text")
        self.assertEqual(image.embeddedTextCaption, "Embedded Text")

    def test_set_image_embedUrl(self):
        media = ImageObject()
        media.set_embedUrl("http://example.com/embed")
        self.assertEqual(media.embedUrl, "http://example.com/embed")

    def test_set_image_uploadDate(self):
        media = ImageObject()
        media.set_uploadDate("2023-01-01")
        self.assertEqual(media.uploadDate, "2023-01-01")

    def test_set_video_videoFrameSize(self):
        video = VideoObject()
        video.set_videoFrameSize("1280x720")
        self.assertEqual(video.videoFrameSize, "1280x720")

if __name__ == '__main__':
    unittest.main()