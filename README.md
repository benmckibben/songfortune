# songfortune [![Build Status](https://travis-ci.org/benmckibben/songfortune.svg?branch=master)](https://travis-ci.org/benmckibben/songfortune)

For the uninformed, the description is a reference to [Hitler quotes existing in FreeBSD's fortune implementation](https://github.com/freebsd/freebsd/commit/0271df5714d9ce5274f82889febb6536a2fdba59).

Here is a demo of songfortune in action in a terminal:
[![asciicast](https://asciinema.org/a/Bdm5vyl1WWN1l2Ky7nwbQag2g.png)](https://asciinema.org/a/Bdm5vyl1WWN1l2Ky7nwbQag2g)

## Overview
songfortune is a little script meant to mimic the basic functionality of [fortune](https://linux.die.net/man/6/fortune), but with song lyrics from currently popular songs instead of "random, hopefully interesting, adage[s]". This repository is for songfortune's server, which will serve these lyrics from its cache. The cache, which is stored in a Redis instance, is populated from data from [Musixmatch](https://www.musixmatch.com/), which provides both charts of current pop songs and the songs' lyrics. The songfortune server will also refresh this cache and pull fresh data from Musixmatch after the cache has become older than a day.

Full disclosure: publishing this project was more of a way for me to get practice with [Docker](https://www.docker.com) and [Travis CI](https://travis-ci.org/). That said, feel free to contribute by making pull requests or raising issues!

## Installation
### Environment variables
songfortune expects the following environment variables to be set, regardless of how you choose to deploy:
- `REDIS_URL`: a URL to the Redis instance you choose to use as the datastore. This URL should include host, username, and password information. Examples:
  - `redis://<username>:<password>@<host>:<port>/`
  - `redis://<host>:<port>/`, when username and password are irrelevant.
- `MUSIXMATCH_API_KEY`: an API key for Musixmatch. See [here](https://developer.musixmatch.com/documentation) for more information.

### Manual(ish) installation
The server runs on **Python 3.3+**; anything else is not supported. This is because the HTTP API and CLI runs on [hug](http://www.hug.rest/), which only supports Python 3, and the tests use [`unittest.mock`](https://docs.python.org/3/library/unittest.mock.html), which is only built-in to Python 3.3+.

After installing Python 3.3+, preferably in a [virtualenv](https://virtualenv.pypa.io/en/stable/), install the dependencies:
```bash
pip install -r requirements.txt
```

Set the environment variables however you would like. For example:
```bash
export REDIS_URL=redis://<username>:<password>@<host>:<port>/
export MUSIXMATCH_API_KEY=XXXXXXXXXXXXXXXX
```

Run tests:
```bash
pytest
```

Run the HTTP server either with hug's development server:
```bash
hug -f api.py
```
or with [gunicorn](http://gunicorn.org/):
```bash
gunicorn api:__hug_wsgi__
```

### Docker
Docker builds automatically execute and are pushed to `benmckibben/songfortune:latest` with each push to master here. However, this Docker image does not run the server automatically. You will need to both export the environment variables and run the server however you choose to deploy the image as defined in this repository's `Dockerfile`. Here is an example of deploying both songfortune and the Redis instance using [Docker Compose](https://docs.docker.com/compose/):
```yaml
version: "3"
services:
  redis:
    image: redis
    restart: always
    volumes:
      - /docker/redis:/data
    deploy:
      placement:
        constraints: [node.role == manager]
    command: redis-server --appendonly yes
    networks:
      - backend
  songfortune:
    image: benmckibben/songfortune:latest
    depends_on:
      - redis
    restart: always
    environment:
      - REDIS_URL=redis://redis/
      - MUSIXMATCH_API_KEY=XXXXXXXXXXXXX
    command: gunicorn api:__hug_wsgi__ -b 0.0.0.0:8000
    ports:
      - "8000:8000"
    networks:
      - frontend
      - backend
networks:
  frontend:
  backend:
```
I also manually maintain a build for ARMv7 at `benmckibben/songfortune:latest-arm`.

## Usage
### CLI
Using hug, a CLI is provided with the following commands:
- `songfortune`: prints out a songfortune. This is wrapped in the file `main`.
- `last_updated`: show when the cache was last updated.
- `refresh`: force a refresh of the cache. This is wrapped in the file `refresh`.

Examples:
```bash
songfortune$ hug -f api.py -c songfortune
Got me feelin' some kind of way - Luis Fonsi feat. Daddy Yankee & Justin Bieber
songfortune$ hug -f api.py -c last_updated
{'last_updated': datetime.datetime(2017, 12, 30, 0, 5, 5, 595681)}
songfortune$ hug -f api.py -c refresh
Cache refresh succeeded.
```

### HTTP API
Running the server with either hug's development server or gunicorn, as described above, makes two routes available:
- `GET /`: return a JSON object with a new songfortune.
  ```bash
  songfortune$ curl localhost:8000
  {"message": "Not too many people, save her daddy some money - Thomas Rhett"}
  ```
- `GET /last_updated`: return a JSON object describing when the cache was last updated.
  ```bash
  songfortune$ curl localhost:8000/last_updated
  {"last_updated": "2017-12-30T00:42:51.053140"}
  ```
  
## What now?
I will probably look into adding more functionality to this, starting with returning more song data with a songfortune instead of just the randomly chosen lyric. Additional options / arguments like fortune's might be fun to implement as well. I'll possibly also end up writing a command line tool that just requests a songfortune from either the "default" songfortune server I (will) maintain or a server of the user's choice (specified via environment variable). Again, if you would like to contribute, let me know with a pull request or an issue!

thxxx

![bridge across some water](https://i.imgur.com/73A7gym.png)
