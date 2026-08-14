"""Default handler: PII detection → masking → model routing → LiteLLM forward."""
from ..clients.litellm import LiteLLMClient
from ..masking.masker import Masker
from ..models.chat import ChatRequest, ChatResponse, Message
from ..models.context import RequestContext
from ..observability.metrics import pii_detections_total, routing_decisions_total
from ..pii.detector import Detector
from ..routing.router import Router


class PipelineHandler:
    def __init__(
        self,
        detector: Detector,
        masker: Masker,
        router: Router,
        client: LiteLLMClient,
    ):
        self.detector = detector
        self.masker = masker
        self.router = router
        self.client = client

    async def handle(
        self,
        request: ChatRequest,
        context: RequestContext,
    ) -> ChatResponse:
        # Scan concatenated text so routing sees any PII in any message.
        overall_matches = self.detector.detect(request.text)

        for m in overall_matches:
            pii_detections_total.labels(pii_type=m.type.value).inc()

        # Mask each message independently (offsets are per-message).
        if overall_matches:
            request.messages = [
                Message(
                    role=m.role,
                    content=self.masker.mask(m.content, self.detector.detect(m.content)),
                )
                for m in request.messages
            ]

        request.model = self.router.route(overall_matches)
        routing_decisions_total.labels(
            target_model=request.model,
            pii_detected="true" if overall_matches else "false",
        ).inc()

        result = await self.client.chat_completions(request.to_openai_body())
        return ChatResponse(body=result)
