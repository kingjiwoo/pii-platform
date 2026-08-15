"""Chat request/response types normalized from OpenAI-format bodies."""
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class Message:
    role: Literal["system", "user", "assistant", "tool"]
    content: str


@dataclass
class ChatRequest:
    model: str
    messages: list[Message]
    # Preserve original body so extra params (temperature, max_tokens, tools, ...) survive forwarding.
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_openai_body(cls, body: dict[str, Any]) -> "ChatRequest":
        messages = [
            Message(role=m["role"], content=m.get("content", "") or "")
            for m in body.get("messages", [])
        ]
        return cls(model=body.get("model", ""), messages=messages, raw=body)

    @property
    def text(self) -> str:
        """Concatenated user-visible text; input to PII detection."""
        return "\n".join(m.content for m in self.messages if m.content)

    def to_openai_body(self) -> dict[str, Any]:
        body = dict(self.raw)
        body["model"] = self.model
        body["messages"] = [{"role": m.role, "content": m.content} for m in self.messages]
        return body


@dataclass
class ChatResponse:
    """Wraps the LiteLLM response body; kept as a type for future extension (streaming, metrics)."""
    body: dict[str, Any]

    def to_openai_body(self) -> dict[str, Any]:
        return self.body
