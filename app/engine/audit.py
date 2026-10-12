"""Audit trail: canonical serialisation, input hash and assumption register."""
from __future__ import annotations

import dataclasses
import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable

from .models import Param, Source


def to_jsonable(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.value
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: to_jsonable(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_jsonable(v) for v in obj]
    if hasattr(obj, "item"):
        return obj.item()
    return obj


def input_hash(inputs: dict) -> str:
    blob = json.dumps(to_jsonable(inputs), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _walk_params(obj: Any, path: str = "") -> Iterable[tuple[str, Param]]:
    if isinstance(obj, Param):
        yield path, obj
    elif dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        for f in dataclasses.fields(obj):
            yield from _walk_params(getattr(obj, f.name), f"{path}.{f.name}" if path else f.name)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk_params(v, f"{path}[{k}]")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            yield from _walk_params(v, f"{path}[{i}]")


def assumption_register(inputs: dict) -> list[dict]:
    """Every Param whose source is not Literature/Historical is listed, so assumptions
    cannot be presented as established facts."""
    rows = []
    for path, p in _walk_params(inputs):
        if p.source in (Source.ASSUMPTION, Source.EXPERT, Source.USER):
            rows.append({"input": path, "value": p.value, "source": p.source.value, "note": p.note,
                         "evidence_ids": list(p.evidence_ids)})
    return rows


def build_record(inputs: dict, results: dict, *, seed: int, n: int, criterion: str) -> dict:
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "input_hash_sha256": input_hash(inputs),
        "seed": seed,
        "iterations": n,
        "decision_criterion": criterion,
        "assumptions_and_non_literature_inputs": assumption_register(inputs),
        "inputs": to_jsonable(inputs),
        "results": to_jsonable(results),
    }
