"""Korean PII regex patterns.

Uses explicit digit boundaries `(?<!\\d)` / `(?!\\d)` instead of `\\b` because
Python's `\\w` includes Hangul, so `\\b` fails between digits and Korean chars
(e.g. `123-456-789로` — no boundary between `9` and `로`).
"""
import re

from .models import PIIType

PATTERNS: dict[PIIType, re.Pattern] = {
    # 주민등록번호: YYMMDD-GXXXXXX (G is 1-4)
    PIIType.KOREAN_RRN: re.compile(r"(?<!\d)\d{6}-?[1-4]\d{6}(?!\d)"),
    # 카드번호: 16 digits with optional hyphen/space separators
    PIIType.CARD: re.compile(r"(?<!\d)\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}(?!\d)"),
    # 계좌번호: 은행별 다양한 형식 근사 (3-6, 2-6, 2-6 digit blocks)
    PIIType.ACCOUNT: re.compile(r"(?<!\d)\d{3,6}-\d{2,6}-\d{2,6}(?!\d)"),
    # 전화번호: 010-1234-5678, 02-123-4567 등
    PIIType.PHONE: re.compile(r"(?<!\d)0\d{1,2}-?\d{3,4}-?\d{4}(?!\d)"),
}
