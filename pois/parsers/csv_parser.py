import csv
from typing import Dict, Any, List
from django.db import transaction
from pois.models import Poi
from pois.utils import normalize_record, calculate_chunks, create_chunks, progress_messages, save_by_name_and_category


def load_csv(path: str, show_progress: bool = True) -> int:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows: List[Dict[str, Any]] = list(reader)

    total = len(rows)
    if total == 0:
        return 0

    batch_size = calculate_chunks(total)
    created = 0
    memo = {}
    for batch in create_chunks(rows, batch_size):
        objs = []
        for rec in batch:
            data = normalize_record(rec, "csv")
            if not data.get("external_id"):
                continue
            save_by_name_and_category(data, memo)
            objs.append(Poi(
                external_id=data["external_id"],
                name=data["name"],
                category=data["category"],
                latitude=data["latitude"],
                longitude=data["longitude"],
                avg_rating=data["avg_rating"],
            ))
        if objs:
            with transaction.atomic():
                Poi.objects.bulk_create(objs, ignore_conflicts=True)
                created += len(objs)
        if show_progress and batch_size != total:
            print(progress_messages(min(created, total), total))

    return created
