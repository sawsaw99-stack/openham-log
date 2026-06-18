import os
import importlib.util
import logging

class PluginManager:
    def __init__(self, app_context):
        self.app = app_context
        self.plugins = {}
        # Simple registry mapping event names to lists of callback functions
        self.hooks = {
            "on_ui_init": [],
            "on_pre_log": [],
            "on_post_log": [],
            "on_pre_lookup": [],    # Added! Runs before internet lookup
            "on_post_lookup": []    # Added! Runs after internet lookup
}

    def load_plugins(self, plugin_folder="plugins"):
        """Scans the folder and loads all valid Python plugins."""
        if not os.path.exists(plugin_folder):
            os.makedirs(plugin_folder)
            return

        for filename in os.listdir(plugin_folder):
            if filename.endswith(".py") and filename != "__init__.py":
                plugin_path = os.path.join(plugin_folder, filename)
                plugin_name = filename[:-3]
                
                try:
                    # Dynamically import the module
                    spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Instantiate the plugin class (assuming it's named 'Plugin')
                    if hasattr(module, "Plugin"):
                        plugin_instance = module.Plugin(self.app)
                        plugin_instance.activate()
                        self.plugins[plugin_name] = plugin_instance
                        print(f"Successfully loaded plugin: {plugin_instance.name} v{plugin_instance.version}")
                except Exception as e:
                    print(f"Failed to load plugin {filename}: {e}")

    def register_hook(self, hook_name, callback):
        """Allows plugins to register a function to an event."""
        if hook_name in self.hooks:
            self.hooks[hook_name].append(callback)

    def trigger_hook(self, hook_name, *args, **kwargs):
        """Called by the core app to execute all registered plugin behaviors."""
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    # Pass arguments to the plugin hook; return values can alter core behavior
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Error executing hook {hook_name} in plugin: {e}")