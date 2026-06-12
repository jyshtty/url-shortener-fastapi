from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import RedirectResponse

import random
import string

app = FastAPI()

# constants
BASE_URL = "www.xyz.com"


# pydantic
class InputRequest(BaseModel):
    long_url: str


class KeyMap(BaseModel):
    long_url: str
    visits: int


# store
long_url_store: dict[str, str] = {}
key_store: dict[str, KeyMap] = {}


# helpers
def generate_key() -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choices(alphabet, k=5))


@app.post("/shorten", status_code=201)
def create_shorten_url(request: InputRequest):
    long_url = request.long_url
    if not long_url.startswith(("http://", "https://")):
        long_url = "https://" + long_url

    if long_url in long_url_store:
        return {"short_url": BASE_URL + '/' +  long_url_store[long_url]}

    for _ in range(10):
        key = generate_key()
        if key not in key_store:
            break
    else:
        raise HTTPException(status_code=500, detail="Not able to generate key")

    long_url_store[long_url] = key
    key_store[key] = KeyMap(long_url=long_url, visits=0)

    return {"short_url": BASE_URL + '/' + key}


@app.get("/url/{key}")
def get_original_url(key: str):
    data = key_store.get(key)
    if not data:
        raise HTTPException(status_code=404, detail="key not found")
    return {"long_url": data.long_url}


@app.get("/count/{key}")
def get_visits(key: str):
    data = key_store.get(key)
    if not data:
        raise HTTPException(status_code=404, detail="key not found")
    return {"count": data.visits}


@app.get("/{key}")
def redirection(key: str):
    data = key_store.get(key)
    if not data:
        raise HTTPException(status_code=404, detail="key not found")
    data.visits += 1
    return RedirectResponse(url=data.long_url, status_code=307)
