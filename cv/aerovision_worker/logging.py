from __future__ import annotations

import logging
import re

SENSITIVE_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(database_url|postgres_password|jwt_secret_key|admin_password|password|token)"
    r"\s*=\s*\S+"
)
DATABASE_URL_RE = re.compile(r"postgresql(?:\+\w+)?://[^\s]+", re.IGNORECASE)
JWT_LIKE_RE = re.compile(r"\b[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")
ABSOLUTE_PATH_RE = re.compile(r"(?i)(?:[A-Z]:\\[^\s]+|/[A-Za-z0-9_./-]+)")
SECRET_WORD_RE = re.compile(r"(?i)\b(top-secret|secret)\b")


def redact_sensitive_text(value: object) -> str:
    text = str(value)
    text = DATABASE_URL_RE.sub("<redacted-database-url>", text)
    text = SENSITIVE_ASSIGNMENT_RE.sub(lambda m: f"{m.group(1)}=<redacted>", text)
    text = JWT_LIKE_RE.sub("<redacted-token>", text)
    text = ABSOLUTE_PATH_RE.sub("<path>", text)
    text = SECRET_WORD_RE.sub("<redacted>", text)
    return text


class RedactionFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_sensitive_text(record.getMessage())
        record.args = ()
        return True


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.addFilter(RedactionFilter())
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
