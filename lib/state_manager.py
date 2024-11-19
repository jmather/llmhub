import os
import json
import re
from datetime import datetime

class StateManager:
    def __init__(self, state_dir=None):
        self.state_dir = state_dir or os.path.expanduser('~/.llmhub/states')
        self._ensure_directory(self.state_dir)

    def _ensure_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def _scrub_process_name(self, process_name):
        # Replace any character that is not a letter, number, hyphen, or underscore with an underscore
        return re.sub(r'[^a-zA-Z0-9_-]', '_', process_name)

    def save_state(self, process_name, data):
        data['name'] = process_name
        scrubbed_name = self._scrub_process_name(process_name)
        state_file = os.path.join(self.state_dir, f"{scrubbed_name}.json")
        with open(state_file, 'w') as f:
            json.dump(data, f)

    def load_state(self, process_name):
        scrubbed_name = self._scrub_process_name(process_name)
        state_file = os.path.join(self.state_dir, f"{scrubbed_name}.json")
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                return json.load(f)
        return None

    def delete_state(self, process_name):
        scrubbed_name = self._scrub_process_name(process_name)
        state_file = os.path.join(self.state_dir, f"{scrubbed_name}.json")
        if os.path.exists(state_file):
            os.remove(state_file)

    def list_states(self):
        # We need to load the json files and read the 'name' property in.
        for state_file in os.listdir(self.state_dir):
            with open(os.path.join(self.state_dir, state_file), 'r') as f:
                state = json.load(f)
                yield state['name']

    def clear_all_states(self):
        for state_file in os.listdir(self.state_dir):
            self.delete_state(os.path.splitext(state_file)[0])