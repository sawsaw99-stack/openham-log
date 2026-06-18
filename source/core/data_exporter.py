import csv
import json
import os

class DataExchangeManager:
    def __init__(self, db_manager):
        """
        Accepts the active DatabaseManager instance 
        to read raw logs directly from SQLite.
        """
        self.db = db_manager

    def export_to_csv(self, file_path):
        """Fetches all records from the DB and writes them to a standard CSV file."""
        try:
            records = self.db.get_all_qsos()
            if not records:
                return False, "No log records found to export."

            # Use the dictionary keys from the first row as CSV headers
            headers = records[0].keys()

            with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(records)

            return True, f"Successfully exported {len(records)} contacts to CSV."
        except Exception as e:
            return False, f"CSV Export failed: {str(e)}"

    def export_to_json(self, file_path):
        """Fetches all records from the DB and writes them to a structured JSON file."""
        try:
            records = self.db.get_all_qsos()
            if not records:
                return False, "No log records found to export."

            with open(file_path, mode='w', encoding='utf-8') as json_file:
                # indent=4 formats the output nicely for human readability
                json.dump(records, json_file, indent=4, ensure_ascii=False)

            return True, f"Successfully exported {len(records)} contacts to JSON."
        except Exception as e:
            return False, f"JSON Export failed: {str(e)}"

    def import_from_json(self, file_path):
        """Loads contacts from a valid JSON log file and inserts them into SQLite."""
        try:
            if not os.path.exists(file_path):
                return False, "File not found."

            with open(file_path, mode='r', encoding='utf-8') as json_file:
                records = json.load(json_file)

            imported_count = 0
            for record in records:
                # Pop the primary key ID if it exists so SQLite generates a fresh, consecutive ID
                record.pop('id', None)
                self.db.log_qso(record)
                imported_count += 1

            return True, f"Successfully imported {imported_count} contacts into the log."
        except Exception as e:
            return False, f"JSON Import failed: {str(e)}"