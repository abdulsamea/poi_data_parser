import json

def parse_json(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Accept array at root or objects under common keys (items/pois)
    items = data if isinstance(data, list) else (data.get("items") or data.get("pois") or [])

    for obj in items:
        coords = obj.get("coordinates") or {}
        lat = coords.get("latitude") if isinstance(coords, dict) else None
        lng = coords.get("longitude") if isinstance(coords, dict) else None
        rows.append(
            {
                "external_id": str(obj.get("id", "") or ""),
                "name": obj.get("name", "") or "",
                "latitude": lat if lat not in (None, "") else None,
                "longitude": lng if lng not in (None, "") else None,
                "category": obj.get("category", "") or "",
                "ratings": obj.get("ratings"),
            }
        )
    return rows
