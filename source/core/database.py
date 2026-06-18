import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="ham_log.db"):
        self.db_name = db_name
        self.init_db()

    def _get_connection(self):
        """Returns a connection to the SQLite database."""
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """Creates the QSO table if it doesn't exist yet."""
        query = """
        CREATE TABLE IF NOT EXISTS qso_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            callsign TEXT NOT NULL,
            band TEXT NOT NULL,
            mode TEXT NOT NULL,
            freq TEXT,
            rst_sent TEXT,
            rst_rcvd TEXT,
            operator_gridsquare TEXT,
            station_gridsquare TEXT,
            notes TEXT
        );
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    def log_qso(self, qso_data):
        """
        Inserts a new QSO into the database.
        Expects a dictionary containing the log data.
        """
        query = """
        INSERT INTO qso_log (
            timestamp, callsign, band, mode, freq, rst_sent, rst_rcvd, operator_gridsquare, station_gridsquare, notes
        ) VALUES (:timestamp, :callsign, :band, :mode, :freq, :rst_sent, :rst_rcvd, :operator_gridsquare, :station_gridsquare, :notes)
        """
        # Ensure timestamp is set if not provided
        if not qso_data.get("timestamp"):
            qso_data["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Set default values for missing keys to avoid KeyErrors
        defaults = {
            "freq": "", "rst_sent": "59", "rst_rcvd": "59",
            "operator_gridsquare": "", "station_gridsquare": "", "notes": ""
        }
        for key, val in defaults.items():
            qso_data.setdefault(key, val)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, qso_data)
            conn.commit()
            return cursor.lastrowid

    def get_all_qsos(self):
        """Fetches all logged contacts ordered by newest first."""
        query = "SELECT * FROM qso_log ORDER BY timestamp DESC"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row  # Allows accessing columns by name
            cursor = conn.cursor()
            cursor.execute(query)
            # Convert rows to standard Python dictionaries
            return [dict(row) for row in cursor.fetchall()]