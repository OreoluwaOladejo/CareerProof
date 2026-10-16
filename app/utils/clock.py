from datetime import datetime
from datetime import timezone


def utc_now() -> datetime:
    # Returns the current time as a timezone-aware UTC datetime.
    # Every model uses this one function for its timestamps, so the
    # rule "always UTC, always timezone-aware" lives in exactly one place.
    # (datetime.utcnow() is deprecated and returns a NAIVE datetime,
    # which is why we are replacing it.)
    return datetime.now(timezone.utc)