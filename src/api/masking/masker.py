"""Masking protocol and template-based implementation."""
from typing import Protocol

from ..pii.models import PIIMatch, PIIType


class Masker(Protocol):
    def mask(self, text: str, matches: list[PIIMatch]) -> str: ...


class TemplateMasker:
    _TEMPLATES: dict[PIIType, str] = {
        PIIType.KOREAN_RRN: "[REDACTED_RRN]",
        PIIType.ACCOUNT: "[REDACTED_ACCOUNT]",
        PIIType.CARD: "[REDACTED_CARD]",
        PIIType.PHONE: "[REDACTED_PHONE]",
    }

    # Tie-breaker when overlapping matches have equal length.
    # More specific types win: RRN > CARD > PHONE > ACCOUNT (loosest).
    _PRIORITY: dict[PIIType, int] = {
        PIIType.KOREAN_RRN: 4,
        PIIType.CARD: 3,
        PIIType.PHONE: 2,
        PIIType.ACCOUNT: 1,
    }

    def mask(self, text: str, matches: list[PIIMatch]) -> str:
        # Resolve overlaps: prefer longer matches, then more specific type.
        ranked = sorted(
            matches,
            key=lambda m: (m.end - m.start, self._PRIORITY.get(m.type, 0)),
            reverse=True,
        )
        selected: list[PIIMatch] = []
        for m in ranked:
            if not any(m.start < s.end and m.end > s.start for s in selected):
                selected.append(m)

        # Apply masks from tail to head so earlier offsets stay valid.
        for m in sorted(selected, key=lambda x: -x.start):
            template = self._TEMPLATES.get(m.type, "[REDACTED]")
            text = text[: m.start] + template + text[m.end :]
        return text
