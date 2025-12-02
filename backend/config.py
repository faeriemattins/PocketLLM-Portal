import json
import os

CONFIG_FILE = "config.json"

class ConfigManager:
    def __init__(self):
        self.config = {
            "max_prompts": 20,
            "max_cached_sessions": 10,
            "safety_enabled": True,
            "default_temperature": 0.7,
            "default_top_p": 0.9,
            "default_max_tokens": 2048,
            "system_prompt": "You are a helpful AI assistant."
        }
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

config_manager = ConfigManager()
