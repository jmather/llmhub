import click
from llmhub_lib.app_dependency_container import AppDependencyContainer
from llmhub_lib.helpers import start_proxy_process, stop_proxy_process

service_manager = AppDependencyContainer.get("service_manager")

@click.command()
@click.argument('model_name', required=False)
def start(model_name=None):
    """Start a specific model process or all processes if no model_name is provided."""
    if model_name.startswith("proxy-"):
        start_proxy_process(service_manager)
    elif model_name:
        service_manager.start_service(model_name, quant="Q5_K_M")  # Example quant value
    else:
        service_manager.update_services()

@click.command()
@click.argument('model_name', required=False)
def stop(model_name=None):
    """Stop a specific process or all processes if no model_name is provided."""
    # Stop the proxy process if the model_name starts with "proxy-"
    if model_name.startswith("proxy-"):
        stop_proxy_process(service_manager)
    elif model_name:
        service_manager.stop_service(model_name)
    else:
        service_manager.stop_all_services()

@click.command()
@click.argument('model_name', required=False)
def restart(model_name=None):
    """Restart a specific process or all processes if no model_name is provided."""
    if model_name.startswith("proxy-"):
        stop_proxy_process(service_manager)
        start_proxy_process(service_manager)
    elif model_name:
        service_manager.stop_service(model_name)
        service_manager.start_service(model_name, quant="Q5_K_M")  # Example quant value
    else:
        service_manager.stop_all_services()
        service_manager.update_services()

@click.command()
def update():
    """Update and restart all configured processes."""
    service_manager.update_services()
