"""PII detector protocol and regex-based implementation.

Alternative implementations (Presidio, LLM-based) can drop in behind the Detector protocol.
"""
from typing import Protocol

from .models import PIIMatch
from .patterns import PATTERNS


class Detector(Protocol):
    def detect(self, text: str) -> list[PIIMatch]: ...


class RegexDetector:
    def __init__(self, patterns=None):
        self.patterns = patterns if patterns is not None else PATTERNS

    def detect(self, text: str) -> list[PIIMatch]:
        matches: list[PIIMatch] = []
        for pii_type, pattern in self.patterns.items():
            for m in pattern.finditer(text):
                matches.append(
                    PIIMatch(type=pii_type, start=m.start(), end=m.end(), text=m.group())
                )
        return matches
