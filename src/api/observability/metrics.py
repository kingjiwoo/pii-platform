"""Custom Prometheus metrics for domain events (PII, routing).

HTTP-level metrics come from prometheus-fastapi-instrumentator (main.py).
These are the project-specific signals: PII detection outcomes and routing decisions.
"""
from prometheus_client import Counter

pii_detections_total = Counter(
    "pii_detections_total",
    "Number of PII entities detected in inbound requests.",
    labelnames=["pii_type"],
)

routing_decisions_total = Counter(
    "routing_decisions_total",
    "Number of routing decisions made by the gateway.",
    labelnames=["target_model", "pii_detected"],
)
