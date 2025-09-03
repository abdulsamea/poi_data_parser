from statistics import mean
from typing import Optional, Iterable
from .models import Poi

def compute_avg(ratings) -> Optional[float]:
    if ratings is None:
        return None
    try:
        nums = []
        for r in ratings:
            if r is None or str(r).strip() == "":
                continue
            nums.append(float(r))
        return round(mean(nums), 2) if nums else None
    except Exception:
        return None

def upsert_poi(payload: dict) -> Poi:
    obj, _created = Poi.objects.update_or_create(
        external_id=payload["external_id"],
        defaults={
            "name": payload.get("name", "") or "",
            "category": payload.get("category", "") or "",
            "latitude": payload.get("latitude"),
            "longitude": payload.get("longitude"),
            "avg_rating": payload.get("avg_rating"),
        },
    )
    return obj
