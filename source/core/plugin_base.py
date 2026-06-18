class BasePlugin:
    """All custom mods must inherit from this class."""
    def __init__(self, app_context):
        # app_context gives the plugin access to the GUI, database, and settings
        self.app = app_context
        self.name = "Abstract Plugin"
        self.version = "1.0.0"

    def activate(self):
        """Called when the plugin is loaded."""
        pass

    def deactivate(self):
        """Called when the plugin is disabled or app closes."""
        pass