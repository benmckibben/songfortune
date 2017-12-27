import cPickle as pickle
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

import songfortune
from songfortune.data_utils import _get_data_from_db
from songfortune.data_utils import _get_data_from_musixmatch
from songfortune.data_utils import _store_data_in_db
from songfortune.data_utils import CACHE_KEY


class BaseDataUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_redis_client = mock.Mock()
        songfortune.data_utils.redis_client = self.mock_redis_client

        self.mock_musixmatch = mock.Mock()
        songfortune.data_utils.musixmatch = self.mock_musixmatch


class TestGetDataFromDb(BaseDataUtilsTestCase):
    def test_get_no_data(self):
        self.mock_redis_client.get.return_value = None
        self.assertEqual(_get_data_from_db(), None)
        self.mock_redis_client.get.assert_called_once_with(CACHE_KEY)

    def test_get_some_data(self):
        sample_data = ['This', 'is', 'a', 6, 'length', 'list']
        pickled_sample = pickle.dumps(sample_data)
        self.mock_redis_client.get.return_value = pickled_sample
        self.assertEqual(_get_data_from_db(), sample_data)
        self.mock_redis_client.get.assert_called_once_with(CACHE_KEY)


class TestStoreDataInDb(BaseDataUtilsTestCase):
    def test_empty_cache(self):
        pickled_sample = pickle.dumps(None)
        _store_data_in_db(None)
        self.mock_redis_client.set.assert_called_once_with(
            CACHE_KEY,
            pickled_sample,
        )

    def test_non_empty_cache(self):
        sample_data = ['This', 'is', {'some': 'sample'}, 'data', {4: 'u'}]
        pickled_sample = pickle.dumps(sample_data)
        _store_data_in_db(sample_data)
        self.mock_redis_client.set.assert_called_once_with(
            CACHE_KEY,
            pickled_sample,
        )


class TestGetDataFromMusixmatch(BaseDataUtilsTestCase):
    def test_empty_chart(self):
        self.mock_musixmatch.get_chart.return_value = []
        self.assertEqual(_get_data_from_musixmatch(), [])

    def test_non_empty_chart(self):
        sample_chart = [
            'Song A',
            'Song B',
        ]
        expected_result = [
            {
                'track': 'Song A',
                'lyrics': 'A',
            },
            {
                'track': 'Song B',
                'lyrics': 'B',
            },
        ]
        self.mock_musixmatch.get_chart.return_value = sample_chart
        self.mock_musixmatch.get_track_lyrics.side_effect = ['A', 'B']
        self.assertEqual(_get_data_from_musixmatch(), expected_result)
