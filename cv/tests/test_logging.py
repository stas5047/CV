import logging

from aerovision_worker.logging import redact_sensitive_text


def test_redact_sensitive_text_removes_secret_values() -> None:
    message = (
        "DATABASE_URL=postgresql+psycopg://user:secret@postgres:5432/db "
        "JWT_SECRET_KEY=top-secret token=abc.def.ghi /app/storage/uploads/file.jpg"
    )

    redacted = redact_sensitive_text(message)

    assert "secret" not in redacted
    assert "top-secret" not in redacted
    assert "abc.def.ghi" not in redacted
    assert "/app/storage" not in redacted


def test_redaction_filter_mutates_log_record_message() -> None:
    from aerovision_worker.logging import RedactionFilter

    record = logging.LogRecord(
        name="worker",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="database password secret at /app/storage",
        args=(),
        exc_info=None,
    )

    assert RedactionFilter().filter(record)
    assert "secret" not in record.getMessage()
    assert "/app/storage" not in record.getMessage()
