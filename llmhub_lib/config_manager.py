# llmhub_lib/config_manager.py
import yaml
import os

class ConfigManager:
    def __init__(self, global_config_path="~/.llmhub/config.yaml", overlay_config_path=None):
        self.global_config_path = os.path.expanduser(global_config_path)
        self.overlay_config_path = overlay_config_path
        self.global_config = self.load_config(self.global_config_path)
        self.global_config = self.merge_configs(self.get_default_config(), self.global_config)
        self.model_config_path = os.path.expanduser(self.global_config.get('model_config_path', "~/.llmhub/models.yaml"))
        self.model_config = self.load_config(self.model_config_path)
        self.global_config['models'] = self.model_config
        self.overlay_config = self.load_config(self.overlay_config_path) if overlay_config_path else {}
        self.merged_config = self.merge_configs(self.global_config, self.overlay_config)

    def load_config(self, path):
        if path and os.path.exists(path):
            with open(path, 'r') as file:
                return yaml.safe_load(file)
        return {}

    def merge_configs(self, global_config, overlay_config):
        merged_config = global_config.copy()
        merged_config.update(overlay_config)
        return merged_config

    def get_global_config(self):
        return self.global_config

    def get_overlay_config(self):
        return self.overlay_config

    def get_merged_config(self):
        return self.merged_config

    def save_config(self, filepath, config):
        with open(filepath, 'w') as file:
            yaml.safe_dump(config, file)

    def update_overlay_config(self, new_config):
        self.overlay_config.update(new_config)
        self.merged_config = self.merge_configs(self.global_config, self.overlay_config)

    def save_overlay_config(self):
        if self.overlay_config_path:
            self.save_config(self.overlay_config_path, self.overlay_config)
        else:
            raise ValueError("Overlay config path not set.")

    def get_default_config(self):
        return {
            "model_search_paths": [
                "~/.cache/lm-studio/models",
                "~/.cache/huggingface/hub"
            ],
            "default_context_size": 4196,
            "engine_port_min": 8081,
            "engine_port_max": 9999,
            "on_start": {},
            "models": {},
            "engines": {},
            "enable_proxy": False,
            "port": 8080
        }