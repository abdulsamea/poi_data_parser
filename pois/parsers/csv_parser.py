import csv

def _parse_ratings(text):
    if text is None:
        return None
    try:
        parts = [t.strip() for t in str(text).split(",") if str(t).strip() != ""]
        nums = [float(p) for p in parts]
        return nums if nums else None
    except Exception:
        return None

def parse_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Expected headers: poi_id, poi_name, poi_latitude, poi_longitude, poi_category, poi_ratings
        for r in reader:
            rows.append(
                {
                    "external_id": r.get("poi_id", "") or "",
                    "name": r.get("poi_name", "") or "",
                    "latitude": float(r["poi_latitude"]) if r.get("poi_latitude") not in (None, "") else None,
                    "longitude": float(r["poi_longitude"]) if r.get("poi_longitude") not in (None, "") else None,
                    "category": r.get("poi_category", "") or "",
                    "ratings": _parse_ratings(r.get("poi_ratings")),
                }
            )
    return rows
