"""Maharashtra PWD State Schedule of Rates (SSR) 2022-23: the only source of labour wage rates in the tool."""
from __future__ import annotations

import json
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "ssr_maharashtra.json"


def load_ssr(path: Path = DEFAULT_PATH) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))
