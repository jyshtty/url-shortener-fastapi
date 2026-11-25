# URL Shortener FastAPI

A small URL shortener built with FastAPI. Send it a long URL and it returns a 5-character key. Opening that key redirects to the original URL, and the service counts each redirect.

Everything lives in one file, [`url_shortener.py`](url_shortener.py). Data is held in memory, so it is lost when the server stops.

## Requirements

- Python 3.13 or newer
- FastAPI with the standard extras, which include Uvicorn

## Getting started

```bash
# create and activate a virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# install dependencies
pip install "fastapi[standard]"

# start the dev server with auto-reload
fastapi dev url_shortener.py
```

The API is now at <http://127.0.0.1:8000>. FastAPI also serves interactive docs at <http://127.0.0.1:8000/docs>.

> `pyproject.toml` doesn't list dependencies yet, so install them with the `pip` command above.

## API

| Method | Path            | Description                                    | Success             |
| ------ | --------------- | ---------------------------------------------- | ------------------- |
| POST   | `/shorten`      | Create a short key for a URL                   | `201 Created`       |
| GET    | `/url/{key}`    | Look up the original URL without redirecting   | `200 OK`            |
| GET    | `/count/{key}`  | Get how many times a key has been followed     | `200 OK`            |
| GET    | `/{key}`        | Redirect to the original URL and count a visit | `307 Temporary Redirect` |

An unknown key returns `404` with `{"detail": "key not found"}`.

### Shorten a URL

```bash
curl -X POST http://127.0.0.1:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"long_url": "example.com/docs"}'
```

```json
{"short_url": "www.xyz.com/BQgVc"}
```

- If the URL has no `http://` or `https://` prefix, `https://` is added.
- Shortening the same URL again returns the same key.
- Keys are random letters and digits. If 10 attempts in a row all collide with existing keys, the API returns `500`.

### Look up the original URL

```bash
curl http://127.0.0.1:8000/url/BQgVc
```

```json
{"long_url": "https://example.com/docs"}
```

### Follow a short link

```bash
curl -i http://127.0.0.1:8000/BQgVc
```

```
HTTP/1.1 307 Temporary Redirect
location: https://example.com/docs
```

Add `-L` to have curl follow the redirect. Opening the key in a browser also works.

### Get the visit count

```bash
curl http://127.0.0.1:8000/count/BQgVc
```

```json
{"count": 1}
```

Only requests to `/{key}` increase the count. Calls to `/url/{key}` and `/count/{key}` don't.

## Configuration

`BASE_URL` in `url_shortener.py` is the prefix added to the `short_url` in the `/shorten` response. It is a placeholder (`www.xyz.com`) with no scheme, so the returned link won't work locally. Use only the key, for example `http://127.0.0.1:8000/BQgVc`. Change `BASE_URL` to your own domain when you deploy.

## Limitations

- **No persistence.** Both stores are plain dicts, so restarting the server clears all links.
- **Single process only.** Memory isn't shared between workers, so run one worker.
- **No URL validation.** Any string is accepted and given an `https://` prefix if it lacks a scheme.
- **No collision with built-in routes.** `/{key}` is registered last, so `/docs`, `/shorten` and the others take priority. Generated keys are 5 characters, so they never clash with these paths.

## Project layout

```
.
├── url_shortener.py   # the FastAPI app: models, in-memory stores, routes
├── pyproject.toml     # project metadata
└── README.md
```
