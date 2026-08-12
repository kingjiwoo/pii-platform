"""Handler protocol: strategy for processing a chat request.

Current implementation: PipelineHandler (PII → mask → route → forward).
Future: AgentHandler (LangGraph orchestration with tool use).
"""
from typing import Protocol

from ..models.chat import ChatRequest, ChatResponse
from ..models.context import RequestContext


class Handler(Protocol):
    async def handle(
        self,
        request: ChatRequest,
        context: RequestContext,
    ) -> ChatResponse: ...
