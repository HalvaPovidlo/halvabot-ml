import json
import logging

from fastapi import FastAPI, Request
import uvicorn

from source.autocomplete import Autocomplete
import source.db as db

logger = logging.getLogger(__name__)

app = FastAPI()

pool = {}


@app.on_event("startup")
async def initialize_pool():
    logger.info("Initialize pool")
    song_titles = db.get_song_titles()
    autocomplete = Autocomplete(song_titles)
    pool['autocomplete'] = autocomplete


@app.get("/alive")
async def check_health():
    return {'alive': True}


@app.get("/api/autocomplete")
async def process_autocomplete(request: Request):
    body_bytes = await request.body()
    try:
        query = dict(request.headers)['query']
    except Exception:
        return {'error': 'Wrong format'}
    top_queries = pool['autocomplete'].calculate_levenshtein(query)
    return {'queries': top_queries}


if __name__ == '__main__':
    uvicorn.run(app,
                port=9092)
