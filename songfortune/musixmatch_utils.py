import os

import requests


API_PREFIX = 'https://api.musixmatch.com/ws/1.1'
API_KEY = os.environ.get('MUSIXMATCH_API_KEY', 'null')

CHART_ENDPOINT = '/chart.tracks.get'
LYRICS_ENDPOINT = '/track.lyrics.get'
TRACK_ENDPOINT = '/track.get'

# -- private

def _make_chart_payload():
    return {
        'format': 'json',
        'country': 'us',
        'page_size': 40,
        'f_has_lyrics': True,
        'apikey': API_KEY
    }

def _make_lyrics_payload(track_id):
    return {
        'format': 'json',
        'apikey': API_KEY,
        'track_id': track_id
    }

def _make_track_payload(track_id):
    return {
        'format': 'json',
        'apikey': API_KEY,
        'track_id': track_id
    }

def _api_call(endpoint, payload):
    return requests.get(
        API_PREFIX + endpoint,
        params=payload
    ).json()

def _get_track_id(track):
    return track['track_id']

def _get_track_lyrics_by_id(track_id):
    response = _api_call(
        LYRICS_ENDPOINT,
        _make_lyrics_payload(track_id)
    )
    return response['message']['body']['lyrics']['lyrics_body']

# -- public

def get_track(track_id):
    response = _api_call(
        TRACK_ENDPOINT,
        _make_track_payload(track_id)
    )
    return response['message']['body']['track']

def get_chart():
    response = _api_call(
        CHART_ENDPOINT,
        _make_chart_payload()
    )
    chart = response['message']['body']['track_list']
    return [x['track'] for x in chart]

def get_track_lyrics(track):
    track_id = _get_track_id(track)
    return _get_track_lyrics_by_id(track_id)
