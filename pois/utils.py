from typing import Iterable, List, Dict, Any, Generator
from decimal import Decimal
from statistics import mean
from typing import Any, List


def parse_ratings(raw: Any) -> List[Decimal]:
    if raw is None or (isinstance(raw, str) and raw.strip() == ""):
        return []
    if isinstance(raw, (list, tuple)):
        vals = raw
    elif isinstance(raw, str):
        s = raw.strip()
        # Strip curly braces found in CSV like "{10.0,10.0,...}"
        if s.startswith("{") and s.endswith("}"):
            s = s[1:-1]
        parts = [p.strip() for p in s.split(",")]
        vals = [p for p in parts if p != ""]
    else:
        vals = [raw]

    out: List[Decimal] = []
    for v in vals:
        try:
            out.append(Decimal(str(v).strip()))
        except Exception:
            continue
    return out

def average_rating(ratings: List[Decimal]) -> Decimal | None:
    return round(mean(ratings), 2) if ratings else None


def normalize_record(record: Dict[str, Any], file_type: str) -> Dict[str, Any]:
    # Map source keys for different files to common key-value data and return it.
    if file_type == "csv":
        ext_id = record.get("poi_id")
        name = record.get("poi_name")
        category = record.get("poi_category")
        lat = record.get("poi_latitude")
        lon = record.get("poi_longitude")
        ratings_raw = record.get("poi_ratings")
    elif file_type == "json":
        ext_id = record.get("id")
        name = record.get("name")
        category = record.get("category")
        coords = record.get("coordinates") or {}
        lat = (coords.get("latitude") if isinstance(coords, dict)
               else (coords if isinstance(coords, (list, tuple)) and len(coords) > 0 else None))
        lon = (coords.get("longitude") if isinstance(coords, dict)
               else (coords[3] if isinstance(coords, (list, tuple)) and len(coords) > 1 else None))
        ratings_raw = record.get("ratings")
    elif file_type == "xml":
        ext_id = record.get("pid")
        name = record.get("pname")
        category = record.get("pcategory")
        lat = record.get("platitude")
        lon = record.get("plongitude")
        ratings_raw = record.get("pratings")
    else:
        raise ValueError(f"Unsupported file_type: {file_type}")

    ratings = parse_ratings(ratings_raw)
    avg = average_rating(ratings)
    # latitude, longitude are not needed on admin site, but keep it for now.
    return {
        "external_id": str(ext_id).strip() if ext_id is not None else None,
        "name": (str(name).strip() if name is not None else None) or "",
        "category": (str(category).strip() if category is not None else None) or "",
        "latitude": float(lat) if lat not in (None, "") else None,
        "longitude": float(lon) if lon not in (None, "") else None,
        "ratings": ratings,
        "avg_rating": avg,
    }


def chunk_by_parts(total: int) -> int:
    """
        This function simply provides number of chunks for batch processing if records are more than 1K.
        Parameters
        ----------
        total : str
            Total number of records in the file.
        """
    if total <= 1000:
        return total
    if total >= 100_000:
        parts = 10
    else:
        # 2 parts if records are  greater than 1000 and less than 100k
        parts = 2
    size = max(1, (total + parts - 1) // parts)
    return size

def chunked(iterable: Iterable[Any], size: int) -> Generator[List[Any], None, None]:
    buf: List[Any] = []
    for item in iterable:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf

def progress_messages(done: int, total: int) -> str:
    pct = (done / total * 100) if total else 100.0
    return f"Processed {done}/{total} records ({pct:.1f}%)."
