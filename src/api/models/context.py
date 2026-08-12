"""Per-request context passed through the handler pipeline.

Future extensions: available tools, budget limits, tenant_id.
"""
from dataclasses import dataclass


@dataclass
class RequestContext:
    session_id: str | None = None
    user_id: str | None = None

    @classmethod
    def from_headers(cls, headers) -> "RequestContext":
        return cls(
            session_id=headers.get("x-session-id"),
            user_id=headers.get("x-user-id"),
        )
