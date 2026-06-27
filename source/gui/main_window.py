import sys, os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
                             QInputDialog, QMenu, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from core.database import DatabaseManager
from core.api_client import CallsignLookupManager
from core.geo_math import GeoMath

class MainWindow(QMainWindow):
    def __init__(self, app_context):
        super().__init__()
        self.app = app_context
        self.setWindowTitle("Ham Radio Logger & Tracker")
        self.resize(1100, 650)

        if getattr(sys, 'frozen', False):
            # When frozen, PyInstaller extracts resources to sys._MEIPASS
            icon_path = os.path.join(sys._MEIPASS, "logo.ico")
        else:
            # Local development path
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.ico")
            
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Central Widget & Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top Split Pane (Form on left, Map on right)
        top_layout = QHBoxLayout()
        
        # 1. Log Form Group
        form_group = QGroupBox("New QSO Entry")
        form_layout = QVBoxLayout(form_group)
        
        self.call_input = QLineEdit()
        self.call_input.setPlaceholderText("Callsign (e.g., G4XYZ)")
        # Look up data when the user finishes typing the callsign
        self.call_input.editingFinished.connect(self.handle_lookup)
        
        self.band_input = QLineEdit("20m")
        self.mode_input = QLineEdit("SSB")
        self.rst_s_input = QLineEdit("59")
        self.rst_r_input = QLineEdit("59")
        self.notes_input = QLineEdit()
        
        form_layout.addWidget(QLabel("Callsign:"))
        form_layout.addWidget(self.call_input)
        form_layout.addWidget(QLabel("Band:"))
        form_layout.addWidget(self.band_input)
        form_layout.addWidget(QLabel("Mode:"))
        form_layout.addWidget(self.mode_input)
        form_layout.addWidget(QLabel("RST Sent / Rcvd:"))
        rst_layout = QHBoxLayout()
        rst_layout.addWidget(self.rst_s_input)
        rst_layout.addWidget(self.rst_r_input)
        form_layout.addLayout(rst_layout)
        form_layout.addWidget(QLabel("Notes:"))
        form_layout.addWidget(self.notes_input)
        
        self.save_btn = QPushButton("Log Contact")
        self.save_btn.clicked.connect(self.handle_log_qso)
        form_layout.addWidget(self.save_btn)
        
        top_layout.addWidget(form_group, 1)

        # 2. Map / Telemetry Pane Group
        map_group = QGroupBox("Path Tracker & Beam Heading")
        self.map_layout = QVBoxLayout(map_group)
        self.telemetry_label = QLabel("Enter a callsign to calculate path info...")
        self.telemetry_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_layout.addWidget(self.telemetry_label)
        
        top_layout.addWidget(map_group, 2)
        main_layout.addLayout(top_layout, 1)

        # 3. Log History Table (Bottom Pane)
        table_group = QGroupBox("Station Log History")
        table_layout = QVBoxLayout(table_group)
        self.history_table = QTableWidget(0, 6)
        self.history_table.setHorizontalHeaderLabels(["Timestamp", "Callsign", "Band", "Mode", "RST S", "RST R"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_layout.addWidget(self.history_table)
        
        main_layout.addWidget(table_group, 1)

        # Load initial data from SQLite & trigger UI Plugin initialization
        self.refresh_log_table()
        self.ensure_home_station()
        self.app.plugin_manager.trigger_hook("on_ui_init", self)

    def ensure_home_station(self):
        """Prompt once for the user's callsign so real-distance math has a home reference."""
        if self.app.home_callsign and self.app.home_lat is not None and self.app.home_lon is not None:
            return

        default_value = self.app.settings_manager.load_callsign()
        callsign, ok = QInputDialog.getText(
            self,
            "Set Your Station Callsign",
            "Enter your callsign to calculate real home-to-station distances:",
            text=default_value
        )

        if ok and callsign.strip():
            self.app.refresh_home_location(callsign)
            self.telemetry_label.setText(
                f"<b>Home Station:</b> {self.app.home_callsign}<br>"
                f"<b>Reference Grid:</b> {self.app.home_grid}"
            )

    def handle_lookup(self):
        """Runs an automatic background API check as soon as callsign field is exited."""
        callsign = self.call_input.text().strip().upper()
        if not callsign:
            return

        info = self.app.lookup_service.lookup(callsign)
        
        # Calculate mapping telemetry data
        dx_lat, dx_lon = info.get("lat"), info.get("lon")
        if not dx_lat and info.get("grid"):
            dx_lat, dx_lon = GeoMath.grid_to_latlon(info["grid"])

        distance, bearing = GeoMath.calculate_distance_bearing(
            self.app.home_lat, self.app.home_lon, dx_lat, dx_lon
        )

        # Update HUD Text Panel
        self.telemetry_label.setText(
            f"<b>Station:</b> {info['name']}<br>"
            f"<b>Country:</b> {info['country']} ({info['grid'] or 'Unknown Grid'})<br>"
            f"<b>Distance:</b> {distance} km ({round(distance*0.621, 1)} miles)<br>"
            f"<b>Antenna Heading:</b> {bearing}°"
        )

    def handle_log_qso(self):
        """Assembles data from GUI fields and saves it through the application pipe."""
        qso_data = {
            "callsign": self.call_input.text().upper(),
            "band": self.band_input.text(),
            "mode": self.mode_input.text(),
            "rst_sent": self.rst_s_input.text(),
            "rst_rcvd": self.rst_r_input.text(),
            "notes": self.notes_input.text()
        }
        
        if not qso_data["callsign"]:
            return

        # Core app orchestration pipeline fires hooks and writes to SQLite
        self.app.save_new_contact(qso_data)
        
        # Clear form fields out and refresh the database ledger layout
        self.call_input.clear()
        self.notes_input.clear()
        self.refresh_log_table()

    def refresh_log_table(self):
        """Queries SQLite and syncs the QTableWidget display grid."""
        self.history_table.setRowCount(0)
        logs = self.app.db.get_all_qsos()
        
        # Turn on custom context menus for right-clicking rows
        self.history_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_table.customContextMenuRequested.connect(self.show_context_menu)
        
        for row_idx, log in enumerate(logs):
            self.history_table.insertRow(row_idx)
            self.history_table.setItem(row_idx, 0, QTableWidgetItem(log["timestamp"]))
            self.history_table.setItem(row_idx, 1, QTableWidgetItem(log["callsign"]))
            self.history_table.setItem(row_idx, 2, QTableWidgetItem(log["band"]))
            self.history_table.setItem(row_idx, 3, QTableWidgetItem(log["mode"]))
            self.history_table.setItem(row_idx, 4, QTableWidgetItem(log["rst_sent"]))
            self.history_table.setItem(row_idx, 5, QTableWidgetItem(log["rst_rcvd"]))
            
            # CRITICAL: Store the hidden database ID inside the callsign cell's custom data role
            # This allows us to know exactly which SQL row to delete later!
            self.history_table.item(row_idx, 1).setData(Qt.ItemDataRole.UserRole, log["id"])
    
    def show_context_menu(self, position):
        """Triggers when a user right-clicks a row in the log view grid."""
        item = self.history_table.itemAt(position)
        if not item:
            return
            
        row = item.row()
        
        # Pull the hidden database ID out of column 1 (Callsign column)
        qso_id = self.history_table.item(row, 1).data(Qt.ItemDataRole.UserRole)
        callsign = self.history_table.item(row, 1).text()

        # Build a native popup menu right under the mouse cursor
        menu = QMenu()
        delete_action = menu.addAction(f"Delete QSO with {callsign}")
        
        # Execute menu and check if the user clicked delete
        action = menu.exec(self.history_table.viewport().mapToGlobal(position))
        if action == delete_action:
            self.confirm_and_delete_qso(qso_id, callsign)

    def confirm_and_delete_qso(self, qso_id, callsign):
        """Shows a safety confirmation modal before calling the delete pipe logic."""
        confirm = QMessageBox.question(
            self,
            "Delete Confirmation",
            f"Are you sure you want to permanently delete the contact with {callsign}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Delete from DB backend file
            self.app.db.delete_qso(qso_id)
            # Instantly update grid ledger frame overlay display layout
            self.refresh_log_table()
