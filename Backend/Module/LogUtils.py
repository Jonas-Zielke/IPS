import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List

from Config import LOG_MAX_RECORDS, LOG_MAX_AGE_DAYS


def _parse_time(entry: Any) -> datetime | None:
    """Return a datetime from common keys in a log entry if present."""
    for key in ("timestamp", "start_time", "end_time"):
        ts = entry.get(key)
        if ts:
            try:
                return datetime.fromisoformat(ts)
            except (ValueError, TypeError):
                continue
    return None


def prune_log_file(path: str | Path) -> None:
    """Truncate the log so it respects configured limits."""
    p = Path(path)
    if not p.exists():
        return
    try:
        with open(p, "r") as f:
            data: List[Any] = json.load(f)
    except json.JSONDecodeError:
        data = []
    if not isinstance(data, list):
        data = [data]

    # Filter by age
    if LOG_MAX_AGE_DAYS is not None:
        cutoff = datetime.now() - timedelta(days=LOG_MAX_AGE_DAYS)
        data = [d for d in data if (_parse_time(d) or datetime.now()) >= cutoff]

    # Trim to last N records
    if LOG_MAX_RECORDS is not None and len(data) > LOG_MAX_RECORDS:
        data = data[-LOG_MAX_RECORDS:]

    with open(p, "w") as f:
        json.dump(data, f, indent=4)
