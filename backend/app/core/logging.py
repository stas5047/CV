import logging
from collections.abc import Iterable

SENSITIVE_KEYS = (
    "password",
    "secret",
    "token",
    "database_url",
    "authorization",
)
MIN_SENSITIVE_VALUE_LENGTH = 8


class SecretRedactionFilter(logging.Filter):
    def __init__(self, sensitive_values: Iterable[str] | None = None) -> None:
        super().__init__()
        self.sensitive_values = tuple(
            value
            for value in (sensitive_values or ())
            if isinstance(value, str) and len(value) >= MIN_SENSITIVE_VALUE_LENGTH
        )

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        lowered = message.lower()
        if any(key in lowered for key in SENSITIVE_KEYS) or any(
            value in message for value in self.sensitive_values
        ):
            record.msg = "[redacted sensitive log message]"
            record.args = ()
        return True


def configure_logging(sensitive_values: Iterable[str] | None = None) -> None:
    handler = logging.StreamHandler()
    handler.addFilter(SecretRedactionFilter(sensitive_values))
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
