# actions.py
import sys

from .app_dependency_container import AppDependencyContainer
from llmhub_lib import web_server
from pathlib import Path

config_manager = AppDependencyContainer.get("config_manager")
state_manager = AppDependencyContainer.get("state_manager")
log_manager = AppDependencyContainer.get("log_manager")
process_manager = AppDependencyContainer.get("process_manager")
model_manager = AppDependencyContainer.get("model_manager")


def start_proxy_process():
    """Start the proxy (web server) process if not already running."""
    config = config_manager.get_merged_config
    if config.get('enable_proxy', False):
        web_port = config.get('port', 5000)
        proxy_process_name = f"proxy-{web_port}"
        running_processes = state_manager.list_states

        if proxy_process_name not in running_processes:
            # Dynamically determine the location of web_server.py
            script_path = Path(web_server.__file__).resolve()
            proxy_cmd = [sys.executable, str(script_path)]
            print(f"Attempting to start proxy process: {proxy_cmd} on port {web_port}")
            process_manager.start_process(proxy_cmd, proxy_process_name, web_port)
            print(f"Proxy process {proxy_process_name} should now be running.")
        else:
            print(f"Proxy process {proxy_process_name} is already running.")
    else:
        print("Proxy is disabled in the configuration.")


def stop_proxy_process():
    """Stop the proxy (web server) process if it is running."""
    config = config_manager.get_merged_config()
    if config.get('enable_proxy', False):
        web_port = config.get('port', 5000)
        proxy_process_name = f"proxy-{web_port}"
        running_processes = state_manager.list_states()
        if proxy_process_name in running_processes:
            print(f"Stopping proxy process: {proxy_process_name}")
            process_manager.stop_process(proxy_process_name)
        else:
            print(f"Proxy process {proxy_process_name} is not running.")
    else:
        print("Proxy is disabled in the configuration.")


def start_specific_process(model_name, quant, engine=None, context_size=4096, port=8081):
    """Start a specific model process."""
    config = config_manager.get_merged_config()

    if not engine:
        engine = next(iter(config['engines']))  # Default to the first engine if not provided

    engine_config = config['engines'][engine]
    quant_path = config['models'][model_name]['gguf'].get(quant)
    if not quant_path:
        raise ValueError(f"Quantization {quant} not found for model {model_name}.")

    model_path = f"{config['model_directories']['lm_studio']}/{quant_path}"

    cmd = [
        engine_config['path'],
        *engine_config['arguments'].split(),
        engine_config['model_flag'], model_path,
        engine_config['context_size_flag'], str(context_size),
        engine_config['port_flag'], str(port)
    ]

    process_manager.start_process(cmd, f"{model_name}-{quant}-{context_size}", port)


def update_processes():
    """Update and restart all configured processes."""
    process_manager.update_processes()


def stop_all_processes():
    """Stop all running processes."""
    process_manager.stop_all_processes()


def stop_specific_process(model_name):
    """Stop a specific process."""
    process_manager.stop_process(model_name)


def start_model(model_name):
    expected_processes = process_manager.generate_expected_processes()
    if model_name:
        matches = [model for model in expected_processes.keys() if model_name in model]
        if len(matches) == 0:
            raise ValueError(f"Model {model_name} not found in the expected processes.")
        for model in matches:
            (cmd, port) = expected_processes[model]
            process_manager.start_process(cmd, model, port)
    else:
        for model_name, (cmd, port) in expected_processes.items():
            process_manager.start_process(cmd, model_name, port)


def get_matching_expected_processes(model_name):
    expected_processes = process_manager.generate_expected_processes()
    return {model: (cmd, port) for model, (cmd, port) in expected_processes.items() if model_name in model}


def get_matching_running_processes(model_name):
    running_processes = state_manager.list_states()
    return [proc_name for proc_name in running_processes if model_name in proc_name]


def stop_model(model_name):
    if not model_name:
        process_manager.stop_all_processes()
        return

    matched_procs = get_matching_expected_processes(model_name)

    for proc_name, (cmd, port) in matched_procs.items():
        process_manager.stop_process(proc_name)

    if matched_procs:
        print(f"Stopped processes: {', '.join(matched_procs)}")
        return

    matched_proc = get_matching_running_processes(model_name)
    if not matched_proc:
        print(f"No running processes found for model {model_name}")
        return
    for proc_name in matched_proc:
        process_manager.stop_process(proc_name)