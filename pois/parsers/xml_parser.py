from xml.etree import ElementTree as ET
from typing import Dict, Any, List
from django.db import transaction
from pois.models import Poi
from pois.utils import normalize_record, chunk_by_parts, chunked, progress_messages

def _element_to_dict(el: ET.Element) -> Dict[str, Any]:
    d: Dict[str, Any] = {}
    for child in el:
        tag = child.tag.strip().lower()
        text = (child.text or "").strip()
        d[tag] = text
    return d

def load_xml(path: str, show_progress: bool = True) -> int:
    tree = ET.parse(path)
    root = tree.getroot()

    # Accept <pois><poi>...</poi></pois> or flat list
    poi_nodes = root.findall(".//poi") or list(root)

    rows: List[Dict[str, Any]] = [_element_to_dict(node) for node in poi_nodes]

    total = len(rows)
    if total == 0:
        return 0

    batch_size = chunk_by_parts(total)
    created = 0
    for batch in chunked(rows, batch_size):
        objs = []
        for rec in batch:
            data = normalize_record(rec, "xml")
            if not data.get("external_id"):
                continue
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
