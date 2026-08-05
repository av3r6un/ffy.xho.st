import unittest

from src.services.ytdl import Youtube


class ExtractVideoIdTests(unittest.TestCase):
  VIDEO_ID = 'dQw4w9WgXcQ'

  def test_extracts_watch_url(self):
    self.assertEqual(
      Youtube.extract_id_from_url(
        f'https://www.youtube.com/watch?v={self.VIDEO_ID}&feature=share',
      ),
      self.VIDEO_ID,
    )

  def test_extracts_short_url(self):
    self.assertEqual(
      Youtube.extract_id_from_url(f'https://youtu.be/{self.VIDEO_ID}?si=test'),
      self.VIDEO_ID,
    )

  def test_extracts_path_urls(self):
    for path in ('shorts', 'live', 'embed'):
      with self.subTest(path=path):
        self.assertEqual(
          Youtube.extract_id_from_url(
            f'https://youtube.com/{path}/{self.VIDEO_ID}',
          ),
          self.VIDEO_ID,
        )

  def test_accepts_url_without_scheme(self):
    self.assertEqual(
      Youtube.extract_id_from_url(
        f'm.youtube.com/watch?v={self.VIDEO_ID}',
      ),
      self.VIDEO_ID,
    )

  def test_rejects_invalid_urls(self):
    for value in (None, '', 'https://example.com/watch?v=dQw4w9WgXcQ', 'bad'):
      with self.subTest(value=value):
        self.assertIsNone(Youtube.extract_id_from_url(value))


if __name__ == '__main__':
  unittest.main()
