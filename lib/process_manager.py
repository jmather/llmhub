# llmhub_lib/process_manager.py
import os
import subprocess
import psutil
from .config_manager import ConfigManager
from .state_manager import StateManager
from .log_manager import LogManager

used_ports = set()  # Clear the used_ports set to start fresh


def get_next_port(used_ports, min_port, max_port):
    for port in range(min_port, max_port + 1):
        if port not in used_ports:
            used_ports.add(port)
            return port
    return None


class ProcessManager:
    def __init__(self, config_manager: ConfigManager, state_manager: StateManager, log_manager: LogManager):
        self.config_manager = config_manager
        self.state_manager = state_manager
        self.log_manager = log_manager

    def generate_expected_processes(self, config=None):
        fresh_used_ports = set()  # Clear the used_ports set to start fresh

        config = config or self.config_manager.get_merged_config()
        expected_processes = {}

        for model_name, start_config in config['on_start'].items():
            quant_name = start_config['quant']
            context_sizes = start_config.get('context_size', [])
            if not context_sizes:
                context_sizes = [config['default_context_size']]
            quant_path = config['models'][model_name]['gguf'][quant_name]

            for context_size in context_sizes:
                process_name = f"{model_name}-{quant_name}-{context_size}"
                engine_name = start_config.get('engine', None)
                if not engine_name:
                    engine_name = next(iter(config['engines']))

                engine_config = config['engines'][engine_name]
                port = get_next_port(fresh_used_ports, config['engine_port_min'], config['engine_port_max'])
                fresh_used_ports.add(port)
                cmd = [
                    engine_config['path'],
                    *engine_config['arguments'].split(),
                    engine_config['model_flag'], quant_path,
                    engine_config['context_size_flag'], str(context_size),
                    engine_config['port_flag'], str(port)
                ]

                expected_processes[process_name] = (cmd, port)

        # Add the proxy process if enabled
        if config.get('enable_proxy', False):
            web_port = config.get('port', 5000)
            proxy_process_name = f"proxy-{web_port}"
            proxy_cmd = ["python", "web_server.py"]
            expected_processes[proxy_process_name] = (proxy_cmd, web_port)

        return expected_processes

    def estimate_memory_usage(self, config=None):
        """Estimate the memory usage for each defined model in on_start."""
        memory_usage = {}
        model_sizes = {}

        config = config or self.config_manager.get_global_config()

        for model_name, start_config in config['on_start'].items():
            quant_name = start_config['quant']
            context_sizes = start_config.get('context_size', [])
            quant_path = config['models'][model_name]['gguf'][quant_name]

            model_file_path = f"{self.config_manager.get_model_directory()}/{quant_path}"
            model_size = os.path.getsize(model_file_path) / (1024 * 1024)  # Convert to MB
            model_sizes[model_name] = model_size

            for context_size in context_sizes:
                # Memory usage for a single process is the model size (shared) plus context size (unique)
                context_memory = (context_size * 1.5 / 1024)  # Convert context size to MB
                process_name = f"{model_name}-{quant_name}-{context_size}"
                memory_usage[process_name] = (model_size, context_memory)

        return memory_usage, model_sizes

    def start_process(self, cmd, process_name, port):
        log_file = self.log_manager.create_log_file(process_name)

        print(f"Starting process {process_name} with command: {' '.join(cmd)}")

        with open(log_file, 'a') as log:
            process = subprocess.Popen(cmd, stdout=log, stderr=log)
            self.state_manager.save_state(process_name, {"pid": process.pid, "port": port})
            print(f"Process {process_name} started with PID {process.pid} on port {port}")
            return process.pid

    def stop_process(self, process_name):
        state = self.state_manager.load_state(process_name)
        if state:
            pid = state['pid']
            try:
                p = psutil.Process(pid)
                p.terminate()
                p.wait()
                self.state_manager.delete_state(process_name)
                return pid
            except psutil.NoSuchProcess:
                self.state_manager.delete_state(process_name)
                return None
        return None

    def update_processes(self):
        """Update and restart all configured processes."""
        config = self.config_manager.get_merged_config()
        expected_processes = self.generate_expected_processes(config)

        running_processes = set(self.state_manager.list_states())

        for process_name, (cmd, port) in expected_processes.items():
            if process_name in running_processes:
                state = self.state_manager.load_state(process_name)
                current_cmd = subprocess.list2cmdline(cmd)
                try:
                    process = psutil.Process(state['pid'])
                    running_cmd = subprocess.list2cmdline(process.cmdline())

                    # For the proxy process, just check if it's running; don't compare the command
                    if process_name.startswith("proxy"):
                        if process.is_running():
                            print(f"Proxy process {process_name} is already running with the correct configuration.")
                            continue
                    else:
                        # For other processes, check if command matches
                        if process.is_running() and current_cmd == running_cmd:
                            print(f"Process {process_name} is already running with the correct configuration.")
                            continue

                    print(f"Restarting {process_name} due to configuration change.")
                    self.stop_process(process_name)
                except psutil.NoSuchProcess:
                    print(f"Process {process_name} not found, restarting it.")
            self.start_process(cmd, process_name, port)

        for process_name in running_processes:
            if process_name not in expected_processes:
                self.stop_process(process_name)

        print("Processes updated.")

    def display_status(self, expected_processes):
        """Display the status of the expected processes."""
        running_processes = set(self.state_manager.list_states())
        seen = set()

        for process_name, (cmd, port) in expected_processes.items():
            seen.add(process_name)
            if process_name in running_processes:
                print(f"{process_name} is running on port {port}.")
            else:
                print(f"{process_name} is not running.")

        for process_name in running_processes:
            if process_name not in seen:
                print(f"{process_name} is running but not expected.")

    def stop_all_processes(self):
        """Stop all running processes."""
        running_processes = self.state_manager.list_states()
        if not running_processes:
            print("No running processes to stop.")
        else:
            for process_name in running_processes:
                self.stop_process(process_name)
                print(f"Stopped process {process_name}.")