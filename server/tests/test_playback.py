import os
import unittest

from jwt import InvalidTokenError

from src.services.playback import PlaybackTokenService


class PlaybackTokenTests(unittest.TestCase):
  def setUp(self):
    self.previous_secret = os.environ.get('PLAYBACK_SECRET')
    os.environ['PLAYBACK_SECRET'] = 'test-playback-secret-with-32-characters'

  def tearDown(self):
    if self.previous_secret is None:
      os.environ.pop('PLAYBACK_SECRET', None)
    else:
      os.environ['PLAYBACK_SECRET'] = self.previous_secret

  def test_issues_and_verifies_token(self):
    token = PlaybackTokenService.issue('session1', 'dQw4w9WgXcQ')

    payload = PlaybackTokenService.verify(token, 'dQw4w9WgXcQ')

    self.assertEqual(payload['sub'], 'session1')
    self.assertEqual(payload['vid'], 'dQw4w9WgXcQ')

  def test_rejects_token_for_another_video(self):
    token = PlaybackTokenService.issue('session1', 'dQw4w9WgXcQ')

    with self.assertRaises(InvalidTokenError):
      PlaybackTokenService.verify(token, 'abcdefghijk')


if __name__ == '__main__':
  unittest.main()
