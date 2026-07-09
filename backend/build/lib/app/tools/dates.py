"""Date Tool — single source of truth for timestamps in the pipeline."""
from datetime import UTC, datetime, timedelta


def now_utc() -> datetime:
    return datetime.now(UTC)


def timestamp_display() -> str:
    return now_utc().strftime("%B %d, %Y at %H:%M UTC")


def timestamp_file() -> str:
    return now_utc().strftime("%Y%m%d-%H%M%S")


def offset_date(weeks: int) -> str:
    return (now_utc() + timedelta(weeks=weeks)).strftime("%b %d, %Y")
