import time
import uuid
from typing import Dict, Any

_STORE: Dict[str, Dict[str, Any]] = {}


def get_or_create_thread(thread_id: str | None) -> str:
    if thread_id and thread_id in _STORE:
        return thread_id
    tid = str(uuid.uuid4())
    _STORE[tid] = {"created_at": time.time(), "ctx": {}, "last_table": None}
    return tid


def get_ctx(thread_id: str) -> dict:
    return _STORE[thread_id]["ctx"]


def set_ctx(thread_id: str, **kv):
    _STORE[thread_id]["ctx"].update(kv)


def set_last_table(thread_id: str, table_payload: dict | None):
    _STORE[thread_id]["last_table"] = table_payload


def get_last_table(thread_id: str):
    if thread_id not in _STORE:
        return None
    return _STORE[thread_id].get("last_table")
