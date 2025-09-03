from __future__ import annotations
from typing import Iterable, List, Tuple

def _to_floats_and_avg(tokens: Iterable[str | float | int]) -> Tuple[List[float], float | None]:
    vals: List[float] = []
    for x in tokens:
        # normalize to stripped string for strings, else skip
        if isinstance(x, str):
            x = x.strip()
            if not x:
                continue
        try:
            vals.append(float(x))
        except (TypeError, ValueError):
            continue
    if not vals:
        return [], None
    return vals, sum(vals) / len(vals)

def parse_csv_ratings(cell: str | None) -> Tuple[List[float], float | None]:
    # CSV shape: "{3.0,4.0,3.0,5.0,2.0,3.0,2.0,2.0,2.0,2.0}"
    if not cell:
        return [], None
    s = cell.strip()
    if s.startswith("{") and s.endswith("}"):
        s = s[1:-1]
    tokens = (p for p in s.split(","))
    return _to_floats_and_avg(tokens)

def parse_json_ratings(arr) -> Tuple[List[float], float | None]:
    # JSON shape: [2, 3, 1, 1, 4]
    if not isinstance(arr, list):
        return [], None
    return _to_floats_and_avg(arr)

def parse_xml_ratings(text: str | None) -> Tuple[List[float], float | None]:
    # XML shape: "1,1,3,1,4,1,5,3,1,2"
    if not text:
        return [], None
    tokens = (p for p in text.strip().split(","))
    return _to_floats_and_avg(tokens)
