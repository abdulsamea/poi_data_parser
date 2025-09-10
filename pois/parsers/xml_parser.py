from xml.etree import ElementTree as ET
from typing import Dict, Any, List
from django.db import transaction
from pois.models import Poi
from pois.utils import normalize_record, calculate_chunks, create_chunks, progress_messages


def element_to_dict(el: ET.Element) -> Dict[str, Any]:
    d: Dict[str, Any] = {}
    for child in el:
        tag = child.tag.strip().lower()
        text = (child.text or "").strip()
        d[tag] = text
    return d


def load_xml(path: str, show_progress: bool = True) -> int:
    tree = ET.parse(path)
    root = tree.getroot()

    poi_nodes = root.findall(".//DATA_RECORD") or list(root)

    rows: List[Dict[str, Any]] = [element_to_dict(node) for node in poi_nodes]

    total = len(rows)
    if total == 0:
        return 0

    batch_size = calculate_chunks(total)
    processed = 0

    # This list has Fields that are allowed to change on updates
    updatable_fields = ["name", "category", "latitude", "longitude", "avg_rating"]

    for batch in create_chunks(rows, batch_size):
        to_insert: List[Poi] = []

        track_incoming_poi_data: Dict[str, Dict[str, Any]] = {}

        for rec in batch:
            data = normalize_record(rec, "xml")
            ext_id = data.get("external_id")
            if not ext_id:
                continue
            track_incoming_poi_data[ext_id] = data
            to_insert.append(Poi(
                external_id=ext_id,
                name=data["name"],
                category=data["category"],
                latitude=data["latitude"],
                longitude=data["longitude"],
                avg_rating=data["avg_rating"],
            ))

        if not track_incoming_poi_data:
            continue

        with transaction.atomic():
            if to_insert:
                Poi.objects.bulk_create(to_insert, ignore_conflicts=True)

            ext_ids = list(track_incoming_poi_data.keys())
            existing = Poi.objects.filter(external_id__in=ext_ids).only(
                "id", "external_id", "name", "category", "latitude", "longitude", "avg_rating",
            )

            to_update: List[Poi] = []
            for obj in existing:
                data = track_incoming_poi_data[obj.external_id]
                changed = False
                if obj.name != data["name"]:
                    obj.name = data["name"]; changed = True
                if obj.category != data["category"]:
                    obj.category = data["category"]; changed = True
                if obj.latitude != data["latitude"]:
                    obj.latitude = data["latitude"]; changed = True
                if obj.longitude != data["longitude"]:
                    obj.longitude = data["longitude"]; changed = True
                if obj.avg_rating != data["avg_rating"]:
                    obj.avg_rating = data["avg_rating"]; changed = True
                if changed:
                    to_update.append(obj)

            if to_update:
                Poi.objects.bulk_update(to_update, updatable_fields)

        processed += len(track_incoming_poi_data)

        if show_progress and batch_size != total:
            print(progress_messages(min(processed, total), total))

    return processed
