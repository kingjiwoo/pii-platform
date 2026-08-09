"""FastAPI stub for hybrid LLM gateway (PR 1 / T1.13).

Day 1 scope: transparent forwarder to LiteLLM.
PII detection / routing decision arrives in PR 3.
"""
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request

LITELLM_URL = os.environ.get(
    "LITELLM_URL",
    "http://gateway-litellm.pii.svc.cluster.local:4000",
)
LITELLM_MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY", "sk-1234")
REQUEST_TIMEOUT = float(os.environ.get("LITELLM_TIMEOUT_SECONDS", "30"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)
    yield
    await app.state.http.aclose()


app = FastAPI(title="PII Gateway", lifespan=lifespan)


@app.get("/health/liveliness")
async def liveliness():
    return {"status": "ok"}


@app.get("/health/readiness")
async def readiness():
    return {"status": "ok"}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    try:
        resp = await request.app.state.http.post(
            f"{LITELLM_URL}/v1/chat/completions",
            json=body,
            headers={
                "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                "Content-Type": "application/json",
            },
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"LiteLLM unreachable: {e}")
    return resp.json()
