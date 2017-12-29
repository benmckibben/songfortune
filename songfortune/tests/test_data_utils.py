import pickle
from datetime import datetime
from datetime import timedelta
from unittest import mock
from unittest import TestCase

import songfortune
from songfortune.data_utils import CACHE_KEY
from songfortune.data_utils import LAST_UPDATED_KEY
from songfortune.data_utils import _get_data_from_db
from songfortune.data_utils import _get_data_from_musixmatch
from songfortune.data_utils import _store_data_in_db
from songfortune.data_utils import get_data


class BaseDataUtilsTestCase(TestCase):
    def setUp(self):
        self.mock_redis_client = mock.Mock()
        songfortune.data_utils.redis_client = self.mock_redis_client

        self.mock_musixmatch = mock.Mock()
        songfortune.data_utils.musixmatch = self.mock_musixmatch

        self.mock_datetime = mock.Mock()
        songfortune.data_utils.datetime = self.mock_datetime
        self.test_now = datetime.now()
        self.mock_datetime.now.return_value = self.test_now


class TestGetDataFromDb(BaseDataUtilsTestCase):
    def test_no_last_updated(self):
        self.mock_redis_client.get.return_value = None
        self.assertEqual(_get_data_from_db(), None)
        self.mock_redis_client.get.assert_called_once_with(LAST_UPDATED_KEY)

    def test_no_cache(self):
        self.mock_redis_client.get.side_effect = [
            pickle.dumps(self.test_now),
            None,
        ]
        self.assertEqual(_get_data_from_db(), None)
        self.mock_redis_client.get.assert_has_calls([
            mock.call(LAST_UPDATED_KEY),
            mock.call(CACHE_KEY),
        ])

    def test_nonempty_current_cache(self):
        sample_data = ['This', 'is', 'a', 6, 'length', 'list']
        self.mock_redis_client.get.side_effect = [
            pickle.dumps(self.test_now),
            pickle.dumps(sample_data),
        ]
        self.assertEqual(_get_data_from_db(), sample_data)
        self.mock_redis_client.get.assert_has_calls([
            mock.call(LAST_UPDATED_KEY),
            mock.call(CACHE_KEY),
        ])

    def test_outdated_cache(self):
        two_days_ago = self.test_now - timedelta(days=2)
        sample_data = ['This', 'is', 'a', 6, 'length', 'list']
        self.mock_redis_client.get.side_effect = [
            pickle.dumps(two_days_ago),
            pickle.dumps(sample_data),
        ]
        self.assertEqual(_get_data_from_db(), None)
        self.mock_redis_client.get.assert_called_once_with(LAST_UPDATED_KEY)


class TestStoreDataInDb(BaseDataUtilsTestCase):
    def test_empty_cache(self):
        pickled_sample = pickle.dumps(None)
        _store_data_in_db(None)
        self.mock_redis_client.set.assert_has_calls([
            mock.call(CACHE_KEY, pickled_sample),
            mock.call(LAST_UPDATED_KEY, pickle.dumps(self.test_now)),
        ])

    def test_non_empty_cache(self):
        sample_data = ['This', 'is', {'some': 'sample'}, 'data', {4: 'u'}]
        pickled_sample = pickle.dumps(sample_data)
        _store_data_in_db(sample_data)
        self.mock_redis_client.set.assert_has_calls([
            mock.call(CACHE_KEY, pickled_sample),
            mock.call(LAST_UPDATED_KEY, pickle.dumps(self.test_now)),
        ])


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


class TestGetData(BaseDataUtilsTestCase):
    def test_cache_after_musixmatch_fetch(self):
        self.mock_redis_client.get.return_value = None
        self.mock_musixmatch.get_chart.return_value = []
        self.assertEqual(get_data(), [])
        self.mock_redis_client.set.assert_has_calls([
            mock.call(CACHE_KEY, pickle.dumps([])),
            mock.call(LAST_UPDATED_KEY, pickle.dumps(self.test_now)),
        ])
