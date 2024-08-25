# llmhub_lib/log_manager.py
import os
from datetime import datetime, time


class LogManager:
    def __init__(self, state_manager, log_dir=None):
        self.state_manager = state_manager
        self.log_dir = log_dir or os.path.expanduser('~/.llmhub/logs')
        self._ensure_directory(self.log_dir)

    def _ensure_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def rotate_log_file(self, log_file):
        if os.path.exists(log_file):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_log_file = f"{log_file}.{timestamp}"
            os.rename(log_file, new_log_file)

    def create_log_file(self, process_name):
        log_file = os.path.join(self.log_dir, f"{process_name}.log")
        dir_name = os.path.dirname(log_file)
        os.makedirs(dir_name, exist_ok=True)
        self.rotate_log_file(log_file)
        return log_file

    def get_log_file(self, process_name):
        return os.path.join(self.log_dir, f"{process_name}.log")

    def list_logs(self):
        return [f for f in os.listdir(self.log_dir) if f.endswith('.log')]

    def tail_log(self, process_name, n=50):
        log_file = self.get_log_file(process_name)
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                return ''.join(f.readlines()[-n:])
        return None

    def follow_log(self, process_name):
        log_file = self.get_log_file(process_name)
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                f.seek(0, os.SEEK_END)
                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    yield line
        return None