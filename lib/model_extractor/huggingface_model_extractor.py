import json
import os
import re

from llmhub_lib.model_extractor.utils import find_quantization, find_version, get_model_data_from_file_name, massage_model_name


class HuggingfaceModelExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.get_model_data()

    def get_repo_uri(self):
        return self.data.get('source') + '/' + self.data.get('creator') + '/' + self.data.get(
            'model_name') + '/' + self.data.get('version') + '/' + self.data.get('quantization')

    def get_model_data(self):
        # Huggingface has json files that contain metadata about the model
        # So we should look for either config.json or adapter_config.json
        # and extract the relevant data from there

        dir_name = os.path.dirname(self.file_path)
        config_path = os.path.join(dir_name, "config.json")
        adapter_config_path = os.path.join(dir_name, "adapter_config.json")

        if os.path.exists(config_path):
            data = self.get_model_data_from_config(self.file_path, config_path)
        elif os.path.exists(adapter_config_path):
            data = self.get_model_data_from_adapter_config(self.file_path, adapter_config_path)
        else:
            data = self.get_model_data_from_path(self.file_path)

        name = data.get('model_name')
        print(f"[HuggingfaceModelExtractor] Extracted model data for {name}: {data}")
        if name.count('--') > 1:
            name = name.split('--')[0]
            data['model_name'] = name

        return data


# Example config:
# {
#   "architectures": [
#     "BertForMaskedLM"
#   ],
#   "attention_probs_dropout_prob": 0.1,
#   "gradient_checkpointing": false,
#   "hidden_act": "gelu",
#   "hidden_dropout_prob": 0.1,
#   "hidden_size": 768,
#   "initializer_range": 0.02,
#   "intermediate_size": 3072,
#   "layer_norm_eps": 1e-12,
#   "max_position_embeddings": 512,
#   "model_type": "bert",
#   "num_attention_heads": 12,
#   "num_hidden_layers": 12,
#   "pad_token_id": 0,
#   "position_embedding_type": "absolute",
#   "transformers_version": "4.6.0.dev0",
#   "type_vocab_size": 2,
#   "use_cache": true,
#   "vocab_size": 30522
# }

    def get_model_data_from_config(self, file_path, config_path):
        print(f"[HuggingfaceModelExtractor.get_model_data_from_config] Extracting model data from config: {config_path}")
        # Parse the config file to extract the model data
        with open(config_path, "r") as file:
            config = json.load(file)

        base_config = self.get_model_data_from_path(file_path)

        base_config.update({
            'model_type': config.get("model_type"),
            'version': config.get("transformers_version")
        })

        return base_config

# Example adapter_config:
# {
#   "alpha_pattern": {},
#   "auto_mapping": null,
#   "base_model_name_or_path": "google-bert/bert-large-uncased",
#   "bias": "none",
#   "fan_in_fan_out": false,
#   "inference_mode": true,
#   "init_lora_weights": true,
#   "layer_replication": null,
#   "layers_pattern": null,
#   "layers_to_transform": null,
#   "loftq_config": {},
#   "lora_alpha": 32,
#   "lora_dropout": 0.1,
#   "megatron_config": null,
#   "megatron_core": "megatron.core",
#   "modules_to_save": null,
#   "peft_type": "LORA",
#   "r": 8,
#   "rank_pattern": {},
#   "revision": null,
#   "target_modules": [
#     "query",
#     "value"
#   ],
#   "task_type": "SEQ_CLS",
#   "use_dora": false,
#   "use_rslora": false
# }
    # We also need to return the model that this adapter config is for
    def get_model_data_from_adapter_config(self, file_path, adapter_config_path):
        print(f"[HuggingfaceModelExtractor.get_model_data_from_adapter_config] Extracting model data from adapter config: {adapter_config_path}")
        # Parse the adapter config file to extract the model data
        with open(adapter_config_path, "r") as file:
            adapter_config = json.load(file)

        base_model_name = adapter_config.get("base_model_name_or_path")

        base_data = self.get_model_data_from_path(file_path)

        base_data.update({'base_model': base_model_name})

        return base_data

    # this will look like /Users/user/.cache/huggingface/hub/models--google-bert--bert-base-uncased/snapshots/86b5e0934494bd15c9632b12f734a8a67f723594/
    # we should extract 'huggingface' for source, 'google-bert' for creator, 'bert-base-uncased' for model_name, '86b5e0934494bd15c9632b12f734a8a67f723594' for version, and 'no_quant' for quantization
    def get_model_data_from_path(self, file_path):
        print(f"[HuggingfaceModelExtractor.get_model_data_from_path] Extracting model data from path: {file_path}")
        # Check to see if path has both "hub" and "snapshots" in it. If not, we just return what we can from the path
        if "hub" not in file_path and "snapshots" not in file_path:
            print(f"[HuggingfaceModelExtractor.get_model_data_from_path] Path does not contain 'hub' or 'snapshots', returning data from file name.")
            return get_model_data_from_file_name(file_path)


        path_parts = file_path.split('/')
        # now we want the segment between "hub" and "snapshots"
        hub_index = path_parts.index("hub")

        # This will look like:
        # - models--google-bert--bert-base-uncased
        # - models--leonvanbokhorst--emotion-bert-large-uncased-lora

        description = path_parts[hub_index + 1]
        description_parts = description.split("--")
        creator = description_parts[1]
        model_name = description_parts[2]
        version = find_version(model_name)
        quantization = find_quantization(file_path)
        model_name = massage_model_name(model_name, version, quantization)

        result = {
            'source': 'huggingface',
            'creator': creator,
            'model_name': model_name,
            'version': version,
            'quantization': quantization,
            'path': file_path
        }

        print(f"[HuggingfaceModelExtractor.get_model_data_from_path] Extracted model data: {result}")
        return result
