import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from songfortune.songfortune import _get_random_lyric
from songfortune.songfortune import _get_track_artist
from songfortune.songfortune import main


class TestGetTrackArtist(unittest.TestCase):
    def test_single_track(self):
        sample_track = {
            'artist_name': 'Kesha',
        }
        self.assertEqual(
            _get_track_artist(sample_track),
            'Kesha',
        )

    def test_no_tracks(self):
        with self.assertRaises(KeyError):
            _get_track_artist({})
    

class TestGetRandomLyric(unittest.TestCase):
    def test_get_lyric(self):
        lyrics = '''This is a made up lyric.
        ******* This Lyrics is NOT for Commercial use *******'''
        expected_result = 'This is a made up lyric.'
        self.assertEqual(
            _get_random_lyric(lyrics),
            expected_result,
        )

    def test_get_single_lyric(self):
        lyrics = 'I am but a single lyric'
        self.assertEqual(_get_random_lyric(lyrics), lyrics)

    def test_only_pesky_notice(self):
        lyrics = '****** This Lyrics is NOT for Commercial use *******'
        with self.assertRaises(IndexError):
            _get_random_lyric(lyrics)


class TestMain(unittest.TestCase):
    @mock.patch('songfortune.data_utils.get_data')
    def test_main(self, mock_get_data):
        sample_data = [
            {
                'track': {
                    'title': 'Say It Ain\'t So',
                    'artist_name': 'Weezer',
                },
                'lyrics': '''Dear daddy,
                I write you
                ****** This Lyrics is NOT for Commercial use *******''',
            },
        ]
        mock_get_data.return_value = sample_data
        
        expected_result = u'I write you - Weezer'
        self.assertEqual(main(), expected_result)
