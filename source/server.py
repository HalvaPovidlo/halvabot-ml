import json
import logging

from fastapi import FastAPI, Request
import uvicorn

from source.autocomplete import Autocomplete

logger = logging.getLogger(__name__)

app = FastAPI()

pool = {}


@app.on_event("startup")
async def initialize_pool():
    logger.info("Initialize pool")
    all_text_from_db = []
    autocomplete = Autocomplete(all_text_from_db)
    pool['autocomplete'] = autocomplete


@app.get("/alive")
async def check_health():
    return {'alive': True}


@app.get("api/autocomplete")
async def process_autocomplete(request: Request):
    body_bytes = await request.body()
    body = json.loads(body_bytes)
    try:
        query = body['query']
    except Exception:
        return {'error': 'Wrong format'}
    top_queries = pool['autocomplete'].calculate_levenshtein(query)
    return {'queries': top_queries}


if __name__ == '__main__':
    uvicorn.run(app,
                port=9092)
