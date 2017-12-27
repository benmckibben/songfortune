import random

from . import data_utils


# -- private

def _get_track_artist(track):
    return track['artist_name']

def _get_random_lyric(lyrics):
    lyrics_split = lyrics.split('\n')[:-1]  # splice out copyright notice
    return random.choice(lyrics_split).strip()

# -- public

def main():
    data = data_utils.get_data()
    # keep choosing random song lyrics until the lyric is sufficiently long
    lyric = None
    while True:
        # get a random track and it's lyrics
        datum = random.choice(data)
        track = datum['track']
        lyrics = datum['lyrics']

        lyric = _get_random_lyric(lyrics)
        if len(lyric.split(' ')) > 2:
            break

    artist = _get_track_artist(track)
    return u'{} - {}'.format(lyric, artist)

if __name__ == '__main__':
    print(main())
