from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from pois.parsers.csv_parser import parse_csv
from pois.parsers.json_parser import parse_json
from pois.parsers.xml_parser import parse_xml
from pois.utils import compute_avg, upsert_poi

class Command(BaseCommand):
    help = "Import PoI data from CSV, JSON, or XML files. Supports multiple file paths."

    def add_arguments(self, parser):
        parser.add_argument("paths", nargs="+", help="One or more file paths to import")

    def handle(self, *args, **options):
        paths: list[str] = options["paths"]
        if not paths:
            raise CommandError("No file paths provided")

        total = 0
        for p in paths:
            file_path = Path(p)
            if not file_path.exists() or not file_path.is_file():
                raise CommandError(f"File not found: {p}")

            suffix = file_path.suffix.lower()
            if suffix == ".csv":
                rows = parse_csv(file_path)
            elif suffix == ".json":
                rows = parse_json(file_path)
            elif suffix == ".xml":
                rows = parse_xml(file_path)
            else:
                raise CommandError(f"Unsupported file type: {suffix}")

            imported = 0
            for row in rows:
                ext_id = str(row.get("external_id", "")).strip()
                if not ext_id:
                    continue
                ratings = row.get("ratings", None)
                avg = compute_avg(ratings)
                payload = {
                    "name": (row.get("name") or "").strip(),
                    "external_id": ext_id,
                    "category": (row.get("category") or "").strip(),
                    "latitude": row.get("latitude"),
                    "longitude": row.get("longitude"),
                    "avg_rating": avg,
                }
                upsert_poi(payload)
                imported += 1

            total += imported
            self.stdout.write(self.style.SUCCESS(f"Imported {imported} records from {file_path.name}"))

        self.stdout.write(self.style.SUCCESS(f"Total imported/updated: {total}"))
