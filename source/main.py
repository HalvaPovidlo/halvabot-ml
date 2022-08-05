import json
import logging
import time

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn

from autocomplete import Autocomplete

logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pool = {}


@app.on_event("startup")
async def initialize_pool():
    logger.info("initialize pool")
    autocomplete = Autocomplete()
    pool['autocomplete'] = autocomplete


@app.get("/alive")
async def check_health():
    return {'alive': True}


@app.post("/api/v1/complete/song")
async def process_autocomplete(request: Request):
    body_bytes = await request.body()
    try:
        query = json.loads(body_bytes)['query']
    except Exception:
        raise HTTPException(status_code=400, detail="Wrong format")
    top_queries = pool['autocomplete'].calculate_levenshtein(query)
    return {'items': top_queries}


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
