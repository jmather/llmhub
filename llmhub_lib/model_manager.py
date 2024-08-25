import os
import glob
import yaml
from .config_manager import ConfigManager
from .state_manager import StateManager
from .model_extractor import extract_model


MODEL_EXTENSIONS = ["*.bin", "*.safetensors", "*.gguf"]


def combine_model_data(current_model_data, model_data):
    # first we determine file type
    file_type = model_data.get("path").split(".")[-1]
    if file_type == "safetensors":
        current_model_data['safetensors'] = model_data.get("path")
    elif file_type == "coreml":
        current_model_data['coreml'] = model_data.get("path")
    elif file_type == "gguf":
        current_model_data.setdefault('gguf', {})[model_data.get("quantization")] = model_data.get("path")
    elif file_type == "onnx":
        current_model_data['onnx'] = model_data.get("path")




class ModelManager:
    def __init__(self, config_manager: ConfigManager, state_manager: StateManager):
        self.config_manager = config_manager
        self.state_manager = state_manager

    def get_running_processes(self):
        """Get the list of running processes related to models."""
        return self.state_manager.list_states()

    def match_model(self, model_name):
        """Match a given model name to a running process, if any."""
        running_processes = self.get_running_processes()
        matched_process = None
        for process_name in running_processes:
            if process_name.startswith(model_name):
                matched_process = process_name
                break

        if not matched_process:
            available_models = [process.split('-')[0] for process in running_processes]
            return None, available_models

        return matched_process, None

    def match_model_name(self, model_name):
        """Match a given model name to a known model, if any."""
        models = self.list_models()
        matched_model = None
        for model in models:
            if model['id'].startswith(model_name):
                matched_model = model
                break

        if not matched_model:
            available_models = [model['id'] for model in models]
            return None, available_models

        return matched_model, None

    def list_models(self):
        """List all models from the configuration along with their running status."""
        config = self.config_manager.get_global_config()
        running_processes = self.state_manager.list_states()
        available_models = []

        for model_name, model_config in config.get('models', {}).items():
            for file_type, quant_paths in model_config.items():
                # Ensure quant_paths is a dictionary
                if isinstance(quant_paths, dict):
                    for quant_name, quant_path in quant_paths.items():
                        process_name = f"{model_name}-{quant_name}"
                        status = "running" if process_name in running_processes else "stopped"
                        available_models.append({
                            "id": process_name,
                            "object": "model",
                            "status": status,
                            "file_type": file_type
                        })
                else:
                    # Handle the case where quant_paths is not a dictionary
                    print(f"Warning: Expected dict for quant_paths, but got {type(quant_paths).__name__}")
                    continue

        return available_models

    def find_and_update_models(self):
        """Find models in the search paths and update the internal models dictionary."""
        model_search_paths = self.config_manager.get_merged_config().get('model_search_paths', [])
        # now we expand the user paths
        paths = [os.path.expanduser(path) for path in model_search_paths]

        print(f"[Search] Searching in: {paths}")
        models = {}

        followup_models = []

        for search_path in paths:
            # We use glob and EXTENSIONS to search for all model files
            for ext in MODEL_EXTENSIONS:
                print(f"[Search] Searching for: {search_path}/**/{ext}")
                for path in glob.glob(f"{search_path}/**/{ext}", recursive=True):
                    print(f"[Search] Found model file: {path}")
                    model_data = extract_model(path)
                    print(f"[Result] Model data extracted from {path}: {model_data}")

                    if model_data.get('base_model'):
                        print(f"[Debug] Found a model with a base model: {model_data}, deferring for later processing.")
                        followup_models.append(model_data)
                        continue

                    model_name_key = model_data.get('creator') + '/' + model_data.get('model_name')
                    current_model_data = models.get(model_name_key, {})
                    combine_model_data(current_model_data, model_data)
                    models.update({model_name_key: current_model_data})

                    # Debug output to ensure the model data is being populated
                    print(f"[Debug] Current model data for {model_name_key}: {models[model_name_key]}")

        # Now we process the followup models
        for model_data in followup_models:
            base_model_name = model_data.get('base_model')
            base_model = models.get(base_model_name, {})
            base_model_loras = base_model.get('loras', {})
            model_name = model_data.get('creator') + '/' + model_data.get('model_name')
            base_model_loras.update({model_name: model_data.get('path')})
            base_model.update({'loras': base_model_loras})
            models.update({base_model_name: base_model})

        print(f"[Result] Final models dictionary: {models}")
        self.save_models_to_yaml(models)

    def save_models_to_yaml(self, models):
        """Save the discovered models to a YAML file."""
        models_file_path = os.path.expanduser('~/.llmhub/models.yaml')
        with open(models_file_path, 'w') as f:
            yaml.dump(models, f)
        print(f"[Save] Models found, saving to {models_file_path}")