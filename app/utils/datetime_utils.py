from datetime import datetime, timedelta, timezone


# Vietnam timezone base (GMT+7)
VN_TZ = timezone(timedelta(hours=7))


def vn_now() -> datetime:
    """Return current Vietnam time as naive datetime (base GMT+7)."""
    return datetime.now(VN_TZ).replace(tzinfo=None)


def to_vn_naive(value: datetime) -> datetime:
    """
    Normalize a datetime to Vietnam timezone and store as naive datetime.

    - Naive input is assumed to already be GMT+7.
    - Aware input is converted to GMT+7, then tzinfo is stripped for DB consistency.
    """
    if value.tzinfo is None:
        return value
    return value.astimezone(VN_TZ).replace(tzinfo=None)
