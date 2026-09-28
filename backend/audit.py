"""Append-only audit trail for Campus Customs agent runs.

Every agent loop writes one entry to ``output/audit_trail.json`` describing what the agent was
asked, which database tools it called with what arguments, what those tools returned, and why
the loop stopped. Existing entries are never rewritten or removed: the file is read, the new
entry is appended to the end of ``entries``, and the whole document is written back through a
temporary file and an atomic replace so a crash mid-write cannot truncate the history.

Nothing sensitive is recorded. Values are passed through a redactor that drops any key whose
name looks like a credential, and free text is truncated. The shopper's email is deliberately
never written; an authenticated run records only the internal ``user_id``.
"""

import json
import os
import re
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
AUDIT_PATH = Path(
    os.environ.get("CAMPUS_CUSTOMS_AUDIT_LOG", PROJECT_ROOT / "output" / "audit_trail.json")
).expanduser()

SCHEMA_VERSION = 1
MAX_TEXT = 300
MAX_ITEMS = 8
MAX_DEPTH = 10

# Any key matching this is replaced with "[redacted]" rather than logged.
SENSITIVE_KEY = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|authorization|auth|cookie|session|credential|hash|bearer)",
    re.IGNORECASE,
)

_lock = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_run_id() -> str:
    return uuid.uuid4().hex[:12]


def _truncate(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= MAX_TEXT else text[:MAX_TEXT] + "…"


def redact(value: Any, depth: int = 0) -> Any:
    """Return a log-safe copy: credential-shaped keys dropped, text and lists truncated.

    The depth budget has to clear the deepest real structure, which is reached because tool
    results are summarized (and redacted) once and then redacted again as part of the whole
    entry: entry -> tool_calls -> call -> result -> inventory -> row -> value is seven levels.
    """
    if depth > MAX_DEPTH:
        return "[truncated]"
    if isinstance(value, dict):
        safe: dict[str, Any] = {}
        for key, item in value.items():
            if SENSITIVE_KEY.search(str(key)):
                safe[str(key)] = "[redacted]"
            else:
                safe[str(key)] = redact(item, depth + 1)
        return safe
    if isinstance(value, (list, tuple)):
        items = [redact(v, depth + 1) for v in list(value)[:MAX_ITEMS]]
        if len(value) > MAX_ITEMS:
            items.append(f"[+{len(value) - MAX_ITEMS} more]")
        return items
    if isinstance(value, str):
        return _truncate(value)
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return _truncate(str(value))


def _empty_document() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "description": (
            "Append-only audit trail of Campus Customs agent runs. Entries are only ever added "
            "to the end of this list; no entry is edited or removed."
        ),
        "created_at": _now(),
        "entries": [],
    }


def _load() -> dict[str, Any]:
    if not AUDIT_PATH.is_file():
        return _empty_document()
    try:
        document = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        # Never destroy an unreadable history: keep it beside the new file for inspection.
        try:
            AUDIT_PATH.replace(AUDIT_PATH.with_suffix(f".corrupt-{_now()}.json"))
        except OSError:
            pass
        return _empty_document()
    if not isinstance(document, dict) or not isinstance(document.get("entries"), list):
        return _empty_document()
    return document


def record_run(
    *,
    run_id: str,
    message: str,
    stop_reason: str,
    tool_calls: list[dict[str, Any]] | None = None,
    authenticated_user_id: int | None = None,
    page_path: str | None = None,
    page_type: str | None = None,
    model: str | None = None,
    duration_ms: int | None = None,
    response_preview: str | None = None,
    product_card_count: int | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    """Append one agent-loop entry and return it. Existing entries are preserved."""
    entry: dict[str, Any] = {
        "entry_id": None,  # filled in under the lock so ids stay sequential
        "timestamp": _now(),
        "run_id": run_id,
        "event": "agent_run",
        "model": model,
        "caller": (
            {"authenticated": True, "user_id": authenticated_user_id}
            if authenticated_user_id is not None
            else {"authenticated": False, "user_id": None}
        ),
        "page": {"path": redact(page_path), "type": page_type},
        "message_preview": redact(message),
        "tool_calls": redact(tool_calls or []),
        "tool_call_count": len(tool_calls or []),
        "response_preview": redact(response_preview) if response_preview else None,
        "product_cards_returned": product_card_count,
        "duration_ms": duration_ms,
        "stop_reason": stop_reason,
        "error": redact(error) if error else None,
    }

    with _lock:
        document = _load()
        entry["entry_id"] = len(document["entries"]) + 1
        document["entries"].append(entry)
        document["last_appended_at"] = entry["timestamp"]
        document["entry_count"] = len(document["entries"])
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Atomic replace: the existing file stays intact until the new one is complete.
        handle = tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=AUDIT_PATH.parent, prefix=".audit-", suffix=".tmp", delete=False
        )
        try:
            with handle as stream:
                json.dump(document, stream, indent=2, ensure_ascii=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(handle.name, AUDIT_PATH)
        except BaseException:
            Path(handle.name).unlink(missing_ok=True)
            raise
    return entry


def extract_tool_calls(messages: list[Any]) -> list[dict[str, Any]]:
    """Pull tool calls and their returns out of a PydanticAI message history."""
    from pydantic_ai.messages import ToolCallPart, ToolReturnPart

    calls: dict[str, dict[str, Any]] = {}
    ordered: list[dict[str, Any]] = []
    for message in messages:
        for part in getattr(message, "parts", []) or []:
            if isinstance(part, ToolCallPart):
                try:
                    args = part.args_as_dict()
                except Exception:
                    args = {"raw": str(getattr(part, "args", ""))}
                record = {
                    "timestamp": _now(),
                    "tool": part.tool_name,
                    "arguments": redact(args),
                    "result": None,
                }
                calls[part.tool_call_id] = record
                ordered.append(record)
            elif isinstance(part, ToolReturnPart):
                record = calls.get(part.tool_call_id)
                if record is not None:
                    record["result"] = _summarize_tool_result(part.content)
    return ordered


def _summarize_tool_result(content: Any) -> Any:
    """Summarize a tool return: the shape and key facts, not the whole payload."""
    data = content
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    if isinstance(data, dict):
        summary: dict[str, Any] = {}
        for key in (
            "status", "found", "matched_product_id", "total_matches", "product_id",
            "product_name", "name", "price", "requested_size", "matched_size",
            "quantity", "available", "out_of_stock", "total_stock",
        ):
            if key in data and data[key] is not None:
                summary[key] = redact(data[key])
        if isinstance(data.get("matches"), list):
            summary["matches_returned"] = len(data["matches"])
            summary["match_ids"] = redact([m.get("product_id") for m in data["matches"] if isinstance(m, dict)])
        if isinstance(data.get("inventory"), list):
            summary["inventory"] = redact(data["inventory"])
        if data.get("clarification_question"):
            summary["clarification_question"] = redact(data["clarification_question"])
        return summary or redact(data)
    return redact(data)
