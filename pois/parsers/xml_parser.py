import xml.etree.ElementTree as ET

def _get_text(elem, tag):
    node = elem.find(tag)
    return node.text if node is not None else ""

def parse_xml(path):
    rows = []
    tree = ET.parse(path)
    root = tree.getroot()
    # Expect children elements each representing a PoI with fields:
    # pid, pname, platitude, plongitude, pcategory, pratings
    for item in root:
        lat_text = _get_text(item, "platitude")
        lng_text = _get_text(item, "plongitude")
        rate_text = _get_text(item, "pratings")
        rows.append(
            {
                "external_id": _get_text(item, "pid"),
                "name": _get_text(item, "pname"),
                "latitude": float(lat_text) if lat_text else None,
                "longitude": float(lng_text) if lng_text else None,
                "category": _get_text(item, "pcategory"),
                "ratings": [p.strip() for p in rate_text.split(",")] if rate_text else None,
            }
        )
    return rows
