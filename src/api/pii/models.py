"""PII data types."""
from dataclasses import dataclass
from enum import Enum


class PIIType(str, Enum):
    KOREAN_RRN = "korean_rrn"
    ACCOUNT = "account"
    CARD = "card"
    PHONE = "phone"


@dataclass
class PIIMatch:
    type: PIIType
    start: int
    end: int
    text: str
