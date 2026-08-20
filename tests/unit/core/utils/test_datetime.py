from datetime import datetime, timedelta, timezone

from src.core.utils.datetime import get_utc_now


def test_get_utc_now_returns_datetime():
    result = get_utc_now()
    assert isinstance(result, datetime)


def test_get_utc_now_is_naive():
    result = get_utc_now()
    assert result.tzinfo is None


def test_get_utc_now_difference():
    result = get_utc_now()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = abs(now - result)
    assert diff < timedelta(seconds=60)
