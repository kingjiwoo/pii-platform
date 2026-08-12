"""FastAPI entrypoint.

Layered architecture:
- models/    typed data (ChatRequest, RequestContext)
- pii/       PII detection domain (Detector protocol + RegexDetector)
- masking/   masking domain (Masker protocol + TemplateMasker)
- routing/   model routing decision (Router protocol + RuleBasedRouter)
- clients/   external service adapters (LiteLLMClient)
- handlers/  request processing strategies (Handler protocol)
              - PipelineHandler: current PII → mask → route → forward
              - AgentHandler:    future (LangGraph)

main.py wires defaults; env vars override.
"""
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request

from .clients.litellm import LiteLLMClient
from .handlers.base import Handler
from .handlers.pipeline import PipelineHandler
from .masking.masker import TemplateMasker
from .models.chat import ChatRequest
from .models.context import RequestContext
from .pii.detector import RegexDetector
from .routing.router import RuleBasedRouter

LITELLM_URL = os.environ.get(
    "LITELLM_URL",
    "http://gateway-litellm.pii.svc.cluster.local:4000",
)
LITELLM_MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY", "sk-1234")
REQUEST_TIMEOUT = float(os.environ.get("LITELLM_TIMEOUT_SECONDS", "30"))

PII_MODEL = os.environ.get("PII_MODEL", "vllm-qwen")
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "gpt-4o-mini")


def build_default_handler(client: LiteLLMClient) -> Handler:
    return PipelineHandler(
        detector=RegexDetector(),
        masker=TemplateMasker(),
        router=RuleBasedRouter(pii_model=PII_MODEL, default_model=DEFAULT_MODEL),
        client=client,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = LiteLLMClient(LITELLM_URL, LITELLM_MASTER_KEY, timeout=REQUEST_TIMEOUT)
    app.state.client = client
    app.state.handler = build_default_handler(client)
    yield
    await client.aclose()


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
    chat_req = ChatRequest.from_openai_body(body)
    context = RequestContext.from_headers(request.headers)

    try:
        response = await request.app.state.handler.handle(chat_req, context)
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"LiteLLM unreachable: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    return response.to_openai_body()
