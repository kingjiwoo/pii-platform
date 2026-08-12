"""Model routing protocol and rule-based implementation.

Alternatives can implement sensitivity levels, cost-aware routing, or A/B experiments.
"""
from typing import Protocol

from ..pii.models import PIIMatch


class Router(Protocol):
    def route(self, matches: list[PIIMatch]) -> str: ...


class RuleBasedRouter:
    def __init__(self, pii_model: str, default_model: str):
        self.pii_model = pii_model
        self.default_model = default_model

    def route(self, matches: list[PIIMatch]) -> str:
        return self.pii_model if matches else self.default_model
