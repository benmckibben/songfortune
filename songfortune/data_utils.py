import cPickle as pickle
import os

from redis import StrictRedis

from . import musixmatch_utils as musixmatch


redis_client = StrictRedis.from_url(os.environ.get('REDIS_URL', 'redis://localhost'))
CACHE_KEY = 'songfortune:cache'

# -- private

def _get_data_from_db():
    cache = redis_client.get(CACHE_KEY)

    if cache == None:
        return None
    
    return pickle.loads(cache)

def _store_data_in_db(cache):
    pickled_cache = pickle.dumps(cache)
    redis_client.set(CACHE_KEY, pickled_cache)

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
    
    return data

def refresh_cache():
    data = _get_data_from_musixmatch()
    _store_data_in_db(data)
