from __future__ import annotations

import json
import os
from datetime import datetime
from threading import Lock
from typing import Dict, List


STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
STORAGE_DIR = os.path.abspath(STORAGE_DIR)
STORAGE_PATH = os.path.join(STORAGE_DIR, "reports.json")
_lock = Lock()


def initialize_storage() -> None:
    os.makedirs(STORAGE_DIR, exist_ok=True)
    if not os.path.exists(STORAGE_PATH):
        with open(STORAGE_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)


def _read_all() -> List[Dict]:
    initialize_storage()
    with open(STORAGE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_all(records: List[Dict]) -> None:
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def add_report(record: Dict) -> None:
    with _lock:
        records = _read_all()
        record["created_at"] = datetime.utcnow().isoformat()
        records.append(record)
        _write_all(records)


def search_reports(criteria: Dict, limit: int = 5) -> List[Dict]:
    records = _read_all()
    target_type = criteria.get("type")
    desired_item = (criteria.get("item") or "").lower()
    desired_color = (criteria.get("color") or "").lower()
    desired_location = (criteria.get("location") or "").lower()
    desired_date = criteria.get("date_iso")

    def score(record: Dict) -> int:
        s = 0
        if desired_item and desired_item in (record.get("item") or "").lower():
            s += 2
        if desired_color and desired_color == (record.get("color") or "").lower():
            s += 1
        if desired_location and desired_location in (record.get("location") or "").lower():
            s += 1
        if desired_date and desired_date == record.get("date_iso"):
            s += 1
        return s

    filtered = [r for r in records if not target_type or r.get("type") == target_type]
    scored = sorted(filtered, key=score, reverse=True)
    top = [r for r in scored if score(r) > 0][:limit]
    return top

