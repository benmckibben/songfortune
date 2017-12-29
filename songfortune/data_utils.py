import pickle
import os
from datetime import datetime
from datetime import timedelta

from redis import StrictRedis

from . import musixmatch_utils as musixmatch


redis_client = StrictRedis.from_url(os.environ.get('REDIS_URL', 'redis://localhost'))
CACHE_KEY = 'songfortune:cache'
LAST_UPDATED_KEY = 'songfortune:lastupdated'

# -- private

def _get_data_from_db():
    # Check when the cache was last updated.
    last_updated = redis_client.get(LAST_UPDATED_KEY)
    last_updated = pickle.loads(last_updated) if last_updated else None

    # Force a cache refresh if there is no last updated time or if the cache is
    # older than a day.
    if last_updated is None or datetime.now() - last_updated > timedelta(days=1):
        return None

    cache = redis_client.get(CACHE_KEY)

    if cache is None:
        return None

    return pickle.loads(cache)

def _store_data_in_db(cache):
    pickled_cache = pickle.dumps(cache)
    redis_client.set(CACHE_KEY, pickled_cache)

    pickled_now = pickle.dumps(datetime.now())
    redis_client.set(LAST_UPDATED_KEY, pickled_now)

def _get_data_from_musixmatch():
    # get the track data from musixmatch
    chart = musixmatch.get_chart()
    
    # build the data structure
    data = []
    for track in chart:
        lyrics = musixmatch.get_track_lyrics(track)
        data.append({
            'track': track,
            'lyrics': lyrics,
        })

    return data

# -- public

def get_data():
    data = _get_data_from_db()
    if not data:
        data = _get_data_from_musixmatch()
        _store_data_in_db(data)
    
    return data

def refresh_cache():
    data = _get_data_from_musixmatch()
    _store_data_in_db(data)
