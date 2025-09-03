from pathlib import Path
from typing import List
from django.core.management.base import BaseCommand, CommandError

from pois.parsers.csv_parser import load_csv
from pois.parsers.json_parser import load_json
from pois.parsers.xml_parser import load_xml

class Command(BaseCommand):
    help = "Import PoI data from CSV, JSON, or XML files."

    def add_arguments(self, parser):
        parser.add_argument("paths", nargs="+", help="One or more file paths to import.")

    def handle(self, *args, **options):
        paths: List[str] = options["paths"]
        if not paths:
            raise CommandError("Provide at least one file path.")

        total_created = 0
        for p in paths:
            fp = Path(p)
            if not fp.exists() or not fp.is_file():
                self.stderr.write(self.style.ERROR(f"File not found: {fp}"))
                continue

            suffix = fp.suffix.lower()
            self.stdout.write(self.style.NOTICE(f"Importing {fp} ..."))
            try:
                if suffix == ".csv":
                    created = load_csv(str(fp), show_progress=True)
                elif suffix == ".json":
                    created = load_json(str(fp), show_progress=True)
                elif suffix == ".xml":
                    created = load_xml(str(fp), show_progress=True)
                else:
                    self.stderr.write(self.style.WARNING(f"Skipping unsupported file type: {fp}"))
                    continue
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"Failed {fp}: {exc}"))
                continue

            total_created += created
            self.stdout.write(self.style.SUCCESS(f"Imported {created} records from {fp}."))

        self.stdout.write(self.style.SUCCESS(f"Done. Total imported: {total_created}."))
