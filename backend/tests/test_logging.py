import logging
from io import StringIO

from app.core.logging import SecretRedactionFilter


def test_logging_redacts_sensitive_messages() -> None:
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.addFilter(SecretRedactionFilter())
    logger = logging.getLogger("aerovision.test.redaction")
    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(logging.INFO)

    logger.info("JWT_SECRET_KEY=jwt-secret-value")

    output = stream.getvalue()
    assert "jwt-secret-value" not in output
    assert "[redacted sensitive log message]" in output


def test_logging_redacts_configured_sensitive_values_without_key_names() -> None:
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.addFilter(SecretRedactionFilter(["plain-secret-value"]))
    logger = logging.getLogger("aerovision.test.value_redaction")
    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(logging.INFO)

    logger.info("Loaded configured value %s", "plain-secret-value")

    output = stream.getvalue()
    assert "plain-secret-value" not in output
    assert "[redacted sensitive log message]" in output
