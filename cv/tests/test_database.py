from sqlalchemy import text

from aerovision_worker.database import check_database, create_session_factory, wait_for_database


class FlakyChecker:
    def __init__(self, fail_count: int) -> None:
        self.fail_count = fail_count
        self.calls = 0

    def __call__(self) -> None:
        self.calls += 1
        if self.calls <= self.fail_count:
            raise RuntimeError("database unavailable")


def test_create_session_factory_builds_working_sqlite_session() -> None:
    factory = create_session_factory("sqlite+pysqlite:///:memory:")

    with factory() as session:
        assert session.execute(text("select 1")).scalar_one() == 1


def test_check_database_executes_select_one() -> None:
    factory = create_session_factory("sqlite+pysqlite:///:memory:")

    check_database(factory)


def test_wait_for_database_retries_until_checker_succeeds() -> None:
    checker = FlakyChecker(fail_count=2)

    wait_for_database(checker, attempts=3, delay_seconds=0)

    assert checker.calls == 3


def test_wait_for_database_raises_after_exhausting_attempts() -> None:
    checker = FlakyChecker(fail_count=3)

    try:
        wait_for_database(checker, attempts=2, delay_seconds=0)
    except RuntimeError as exc:
        assert "database unavailable after 2 attempts" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("wait_for_database should fail")
