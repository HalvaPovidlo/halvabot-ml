import json
import logging

from fastapi import FastAPI, Request
import uvicorn
from fastapi.openapi.utils import get_openapi

from autocomplete import Autocomplete
import db

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


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Halvabot ML server",
        version="1.0.0",
        description="Halvabot website functions that require python",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=9092)

