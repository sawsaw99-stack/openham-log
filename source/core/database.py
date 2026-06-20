import os
import sys
import sqlite3
from datetime import datetime

class DatabaseInitializationError(Exception):
    pass

class DatabaseManager:
    def __init__(self, db_name="ham_log.db"):
        if getattr(sys, 'frozen', False):
            # 1. Target the Windows AppData directory (e.g., C:\Users\Name\AppData\Roaming\OpenHam)
            base_dir = os.path.join(os.environ["APPDATA"], "OpenHam")
            # Create the OpenHam folder if it doesn't exist yet
            os.makedirs(base_dir, exist_ok=True)
        else:
            # 2. Keep it in your local folder during development
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.db_path = os.path.join(base_dir, db_name)
            
        try:
            self.init_db()
        except sqlite3.Error as e:
            raise DatabaseInitializationError(f"Database storage failed to initialize: {e}")

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
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

    def delete_qso(self, qso_id):
        """Deletes a specific QSO from the log using its database row ID."""
        query = "DELETE FROM qso_log WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (qso_id,))
            conn.commit()
            return cursor.rowcount > 0