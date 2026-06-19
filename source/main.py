import sys, os
from PySide6.QtWidgets import QApplication
from core.database import DatabaseManager
from core.plugin_manager import PluginManager
from core.data_exporter import DataExchangeManager
from core.api_client import CallsignLookupManager
from core.geo_math import GeoMath
from core.settings import SettingsManager
from gui.main_window import MainWindow

if getattr(sys, 'frozen', False):
    # Allows external loose .py plugins to import packages bundled inside the EXE
    sys.path.append(sys._MEIPASS)

class ApplicationContext:
    def __init__(self, home_grid="EN53"):
        self.settings_manager = SettingsManager()
        self.home_grid = home_grid
        self.home_callsign = self.settings_manager.load_callsign()
        self.home_lat, self.home_lon = GeoMath.grid_to_latlon(self.home_grid)
        
        # Initialize Core Services
        self.db = DatabaseManager("ham_log.db")
        self.plugin_manager = PluginManager(self)
        self.data_exchange = DataExchangeManager(self.db)
        self.lookup_service = CallsignLookupManager(self)

        if self.home_callsign:
            self.refresh_home_location(self.home_callsign)
        
        # Boot Plugin System
        self.plugin_manager.load_plugins()

    def refresh_home_location(self, callsign):
        """Loads and stores the user's station coordinates from their callsign."""
        normalized = self.settings_manager.save_callsign(callsign)
        info = self.lookup_service.lookup(normalized)

        if info.get("lat") is not None and info.get("lon") is not None:
            self.home_callsign = normalized
            self.home_grid = info.get("grid", self.home_grid)
            self.home_lat, self.home_lon = info["lat"], info["lon"]
        elif info.get("grid"):
            self.home_callsign = normalized
            self.home_grid = info["grid"]
            self.home_lat, self.home_lon = GeoMath.grid_to_latlon(self.home_grid)

        return self.home_lat, self.home_lon

    def save_new_contact(self, contact_dict):
        """Core logging pipeline."""
        self.plugin_manager.trigger_hook("on_pre_log", contact_dict)
        qso_id = self.db.log_qso(contact_dict)
        contact_dict["id"] = qso_id
        self.plugin_manager.trigger_hook("on_post_log", contact_dict)

if __name__ == "__main__":
    # Create the Qt GUI instance
    qt_app = QApplication(sys.argv)
    
    # Initialize the runtime backend system engine context
    app_context = ApplicationContext(home_grid="EN53")
    
    # Create and display the main window interface
    window = MainWindow(app_context)
    window.show()
    
    # Hand off execution handle controls to Qt engine framework context loop
    sys.exit(qt_app.exec())
