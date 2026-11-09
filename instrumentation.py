"""
Structured logging for FitFindr runs.

One JSON object per line, appended to config.LOG_FILE, one record per call to
agent.run_agent(). A file you can read back with a text editor or `grep`, not
output that only ever existed in a terminal that's since closed.

Every record, success or failure, holds the same named fields:

    timestamp              UTC, ISO 8601
    query                  what the user asked for
    outcome                "ok" or "error"
    error                  the message in session["error"], or None
    duration_seconds       wall-clock time for the whole run_agent() call
    search_result_count    len(session["search_results"])
    selected_item_id       the id of session["selected_item"], or None
    condition_flags        what flag_condition_issues returned for that item
    model_calls            calls to generate() made during this run
    cache_hits             of those, how many were served from cache
    tokens_total           prompt + output tokens actually billed this run

A run that raises before run_agent returns still gets a record — the
try/finally in run_agent logs on every exit, not just the successful ones.
"""

import json
from datetime import datetime, timezone

import config


def log_run(record: dict) -> None:
    """Append one record as a line of JSON. Creates the log file's directory
    on first use."""
    config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with config.LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def build_record(
    query: str,
    session: dict,
    duration_seconds: float,
    model_calls: int,
    cache_hits: int,
    tokens_total: int,
) -> dict:
    """Turn one finished (or failed) session into a log record."""
    selected = session.get("selected_item") or {}
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "query": query,
        "outcome": "error" if session.get("error") else "ok",
        "error": session.get("error"),
        "duration_seconds": round(duration_seconds, 3),
        "search_result_count": len(session.get("search_results") or []),
        "selected_item_id": selected.get("id"),
        "condition_flags": session.get("condition_flags") or [],
        "model_calls": model_calls,
        "cache_hits": cache_hits,
        "tokens_total": tokens_total,
    }


def read_log() -> list[dict]:
    """Every record written so far, oldest first. Empty list if nothing's
    been logged yet."""
    if not config.LOG_FILE.exists():
        return []
    records = []
    for line in config.LOG_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records
