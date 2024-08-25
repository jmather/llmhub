# llmhub_lib/actions.py
from llmhub_lib.app_dependency_container import AppDependencyContainer
from llmhub_lib.helpers import update_processes, start_specific_process, stop_all_processes, stop_specific_process, start_proxy_process, stop_proxy_process

service_manager = AppDependencyContainer.get("service_manager")

def start_proxy():
    start_proxy_process(service_manager)

def stop_proxy():
    stop_proxy_process(service_manager)

def start_model(model_name, quant, engine=None, context_size=4096, port=8081):
    start_specific_process(service_manager, model_name, quant, engine, context_size, port)

def stop_model(model_name):
    stop_specific_process(service_manager, model_name)

def update_all_processes():
    update_processes(service_manager)

def stop_all_models():
    stop_all_processes(service_manager)
